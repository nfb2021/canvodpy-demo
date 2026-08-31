# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvod-grids>=0.2.3",
#   "plotly>=5.0",
#   "marimo>=0.21.1",
# ]
#
# [tool.marimo.opengraph]
# title = "19 · Grid Exploration"
# description = "Interactive explorer for canVODpy's hemispheric grid schemes. Compare equal-area, equal-angle, geodesic, and Fibonacci partitions at different resolutions."
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium", app_title="Grid Exploration", css_file="canvod_nordic.css"
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Interactive Hemispheric Grid Exploration

    Explore per-cell VOD data on the hemispheric equal-area grid.
    Select cells by clicking on the 3D or 2D view to inspect timeseries
    and statistics.

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


# ---------------------------------------------------------------------------
# Grid setup — create or load a hemispheric grid
# ---------------------------------------------------------------------------


@app.cell
def _(np):
    from canvod.grids import create_hemigrid

    grid = create_hemigrid("equal_area", angular_resolution=5.0)

    # Pre-compute Cartesian cell centers for 3D widget
    theta = grid.grid["theta"].to_numpy()  # zenith, radians
    phi = grid.grid["phi"].to_numpy()  # azimuth, radians

    cell_x = np.sin(theta) * np.cos(phi)
    cell_y = np.sin(theta) * np.sin(phi)
    cell_z = np.cos(theta)

    return cell_x, cell_y, cell_z, grid, phi, theta


# ---------------------------------------------------------------------------
# UI Controls
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    color_by = mo.ui.dropdown(
        ["mean", "median", "std", "count", "coverage"],
        value="mean",
        label="Color by",
    )
    view_mode = mo.ui.switch(value=True, label="3D view")

    system_dropdown = mo.ui.dropdown(
        ["All", "GPS (G)", "Galileo (E)", "GLONASS (R)", "BeiDou (C)"],
        value="All",
        label="System",
    )
    band_dropdown = mo.ui.dropdown(
        ["All", "L1", "L2", "L5", "E1", "E5a", "E5b", "G1", "G2"],
        value="All",
        label="Band",
    )
    vod_range = mo.ui.range_slider(
        start=0.0,
        stop=5.0,
        step=0.05,
        value=[0.0, 3.0],
        label="VOD range",
    )

    mo.hstack(
        [
            mo.vstack([system_dropdown, band_dropdown]),
            mo.vstack([color_by, vod_range]),
            view_mode,
        ],
        justify="start",
        gap=2,
    )

    return band_dropdown, color_by, system_dropdown, vod_range, view_mode


# ---------------------------------------------------------------------------
# Synthetic data (used when no store is available)
# ---------------------------------------------------------------------------


@app.cell
def _(grid, np):
    # Generate synthetic VOD-like data for demonstration
    _rng = np.random.default_rng(42)
    ncells = grid.ncells

    _synthetic_mean = (
        0.3 + 0.5 * np.cos(grid.grid["theta"].to_numpy()) + _rng.normal(0, 0.05, ncells)
    )
    _synthetic_std = 0.05 + 0.1 * _rng.random(ncells)
    _synthetic_median = _synthetic_mean + _rng.normal(0, 0.02, ncells)
    _synthetic_count = _rng.integers(10, 500, ncells).astype(float)
    _synthetic_coverage = np.clip(0.3 + 0.6 * _rng.random(ncells), 0, 1)

    cell_stats = {
        "mean": _synthetic_mean,
        "median": _synthetic_median,
        "std": _synthetic_std,
        "count": _synthetic_count,
        "coverage": _synthetic_coverage,
    }

    return cell_stats, ncells


# ---------------------------------------------------------------------------
# Prepare widget data
# ---------------------------------------------------------------------------


@app.cell
def _(cell_stats, color_by, grid, ncells, np, theta):
    stat_name = color_by.value
    values = cell_stats[stat_name].copy()

    # Replace NaN with 0 for visualization
    values = np.where(np.isfinite(values), values, 0.0)

    # Build labels
    _theta_deg = np.degrees(theta)
    _phi_deg = np.degrees(grid.grid["phi"].to_numpy())
    labels = [
        f"Cell {i}\n  theta={_theta_deg[i]:.1f} deg\n  phi={_phi_deg[i]:.1f} deg\n  {stat_name}={values[i]:.4f}"
        for i in range(ncells)
    ]

    return labels, values


# ---------------------------------------------------------------------------
# 3D Hemisphere Widget
# ---------------------------------------------------------------------------


