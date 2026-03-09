import marimo

__generated_with = "0.20.1"
app = marimo.App(width="medium", css_file="canvod_nordic.css")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # RINEX Reader

    `canvod-readers` parses RINEX v3 observation files into `xarray.Dataset` objects
    with a **two-dimensional** structure: `(epoch, sid)`.

    **Signal ID (SID)** encodes satellite PRN, carrier band and ranging code in a
    single coordinate string — e.g. `G07|L1|C` is GPS PRN 07 on L1, C-code.
    This avoids a 4-D array that would be mostly NaN.

    ## Sections

    1. Locate test data
    2. Inspect a RINEX file object (header, epochs)
    3. Convert to `xr.Dataset` with `to_ds()`
    4. Dataset structure: dimensions, coordinates, variables, attributes
    5. Load several files and concatenate
    6. Select subsets by SID
    """)
    return


@app.cell
def _():
    from pathlib import Path

    # Test data bundled with canvod-readers
    _TEST_DATA = (
        Path(__file__).resolve().parent.parent
        / "packages"
        / "canvod-readers"
        / "tests"
        / "test_data"
        / "valid"
        / "rinex_v3_04"
        / "01_Rosalia"
        / "02_canopy"
        / "01_GNSS"
        / "01_raw"
        / "25001"
    )

    RINEX_FILES = sorted(_TEST_DATA.glob("*.25o"))
    RINEX_FILES
    return (RINEX_FILES,)


@app.cell
def _(RINEX_FILES, mo):
    mo.md(f"""
    Found **{len(RINEX_FILES)} RINEX files** in the test data directory.

    Each file covers **15 minutes** of observations from the Rosalia canopy receiver
    (DOY 2025-001, Rosalia forest research site, Austria).

    First file: `{RINEX_FILES[0].name}`
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 1 — Inspect a RINEX file object

    `Rnxv3Obs` parses the RINEX v3 file header and index on construction.
    The raw epoch data is read lazily.
    """)
    return


@app.cell
def _(RINEX_FILES):
    from canvod.readers import Rnxv3Obs

    obs = Rnxv3Obs(fpath=RINEX_FILES[0])
    obs
    return obs, Rnxv3Obs


@app.cell
def _(mo, obs):
    mo.md(f"""
    The **header** holds all RINEX metadata:

    | Field | Value |
    |-------|-------|
    | RINEX version | `{obs.header.rinex_version}` |
    | Receiver type | `{obs.header.rec_type}` |
    | Marker name | `{obs.header.marker_name}` |
    | Approx. position | `{obs.header.approx_position}` |
    | Interval | `{obs.header.interval}` s |
    | Observation types | `{obs.header.obs_types}` |
    """)
    return


@app.cell
def _(obs):
    # The header's approx_position is a named dataclass
    obs.header.approx_position
    return


@app.cell
def _(mo, obs):
    mo.md(f"""
    ### Epochs

    The file contains **{len(obs.epochs)} epochs** at `{obs.infer_sampling_interval()} s` sampling.

    Each epoch is an `Rnxv3ObsEpochRecord` with:
    - `timestamp` — UTC datetime
    - `data` — list of per-satellite observations
    - `info` — the epoch header line (receiver clock offset, flags…)
    """)
    return


@app.cell
def _(obs):
    # First epoch
    obs.epochs[0]
    return


@app.cell
def _(obs):
    # First satellite in first epoch
    obs.epochs[0].data[0]
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 2 — Convert to `xr.Dataset` with `to_ds()`

    `to_ds()` assembles all epochs into a 2-D array `(epoch, sid)`.

    By default only **SNR** is included. Pass `keep_data_vars` to request
    additional observation types.  The returned dataset carries full CF-convention
    metadata on every dimension, coordinate and variable.
    """)
    return


@app.cell
def _(obs):
    ds_snr = obs.to_ds(
        keep_data_vars=["SNR"],
        write_global_attrs=True,
    )
    ds_snr
    return (ds_snr,)


@app.cell
def _(mo, ds_snr):
    mo.md(f"""
    ### Dataset at a glance

    | Item | Value |
    |------|-------|
    | Dimensions | `{dict(ds_snr.sizes)}` |
    | Epochs | **{ds_snr.sizes["epoch"]}** × 30 s = {ds_snr.sizes["epoch"] * 30 // 60} min |
    | Signal IDs | **{ds_snr.sizes["sid"]}** unique `SV|Band|Code` combinations |
    | Data variables | `{list(ds_snr.data_vars)}` |
    | Global attribute "File Hash" | `{ds_snr.attrs.get("File Hash", "n/a")}` |
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### All four observation types

    `Pseudorange`, `Phase`, `Doppler` and `LLI`/`SSI` can be requested.
    The dimension stays the same — more data variables are added.
    """)
    return


@app.cell
def _(obs):
    ds_full = obs.to_ds(
        keep_data_vars=["SNR", "Pseudorange", "Phase", "Doppler"],
        write_global_attrs=True,
    )
    ds_full
    return (ds_full,)


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 3 — Dataset structure in detail

    ### Coordinates

    - **`epoch`** — `datetime64[ns]` UTC timestamps
    - **`sid`** — Signal ID strings, format `SV|Band|Code`

    ### Data variable attributes

    Each variable carries CF-convention attrs:
    - `long_name`, `units`, `standard_name` (where applicable)
    - `source`, `comment`, `references`
    """)
    return


@app.cell
def _(ds_full):
    # Attributes of the SNR variable
    ds_full["SNR"].attrs
    return


@app.cell
def _(ds_full):
    # Some example SID values
    ds_full.sid.values[:20]
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 4 — Concatenate several files

    Load all test files and concatenate along the `epoch` dimension.
    """)
    return


