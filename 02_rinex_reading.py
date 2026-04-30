# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvod-readers>=0.2.3",
#   "pooch>=1.6",
#   "marimo>=0.21.1",
# ]
#
# [tool.marimo.opengraph]
# title = "02 · RINEX v3 Observation Reading"
# description = "Read RINEX v3.04 GNSS observation files into xarray Datasets. Explore SNR, Doppler, pseudorange, and carrier-phase observables across all constellations."
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium",
    app_title="RINEX v3 Observation Reading",
    css_file="canvod_nordic.css",
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # RINEX v3.04 Observation Reading

    This notebook introduces the **canvod-readers** package and demonstrates how
    to read RINEX v3.04 observation files into `xarray.Dataset` objects.

    RINEX (Receiver Independent Exchange Format) is the standard interchange
    format for GNSS observation data.  Version 3.04 supports all modern
    constellations (GPS, Galileo, GLONASS, BeiDou, QZSS, IRNSS, SBAS) and
    encodes carrier phase, pseudorange, Doppler, and signal-to-noise ratio
    (SNR) observables in a fixed-width ASCII layout.

    The canvod-readers package parses RINEX files into labelled, indexed
    `xarray.Dataset` objects with dimensions `(epoch, sid)`, where each SID
    (Signal ID) uniquely identifies a satellite-frequency-tracking-code
    combination.

    ---

    **Test data**: DOY 2025-001, two GNSS receivers (one reference, one canopy).

    """
    )
    return (mo,)


@app.cell
def _():
    import _paths
    from _download import marimo_downloader
    _paths.ensure_data(downloader=marimo_downloader)


@app.cell
def _():
    from pathlib import Path

    from _paths import ROSALIA_CANOPY_DIR, ROSALIA_REFERENCE_DIR

    return ROSALIA_CANOPY_DIR, ROSALIA_REFERENCE_DIR


@app.cell
def _(ROSALIA_CANOPY_DIR, mo):
    _files = sorted(ROSALIA_CANOPY_DIR.glob("25001/*.rnx"))

    mo.md(
        f"""
    ## The raw RINEX v3.04 file

    A RINEX observation file consists of two parts: a **header** section
    (terminated by `END OF HEADER`) and a **data** section.  The header
    declares the receiver, antenna, approximate position, and, critically, 
    the observation types available per GNSS constellation.

    The test data directory contains **{len(_files)} files** for the canopy
    receiver.  The file duration and count per day depend on
    the receiver configuration.

    The filename follows the IGS long-name convention:

    ```
    ROSA01TUW_R_20250010000_15M_05S_AA.rnx
    ^^^^^^^^^ ^ ^^^^^^^^^^^ ^^^ ^^^ ^^
    Site+Rx   R  YYYYDOYHHMM Dur Samp Content
    ```

    | Field | Value | Meaning |
    |-------|-------|---------|
    | `ROSA01TUW` | Site=ROSA, Rx=01, Agency=TUW | Canopy receiver |
    | `R` | | RINEX format |
    | `20250010000` | 2025, DOY 001, 00:00 UTC | Start of observation window |
    | `15M` | 15 minutes | File duration |
    | `05S` | 5 seconds | Sampling interval |
    | `AA` | All observables, all constellations | Content descriptor |
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Loading a single RINEX file

    The `Rnxv3Obs` class wraps a single RINEX v3.04 observation file.
    It is a Pydantic model (frozen, immutable) that lazily parses the header
    on construction and provides methods to iterate epochs or convert the
    full file to an `xarray.Dataset`.
    """)
    return


@app.cell
def _(ROSALIA_CANOPY_DIR, mo):
    from canvod.readers import Rnxv3Obs

    _first_file = sorted(ROSALIA_CANOPY_DIR.glob("25001/*.rnx"))[0]
    reader = Rnxv3Obs(fpath=_first_file)

    mo.md(
        f"""
    ```python
    from canvod.readers import Rnxv3Obs

    reader = Rnxv3Obs(fpath=Path("{_first_file.name}"))
    ```
    """
    )
    return Rnxv3Obs, reader


@app.cell
def _(mo, reader):
    mo.md(f"""
    ### Reader metadata

    | Property | Value |
    |----------|-------|
    | **File** | `{reader.fpath.name}` |
    | **Start** | {reader.start_time} |
    | **End** | {reader.end_time} |
    | **Epochs** | {reader.num_epochs} |
    | **Satellites** | {reader.num_satellites} |
    | **Systems** | {", ".join(reader.systems)} |
    | **Source format** | `{reader.source_format}` |
    | **File hash** | `{reader.file_hash[:16]}...` |

    The `file_hash` is a SHA-256 digest used for deduplication in the store
    layer.  Two files with identical content produce the same hash, regardless
    of filename.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## RINEX header inspection

    The header contains station metadata, receiver and antenna identifiers,
    the approximate receiver position in ECEF (Earth-Centered, Earth-Fixed)
    coordinates, and the list of observation codes available per constellation.
    """)
    return


@app.cell
def _(mo, reader):
    _h = reader.header

    mo.md(
        f"""
    ### Station and receiver

    | Field | Value |
    |-------|-------|
    | **Marker name** | `{_h.marker_name}` |
    | **Observer / Agency** | `{_h.observer}` / `{_h.agency}` |
    | **Receiver** | `{_h.receiver_type}` (S/N: `{_h.receiver_number}`) |
    | **Firmware** | `{_h.receiver_version}` |
    | **Antenna** | `{_h.antenna_type}` (S/N: `{_h.antenna_number}`) |
    | **RINEX version** | {_h.version} |
    | **Systems** | `{_h.systems}` (`M` = mixed / multi-constellation) |

    ### Approximate position (ECEF)

    The RINEX header records the receiver position in ECEF coordinates.
    This position is used later in the pipeline to compute satellite
    azimuth and elevation angles relative to the receiver.

    | Axis | Value |
    |------|-------|
    | **X** | {_h.approx_position[0]} |
    | **Y** | {_h.approx_position[1]} |
    | **Z** | {_h.approx_position[2]} |
    """
    )
    return


@app.cell
def _(mo, reader):
    _obs = reader.header.obs_codes_per_system
    _rows = []
    for _sys, _codes in sorted(_obs.items()):
        _rows.append(f"| `{_sys}` | {len(_codes)} | `{' '.join(_codes)}` |")

    mo.md(
        f"""
    ### Observation types per constellation

    Each GNSS constellation can transmit on multiple frequencies and with
    different tracking codes.  The RINEX header declares which observation
    types were recorded.  The three-character code follows the convention:

    - **1st character**: observable type (`C`=pseudorange, `L`=carrier phase,
      `D`=Doppler, `S`=SNR, `X`=channel number)
    - **2nd character**: frequency band (`1`=L1, `2`=L2, `5`=L5, `6`=E6, etc.)
    - **3rd character**: tracking code (`C`, `W`, `Q`, `P`, etc.)

    For GNSS-T, the primary observable is **SNR** (`S` codes), which quantifies
    the received signal strength in dB-Hz.

    | System | Codes | Observation types |
    |--------|-------|-------------------|
    {chr(10).join(_rows)}
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Converting to xarray.Dataset

    The `to_ds()` method parses all observation epochs and assembles a
    two-dimensional `xarray.Dataset` with dimensions `(epoch, sid)`.

    The `keep_data_vars` parameter controls which observables are retained.
    For GNSS-T, only SNR is needed; omitting other variables reduces memory
    by approximately 80%.
    """)
    return


@app.cell
def _(mo, reader):
    ds_single = reader.to_ds(keep_data_vars=["SNR"])

    mo.md(
        """
    ```python
    ds = reader.to_ds(keep_data_vars=["SNR"])
    ```
    """
    )
    return (ds_single,)


@app.cell
def _(ds_single):
    ds_single
    return


@app.cell
def _(ds_single, mo):
    mo.md(f"""
    ### Dataset structure

    | Property | Value |
    |----------|-------|
    | **Dimensions** | `{dict(ds_single.sizes)}` |
    | **Epochs** | {ds_single.sizes["epoch"]} timestamps at 5-second intervals |
    | **SIDs** | {ds_single.sizes["sid"]} unique satellite-frequency-code combinations |
    | **Data variables** | {list(ds_single.data_vars)} |
    | **Memory** | {ds_single.nbytes / 1024:.0f} KB |

    The dataset is intentionally sparse: not every satellite is visible at
    every epoch.  Values are `NaN` where a satellite was below the horizon
    or not tracked.
    """)
    return


@app.cell
def _(ds_single, mo):
    import numpy as np

    _sids = ds_single.sid.values
    _sample = _sids[:8]
    _rows = []
    for _s in _sample:
        _parts = str(_s).split("|")
        _rows.append(f"| `{_s}` | `{_parts[0]}` | `{_parts[1]}` | `{_parts[2]}` |")

    _sys_vals = ds_single.system.values
    _systems = sorted(set(str(s) for s in _sys_vals if isinstance(s, str)))
    _band_vals = ds_single.band.values
    _bands = sorted(set(str(b) for b in _band_vals if isinstance(b, str)))

    mo.md(
        f"""
    ### Signal ID (SID)

    Each coordinate along the `sid` dimension encodes three pieces of
    information in the format `SV|Band|Code`:

    | SID | SV (satellite) | Band (frequency) | Code (tracking) |
    |-----|----------------|------------------|-----------------|
    {chr(10).join(_rows)}
    | ... | | | |

    The SID is the **fundamental identifier** throughout canvodpy.  Unlike
    the PRN (e.g. `G01`) used by other tools, the SID disambiguates cases
    where the same satellite transmits on multiple frequencies or is tracked
    with different codes.

    **Coverage in this file**:

    - **Constellations**: {", ".join(f"`{s}`" for s in sorted(_systems))}
    - **Bands**: {", ".join(f"`{b}`" for b in sorted(_bands))}
    - **Total SIDs**: {len(_sids)}
    """
    )
    return (np,)


@app.cell
def _(ds_single, mo):
    _coord_rows = []
    for _name, _coord in ds_single.coords.items():
        _dtype = str(_coord.dtype)
        _dims = ", ".join(_coord.dims) if _coord.dims else "scalar"
        _coord_rows.append(f"| `{_name}` | `{_dims}` | `{_dtype}` |")

    mo.md(
        f"""
    ### Coordinate variables

    The dataset carries rich coordinate metadata along the `sid` dimension.
    These are populated from the RINEX header and the GNSS signal
    specification tables bundled with canvod-readers.

    | Coordinate | Dimension(s) | Dtype |
    |------------|-------------|-------|
    {chr(10).join(_coord_rows)}

    The frequency coordinates (`freq_center`, `freq_min`, `freq_max`) are
    derived from the official ITU/ICAO frequency allocations for each
    constellation and band.  They are used downstream for Fresnel zone
    calculations and wavelength-dependent corrections.
    """
    )
    return


@app.cell
def _(ds_single, mo, np):
    _snr = ds_single["SNR"].values
    _valid = np.isfinite(_snr)
    _pct_valid = _valid.sum() / _snr.size * 100

    mo.md(
        f"""
    ### SNR data

    The `SNR` variable contains Signal-to-Noise Ratio measurements in dB-Hz.
    In GNSS-T, this is the primary observable: by comparing SNR at a canopy
    receiver with SNR at a reference receiver for the same satellite and
    epoch, the canopy transmittance is derived.

    | Statistic | Value |
    |-----------|-------|
    | **Valid values** | {_valid.sum():,} of {_snr.size:,} ({_pct_valid:.1f}%) |
    | **Min** | {np.nanmin(_snr):.1f} dB-Hz |
    | **Max** | {np.nanmax(_snr):.1f} dB-Hz |
    | **Mean** | {np.nanmean(_snr):.1f} dB-Hz |
    | **Dtype** | `{_snr.dtype}` |

    The data is stored as `float32` (not `float64`) — a deliberate design
    choice that halves memory usage.  RINEX SNR values have approximately
    0.001 dB precision, so `float32` (7 significant digits) introduces at
    most ~2 x 10^-6 dB truncation error, which is 1000x below measurement
    resolution.
    """
    )
    return


@app.cell
def _(ds_single, mo):
    mo.md(
        r"""
    ## Selecting subsets

    The `sid`-level coordinates enable efficient subsetting using xarray's
    standard selection methods.
    """
    )

    _gps_mask = ds_single.system == "G"
    ds_gps = ds_single.sel(sid=_gps_mask)

    _gal_mask = ds_single.system == "E"
    ds_gal = ds_single.sel(sid=_gal_mask)

    mo.md(
        f"""
    ### By constellation

    ```python
    ds_gps = ds.sel(sid=ds.system == "G")  # GPS only
    ds_gal = ds.sel(sid=ds.system == "E")  # Galileo only
    ```

    | Constellation | SIDs | Epochs |
    |---------------|------|--------|
    | GPS (`G`) | {ds_gps.sizes["sid"]} | {ds_gps.sizes["epoch"]} |
    | Galileo (`E`) | {ds_gal.sizes["sid"]} | {ds_gal.sizes["epoch"]} |
    """
    )
    return


@app.cell
def _(ds_single, mo):
    _l1_mask = ds_single.band == "L1"
    _ds_l1 = ds_single.sel(sid=_l1_mask)

    _l2_mask = ds_single.band == "L2"
    _ds_l2 = ds_single.sel(sid=_l2_mask)

    mo.md(
        f"""
    ### By frequency band

    ```python
    ds_l1 = ds.sel(sid=ds.band == "L1")  # L1 band only
    ds_l2 = ds.sel(sid=ds.band == "L2")  # L2 band only
    ```

    | Band | SIDs | Center frequency |
    |------|------|-----------------|
    | L1 | {_ds_l1.sizes["sid"]} | ~1575.42 MHz |
    | L2 | {_ds_l2.sizes["sid"]} | ~1227.60 MHz |

    For VOD retrieval, a single band is selected for each constellation.
    The choice of band affects the Fresnel zone size and the penetration
    depth into the canopy.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Loading multiple files

    A full day of observations is typically split across multiple files.
    The standard workflow reads all files for a given day and concatenates
    them along the `epoch` dimension using `xarray.concat`.
    """)
    return


@app.cell
def _(ROSALIA_CANOPY_DIR, Rnxv3Obs, mo):
    import xarray as xr

    _files = sorted(ROSALIA_CANOPY_DIR.glob("25001/*.rnx"))[:4]

    _datasets = []
    for _f in _files:
        _r = Rnxv3Obs(fpath=_f)
        _datasets.append(_r.to_ds(keep_data_vars=["SNR"]))

    ds_concat = xr.concat(_datasets, dim="epoch")

    mo.md(
        f"""
    Reading **{len(_files)}** files from DOY 2025-001:

    ```python
    import xarray as xr
    from canvod.readers import Rnxv3Obs

    files = sorted(data_dir.glob("25001/*.rnx"))
    datasets = [Rnxv3Obs(fpath=f).to_ds(keep_data_vars=["SNR"]) for f in files]
    ds = xr.concat(datasets, dim="epoch")
    ```
    """
    )
    return (ds_concat,)


@app.cell
def _(ds_concat, mo, np):
    _t0 = str(ds_concat.epoch.values[0])[:19]
    _t1 = str(ds_concat.epoch.values[-1])[:19]

    mo.md(
        f"""
    ### Concatenated dataset

    | Property | Value |
    |----------|-------|
    | **Epochs** | {ds_concat.sizes["epoch"]} ({_t0} to {_t1}) |
    | **SIDs** | {ds_concat.sizes["sid"]} |
    | **Valid SNR** | {np.isfinite(ds_concat["SNR"].values).sum():,} values |
    | **Memory** | {ds_concat.nbytes / 1024:.0f} KB |

    `xarray.concat` automatically aligns the `sid` dimension: if a satellite
    appears in one file but not another, the missing epochs are filled with
    `NaN`.  This produces a regular, rectangular array without data loss.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Data validation

    The canvod-readers package enforces a **data contract** on every dataset.
    The `validate_dataset()` function checks:

    1. **Dimensions**: `(epoch, sid)` must exist
    2. **Coordinates**: required coords with correct dtypes
    3. **Data variables**: at least `SNR` with `(epoch, sid)` dimensions
    4. **Attributes**: `File Hash`, `Created`, `Software`, `Institution`

    Validation runs automatically inside `to_ds()`.  It can also be called
    explicitly to verify datasets loaded from external sources or after
    manual manipulation.
    """)
    return


@app.cell
def _(ds_single, mo):
    from canvod.readers import validate_dataset

    try:
        validate_dataset(ds_single)
        _result = "Dataset passed all validation checks."
    except ValueError as e:
        _result = f"Validation failed:\n```\n{e}\n```"

    mo.md(
        f"""
    ### Validation result

    {_result}

    The contract constants are importable for reference:

    ```python
    from canvod.readers import REQUIRED_DIMS, REQUIRED_COORDS, REQUIRED_ATTRS
    ```
    """
    )
    return


@app.cell
def _(ROSALIA_CANOPY_DIR, ROSALIA_REFERENCE_DIR, Rnxv3Obs, mo, np):
    _can_files = sorted(ROSALIA_CANOPY_DIR.glob("25001/*.rnx"))[:1]
    _ref_files = sorted(ROSALIA_REFERENCE_DIR.glob("25001/*.rnx"))[:1]

    _can_reader = Rnxv3Obs(fpath=_can_files[0])
    _ref_reader = Rnxv3Obs(fpath=_ref_files[0])

    _ds_can = _can_reader.to_ds(keep_data_vars=["SNR"])
    _ds_ref = _ref_reader.to_ds(keep_data_vars=["SNR"])

    _shared_sids = np.intersect1d(_ds_can.sid.values, _ds_ref.sid.values)
    _shared_epochs = np.intersect1d(_ds_can.epoch.values, _ds_ref.epoch.values)

    mo.md(
        f"""
    ## Canopy and reference receivers

    GNSS-T requires **two receivers** observing the same satellites
    simultaneously.  The reference receiver has an unobstructed sky view;
    the canopy receiver sits beneath the vegetation.

    For the first 15-minute file:

    | | Canopy | Reference |
    |-|-------------------|----------------------|
    | **File** | `{_can_reader.fpath.name}` | `{_ref_reader.fpath.name}` |
    | **Epochs** | {_ds_can.sizes["epoch"]} | {_ds_ref.sizes["epoch"]} |
    | **SIDs** | {_ds_can.sizes["sid"]} | {_ds_ref.sizes["sid"]} |
    | **Shared SIDs** | {len(_shared_sids)} | |
    | **Shared epochs** | {len(_shared_epochs)} | |

    The downstream VOD calculation aligns both datasets on the intersection
    of `(epoch, sid)` pairs.  The transmittance for each pair is:

    $$T = 10^{{(\\text{{SNR}}_{{\\text{{canopy}}}} - \\text{{SNR}}_{{\\text{{ref}}}}) / 10}}$$

    and the Vegetation Optical Depth is:

    $$\\text{{VOD}} = -\\ln(T) \\cdot \\cos(\\theta)$$

    where $\\theta$ is the polar angle to the satellite.
    """
    )
    return


@app.cell
def _(mo, reader):
    mo.md(
        r"""
    ## Memory-efficient epoch iteration

    For very large files or streaming applications, `iter_epochs()` yields
    one epoch at a time without loading the entire file into memory.
    """
    )

    _epochs_sample = []
    for _i, _epoch in enumerate(reader.iter_epochs()):
        if _i >= 3:
            break
        _n_sats = sum(1 for _ in _epoch.data)
        _epochs_sample.append(f"| {_i} | {_epoch.info.epoch} | {_n_sats} |")

    mo.md(
        f"""
    ```python
    for epoch in reader.iter_epochs():
        # process one epoch at a time
        ...
    ```

    | # | Timestamp | Satellites |
    |---|-----------|------------|
    {chr(10).join(_epochs_sample)}

    This is particularly useful for quality control checks that only need
    to inspect a subset of epochs without materialising the full dataset.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    **Next**: [03 — Satellite Catalog](./03_satellite_catalog.py)

    *canVODpy — Apache 2.0*
    """)
    return


if __name__ == "__main__":
    app.run()
