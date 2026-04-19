# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvodpy>=0.2.2",
#   "marimo>=0.21.1",
# ]
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium", app_title="VOD Retrieval", css_file="canvod_nordic.css"
)


# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Vegetation Optical Depth Retrieval

    The **canvod-vod** package implements the core scientific algorithm of
    GNSS Transmissometry: computing **Vegetation Optical Depth (VOD)** from
    paired canopy and reference receiver observations.

    VOD quantifies the attenuation of L-band microwave signals as they
    pass through a vegetation canopy.  Unlike optical remote sensing indices
    (such as NDVI), L-band signals penetrate the entire canopy volume,
    making VOD sensitive to total above-ground biomass, canopy water
    content, and vegetation structure.

    ---

    ## The Tau-Omega Radiative Transfer Model

    The zeroth-order solution of the Tau-Omega model relates the observed
    signal attenuation to the canopy optical depth:

    $$\text{VOD} = -\ln(T) \cdot \cos(\theta)$$

    where:

    - $T$ is the **canopy transmittance** (ratio of signal power reaching
      the below-canopy receiver to the unobstructed reference)
    - $\theta$ is the **polar angle** to the satellite

    The transmittance is derived from the SNR difference between the two
    receivers:

    $$T = 10^{(\text{SNR}_\text{canopy} - \text{SNR}_\text{ref}) / 10}$$

    The $\cos(\theta)$ factor corrects for the geometric path length:
    a signal arriving at low elevation traverses more canopy than one
    arriving from near the zenith.

    ---

    """
    )

    return (mo,)


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------


@app.cell
def _():
    import numpy as np
    import xarray as xr
    from _paths import AUX_DATA_DIR, ROSALIA_CANOPY_DIR, ROSALIA_REFERENCE_DIR

    return AUX_DATA_DIR, ROSALIA_CANOPY_DIR, ROSALIA_REFERENCE_DIR, np, xr


# ---------------------------------------------------------------------------
# Section: prepare paired datasets
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Preparing paired datasets

    VOD retrieval requires two augmented datasets from the same time window:
    a **canopy** dataset (below-canopy receiver) and a **reference** dataset
    (unobstructed receiver).  Both must contain `SNR`, `theta`, and `phi`
    variables with aligned `(epoch, sid)` dimensions.

    Here we load one file from each receiver and augment both
    with satellite geometry from the pre-computed auxiliary Zarr.
    """
    )

    return


@app.cell
def _(AUX_DATA_DIR, ROSALIA_CANOPY_DIR, ROSALIA_REFERENCE_DIR, np, xr):
    from canvod.auxiliary import (
        ECEFPosition,
        add_spherical_coords_to_dataset,
        compute_spherical_coordinates,
    )
    from canvod.readers import Rnxv3Obs

    # Read one file per receiver
    _can_file = sorted(ROSALIA_CANOPY_DIR.glob("25001/*.rnx"))[0]
    _ref_file = sorted(ROSALIA_REFERENCE_DIR.glob("25001/*.rnx"))[0]

    ds_can_raw = Rnxv3Obs(fpath=_can_file).to_ds(
        keep_data_vars=["SNR"], write_global_attrs=True
    )
    ds_ref_raw = Rnxv3Obs(fpath=_ref_file).to_ds(
        keep_data_vars=["SNR"], write_global_attrs=True
    )

    # Load auxiliary data
    _aux = xr.open_zarr(str(AUX_DATA_DIR / "aux_2025001.zarr"))

    # Augment canopy
    _rx = ECEFPosition.from_ds_metadata(ds_can_raw)
    _shared_s = np.intersect1d(ds_can_raw.sid.values, _aux.sid.values)
    _shared_e = np.intersect1d(ds_can_raw.epoch.values, _aux.epoch.values)
    _aux_c = _aux.sel(sid=_shared_s, epoch=_shared_e)
    _ds_c = ds_can_raw.sel(sid=_shared_s, epoch=_shared_e)
    _r, _t, _p = compute_spherical_coordinates(
        _aux_c["X"].values,
        _aux_c["Y"].values,
        _aux_c["Z"].values,
        _rx,
    )
    ds_canopy = add_spherical_coords_to_dataset(_ds_c, _r, _t, _p)

    # Augment reference
    _rx_ref = ECEFPosition.from_ds_metadata(ds_ref_raw)
    _shared_s2 = np.intersect1d(ds_ref_raw.sid.values, _aux.sid.values)
    _shared_e2 = np.intersect1d(ds_ref_raw.epoch.values, _aux.epoch.values)
    _aux_r = _aux.sel(sid=_shared_s2, epoch=_shared_e2)
    _ds_r = ds_ref_raw.sel(sid=_shared_s2, epoch=_shared_e2)
    _r2, _t2, _p2 = compute_spherical_coordinates(
        _aux_r["X"].values,
        _aux_r["Y"].values,
        _aux_r["Z"].values,
        _rx_ref,
    )
    ds_reference = add_spherical_coords_to_dataset(_ds_r, _r2, _t2, _p2)

    return (
        ECEFPosition,
        Rnxv3Obs,
        add_spherical_coords_to_dataset,
        compute_spherical_coordinates,
        ds_can_raw,
        ds_canopy,
        ds_ref_raw,
        ds_reference,
    )


