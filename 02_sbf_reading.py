import marimo

__generated_with = "0.12.0"
app = marimo.App(width="medium", app_title="SBF Binary Reading", css_file="canvod_nordic.css")


# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # SBF Binary Reading

    This notebook demonstrates how to read **Septentrio Binary Format (SBF)**
    files using the `SbfReader` class from **canvod-readers**.

    SBF is the proprietary binary format produced by Septentrio GNSS receivers
    (e.g. PolaRx5, AsteRx).  Unlike the ASCII-based RINEX format, SBF stores
    observations as packed binary blocks, which makes it more compact and
    faster to write in real-time.  Each SBF file contains the same
    fundamental observables as its RINEX counterpart — pseudorange, carrier
    phase, Doppler, and SNR — but also includes **receiver-computed
    metadata** that RINEX does not carry:

    - **Satellite visibility** (azimuth and elevation from the receiver firmware)
    - **DOP values** (PDOP, HDOP, VDOP) per epoch
    - **PVT solution** (receiver position, velocity, time)
    - **Multipath corrections** and signal quality indicators

    The `SbfReader` produces the same `xarray.Dataset` with `(epoch, sid)`
    dimensions as the RINEX reader, satisfying the same data contract.
    Additionally, it can extract the receiver-computed metadata into a
    separate `sbf_obs` dataset via `to_ds_and_auxiliary()`.

    ---

    **Test data**: DOY 2025-001, SBF files per receiver (canopy and reference).

    """
    )

    return (mo,)


# ---------------------------------------------------------------------------
# Imports and paths
# ---------------------------------------------------------------------------


@app.cell
def _():
    from pathlib import Path

    from _paths import SBF_CANOPY_DIR, SBF_REFERENCE_DIR

    return Path, SBF_CANOPY_DIR, SBF_REFERENCE_DIR


# ---------------------------------------------------------------------------
# Section: SBF vs RINEX
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## SBF vs RINEX: format comparison

    Both formats encode the same fundamental GNSS observables, but they
    differ in representation and in what additional information is available.

    | Property | RINEX v3.04 | SBF |
    |----------|-------------|-----|
    | **Encoding** | Fixed-width ASCII | Packed binary blocks |
    | **SNR quantization** | ~0.001 dB | 0.25 dB |
    | **Satellite geometry** | Not included | Firmware-computed azimuth, elevation |
    | **DOP values** | Not included | PDOP, HDOP, VDOP per epoch |
    | **PVT solution** | Not included | Full position/velocity/time |
    | **Multipath** | Not included | Per-signal corrections |
    | **File size** | Larger (text) | Smaller (~40% of RINEX) |
    | **Constellations** | All GNSS | All GNSS |

    The 0.25 dB SNR quantization in SBF is a hardware constraint of the
    Septentrio receiver's measurement engine.  RINEX files converted from
    SBF (via `sbf2rin`) inherit this quantization.  Raw RINEX files from
    other receivers may have finer resolution.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: loading a single SBF file
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Loading a single SBF file

    The `SbfReader` constructor accepts a `Path` to any `.sbf` file.
    Like `Rnxv3Obs`, it is a frozen Pydantic model that lazily parses
    metadata on construction.
    """
    )

    return


@app.cell
def _(SBF_CANOPY_DIR, mo):
    from canvod.readers.sbf import SbfReader

    _first_file = sorted(SBF_CANOPY_DIR.glob("25001/*.sbf"))[0]
    sbf_reader = SbfReader(fpath=_first_file)

    mo.md(
        f"""
    ```python
    from canvod.readers.sbf import SbfReader

    reader = SbfReader(fpath=Path("{_first_file.name}"))
    ```
    """
    )

    return SbfReader, sbf_reader


