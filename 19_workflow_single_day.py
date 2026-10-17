# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvod-auxiliary",
#   "canvod-config",
#   "canvod-grids",
#   "canvod-ops",
#   "canvod-preflight",
#   "canvod-readers",
#   "canvod-store",
#   "canvod-store-metadata",
#   "canvod-utils",
#   "canvod-viz",
#   "canvod-vod",
#   "canvodpy",
#   "zarr>=3.1.2",
#   "marimo>=0.21.1",
#   "numpy==2.5.4",
#   "xarray==2026.9.0",
#   "pyyaml==6.0.3",
# ]
#
# [tool.uv.sources]
# canvod-auxiliary = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-auxiliary", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-config = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-config", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-grids = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-grids", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-ops = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-ops", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-preflight = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-preflight", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-readers = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-readers", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-store = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-store", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-store-metadata = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-store-metadata", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-utils = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-utils", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-viz = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-viz", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-vod = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-vod", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvodpy = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "canvodpy", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
#
# [tool.marimo.opengraph]
# title = "19 · Single-Day Workflow"
# description = "End-to-end GNSS-T processing for a single day: read RINEX files, augment with SP3 ephemeris, assign to a hemispheric grid, and retrieve VOD."
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium", app_title="Single-Day Workflow", css_file="canvod_nordic.css",
    html_head_file="canvod_head.html"
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    <p align="center" class="canvod-logo">
      <img class="canvod-logo-light" src="https://raw.githubusercontent.com/nfb2021/canvodpy/main/docs/assets/logo/canvodpy_logo_bright_mode.svg" alt="canVODpy logo" width="280">
      <img class="canvod-logo-dark" src="https://raw.githubusercontent.com/nfb2021/canvodpy/main/docs/assets/logo/canvodpy_logo_dark_mode.svg" alt="canVODpy logo" width="280">
    </p>

    # Single-Day Processing Workflow

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/19_workflow_single_day.py?mode=edit)

    This notebook walks through a complete single-day GNSS-T processing
    pipeline **step by step**, calling the `canvod-*` packages directly to
    make each stage explicit.  To process a configured site, use
    `canvodpy run` or `Site(...).pipeline().process_date()` instead: the
    manual approach here reveals what happens at each stage, but it does
    not apply the site configuration (e.g. which observables and signals
    to keep), so its numbers can differ.

    **Date**: DOY 2025-001 (January 1, 2025)
    **Receivers**: canopy + reference

    ---

    """
    )

    return (mo,)


@app.cell
def _():
    from canvodpy import demo_data

    root = demo_data("rinex")
    root = demo_data("aux")
    return root


@app.cell
def _():
    from pathlib import Path

    import numpy as np
    import xarray as xr

    return Path, np, xr


@app.cell
def _(root):
    import os
    import shutil
    import tempfile
    import pathlib

    import yaml

    from canvod.utils import testing

    work = pathlib.Path(tempfile.mkdtemp(prefix="canvodpy_demo_"))
    config_dir = work / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    aux_data_dir = work / "aux_data"
    aux_data_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(root / "aux_data" / "01_SP3", aux_data_dir / "01_SP3")
    shutil.copytree(root / "aux_data" / "02_CLK", aux_data_dir / "02_CLK")

    settings = {
        "sites": {
            "rosalia_v3_04": {
                "store_description": (
                    "Reference GNSS-T store for the Rosalia beech forest site,"
                    " built live from real RINEX v3.04 raw data (DOY 2025-001)."
                ),
                "description": (
                    "Beech forest GNSS-T research site, reference test dataset."
                ),
                "country": "AT",
                "latitude": 47.7,
                "longitude": 16.3,
                "altitude_m": 680.0,
                "gnss_site_data_root": str(root / "rinex_v3_04" / "01_Rosalia"),
                "receivers": {
                    "reference_01": {
                        "type": "reference",
                        "directory": "01_reference/01_GNSS/01_raw",
                        "reader_format": "rinex3",
                        "paired_canopies": "all",
                        "description": "Rosalia reference receiver (test data)",
                        "metadata": {
                            "receiver_model": "Septentrio AsteRx-SB3 Pro",
                            "firmware_version": "4.14.4",
                        },
                    },
                    "canopy_01": {
                        "type": "canopy",
                        "directory": "02_canopy/01_GNSS/01_raw",
                        "reader_format": "rinex3",
                        "description": "Rosalia canopy receiver (test data)",
                        "metadata": {
                            "receiver_model": "Septentrio AsteRx-SB3 Pro",
                            "firmware_version": "4.14.4",
                        },
                    },
                },
                "vod_analyses": {
                    "canopy_01_vs_reference_01": {
                        "canopy_receiver": "canopy_01",
                        "reference_receiver": "reference_01",
                    }
                },
            }
        },
        "processing": {
            "metadata": {
                "author": testing.PERSON_NAME,
                "email": testing.PERSON_EMAIL,
                "orcid": testing.PERSON_ORCID,
                "institution": testing.INSTITUTION,
                "institution_ror": "https://ror.org/" + testing.INSTITUTION_ROR,
                "department": testing.DEPARTMENT,
                "research_group": testing.RESEARCH_GROUP,
                "website": testing.WEBSITE,
                "license": "CC-BY-4.0",
                "publisher": testing.PUBLISHER,
                "publisher_url": testing.WEBSITE,
                "naming_authority": testing.NAMING_AUTHORITY,
            },
            "references": {
                "software_repository": "https://github.com/nfb2021/canvodpy",
                "documentation": "https://github.com/nfb2021/canvodpy/tree/main/docs",
                "publications": [],
                "funding": [],
            },
            "storage": {
                "stores_root_dir": str(work / "stores"),
                "aux_data_dir": str(aux_data_dir),
                "shared_aux_cache_dir": None,
            },
            "logging": {"log_dir": str(work / "logs")},
        },
    }
    (config_dir / "canvod-settings.yaml").write_text(
        yaml.safe_dump(settings, sort_keys=False)
    )
    os.environ["CANVOD_CONFIG_DIR"] = str(config_dir)
    return work, config_dir


@app.cell
def _(root):
    canopy_dir = root / "rinex_v3_04" / "01_Rosalia" / "02_canopy" / "01_GNSS" / "01_raw"
    ref_dir = root / "rinex_v3_04" / "01_Rosalia" / "01_reference" / "01_GNSS" / "01_raw"
    return canopy_dir, ref_dir


# ---------------------------------------------------------------------------
# Step 1: discover files
# ---------------------------------------------------------------------------


@app.cell
def _(canopy_dir, ref_dir, mo):
    _can_files = sorted(canopy_dir.glob("25001/*.rnx"))
    _ref_files = sorted(ref_dir.glob("25001/*.rnx"))

    mo.md(
        f"""
    ## Step 1: Discover RINEX files

    The first stage identifies all observation files for the target day.
    Files follow the IGS long-name convention and are organised by
    two-digit year + DOY subdirectory.

    | Receiver | Directory | Files found |
    |----------|-----------|-------------|
    | **Canopy** | `{canopy_dir}/25001/` | {len(_can_files)} |
    | **Reference** | `{ref_dir}/25001/` | {len(_ref_files)} |

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
def _(canopy_dir, ref_dir, mo, xr):
    from canvod.readers import Rnxv3Obs

    # Read first 4 files (one hour) for demonstration
    _can_files = sorted(canopy_dir.glob("25001/*.rnx"))[:4]
    _ref_files = sorted(ref_dir.glob("25001/*.rnx"))[:4]

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
def _(root, work, config_dir, ds_canopy, ds_reference, mo):
    from canvod.auxiliary import ECEFPosition
    from canvod.auxiliary.ephemeris.provider import AgencyEphemerisProvider

    aux_root = work / "aux_data"
    provider = AgencyEphemerisProvider(
        agency="COD", product_type="final", aux_data_dir=aux_root, fetch_clock=True
    )
    provider.preprocess_day("2025001", None)

    def _augment(ds):
        """Augment a dataset with satellite geometry."""
        return provider.augment_dataset(ds, ECEFPosition.from_ds_metadata(ds))

    ds_can_aug = _augment(ds_canopy)
    ds_ref_aug = _augment(ds_reference)

    mo.md(
        f"""
    ## Step 3: Augment with satellite geometry

    Each observation is augmented with the satellite's position in the
    receiver's local spherical coordinate frame: range ($r$), zenith
    angle ($\\theta$), and azimuth ($\\phi$).

    The transformation chain:
    1. Compute satellite positions from the SP3/CLK files (SP3 → Hermite interpolation → 5s grid)
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
        canopy_ds=ds_canopy, sky_ds=ds_reference,
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
# Step 5 (optional): grid assignment
# ---------------------------------------------------------------------------


@app.cell
def _(ds_can_aug, ds_ref_aug, mo, np):
    from canvod.grids import add_cell_ids_to_ds_fast, create_hemigrid

    _grid = create_hemigrid("equal_area", angular_resolution=2.0)

    # Compute VOD first, then assign grid cells
    from canvod.vod import TauOmegaZerothOrder as _T

    _ds_vod = _T.from_datasets(canopy_ds=ds_can_aug, sky_ds=ds_ref_aug)
    ds_vod_gridded = add_cell_ids_to_ds_fast(
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
    from canvod.grids import create_hemigrid, add_cell_ids_to_ds_fast

    grid = create_hemigrid("equal_area", angular_resolution=2.0)
    ds = add_cell_ids_to_ds_fast(ds_vod, grid, grid_name="equal_area_2deg")
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
    | 3 | `AgencyEphemerisProvider.augment_dataset()` | Dataset + SP3/CLK | Dataset + θ, φ, r |
    | 4 | `TauOmegaZerothOrder.from_datasets()` | Canopy + reference | VOD dataset |
    | 5 | `add_cell_ids_to_ds_fast()` | VOD dataset + grid | VOD + cell_id |

    Each step can be run independently, inspected, and debugged.
    `Site.pipeline()` and the `canvodpy run` CLI wrap these exact same
    steps in a more convenient interface.
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

    **Previous**: [18 · Site Pipeline](./18_site_pipeline.py)
    | **Next**: [20 · Batch Processing](./20_workflow_batch_processing.py)

    *canVODpy · Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