@app.cell
def _(ds_canopy, ds_reference, mo, np):
    _shared_sids = np.intersect1d(ds_canopy.sid.values, ds_reference.sid.values)
    _shared_epochs = np.intersect1d(ds_canopy.epoch.values, ds_reference.epoch.values)

    mo.md(
        f"""
    ### Paired datasets

    | | Canopy | Reference |
    |-|--------|-----------|
    | **Epochs** | {ds_canopy.sizes["epoch"]} | {ds_reference.sizes["epoch"]} |
    | **SIDs** | {ds_canopy.sizes["sid"]} | {ds_reference.sizes["sid"]} |
    | **Variables** | {list(ds_canopy.data_vars)} | {list(ds_reference.data_vars)} |

    **Shared**: {len(_shared_epochs)} epochs x {len(_shared_sids)} SIDs

    Both datasets now contain `SNR`, `theta`, `phi`, and `r`.  The VOD
    calculator will align them on the intersection of `(epoch, sid)` pairs
    before computing the transmittance ratio.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: VOD calculation
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Computing VOD

    The `TauOmegaZerothOrder` calculator implements the zeroth-order
    Tau-Omega model.  The convenience class method `from_datasets()`
    handles alignment and instantiation in one step.
    """
    )

    return


@app.cell
def _(ds_canopy, ds_reference):
    from canvod.vod import TauOmegaZerothOrder

    ds_vod = TauOmegaZerothOrder.from_datasets(
        canopy_ds=ds_canopy,
        sky_ds=ds_reference,
        align=True,
    )

    return TauOmegaZerothOrder, ds_vod


@app.cell
def _(ds_vod, mo, np):
    _vod = ds_vod["VOD"].values
    _valid = np.isfinite(_vod)
    _vod_valid = _vod[_valid]

    mo.md(
        f"""
    ### VOD output

    | Property | Value |
    |----------|-------|
    | **Dimensions** | `{dict(ds_vod.sizes)}` |
    | **Variables** | {list(ds_vod.data_vars)} |
    | **Valid VOD** | {_valid.sum():,} of {_vod.size:,} ({_valid.sum() / _vod.size * 100:.1f}%) |
    | **Min** | {np.min(_vod_valid):.4f} |
    | **Max** | {np.max(_vod_valid):.4f} |
    | **Mean** | {np.mean(_vod_valid):.4f} |
    | **Median** | {np.median(_vod_valid):.4f} |

    The output dataset contains three variables:

    - **`VOD`**: Vegetation Optical Depth (dimensionless)
    - **`phi`**: azimuth from the canopy receiver (radians)
    - **`theta`**: polar angle from the canopy receiver (radians)

    Note that `phi` and `theta` are taken from the **canopy** dataset
    (not the reference), because they describe the signal path through
    the vegetation canopy.
    """
    )

    return


@app.cell
def _(ds_vod):
    ds_vod

    return


# ---------------------------------------------------------------------------
# Section: interpreting VOD values
# ---------------------------------------------------------------------------


