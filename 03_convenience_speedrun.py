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
#   "plotly>=5.0",
#   "marimo>=0.21.1",
#   "pyyaml==6.0.3",
#   "numpy==2.5.4",
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
# title = "03 · Speedrun: Full Pipeline"
# description = "Raw GNSS files to Vegetation Optical Depth in five steps. Runs the complete GNSS-T pipeline on real Rosalia test data using canVODpy's convenience API."
# ///

import marimo

__generated_with = "0.23.4"
app = marimo.App(
    width="medium",
    app_title="Speedrun: Full Pipeline",
    css_file="canvod_nordic.css",
    html_head_file="canvod_head.html",
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

    # canVODpy Speedrun

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/03_convenience_speedrun.py?mode=edit)

    Raw GNSS files → Vegetation Optical Depth in five cells.

    This notebook runs the complete GNSS Transmissometry pipeline on the
    bundled Rosalia test data (DOY 2025-001).  It uses the **direct API**
    so every step is visible and no configuration files are required.

    | Step | What happens |
    |------|--------------|
    | **1** | Read RINEX observation files (canopy + reference) |
    | **2** | Augment with satellite geometry (SP3/CLK auxiliary data) |
    | **3** | Compute transmittance and VOD via Tau-Omega model |
    | **4** | Inspect results and plot VOD vs polar angle |

    > For the conceptual background see the
    > [VOD Retrieval notebook](./10_vod_retrieval.py).
    > For production pipelines with configuration see
    > [Single-Day Workflow](./19_workflow_single_day.py).

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


