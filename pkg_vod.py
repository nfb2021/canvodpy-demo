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
    # canvod-vod — Vegetation Optical Depth

    The **canvod-vod** package implements the **zeroth-order tau-omega model**
    for computing Vegetation Optical Depth (VOD) from dual-receiver GNSS
    signal-to-noise ratio (SNR) measurements.

    VOD quantifies how much a vegetation canopy attenuates GNSS signals,
    providing a proxy for above-ground biomass and plant water content.

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
    _base = _test_data / "rinex_v3_04" / "01_Rosalia"
    CANOPY_DIR = _base / "02_canopy" / "01_GNSS" / "01_raw" / "25001"
    REFERENCE_DIR = _base / "01_reference" / "01_GNSS" / "01_raw" / "25001"
    AUX_DATA_DIR = _test_data / "aux_data"

    return AUX_DATA_DIR, CANOPY_DIR, REFERENCE_DIR


# ---------------------------------------------------------------------------
# Read canopy + reference
# ---------------------------------------------------------------------------


@app.cell
def _(CANOPY_DIR, REFERENCE_DIR, mo):
    import xarray as xr

    from canvod.readers import Rnxv3Obs

    _canopy_files = sorted(CANOPY_DIR.glob("*.rnx"))[:4]
    _reference_files = sorted(REFERENCE_DIR.glob("*.rnx"))[:4]

    _canopy_readers = [Rnxv3Obs(fpath=f) for f in _canopy_files]
    _reference_readers = [Rnxv3Obs(fpath=f) for f in _reference_files]

    canopy_raw = xr.concat([r.to_ds() for r in _canopy_readers], dim="epoch")
    reference_raw = xr.concat([r.to_ds() for r in _reference_readers], dim="epoch")

    # Extract position from first reader
    _cp = _canopy_readers[0].header.approx_position
    from canvod.auxiliary import ECEFPosition
    canopy_pos = ECEFPosition(
        x=_cp[0].magnitude, y=_cp[1].magnitude, z=_cp[2].magnitude
    )

    mo.md(f"""
## Data Loaded

| Receiver | Epochs | SIDs |
|---|---|---|
| Canopy | {canopy_raw.sizes['epoch']:,} | {canopy_raw.sizes['sid']:,} |
| Reference | {reference_raw.sizes['epoch']:,} | {reference_raw.sizes['sid']:,} |
""")

    return (
        ECEFPosition, Rnxv3Obs, canopy_pos, canopy_raw, reference_raw, xr,
    )


# ---------------------------------------------------------------------------
# Augment with ephemeris
# ---------------------------------------------------------------------------


@app.cell
def _(AUX_DATA_DIR, canopy_pos, canopy_raw, reference_raw):
    from canvodpy.functional import augment_with_ephemeris

    _kwargs = dict(
        receiver_position=canopy_pos,
        source="final",
        agency="COD",
        date="2025001",
        aux_data_dir=AUX_DATA_DIR,
    )

    canopy_aug = augment_with_ephemeris(canopy_raw, **_kwargs)
    reference_aug = augment_with_ephemeris(reference_raw, **_kwargs)

    return augment_with_ephemeris, canopy_aug, reference_aug


# ---------------------------------------------------------------------------
# The tau-omega model
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Zeroth-Order Tau-Omega Model

    The VOD calculation follows Humphrey & Frankenberg (2022):

    $$
    \Delta \text{SNR} = \text{SNR}_{\text{canopy}} - \text{SNR}_{\text{sky}} \quad [\text{dB}]
    $$

    $$
    T = 10^{\Delta \text{SNR} / 10} \quad \text{(transmissivity)}
    $$

    $$
    \text{VOD} = -\ln(T) \cdot \cos(\theta)
    $$

    Where $\theta$ is the satellite zenith angle.  The $\cos(\theta)$ term
    normalises for path length through the canopy — a signal arriving at
    a low elevation angle traverses more vegetation.
    """
    )


# ---------------------------------------------------------------------------
# Compute VOD
# ---------------------------------------------------------------------------


@app.cell
def _(canopy_aug, mo, reference_aug):
    from canvod.vod import TauOmegaZerothOrder

    vod_calc = TauOmegaZerothOrder(canopy_ds=canopy_aug, sky_ds=reference_aug)
    vod_ds = vod_calc.calculate_vod()

    mo.md(f"""
## VOD Result

| Property | Value |
|---|---|
| Dimensions | epoch={vod_ds.sizes['epoch']:,}, sid={vod_ds.sizes['sid']:,} |
| Variables | {', '.join(f'`{v}`' for v in vod_ds.data_vars)} |
""")

    return TauOmegaZerothOrder, vod_calc, vod_ds


# ---------------------------------------------------------------------------
# VOD statistics
# ---------------------------------------------------------------------------


@app.cell
def _(mo, np, vod_ds):
    _vod = vod_ds["VOD"].values
    _valid = np.isfinite(_vod) & (_vod > 0)

    mo.md(f"""
## VOD Statistics

| Metric | Value |
|---|---|
| Total observations | {_vod.size:,} |
| Valid (finite, > 0) | {_valid.sum():,} ({100 * _valid.sum() / _vod.size:.1f}%) |
| Mean VOD | {np.nanmean(_vod[_valid]):.4f} |
| Median VOD | {np.nanmedian(_vod[_valid]):.4f} |
| Std VOD | {np.nanstd(_vod[_valid]):.4f} |
| Range | {np.nanmin(_vod[_valid]):.4f} — {np.nanmax(_vod[_valid]):.4f} |

Negative or NaN VOD values indicate the canopy signal was stronger than the
reference (possible multipath or no vegetation attenuation).  These are
excluded from the statistics above.
""")


# ---------------------------------------------------------------------------
# Intermediate: delta SNR
# ---------------------------------------------------------------------------


@app.cell
def _(mo, np, vod_calc):
    _delta = vod_calc.get_delta_snr().values
    _valid = np.isfinite(_delta)

    mo.md(f"""
## Delta SNR

$\Delta$SNR = SNR$_{{canopy}}$ − SNR$_{{sky}}$ is the raw signal attenuation
before the cos(θ) correction.

| Metric | Value |
|---|---|
| Mean ΔSNR | {np.nanmean(_delta):.2f} dB |
| Std ΔSNR | {np.nanstd(_delta):.2f} dB |
| Range | {np.nanmin(_delta):.2f} — {np.nanmax(_delta):.2f} dB |

A negative ΔSNR means the canopy attenuated the signal (expected for
vegetation).  Large negative values indicate dense canopy.
""")


# ---------------------------------------------------------------------------
# API patterns
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## API Patterns

    ### From datasets (explicit)

    ```python
    from canvod.vod import TauOmegaZerothOrder

    calc = TauOmegaZerothOrder(canopy_ds=canopy, sky_ds=reference)
    vod = calc.calculate_vod()
    ```

    ### From datasets (convenience)

    ```python
    from canvod.vod import TauOmegaZerothOrder

    vod = TauOmegaZerothOrder.from_datasets(canopy, reference, align=True)
    ```

    ### From Icechunk store

    ```python
    vod = TauOmegaZerothOrder.from_icechunkstore(
        "/path/to/store",
        canopy_group="canopy_01",
        sky_group="reference_01",
    )
    ```

    The `align=True` option performs an inner join on common epochs and SIDs,
    handling mismatched dimensions automatically.
    """
    )


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
