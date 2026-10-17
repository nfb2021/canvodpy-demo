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
# title = "10 · VOD Retrieval"
# description = "Retrieve Vegetation Optical Depth from GNSS transmittance using the Tau-Omega radiative transfer model. Align canopy and reference SNR to compute VOD per sky cell."
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium", app_title="VOD Retrieval", css_file="canvod_nordic.css",
    html_head_file="canvod_head.html"
)


# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    <p align="center" class="canvod-logo">
      <img class="canvod-logo-light" src="https://raw.githubusercontent.com/nfb2021/canvodpy/main/docs/assets/logo/canvodpy_logo_bright_mode.svg" alt="canVODpy logo" width="280">
      <img class="canvod-logo-dark" src="https://raw.githubusercontent.com/nfb2021/canvodpy/main/docs/assets/logo/canvodpy_logo_dark_mode.svg" alt="canVODpy logo" width="280">
    </p>

    # Vegetation Optical Depth Retrieval

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/10_vod_retrieval.py?mode=edit)

    The **canvod-vod** package implements the core scientific algorithm of
    GNSS Transmissometry: computing **Vegetation Optical Depth (VOD)** from
    paired canopy and reference receiver observations.

    VOD quantifies the attenuation of L-band microwave signals as they
    pass through a vegetation canopy.

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

    return np, xr


@app.cell
def _():
    from canvodpy import demo_data

    root = demo_data("rinex")
    root = demo_data("aux")
    return root


@app.cell
def _(root):
    import os
    import shutil
    import tempfile
    from pathlib import Path

    import yaml

    from canvod.utils import testing

    work = Path(tempfile.mkdtemp(prefix="canvodpy_demo_"))
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
    with satellite geometry computed from the SP3/CLK files that
    `demo_data("aux")` downloaded.
    """
    )

    return


@app.cell
def _(root, work, config_dir):
    from canvod.auxiliary import ECEFPosition
    from canvod.auxiliary.ephemeris.provider import AgencyEphemerisProvider
    from canvod.readers import Rnxv3Obs

    canopy_dir = root / "rinex_v3_04" / "01_Rosalia" / "02_canopy" / "01_GNSS" / "01_raw"
    ref_dir = root / "rinex_v3_04" / "01_Rosalia" / "01_reference" / "01_GNSS" / "01_raw"

    # Read one file per receiver
    _can_file = sorted(canopy_dir.glob("25001/*.rnx"))[0]
    _ref_file = sorted(ref_dir.glob("25001/*.rnx"))[0]

    ds_can_raw = Rnxv3Obs(fpath=_can_file).to_ds(
        keep_data_vars=["SNR"], write_global_attrs=True
    )
    ds_ref_raw = Rnxv3Obs(fpath=_ref_file).to_ds(
        keep_data_vars=["SNR"], write_global_attrs=True
    )

    # Compute the satellite geometry from the SP3/CLK files demo_data downloaded
    aux_root = work / "aux_data"
    provider = AgencyEphemerisProvider(
        agency="COD", product_type="final", aux_data_dir=aux_root, fetch_clock=True
    )
    provider.preprocess_day("2025001", None)

    ds_canopy = provider.augment_dataset(
        ds_can_raw, ECEFPosition.from_ds_metadata(ds_can_raw)
    )
    ds_reference = provider.augment_dataset(
        ds_ref_raw, ECEFPosition.from_ds_metadata(ds_ref_raw)
    )
    return ds_canopy, ds_reference


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

    VOD is dimensionless. It follows from the transmissivity
    $T = 10^{\Delta\mathrm{SNR}/10}$ as $\mathrm{VOD} = -\ln(T)\cos\theta$:

    - $\Delta\mathrm{SNR} < 0$ (the canopy receiver records a weaker signal
      than the reference): $T < 1$ and VOD is positive.
    - $\Delta\mathrm{SNR} = 0$: $T = 1$ and VOD is 0.
    - $\Delta\mathrm{SNR} > 0$ (the canopy receiver records a stronger
      signal): $T > 1$ and VOD is negative.

    canVODpy keeps negative values; it does not clip or remove them.

    What a VOD value means for the vegetation depends on the signal
    frequency, the canopy and the site. See the literature on GNSS-T VOD
    for your vegetation type before you interpret absolute values.
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

    A transmittance of 1.0 means the canopy receiver recorded the same
    signal as the reference. The model reads values below 1.0 as
    attenuation by the canopy. Values above 1.0 mean the canopy receiver
    recorded a stronger signal than the reference.
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
        def from_datasets(cls, canopy_ds, sky_ds) -> xr.Dataset
            # Convenience: align + calculate in one call
    ```

    The calculator always aligns both datasets on their shared epochs and
    signals.  For production workflows, compute VOD for a configured site
    with `canvodpy run`, or from Python with `Site(...).vod`, which reads
    the data from the site's Icechunk store (see
    [18 · Site Pipeline](./18_site_pipeline.py)).
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

    **Previous**: [09 · Hemispheric Grids](./09_hemispheric_grids.py)
    | **Next**: [11 · Icechunk Store](./11_icechunk_store.py)

    *canVODpy · Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
