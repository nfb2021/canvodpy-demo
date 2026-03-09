import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium", css_file="canvod_nordic.css")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        r"""
    # canvod-readers — RINEX File Parsing

    The **canvod-readers** package converts raw GNSS observation files into
    structured `xarray.Dataset` objects.  It supports RINEX v3.04 and
    Septentrio SBF binary formats.

    This notebook explores a single RINEX file in detail: the header,
    observation structure, signal IDs, and the dataset contract that all
    downstream packages rely on.

    ---

    *Nicolas F. Bader, CLIMERS — TU Wien*
    *Licensed under Apache 2.0.  Provided "as is" without warranty of any kind.*
    """
    )


@app.cell
def _():
    from pathlib import Path

    import numpy as np

    return Path, np


@app.cell
def _(Path):
    _root = Path(__file__).resolve().parent.parent
    _test_data = _root / "packages" / "canvod-readers" / "tests" / "test_data" / "valid"
    RINEX_DIR = (
        _test_data / "rinex_v3_04" / "01_Rosalia" / "02_canopy" / "01_GNSS" / "01_raw" / "25001"
    )
    SAMPLE_FILE = sorted(RINEX_DIR.glob("*.rnx"))[0]

    return RINEX_DIR, SAMPLE_FILE


# ---------------------------------------------------------------------------
# Parse a single file
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Parsing a RINEX File

    The `Rnxv3Obs` reader takes a file path, parses the RINEX v3.04 header
    and observation blocks, and produces an `xarray.Dataset`.
    """
    )


@app.cell
def _(SAMPLE_FILE):
    from canvod.readers import Rnxv3Obs

    reader = Rnxv3Obs(fpath=SAMPLE_FILE)
    ds = reader.to_ds()

    return Rnxv3Obs, ds, reader


@app.cell
def _(SAMPLE_FILE, mo):
    mo.md(f"Parsed: `{SAMPLE_FILE.name}`")


# ---------------------------------------------------------------------------
# RINEX Header
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## RINEX Header

    The header contains receiver metadata, approximate position, observation
    types per constellation, and timing information.
    """
    )


@app.cell
def _(mo, reader):
    _h = reader.header
    _pos = _h.approx_position

    mo.md(f"""
| Field | Value |
|---|---|
| RINEX version | {_h.version} |
| Marker name | `{_h.marker_name}` |
| Receiver type | {getattr(_h, 'rec_type', '—')} |
| Approx position (ECEF) | X={_pos[0]:.2f}, Y={_pos[1]:.2f}, Z={_pos[2]:.2f} |
| Interval | {getattr(_h, 'interval', '—')} s |
| First obs | {getattr(_h, 'time_of_first_obs', '—')} |
| Systems | {', '.join(getattr(_h, 'sys_obs_types', {}).keys())} |
""")


# ---------------------------------------------------------------------------
# Dataset Structure
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Dataset Structure

    Every reader produces a dataset with the same contract:

    - **Dimensions:** `(epoch, sid)` — time steps x signal IDs
    - **Coordinates:** `epoch`, `sid`, `sv`, `system`, `band`, `code`,
      `freq_center`, `freq_min`, `freq_max`
    - **Variables:** `SNR` (signal-to-noise ratio) at minimum
    - **Attributes:** `File Hash`, `Created`, `Software`, `Institution`
    """
    )


