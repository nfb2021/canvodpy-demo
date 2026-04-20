# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvod-readers>=0.2.3",
#   "canvod-auxiliary>=0.2.3",
#   "canvod-grids>=0.2.3",
#   "canvod-vod>=0.2.3",
#   "marimo>=0.21.1",
# ]
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium", app_title="Single-Day Workflow", css_file="canvod_nordic.css"
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Single-Day Processing Workflow

    This notebook walks through a complete single-day GNSS-T processing
    pipeline **step by step**, using the L4 functional API to make each
    stage explicit.  The same result can be obtained with a single
    `process_date()` call (L1), but the manual approach reveals what
    happens at each stage.

    **Date**: DOY 2025-001 (January 1, 2025)
    **Receivers**: canopy + reference

    ---

    """
    )

    return (mo,)


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------


@app.cell
def _():
    from pathlib import Path

    import numpy as np
    import xarray as xr
    from _paths import AUX_DATA_DIR, ROSALIA_CANOPY_DIR, ROSALIA_REFERENCE_DIR

    return AUX_DATA_DIR, Path, ROSALIA_CANOPY_DIR, ROSALIA_REFERENCE_DIR, np, xr


# ---------------------------------------------------------------------------
# Step 1: discover files
# ---------------------------------------------------------------------------


@app.cell
def _(ROSALIA_CANOPY_DIR, ROSALIA_REFERENCE_DIR, mo):
    _can_files = sorted(ROSALIA_CANOPY_DIR.glob("25001/*.rnx"))
    _ref_files = sorted(ROSALIA_REFERENCE_DIR.glob("25001/*.rnx"))

    mo.md(
        f"""
    ## Step 1: Discover RINEX files

    The first stage identifies all observation files for the target day.
    Files follow the IGS long-name convention and are organised by
    two-digit year + DOY subdirectory.

    | Receiver | Directory | Files found |
    |----------|-----------|-------------|
    | **Canopy** | `{ROSALIA_CANOPY_DIR}/25001/` | {len(_can_files)} |
    | **Reference** | `{ROSALIA_REFERENCE_DIR}/25001/` | {len(_ref_files)} |

    The number of files per day depends on the receiver's file duration
    setting.  This test data has **{len(_can_files)} files** per receiver.

    First file: `{_can_files[0].name if _can_files else "none"}`
    Last file: `{_can_files[-1].name if _can_files else "none"}`
    """
    )

    return


# ---------------------------------------------------------------------------
# Step 2: read files
# ---------------------------------------------------------------------------


@app.cell
def _(ROSALIA_CANOPY_DIR, ROSALIA_REFERENCE_DIR, mo, xr):
    from canvod.readers import Rnxv3Obs

    # Read first 4 files (one hour) for demonstration
    _can_files = sorted(ROSALIA_CANOPY_DIR.glob("25001/*.rnx"))[:4]
    _ref_files = sorted(ROSALIA_REFERENCE_DIR.glob("25001/*.rnx"))[:4]

    _can_datasets = [
        Rnxv3Obs(fpath=f).to_ds(keep_data_vars=["SNR"], write_global_attrs=True)
        for f in _can_files
    ]
    _ref_datasets = [
        Rnxv3Obs(fpath=f).to_ds(keep_data_vars=["SNR"], write_global_attrs=True)
        for f in _ref_files
    ]

    ds_canopy = xr.concat(_can_datasets, dim="epoch")
    ds_reference = xr.concat(_ref_datasets, dim="epoch")

    mo.md(
        f"""
    ## Step 2: Read and concatenate

    Each RINEX file is read with `Rnxv3Obs` and converted to an
    `xr.Dataset` with dimensions `(epoch, sid)`.  We then concatenate
    all files for the day along the `epoch` dimension.

    For this demonstration, we read **4 files** (one hour) to keep
    execution fast.

    ```python
    from canvod.readers import Rnxv3Obs

    datasets = [Rnxv3Obs(fpath=f).to_ds(keep_data_vars=["SNR"]) for f in files]
    ds = xr.concat(datasets, dim="epoch")
    ```

    | | Canopy | Reference |
    |-|--------|-----------|
    | **Epochs** | {ds_canopy.sizes["epoch"]:,} | {ds_reference.sizes["epoch"]:,} |
    | **SIDs** | {ds_canopy.sizes["sid"]} | {ds_reference.sizes["sid"]} |
    | **Variables** | {list(ds_canopy.data_vars)} | {list(ds_reference.data_vars)} |
    """
    )

    return Rnxv3Obs, ds_canopy, ds_reference


# ---------------------------------------------------------------------------
# Step 3: augment with satellite geometry
# ---------------------------------------------------------------------------


@app.cell
def _(AUX_DATA_DIR, ds_canopy, ds_reference, mo, np, xr):
    from canvod.auxiliary import (
        ECEFPosition,
        add_spherical_coords_to_dataset,
        compute_spherical_coordinates,
    )

    _aux = xr.open_zarr(str(AUX_DATA_DIR / "aux_2025001.zarr"), decode_timedelta=False)

    def _augment(ds, aux):
        """Augment a dataset with satellite geometry."""
        rx = ECEFPosition.from_ds_metadata(ds)
        shared_s = np.intersect1d(ds.sid.values, aux.sid.values)
        shared_e = np.intersect1d(ds.epoch.values, aux.epoch.values)
        aux_sel = aux.sel(sid=shared_s, epoch=shared_e)
        ds_sel = ds.sel(sid=shared_s, epoch=shared_e)
        r, theta, phi = compute_spherical_coordinates(
            aux_sel["X"].values,
            aux_sel["Y"].values,
            aux_sel["Z"].values,
            rx,
        )
        return add_spherical_coords_to_dataset(ds_sel, r, theta, phi)

    ds_can_aug = _augment(ds_canopy, _aux)
    ds_ref_aug = _augment(ds_reference, _aux)

    mo.md(
        f"""
    ## Step 3: Augment with satellite geometry

    Each observation is augmented with the satellite's position in the
    receiver's local spherical coordinate frame: range ($r$), zenith
    angle ($\\theta$), and azimuth ($\\phi$).

    The transformation chain:
    1. Load pre-computed auxiliary Zarr (SP3 → Hermite interpolation → 5s grid)
    2. Extract receiver ECEF position from RINEX header
    3. Convert satellite ECEF → receiver-local ENU → spherical

    | | Canopy | Reference |
    |-|--------|-----------|
    | **Epochs** | {ds_can_aug.sizes["epoch"]:,} | {ds_ref_aug.sizes["epoch"]:,} |
    | **SIDs** | {ds_can_aug.sizes["sid"]} | {ds_ref_aug.sizes["sid"]} |
    | **Variables** | {list(ds_can_aug.data_vars)} | {list(ds_ref_aug.data_vars)} |

    Both datasets now contain `SNR`, `theta`, `phi`, and `r`.
    """
    )

    return (
        ECEFPosition,
        add_spherical_coords_to_dataset,
        compute_spherical_coordinates,
        ds_can_aug,
        ds_ref_aug,
    )


# ---------------------------------------------------------------------------
# Step 4: compute VOD
# ---------------------------------------------------------------------------


@app.cell
def _(ds_can_aug, ds_ref_aug, mo, np):
    from canvod.vod import TauOmegaZerothOrder

    ds_vod = TauOmegaZerothOrder.from_datasets(
        canopy_ds=ds_can_aug,
        sky_ds=ds_ref_aug,
        align=True,
    )

    _vod = ds_vod["VOD"].values
    _valid = np.isfinite(_vod)

    mo.md(
        f"""
    ## Step 4: Compute VOD

    The `TauOmegaZerothOrder` calculator aligns the canopy and reference
    datasets on their shared `(epoch, sid)` pairs, then applies the
    Tau-Omega model:

    $$\\text{{VOD}} = -\\ln(T) \\cdot \\cos(\\theta)$$

    where $T = 10^{{(\\text{{SNR}}_{{\\text{{canopy}}}} - \\text{{SNR}}_{{\\text{{ref}}}}) / 10}}$

    ```python
    from canvod.vod import TauOmegaZerothOrder

    ds_vod = TauOmegaZerothOrder.from_datasets(
        canopy_ds=ds_canopy, sky_ds=ds_reference, align=True,
    )
    ```

    | Metric | Value |
    |--------|-------|
    | **Dimensions** | `{dict(ds_vod.sizes)}` |
    | **Valid VOD** | {_valid.sum():,} / {_vod.size:,} ({_valid.sum() / max(_vod.size, 1) * 100:.1f}%) |
    | **Mean** | {np.nanmean(_vod[_valid]):.4f} |
    | **Median** | {np.nanmedian(_vod[_valid]):.4f} |
    | **Range** | [{np.nanmin(_vod[_valid]):.4f}, {np.nanmax(_vod[_valid]):.4f}] |
    """
    )

    return TauOmegaZerothOrder, ds_vod


@app.cell
def _(ds_vod):
    ds_vod

    return


# ---------------------------------------------------------------------------
# Step 5: optional — grid assignment
# ---------------------------------------------------------------------------


@app.cell
def _(ds_can_aug, ds_ref_aug, mo, np):
    from canvod.grids import add_cell_ids_to_vod_fast, create_hemigrid

    _grid = create_hemigrid("equal_area", angular_resolution=2.0)

    # Compute VOD first, then assign grid cells
    from canvod.vod import TauOmegaZerothOrder as _T

    _ds_vod = _T.from_datasets(canopy_ds=ds_can_aug, sky_ds=ds_ref_aug, align=True)
    ds_vod_gridded = add_cell_ids_to_vod_fast(
        _ds_vod,
        _grid,
        grid_name="equal_area_2deg",
    )

    _cell_var = "cell_id_equal_area_2deg"
    _cells = ds_vod_gridded[_cell_var].values
    _unique = np.unique(_cells[np.isfinite(_cells)])

    mo.md(
        f"""
    ## Step 5: Grid assignment (optional)

    Grid assignment maps each VOD observation to a hemispheric grid
    cell based on its $\\phi$ and $\\theta$ coordinates:

    ```python
    from canvod.grids import create_hemigrid, add_cell_ids_to_vod_fast

    grid = create_hemigrid("equal_area", angular_resolution=2.0)
    ds = add_cell_ids_to_vod_fast(ds_vod, grid, grid_name="equal_area_2deg")
    ```

    | Property | Value |
    |----------|-------|
    | **Grid cells total** | {_grid.ncells:,} |
    | **Cells with data** | {len(_unique):,} |
    | **Coverage** | {len(_unique) / _grid.ncells * 100:.1f}% |
    | **New variable** | `{_cell_var}` |

    One hour of data covers {len(_unique):,} of {_grid.ncells:,} cells.
    A full 24-hour day typically covers 60--80% of the hemisphere,
    limited by satellite geometry and horizon obstructions.
    """
    )

    return (ds_vod_gridded,)


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Pipeline summary

    | Step | Function | Input | Output |
    |------|----------|-------|--------|
    | 1 | `glob()` | Directory path | File list |
    | 2 | `Rnxv3Obs().to_ds()` + `xr.concat()` | RINEX files | `xr.Dataset(epoch, sid)` |
    | 3 | `compute_spherical_coordinates()` | Dataset + aux Zarr | Dataset + θ, φ, r |
    | 4 | `TauOmegaZerothOrder.from_datasets()` | Canopy + reference | VOD dataset |
    | 5 | `add_cell_ids_to_vod_fast()` | VOD dataset + grid | VOD + cell_id |

    Each step can be run independently, inspected, and debugged.
    The L1 and L2 APIs wrap these exact same steps in a more
    convenient interface.
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

    **Previous**: [16 — L4 Functional](./16_api_level4_functional.py)
    | **Next**: [18 — Batch Processing](./18_workflow_batch_processing.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