@app.cell
def _(mo, sbf_reader):
    mo.md(
        f"""
    ### Reader metadata

    | Property | Value |
    |----------|-------|
    | **File** | `{sbf_reader.fpath.name}` |
    | **Start** | {sbf_reader.start_time} |
    | **End** | {sbf_reader.end_time} |
    | **Epochs** | {sbf_reader.num_epochs} |
    | **Satellites** | {sbf_reader.num_satellites} |
    | **Systems** | {', '.join(sbf_reader.systems)} |
    | **Source format** | `{sbf_reader.source_format}` |
    | **File hash** | `{sbf_reader.file_hash[:16]}...` |
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: SBF header (ReceiverSetup)
# ---------------------------------------------------------------------------


@app.cell
def _(mo, sbf_reader):
    _h = sbf_reader.header

    mo.md(
        f"""
    ### SBF header (ReceiverSetup block)

    The SBF header is extracted from the `ReceiverSetup` binary block.
    It provides receiver hardware metadata that is also written into the
    RINEX header during SBF-to-RINEX conversion.

    | Field | Value |
    |-------|-------|
    | **Marker** | `{_h.marker_name}` |
    | **Observer / Agency** | `{_h.observer}` / `{_h.agency}` |
    | **Receiver** | `{_h.rx_name}` (S/N: `{_h.rx_serial}`) |
    | **Firmware** | `{_h.rx_version}` |
    | **Antenna** | `{_h.ant_type}` (S/N: `{_h.ant_serial}`) |
    | **Product** | `{_h.product_name}` |
    | **Lat / Lon** | {_h.latitude_rad:.6f} rad / {_h.longitude_rad:.6f} rad |
    | **Height** | {_h.height_m} |
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: observation dataset
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Observation dataset

    `to_ds()` produces the same `(epoch, sid)` dataset as the RINEX reader.
    The data contract is identical: dimensions, coordinates, attributes, and
    the required `SNR` variable all match.
    """
    )

    return


@app.cell
def _(mo, sbf_reader):
    ds_sbf = sbf_reader.to_ds(keep_data_vars=["SNR"])

    mo.md(
        """
    ```python
    ds = reader.to_ds(keep_data_vars=["SNR"])
    ```
    """
    )

    return (ds_sbf,)


@app.cell
def _(ds_sbf):
    ds_sbf

    return


@app.cell
def _(ds_sbf, mo):
    import numpy as np

    _snr = ds_sbf["SNR"].values
    _valid = np.isfinite(_snr)

    mo.md(
        f"""
    ### Dataset structure

    | Property | Value |
    |----------|-------|
    | **Dimensions** | `{dict(ds_sbf.sizes)}` |
    | **Epochs** | {ds_sbf.sizes['epoch']} |
    | **SIDs** | {ds_sbf.sizes['sid']} |
    | **Valid SNR** | {_valid.sum():,} of {_snr.size:,} ({_valid.sum() / _snr.size * 100:.1f}%) |
    | **SNR range** | {np.nanmin(_snr):.1f} -- {np.nanmax(_snr):.1f} dB-Hz |
    | **SNR dtype** | `{_snr.dtype}` |
    | **Memory** | {ds_sbf.nbytes / 1024:.0f} KB |

    Note the larger number of SIDs compared to RINEX.  The SBF reader
    discovers SIDs from the observation data itself (which satellites were
    actually tracked), whereas the RINEX reader uses the header declaration
    (which constellations are *potentially* available).  After `pad_global_sid`
    (enabled by default), both are padded to the same global SID space.
    """
    )

    return (np,)


# ---------------------------------------------------------------------------
# Section: SNR quantization
# ---------------------------------------------------------------------------


@app.cell
def _(ds_sbf, mo, np):
    _snr_flat = ds_sbf["SNR"].values.ravel()
    _snr_valid = _snr_flat[np.isfinite(_snr_flat)]

    _diffs = np.diff(np.sort(np.unique(np.round(_snr_valid, 2))))
    _min_step = np.min(_diffs) if len(_diffs) > 0 else 0

    mo.md(
        f"""
    ### SNR quantization

    The Septentrio receiver quantizes SNR (C/N0) to **0.25 dB** steps.
    This is visible in the data: the minimum step between unique SNR values
    is **{_min_step:.2f} dB**.

    This quantization is a hardware property of the measurement engine and
    cannot be improved in post-processing.  For GNSS-T VOD retrieval, the
    0.25 dB step size introduces a quantization noise of approximately
    0.25 / sqrt(12) = 0.072 dB RMS, which is small relative to the typical
    SNR dynamic range of 20--50 dB-Hz observed through forest canopies.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: SBF metadata dataset (sbf_obs)
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## SBF metadata: receiver-computed geometry

    The key advantage of reading SBF directly (rather than converting to
    RINEX first) is access to the **receiver firmware's satellite geometry
    computation**.  The `to_ds_and_auxiliary()` method returns both the
    observation dataset and a metadata dataset in a single file scan.

    The metadata dataset (`sbf_obs`) contains:

    - **Zenith angle** (`theta`) and **azimuth** (`phi`) from the receiver's
      real-time navigation solution
    - **DOP values** (PDOP, HDOP, VDOP) per epoch
    - **Rise/set state** per satellite
    - **Multipath corrections** (if available)

    These receiver-computed angles use **broadcast ephemeris** (the
    navigation message decoded in real time), which has ~1--2 m orbit
    accuracy.  The canvodpy pipeline can alternatively compute angles from
    **post-processed SP3 orbits** (~2 cm accuracy) via the auxiliary
    package.
    """
    )

    return


@app.cell
def _(mo, sbf_reader):
    ds_obs, aux_dict = sbf_reader.to_ds_and_auxiliary(keep_data_vars=["SNR"])
    ds_meta = aux_dict["sbf_obs"]

    mo.md(
        """
    ```python
    ds_obs, aux_dict = reader.to_ds_and_auxiliary(keep_data_vars=["SNR"])
    ds_meta = aux_dict["sbf_obs"]
    ```
    """
    )

    return aux_dict, ds_meta, ds_obs


@app.cell
def _(ds_meta, mo, np):
    _vars = list(ds_meta.data_vars)
    _coords_1d = [c for c in ds_meta.coords if ds_meta.coords[c].dims == ("epoch",)]

    _theta = ds_meta["theta"].values if "theta" in ds_meta else None
    _phi = ds_meta["phi"].values if "phi" in ds_meta else None

    _rows = []
    for _v in _vars:
        _arr = ds_meta[_v].values
        _n_valid = np.isfinite(_arr).sum() if _arr.dtype.kind == "f" else (_arr != -1).sum()
        _rows.append(f"| `{_v}` | `{_arr.dtype}` | {_n_valid:,} |")

    mo.md(
        f"""
    ### Metadata dataset contents

    **Dimensions**: `{dict(ds_meta.sizes)}`

    **Epoch-level coordinates** (1-D): {', '.join(f'`{c}`' for c in _coords_1d)}

    **Data variables** (2-D: epoch x sid):

    | Variable | Dtype | Valid values |
    |----------|-------|-------------|
    {chr(10).join(_rows)}

    The `theta` (zenith angle) and `phi` (azimuth) variables are in
    **degrees** (geographic convention: 0=N, 90=E).  Note that the canvodpy
    pipeline internally uses **radians** (mathematical convention: phi=0 at
    East, counter-clockwise).  The coordinate transform is handled
    automatically by the auxiliary package.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: DOP values
# ---------------------------------------------------------------------------


@app.cell
def _(ds_meta, mo, np):
    _has_pdop = "pdop" in ds_meta.coords

    if _has_pdop:
        _pdop = ds_meta.coords["pdop"].values
        _pdop_valid = _pdop[np.isfinite(_pdop)]
        _pdop_info = (
            f"| **PDOP range** | {np.min(_pdop_valid):.1f} -- {np.max(_pdop_valid):.1f} |\n"
            f"| **PDOP mean** | {np.mean(_pdop_valid):.2f} |"
        )
    else:
        _pdop_info = "| **PDOP** | Not available in this file |"

    mo.md(
        f"""
    ### Dilution of Precision (DOP)

    DOP quantifies the geometric quality of the satellite constellation
    visible to the receiver at each epoch.  Lower DOP indicates better
    geometry (satellites well-distributed across the sky).

    | Metric | Value |
    |--------|-------|
    {_pdop_info}

    DOP values are useful for quality control: epochs with very high DOP
    (poor geometry) may produce less reliable VOD estimates.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: comparing SBF and RINEX readers
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Unified reader interface

    Both `Rnxv3Obs` and `SbfReader` inherit from the `GNSSDataReader`
    abstract base class.  This guarantees that downstream code (the
    store, auxiliary, and VOD packages) can accept datasets from either
    reader without modification.

    The shared interface is:

    ```python
    class GNSSDataReader(ABC):
        fpath: Path
        file_hash: str          # SHA-256 for deduplication
        start_time: datetime    # First epoch (UTC)
        end_time: datetime      # Last epoch (UTC)
        systems: list[str]      # Active constellations
        num_epochs: int
        num_satellites: int
        source_format: str      # "rinex3" or "sbf"

        def to_ds(...) -> xr.Dataset:
            ...  # (epoch, sid) with SNR, validated

        def iter_epochs() -> Iterator[...]:
            ...  # Memory-efficient streaming
    ```

    The orchestrator in canvodpy detects the file format from the extension
    and selects the appropriate reader automatically.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: when to use SBF vs RINEX
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## When to use SBF vs RINEX

    | Use case | Recommended format |
    |----------|--------------------|
    | **Archival / sharing** | RINEX (open standard, tool-agnostic) |
    | **Real-time monitoring** | SBF (no conversion step, faster I/O) |
    | **Broadcast ephemeris** | SBF (SatVisibility block provides angles directly) |
    | **Post-processed orbits** | Either (SP3/CLK augmentation replaces receiver geometry) |
    | **Maximum SNR precision** | RINEX from non-Septentrio receivers (~0.001 dB) |
    | **Receiver diagnostics** | SBF (DOP, multipath, PVT available) |

    In practice, many GNSS-T sites log SBF natively and convert to RINEX
    for archival.  canvodpy supports both paths: read SBF directly for
    operational processing, or read RINEX for reproducible scientific
    analysis with post-processed orbits.
    """
    )

    return


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ---

    **Previous**: [01 — RINEX Reading](./01_rinex_reading.py)
    | **Next**: [03 — Satellite Catalog](./03_satellite_catalog.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