@app.cell
def _(RINEX_FILES, Rnxv3Obs):
    import xarray as xr

    _datasets = [
        Rnxv3Obs(fpath=f).to_ds(keep_data_vars=["SNR"], write_global_attrs=True)
        for f in RINEX_FILES
    ]

    daily_ds = xr.concat(
        _datasets,
        dim="epoch",
        join="outer",
        coords="different",
    ).sortby("epoch")

    daily_ds
    return daily_ds, xr


@app.cell
def _(daily_ds, mo):
    mo.md(f"""
    ### Concatenated dataset

    | Item | Value |
    |------|-------|
    | Files | {len([1 for _ in range(1)])} per 15 min → {daily_ds.sizes["epoch"]} epochs total |
    | Time span | `{str(daily_ds.epoch.min().values)[:19]}` → `{str(daily_ds.epoch.max().values)[:19]}` |
    | SIDs | {daily_ds.sizes["sid"]} |
    | Missing data | NaN where satellite not observed |
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 5 — Select subsets by SID

    The SID string `SV|Band|Code` makes filtering intuitive:

    | Filter | Example |
    |--------|---------|
    | Specific satellite | `sid.str.startswith("G07")` |
    | All on L1C band | `sid.str.contains("\|L1C\|")` |
    | Only C-code | `sid.str.endswith("C")` |
    | All GPS | `sid.str.startswith("G")` |
    | All GLONASS | `sid.str.startswith("R")` |
    | All Galileo | `sid.str.startswith("E")` |
    """)
    return


@app.cell
def _(daily_ds):
    # All GPS satellites
    ds_gps = daily_ds.sel(sid=[s for s in daily_ds.sid.values if s.startswith("G")])
    ds_gps.sid.values
    return (ds_gps,)


@app.cell
def _(daily_ds):
    # All signals on any L1 band (L1C, L1X, L1W…)
    ds_l1 = daily_ds.sel(sid=[s for s in daily_ds.sid.values if "|L1" in s])
    ds_l1.sid.values
    return (ds_l1,)


@app.cell
def _(daily_ds):
    # GPS L1C specifically
    ds_gps_l1c = daily_ds.sel(
        sid=[s for s in daily_ds.sid.values if s.startswith("G") and "|L1C|" in s]
    )
    ds_gps_l1c.sid.values
    return (ds_gps_l1c,)


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 6 — Visualise: mean SNR time series

    Average SNR across GPS L1C signals over the observation period.
    """)
    return


@app.cell
def _(ds_gps_l1c):
    import matplotlib.pyplot as plt
    import numpy as np

    # Mean SNR across all GPS L1C signals (ignore NaN)
    _mean_snr = ds_gps_l1c["SNR"].mean(dim="sid", skipna=True)

    _fig, _ax = plt.subplots(figsize=(10, 4), constrained_layout=True)
    _ax.plot(
        _mean_snr.epoch.values,
        _mean_snr.values,
        lw=1.5,
        color="steelblue",
    )
    _ax.set_xlabel("Epoch (UTC)")
    _ax.set_ylabel("Mean SNR [dB-Hz]")
    _ax.set_title("Mean GPS L1C SNR — Rosalia canopy receiver, DOY 2025-001")
    _ax.grid(True, alpha=0.3)
    plt.gcf()
    return np, plt


@app.cell
def _(ds_gps_l1c, plt):
    # Per-satellite SNR waterfall (heatmap)
    _snr = ds_gps_l1c["SNR"]

    _fig, _ax = plt.subplots(figsize=(12, 5), constrained_layout=True)
    _im = _ax.imshow(
        _snr.values.T,
        aspect="auto",
        origin="lower",
        vmin=20,
        vmax=55,
        cmap="plasma",
    )
    _ax.set_xlabel("Epoch index")
    _ax.set_ylabel("GPS L1C signal")
    _ax.set_yticks(range(len(_snr.sid)))
    _ax.set_yticklabels(_snr.sid.values, fontsize=7)
    _ax.set_title("GPS L1C SNR — Rosalia canopy, DOY 2025-001")
    plt.colorbar(_im, ax=_ax, label="SNR [dB-Hz]")
    plt.gcf()
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## Summary

    | What | How |
    |------|-----|
    | Load a RINEX file | `Rnxv3Obs(fpath=...)` |
    | Inspect header | `.header` |
    | Convert to xarray | `.to_ds(keep_data_vars=[...])` |
    | Concatenate files | `xr.concat([ds1, ds2, ...], dim="epoch")` |
    | Select by satellite | `ds.sel(sid=[s for s in ds.sid.values if s.startswith("G")])` |
    | Select by band | `ds.sel(sid=[s for s in ds.sid.values if "|L1C|" in s])` |

    **Next:** Open `02_sbf_reader.py` to see how the Septentrio SBF binary
    format is read and how the additional geometry metadata (θ, φ) is extracted.
    """)
    return


if __name__ == "__main__":
    app.run()