@app.cell
def _(mo, np):
    mo.md(
        r"""
    ## Interpreting VOD values

    VOD is dimensionless and theoretically non-negative.  Its physical
    interpretation depends on the signal frequency and canopy type:

    | VOD range | Interpretation |
    |-----------|----------------|
    | 0.0 | No attenuation (open sky) |
    | 0.0 -- 0.3 | Low biomass (grassland, sparse canopy) |
    | 0.3 -- 0.8 | Moderate biomass (deciduous forest, crops) |
    | 0.8 -- 2.0 | Dense canopy (tropical forest, conifers) |
    | > 2.0 | Very dense / wet canopy |
    | < 0 | Negative: SNR gain through canopy (scattering, multipath) |

    Negative VOD values can occur when the canopy receiver receives a
    *stronger* signal than the reference — typically due to constructive
    multipath reflections from the ground or canopy surfaces.  These are
    physically meaningful observations (not noise) and are retained in
    the dataset.

    **Typical uncertainty**: approximately 0.1 for L-band forest canopy
    measurements over 15 minutes, decreasing with temporal and spatial
    averaging.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: step-by-step formula
# ---------------------------------------------------------------------------


@app.cell
def _(ds_canopy, ds_reference, mo, np, xr):
    # Manual calculation to show each step
    _can, _ref = xr.align(ds_canopy, ds_reference, join="inner")

    _delta_snr = _can["SNR"] - _ref["SNR"]
    _transmittance = 10 ** (_delta_snr / 10)
    _vod_manual = -np.log(_transmittance) * np.cos(_can["theta"])

    _dsnr_valid = _delta_snr.values[np.isfinite(_delta_snr.values)]
    _t_valid = _transmittance.values[np.isfinite(_transmittance.values)]

    mo.md(
        f"""
    ## Step-by-step calculation

    The VOD formula can be computed manually in three lines to verify
    the calculator:

    ```python
    # Step 1: align datasets on shared (epoch, sid) pairs
    can, ref = xr.align(ds_canopy, ds_reference, join="inner")

    # Step 2: compute SNR difference (dB)
    delta_snr = can["SNR"] - ref["SNR"]

    # Step 3: convert to transmittance (linear)
    T = 10 ** (delta_snr / 10)

    # Step 4: apply Tau-Omega model
    VOD = -np.log(T) * np.cos(can["theta"])
    ```

    **Intermediate values**:

    | Step | Statistic | Value |
    |------|-----------|-------|
    | $\\Delta$SNR | Mean | {np.nanmean(_dsnr_valid):.2f} dB |
    | $\\Delta$SNR | Range | [{np.nanmin(_dsnr_valid):.1f}, {np.nanmax(_dsnr_valid):.1f}] dB |
    | $T$ (transmittance) | Mean | {np.nanmean(_t_valid):.4f} |
    | $T$ | Range | [{np.nanmin(_t_valid):.4f}, {np.nanmax(_t_valid):.4f}] |

    A transmittance of 1.0 means the signal passes through the canopy
    unattenuated.  Values below 1.0 indicate absorption/scattering by
    the canopy; values above 1.0 indicate constructive multipath.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: the calculator API
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Calculator API

    The `VODCalculator` base class defines the interface; `TauOmegaZerothOrder`
    is the standard implementation.

    ```python
    class VODCalculator(ABC):
        canopy_ds: xr.Dataset   # Must contain "SNR"
        sky_ds: xr.Dataset      # Must contain "SNR"

        def calculate_vod(self) -> xr.Dataset
            # Returns Dataset with VOD, phi, theta

        @classmethod
        def from_datasets(cls, canopy_ds, sky_ds, align=True) -> xr.Dataset
            # Convenience: align + calculate in one call

        @classmethod
        def from_icechunkstore(cls, store_path, canopy_group, sky_group) -> xr.Dataset
            # Load from store and calculate
    ```

    The `from_icechunkstore()` factory loads directly from a versioned
    Icechunk store, avoiding the need to manually read and align datasets.
    This is the recommended entry point for production workflows.
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

    **Previous**: [06 — Hemispheric Grids](./06_hemispheric_grids.py)
    | **Next**: [08 — Icechunk Store](./08_icechunk_store.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