@app.cell
def _(ds, mo):
    mo.md(f"""
### Dimensions

| Dimension | Size | Description |
|---|---|---|
| `epoch` | {ds.sizes['epoch']:,} | Time steps ({ds.sizes['epoch'] * 5 / 60:.0f} min at 5 s sampling) |
| `sid` | {ds.sizes['sid']:,} | Unique signal IDs across all constellations |

### Coordinates

| Coordinate | dtype | Sample values |
|---|---|---|
| `epoch` | `{ds.epoch.dtype}` | {str(ds.epoch.values[0])[:19]} … {str(ds.epoch.values[-1])[:19]} |
| `sid` | `{ds.sid.dtype}` | `{ds.sid.values[0]}`, `{ds.sid.values[1]}`, … |
| `sv` | `{ds.sv.dtype}` | `{ds.sv.values[0]}`, `{ds.sv.values[1]}`, … |
| `system` | `{ds.system.dtype}` | {', '.join(f'`{s}`' for s in sorted(str(v) for v in set(ds.system.values)))} |
| `band` | `{ds.band.dtype}` | {', '.join(f'`{b}`' for b in sorted(str(v) for v in set(ds.band.values))[:8])} … |
| `freq_center` | `{ds.freq_center.dtype}` | {ds.freq_center.values[0]:.1f} … {ds.freq_center.values[-1]:.1f} MHz |

### Data Variables

| Variable | Shape | dtype |
|---|---|---|
""" + "\n".join(
        f"| `{name}` | {tuple(ds[name].dims)} | `{ds[name].dtype}` |"
        for name in ds.data_vars
    ))


# ---------------------------------------------------------------------------
# Signal IDs
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Signal IDs (SIDs)

    Each SID uniquely identifies a GNSS signal: `PRN|Band|Code`.

    - **PRN** — Constellation prefix + satellite number (e.g. `G01` = GPS PRN 01)
    - **Band** — Frequency band (e.g. `L1`, `E5a`, `B1I`)
    - **Code** — Tracking mode (e.g. `C` = C/A, `W` = P(Y), `Q` = pilot)

    The SID coordinate carries all the information needed to filter by
    constellation, satellite, frequency, or tracking mode.
    """
    )


@app.cell
def _(ds, mo):
    _systems = ds.system.values
    _counts = {}
    for _s in _systems:
        _counts[str(_s)] = _counts.get(str(_s), 0) + 1

    _prefixes = {
        "G": "GPS", "E": "Galileo", "R": "GLONASS", "C": "BeiDou",
        "I": "IRNSS", "S": "SBAS", "J": "QZSS",
    }

    _rows = "\n".join(
        f"| {_prefixes.get(k, k)} (`{k}`) | {v} |"
        for k, v in sorted(_counts.items())
    )

    mo.md(f"""
### Signals per Constellation

| Constellation | SID count |
|---|---|
{_rows}
| **Total** | **{len(_systems)}** |
""")


# ---------------------------------------------------------------------------
# SNR Overview
# ---------------------------------------------------------------------------


@app.cell
def _(ds, mo, np):
    _snr = ds["SNR"].values
    _valid = np.isfinite(_snr)
    _pct = 100 * _valid.sum() / _valid.size

    mo.md(f"""
## SNR Overview

| Metric | Value |
|---|---|
| Total observations | {_snr.size:,} |
| Valid (non-NaN) | {_valid.sum():,} ({_pct:.1f}%) |
| Mean SNR | {np.nanmean(_snr):.1f} dB-Hz |
| Std SNR | {np.nanstd(_snr):.1f} dB-Hz |
| Range | {np.nanmin(_snr):.1f} — {np.nanmax(_snr):.1f} dB-Hz |

NaN values correspond to epochs where a satellite was not visible or the
signal was below the receiver's tracking threshold.
""")


# ---------------------------------------------------------------------------
# Dataset Contract
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Dataset Contract & Validation

    The `validate_dataset()` function checks that a dataset meets the
    contract expected by all downstream packages (store, auxiliary, vod).
    """
    )


@app.cell
def _(ds, mo):
    from canvod.readers import validate_dataset

    _issues = validate_dataset(ds)
    _status = "PASS" if not _issues else f"FAIL ({len(_issues)} issues)"

    mo.md(f"Validation: **{_status}**")

    return (validate_dataset,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ---

    *canVODpy — CLIMERS, TU Wien | Apache 2.0 | No warranty*
    """
    )


if __name__ == "__main__":
    app.run()
