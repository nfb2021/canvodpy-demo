# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvod-readers>=0.2.3",
#   "canvod-auxiliary>=0.2.3",
#   "canvod-vod>=0.2.3",
#   "zarr>=3.1.2",
#   "plotly>=5.0",
#   "pooch>=1.6",
#   "marimo>=0.21.1",
# ]
#
# [tool.marimo.opengraph]
# title = "00 · Speedrun — Full Pipeline"
# description = "Raw GNSS files to Vegetation Optical Depth in five steps. Runs the complete GNSS-T pipeline on real Rosalia test data using canVODpy's convenience API."
# ///

import marimo

__generated_with = "0.23.4"
app = marimo.App(
    width="medium",
    app_title="Speedrun — Full Pipeline",
    css_file="canvod_nordic.css",
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # canVODpy — Speedrun

    Raw GNSS files → Vegetation Optical Depth in five cells.

    This notebook runs the complete GNSS Transmissometry pipeline on the
    bundled Rosalia test data (DOY 2025-001).  It uses the **direct API**
    so every step is visible — no configuration files required.

    | Step | What happens |
    |------|--------------|
    | **1** | Read RINEX observation files (canopy + reference) |
    | **2** | Augment with satellite geometry (SP3/CLK auxiliary data) |
    | **3** | Compute transmittance and VOD via Tau-Omega model |
    | **4** | Inspect results and plot VOD vs polar angle |

    > For the conceptual background see the
    > [VOD Retrieval notebook](./07_vod_retrieval.py).
    > For production pipelines with configuration see
    > [Single-Day Workflow](./17_workflow_single_day.py).

    ---
    """
    )
    return (mo,)


@app.cell
def _():
    import _paths
    from _download import marimo_downloader
    _paths.ensure_data(downloader=marimo_downloader)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 1 — Read RINEX observation files
    """)
    return


@app.cell
def _():
    from _paths import AUX_DATA_DIR, ROSALIA_CANOPY_DIR, ROSALIA_REFERENCE_DIR
    from canvod.readers import Rnxv3Obs

    # One 15-minute file per receiver (first file of the day)
    _can_file = sorted(ROSALIA_CANOPY_DIR.glob("25001/*.rnx"))[0]
    _ref_file = sorted(ROSALIA_REFERENCE_DIR.glob("25001/*.rnx"))[0]

    ds_can_raw = Rnxv3Obs(fpath=_can_file).to_ds(
        keep_data_vars=["SNR"], write_global_attrs=True
    )
    ds_ref_raw = Rnxv3Obs(fpath=_ref_file).to_ds(
        keep_data_vars=["SNR"], write_global_attrs=True
    )
    return AUX_DATA_DIR, ds_can_raw, ds_ref_raw


@app.cell
def _(ds_can_raw, ds_ref_raw, mo):
    mo.md(f"""
    | Receiver | Epochs | SIDs | File |
    |----------|--------|------|------|
    | **Canopy** | {ds_can_raw.sizes["epoch"]} | {ds_can_raw.sizes["sid"]} | `{ds_can_raw.attrs.get("source_file", "—")}` |
    | **Reference** | {ds_ref_raw.sizes["epoch"]} | {ds_ref_raw.sizes["sid"]} | `{ds_ref_raw.attrs.get("source_file", "—")}` |

    Each dataset has dimensions `(epoch, sid)` where SID encodes
    satellite + frequency band + tracking code, e.g. `G01|L1|C`.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Step 2 — Augment with satellite geometry

    The auxiliary Zarr cache contains pre-interpolated ECEF satellite
    positions from COD final SP3/CLK products (5-min orbit, 30-s clock).
    `compute_spherical_coordinates()` converts ECEF positions to
    receiver-relative **polar angle** $\theta$ and **azimuth** $\phi$.
    """)
    return


@app.cell
def _(AUX_DATA_DIR, ds_can_raw, ds_ref_raw):
    import numpy as np
    import xarray as xr
    from canvod.auxiliary import (
        ECEFPosition,
        add_spherical_coords_to_dataset,
        compute_spherical_coordinates,
    )

    def _augment(ds_raw):
        aux = xr.open_zarr(str(AUX_DATA_DIR / "aux_2025001.zarr"), decode_timedelta=False)
        shared_s = np.intersect1d(ds_raw.sid.values, aux.sid.values)
        shared_e = np.intersect1d(ds_raw.epoch.values, aux.epoch.values)
        aux_sel = aux.sel(sid=shared_s, epoch=shared_e)
        ds_sel = ds_raw.sel(sid=shared_s, epoch=shared_e)
        rx = ECEFPosition.from_ds_metadata(ds_raw)
        r, theta, phi = compute_spherical_coordinates(
            aux_sel["X"].values,
            aux_sel["Y"].values,
            aux_sel["Z"].values,
            rx,
        )
        return add_spherical_coords_to_dataset(ds_sel, r, theta, phi)

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
    ## Step 3 — Compute VOD

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
        align=True,
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

    Typical L-band VOD for a temperate forest canopy: **0.3 – 0.8**.
    Negative values indicate constructive multipath (physically meaningful, not noise).
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Step 4 — VOD vs polar angle

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
        title="VOD vs Polar Angle — Rosalia, DOY 2025-001 (first 15 min)",
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
    | [02 — RINEX Reading](./02_rinex_reading.py) | Deep dive into the RINEX reader |
    | [05 — Ephemeris & Coordinates](./05_ephemeris_coordinates.py) | SP3/CLK, ECEF → spherical |
    | [07 — VOD Retrieval](./07_vod_retrieval.py) | Full VOD derivation explained |
    | [08 — Icechunk Store](./08_icechunk_store.py) | Persist results in a versioned store |
    | [17 — Single-Day Workflow](./17_workflow_single_day.py) | Production pipeline, all 96 files |

    *canVODpy — Apache 2.0*
    """)
    return


if __name__ == "__main__":
    app.run()