@app.cell
def _(cell_x, cell_y, cell_z, labels, mo, values, view_mode):
    hemisphere_3d = None

    if view_mode.value:
        from _widgets.hemisphere_widgets import HemisphereSelector3D

        hemisphere_3d = mo.ui.anywidget(
            HemisphereSelector3D(
                cell_centers_x=cell_x.tolist(),
                cell_centers_y=cell_y.tolist(),
                cell_centers_z=cell_z.tolist(),
                cell_values=values.tolist(),
                cell_labels=labels,
                colorscale="Viridis",
                marker_size=6,
            )
        )
        mo.output.replace(hemisphere_3d)
    else:
        mo.output.replace(mo.md("*Switch to 3D view to see the hemisphere widget.*"))

    return (hemisphere_3d,)


# ---------------------------------------------------------------------------
# 2D Hemisphere Widget
# ---------------------------------------------------------------------------


@app.cell
def _(labels, mo, phi, theta, values, view_mode):
    hemisphere_2d = None

    if not view_mode.value:
        from _widgets.hemisphere_widgets import HemisphereSelector2D

        hemisphere_2d = mo.ui.anywidget(
            HemisphereSelector2D(
                cell_theta=theta.tolist(),
                cell_phi=phi.tolist(),
                cell_values=values.tolist(),
                cell_labels=labels,
                canvas_size=500,
            )
        )
        mo.output.replace(hemisphere_2d)
    else:
        mo.output.replace(mo.md("*Switch to 2D view to see the polar projection.*"))

    return (hemisphere_2d,)


# ---------------------------------------------------------------------------
# Selection info table
# ---------------------------------------------------------------------------


@app.cell
def _(cell_stats, hemisphere_2d, hemisphere_3d, mo, np, theta, view_mode):
    # Get selected cells from the active widget
    if view_mode.value and hemisphere_3d is not None:
        selected_ids = hemisphere_3d.value.get("selected_cell_ids", [])
    elif not view_mode.value and hemisphere_2d is not None:
        selected_ids = hemisphere_2d.value.get("selected_cell_ids", [])
    else:
        selected_ids = []

    if not selected_ids:
        mo.output.replace(mo.md("*Click cells on the hemisphere to select them.*"))
    else:
        _theta_deg = np.degrees(theta)
        rows = []
        for _idx in sorted(selected_ids):
            rows.append(
                {
                    "cell": _idx,
                    "theta_deg": round(float(_theta_deg[_idx]), 1),
                    "mean": round(float(cell_stats["mean"][_idx]), 4),
                    "std": round(float(cell_stats["std"][_idx]), 4),
                    "count": int(cell_stats["count"][_idx]),
                    "coverage": round(float(cell_stats["coverage"][_idx]), 3),
                }
            )

        mo.output.replace(
            mo.vstack(
                [
                    mo.md(f"### Selected cells ({len(selected_ids)})"),
                    mo.ui.table(rows),
                ]
            )
        )

    return (selected_ids,)


# ---------------------------------------------------------------------------
# Timeseries plot for selected cells
# ---------------------------------------------------------------------------


@app.cell
def _(mo, np, selected_ids):
    if not selected_ids:
        mo.output.replace(mo.md("*Select cells to view timeseries.*"))
    else:
        import plotly.graph_objects as go

        fig = go.Figure()
        _ts_rng = np.random.default_rng(0)

        # Generate synthetic timeseries for selected cells
        hours = np.arange(0, 24 * 7, 0.25)  # 7 days at 15-min resolution
        for _cell_id in sorted(selected_ids)[:8]:  # limit to 8 cells
            base = 0.3 + 0.02 * _cell_id
            diurnal = 0.1 * np.sin(2 * np.pi * hours / 24)
            noise = _ts_rng.normal(0, 0.03, len(hours))
            vod = base + diurnal + noise

            fig.add_trace(
                go.Scatter(
                    x=hours,
                    y=vod,
                    mode="lines",
                    name=f"Cell {_cell_id}",
                    opacity=0.8,
                )
            )

        fig.update_layout(
            title="VOD Timeseries (synthetic)",
            xaxis_title="Hour",
            yaxis_title="VOD",
            height=350,
            margin=dict(l=50, r=20, t=40, b=40),
            legend=dict(orientation="h", y=-0.15),
        )

        mo.output.replace(mo.ui.plotly(fig))

    return


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        """
    ---
    **Note:** This notebook uses synthetic data for demonstration.
    To use real data, open an Icechunk store and pass actual per-cell
    timeseries datasets via `AnalysisStorage.load_percell_timeseries()`.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ---

    **Previous**: [18 — Store Operations](./18_workflow_store_operations.py) | **Next**: [20 — 3D Grid Gallery](./20_grid_3d_gallery.py)

    *canVODpy — Apache 2.0*
    """
    )
    return


if __name__ == "__main__":
    app.run()