@app.cell
def _(mo, root, work):
    mo.md(
        f"""
    The settings for the site are written to `canvod-settings.yaml` in a
    fresh temporary folder (`{work}`), and `CANVOD_CONFIG_DIR` points at
    it: this is how canvodpy finds the site and the SP3/CLK server list
    here. `demo_data()` lays the test data out like a real run, under
    `{root}`; the settings, stores, logs and auxiliary data for this run
    go into the fresh temporary folder `{work}`.
"""
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 1: Read RINEX observation files
    """)
    return


@app.cell
def _(root):
    from canvod.readers import Rnxv3Obs

    canopy_dir = root / "rinex_v3_04" / "01_Rosalia" / "02_canopy" / "01_GNSS" / "01_raw"
    ref_dir = root / "rinex_v3_04" / "01_Rosalia" / "01_reference" / "01_GNSS" / "01_raw"

    # One 15-minute file per receiver (first file of the day)
    _can_file = sorted(canopy_dir.glob("25001/*.rnx"))[0]
    _ref_file = sorted(ref_dir.glob("25001/*.rnx"))[0]

    ds_can_raw = Rnxv3Obs(fpath=_can_file).to_ds(
        keep_data_vars=["SNR"], write_global_attrs=True
    )
    ds_ref_raw = Rnxv3Obs(fpath=_ref_file).to_ds(
        keep_data_vars=["SNR"], write_global_attrs=True
    )
    return ds_can_raw, ds_ref_raw


@app.cell
def _(ds_can_raw, ds_ref_raw, mo):
    mo.md(f"""
    | Receiver | Epochs | SIDs | File |
    |----------|--------|------|------|
    | **Canopy** | {ds_can_raw.sizes["epoch"]} | {ds_can_raw.sizes["sid"]} | `{ds_can_raw.attrs.get("source_file", "n/a")}` |
    | **Reference** | {ds_ref_raw.sizes["epoch"]} | {ds_ref_raw.sizes["sid"]} | `{ds_ref_raw.attrs.get("source_file", "n/a")}` |

    Each dataset has dimensions `(epoch, sid)` where SID encodes
    satellite + frequency band + tracking code, e.g. `G01|L1|C`.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Step 2: Augment with satellite geometry

    The satellite geometry (position, polar angle $\theta$, azimuth $\phi$)
    is computed from the COD final SP3 orbits and CLK clocks that
    `demo_data("aux")` put in the cache. `AgencyEphemerisProvider` reads
    those files and augments each observation with the receiver-relative
    angles, the same way `canvodpy run` does.
    """)
    return


@app.cell
def _(root, work, config_dir, ds_can_raw, ds_ref_raw):
    import numpy as np

    from canvod.auxiliary import ECEFPosition
    from canvod.auxiliary.ephemeris.provider import AgencyEphemerisProvider

    aux_root = work / "aux_data"
    provider = AgencyEphemerisProvider(
        agency="COD", product_type="final", aux_data_dir=aux_root, fetch_clock=True
    )
    provider.preprocess_day("2025001", None)

    def _augment(ds_raw):
        return provider.augment_dataset(
            ds_raw, ECEFPosition.from_ds_metadata(ds_raw)
        )

    ds_canopy = _augment(ds_can_raw)
    ds_reference = _augment(ds_ref_raw)
    return ds_canopy, ds_reference, np


@app.cell
def _(ds_canopy, mo, np):
    import math

    _theta_deg = np.degrees(ds_canopy["theta"].values)
    _valid = np.isfinite(_theta_deg)

    mo.md(
        f"""
    **Augmented canopy dataset** now contains `SNR`, `theta`, `phi`, `r`.

    Polar angle range: **{np.nanmin(_theta_deg):.1f}° – {np.nanmax(_theta_deg):.1f}°**
    (0° = zenith, 90° = horizon; observations below ~75° are typically masked in VOD retrieval)
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Step 3: Compute VOD

    `TauOmegaZerothOrder.from_datasets()` aligns the two datasets on their
    shared `(epoch, sid)` pairs and applies the Tau-Omega formula:

    $$\text{VOD} = -\ln(T) \cdot \cos(\theta), \qquad T = 10^{(\text{SNR}_\text{can} - \text{SNR}_\text{ref}) / 10}$$
    """)
    return


@app.cell
def _(ds_canopy, ds_reference):
    from canvod.vod import TauOmegaZerothOrder

    ds_vod = TauOmegaZerothOrder.from_datasets(
        canopy_ds=ds_canopy,
        sky_ds=ds_reference,
    )
    return (ds_vod,)


@app.cell
def _(ds_vod, mo, np):
    _vod = ds_vod["VOD"].values
    _valid = np.isfinite(_vod)
    _v = _vod[_valid]

    mo.md(
        f"""
    | Metric | Value |
    |--------|-------|
    | **Valid observations** | {_valid.sum():,} / {_vod.size:,} ({_valid.sum() / _vod.size * 100:.0f}%) |
    | **Mean VOD** | {np.mean(_v):.3f} |
    | **Median VOD** | {np.median(_v):.3f} |
    | **Std** | {np.std(_v):.3f} |
    | **Range** | [{np.min(_v):.3f}, {np.max(_v):.3f}] |

    VOD is negative where the canopy receiver recorded a stronger signal
    than the reference ($T > 1$); canVODpy keeps these values. What a
    value means for the vegetation depends on the frequency, the canopy
    and the site: see [10 · VOD Retrieval](./10_vod_retrieval.py).
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Step 4: VOD vs polar angle

    Each point is one `(epoch, sid)` observation.  The $\cos(\theta)$
    path-length correction is already included in the plotted VOD values.
    """)
    return


@app.cell
def _(ds_vod, mo, np):
    import plotly.graph_objects as go

    _theta_deg = np.degrees(ds_vod["theta"].values.ravel())
    _vod_flat = ds_vod["VOD"].values.ravel()
    _phi_deg = np.degrees(ds_vod["phi"].values.ravel())

    _mask = np.isfinite(_theta_deg) & np.isfinite(_vod_flat)
    _theta_plot = _theta_deg[_mask]
    _vod_plot = _vod_flat[_mask]
    _phi_plot = _phi_deg[_mask]

    fig = go.Figure(
        go.Scatter(
            x=_theta_plot,
            y=_vod_plot,
            mode="markers",
            marker=dict(
                color=_phi_plot,
                colorscale="Viridis",
                size=4,
                opacity=0.6,
                colorbar=dict(title="Azimuth (°)"),
            ),
            text=[f"θ={t:.1f}°  φ={p:.1f}°  VOD={v:.3f}"
                  for t, p, v in zip(_theta_plot, _phi_plot, _vod_plot)],
            hoverinfo="text",
        )
    )
    fig.update_layout(
        title="VOD vs Polar Angle, Rosalia, DOY 2025-001 (first 15 min)",
        xaxis_title="Polar angle θ (°)",
        yaxis_title="VOD",
        height=420,
        margin=dict(l=60, r=20, t=50, b=50),
    )
    fig.add_hline(y=0, line_dash="dot", line_color="grey", opacity=0.5)

    mo.ui.plotly(fig)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## What's next?

    | Notebook | Topic |
    |----------|-------|
    | [01 · Running the Pipeline (CLI)](./01_cli_pipeline.py) | The `canvodpy run` command-line interface |
    | [05 · RINEX Reading](./05_rinex_reading.py) | Deep dive into the RINEX reader |
    | [08 · Ephemeris & Coordinates](./08_ephemeris_coordinates.py) | SP3/CLK, ECEF → spherical |
    | [10 · VOD Retrieval](./10_vod_retrieval.py) | Full VOD derivation explained |
    | [11 · Icechunk Store](./11_icechunk_store.py) | Persist results in a versioned store |
    | [19 · Single-Day Workflow](./19_workflow_single_day.py) | Production pipeline, all 96 files |

    **Previous**: [02 · Configuration](./02_configuration.py)
    | **Next**: [04 · Naming Convention](./04_naming_convention.py)

    *canVODpy · Apache 2.0*
    """)
    return


if __name__ == "__main__":
    app.run()
