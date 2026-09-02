# /// script
# requires-python = ">=3.14"
# dependencies = [
#   # canvodpy itself is unused directly here, but canvod-grids's published
#   # build imports canvod_grids.core.grid_builder -> canvodpy.logging, so
#   # every create_hemigrid() call fails with ModuleNotFoundError in a
#   # sandboxed/standalone install without it.
#   "canvodpy",
#   "canvod-grids",
#   "canvod-viz",
#   "healpy>=1.16",
#   "plotly>=5.0",
#   "marimo>=0.21.1",
# ]
#
# [tool.uv.sources]
# canvodpy = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "canvodpy", rev = "6aa534fb8d78251c5640857361505d98a9b7dfb9" }
# canvod-grids = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-grids", rev = "6aa534fb8d78251c5640857361505d98a9b7dfb9" }
# canvod-viz = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-viz", rev = "6aa534fb8d78251c5640857361505d98a9b7dfb9" }
#
# [tool.marimo.opengraph]
# title = "20 · 3D Grid Gallery"
# description = "Interactive 3D gallery comparing every implemented hemispheric grid type: empty geometry, shared random synthetic data, and per-cell sampled-volume as a biomass proxy."
# ///

import marimo

__generated_with = "0.23.14"
app = marimo.App(
    width="medium",
    app_title="3D Grid Gallery",
    css_file="canvod_nordic.css",
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # 3D Grid Gallery

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/20_grid_3d_gallery.py)

    A side-by-side comparison of every hemispheric grid type
    `canvod-grids` implements, each rendered as an **interactive 3D
    Plotly scene** (rotate by dragging, zoom with scroll) in three ways:

    - **a) Empty grid** — the raw tessellation, uniformly coloured, to
      compare cell shape and density
    - **b) Synthetic data** — the same random per-cell values projected
      onto each grid's own cells
    - **c) Cell volume** — each cell's angular wedge volume out to an
      assumed sensing radius, a proxy for how much biomass a signal in
      that direction samples
    - **d) 2D projection comparison** — the same synthetic data rendered
      as a 2D matplotlib polar plot, orthographic vs equidistant, side
      by side for each grid type

    All grids are built at a common **5° angular resolution** via
    `canvod.grids.create_hemigrid()`. Every 3D scene always shows real
    cell boundaries and the project's E/N/Up reference axes — see the
    note after the grid-building step for why.
    """
    )
    return (mo,)


@app.cell
def _():
    import numpy as np

    return (np,)


@app.cell
def _(mo):
    from canvod.grids import create_hemigrid

    GRID_LABELS = {
        "equal_area": "Equal Area",
        "equal_angle": "Equal Angle",
        "equirectangular": "Equirectangular",
        "htm": "HTM",
        "geodesic": "Geodesic",
        "fibonacci": "Fibonacci",
        "healpix": "HEALPix",
    }
    RESOLUTION_DEG = 5.0

    grids = {}
    _build_errors = {}
    for _gtype in GRID_LABELS:
        try:
            grids[_gtype] = create_hemigrid(_gtype, angular_resolution=RESOLUTION_DEG)
        except Exception as _e:
            _build_errors[_gtype] = str(_e).splitlines()[0]

    _rows = "\n".join(
        f"| {GRID_LABELS[_t]} | `{_t}` | {grids[_t].ncells:,} | ✅ built |"
        if _t in grids
        else f"| {GRID_LABELS[_t]} | `{_t}` | — | ⏭️ skipped: {_build_errors[_t]} |"
        for _t in GRID_LABELS
    )

    mo.md(
        f"""
    ## Building all implemented grid types

    | Grid | key | Cells (5°) | Status |
    |---|---|---:|---|
    {_rows}

    HEALPix requires the optional `healpy` dependency. If it isn't
    installed, that row is skipped above and the rest of this notebook
    simply shows one fewer tab in each gallery.
    """
    )
    return GRID_LABELS, grids


@app.cell
def _(mo):
    mo.md(r"""
    ## Every 3D scene includes cell boundaries and reference axes

    `canvod-viz`'s Plotly 3D scenes hide the native Cartesian
    x/y/z axes (`showbackground=False`) since raw sin/cos-projected
    coordinates aren't physically meaningful on their own.
    `HemisphereVisualizer3D.add_custom_axes()` draws artificial E/N/Up
    axis lines and labels in their place — not real Plotly axes, but
    built to read as if they were. `add_spherical_overlays()` adds
    elevation rings and meridians as an angular reference grid.
    Without these, a 3D hemisphere plot has no orientation or scale
    reference at all — every figure in this notebook applies both,
    plus real cell-boundary wireframes (`show_wireframe=True`, fixed
    2026-07-19 — previously a declared-but-unwired no-op parameter in
    `plot_hemisphere_surface`; cell edges were never actually drawn).
    """)
    return


@app.cell
def _():
    from canvod.viz import HemisphereVisualizer3D

    def add_reference_frame(fig, viz: HemisphereVisualizer3D):
        """Apply this project's standard 3D reference frame to `fig`.

        Elevation rings + meridians (`add_spherical_overlays`) and the
        artificial-but-native-looking E/N/Up axes (`add_custom_axes`)
        are a non-negotiable part of every 3D hemisphere plot in this
        project -- see canvodpy-perf/CLAUDE.md's "3D visualization
        conventions" section.
        """
        fig = viz.add_spherical_overlays(fig)
        fig = viz.add_custom_axes(fig)
        return fig

    return HemisphereVisualizer3D, add_reference_frame


@app.cell
def _(mo):
    mo.md(r"""
    ## Synthetic data

    Each grid gets independent random per-cell values from a fixed
    seed — not a physically meaningful field, just enough variation to
    compare how each tessellation renders data.
    """)
    return


@app.cell
def _(grids, np):
    _rng = np.random.default_rng(42)
    synthetic_data = {_t: _rng.uniform(0.1, 1.0, _g.ncells) for _t, _g in grids.items()}
    return (synthetic_data,)


@app.cell
def _(mo):
    mo.md(r"""
    ## Cell volume — a biomass-sampling proxy

    Grid cells are purely angular (theta, phi) partitions of the sky as
    seen from the antenna -- they have a solid angle but no inherent
    physical size. What actually determines how much canopy biomass a
    satellite signal in a given cell's direction samples is the
    **volume** of space that direction subtends, not its solid angle
    alone.

    Modelling the canopy as a uniform-density region extending out to a
    fixed **sensing radius** $R$ around the antenna, each cell is a
    spherical sector (a cone from the antenna out to radius $R$)
    with volume

    $$
    V_{\text{cell}} = \frac{1}{3} \, \Omega_{\text{cell}} \, R^3
    $$

    where $\Omega_{\text{cell}}$ is the cell's solid angle
    (`GridData.get_solid_angles()`, fixed and verified 2026-07-19 for
    all 6 non-HEALPix grid types). Since $R$ is the same for every
    cell, the *relative* pattern across cells is identical to the
    solid-angle pattern -- but expressed in physically interpretable
    units (m³), it directly answers "how much more/less biomass would
    a uniform canopy contribute to this cell than that one," which
    solid angle alone (steradians) does not communicate as directly.

    $R$ below is illustrative (a plausible forest canopy depth), not a
    calibrated value -- adjust `SENSING_RADIUS_M` for a real site.

    **On Fibonacci specifically:** its horizon-boundary cells are real
    spherical-Voronoi regions bounded by actual southern-hemisphere
    lattice points (needed to avoid the 4π double-counting bug fixed
    2026-07-19), so a handful of them genuinely dip a few degrees past
    the horizon (verified: ~6° at 10° resolution, ~12° at 20° — worse
    at coarser resolutions, but nowhere near reaching the far pole).
    That's still enough to skew a colour range shared across grid
    types, which is why each tab below uses its **own** scale instead:
    a shared one would let those few boundary cells compress every
    other grid's real distortion pattern into one indistinguishable
    colour. Each figure's title shows its own value range so the
    absolute numbers stay comparable even though the colours aren't
    directly comparable tab-to-tab.
    """)
    return


@app.cell
def _(grids):
    SENSING_RADIUS_M = 20.0

    cell_volumes = {
        _t: _g.get_solid_angles() * SENSING_RADIUS_M**3 / 3 for _t, _g in grids.items()
    }
    return (cell_volumes,)


@app.cell
def _(mo):
    mo.md(r"""
    ## a) Empty grids — geometry only

    Uniform cell colour, no data — only the tessellation itself is
    visible: cell shape, density, and horizon coverage.
    """)
    return


@app.cell
def _(GRID_LABELS, HemisphereVisualizer3D, add_reference_frame, grids, mo):
    _empty_figs = {}
    for _t, _g in grids.items():
        _viz = HemisphereVisualizer3D(_g)
        _fig = _viz.plot_hemisphere_surface(
            data=None,
            title=f"{GRID_LABELS[_t]} — {_g.ncells:,} cells",
            colorscale="Blues",
            opacity=0.85,
            show_wireframe=True,
            width=650,
            height=500,
        )
        _fig = add_reference_frame(_fig, _viz)
        _empty_figs[GRID_LABELS[_t]] = _fig

    mo.ui.tabs(_empty_figs, lazy=True)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## b) Synthetic data on each grid

    Same random values everywhere, but **each tab has its own colour
    scale** (auto-scaled to that grid's own min/max) rather than one
    shared range — a shared scale would compress everything toward one
    colour once any grid has a wider spread than the others. The title
    on each figure shows its actual value range so the numbers stay
    comparable even though the colours aren't.
    """)
    return


@app.cell
def _(
    GRID_LABELS,
    HemisphereVisualizer3D,
    add_reference_frame,
    grids,
    mo,
    synthetic_data,
):
    _data_figs = {}
    for _t, _g in grids.items():
        _viz = HemisphereVisualizer3D(_g)
        _vals = synthetic_data[_t]
        _fig = _viz.plot_hemisphere_surface(
            data=_vals,
            title=f"{GRID_LABELS[_t]} — synthetic data ({_vals.min():.2f}–{_vals.max():.2f})",
            colorscale="YlGn",
            opacity=0.95,
            show_wireframe=True,
            width=650,
            height=500,
        )
        _fig = add_reference_frame(_fig, _viz)
        _data_figs[GRID_LABELS[_t]] = _fig

    mo.ui.tabs(_data_figs, lazy=True)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## c) Cell volume — biomass-sampling proxy

    Colour now encodes each cell's own sampled volume, not a
    projection-distortion probe. **Each tab is scaled to its own
    min/max**, not a shared range — with a shared scale, Fibonacci's
    few over-horizon outlier cells (see note above) would stretch the
    colour range so wide that every other grid's real distortion
    pattern gets compressed into one indistinguishable colour. The
    title on each figure shows its actual m³ range, so `equal_area`
    reading as visually flat *and* a tight title range together
    confirm genuine uniformity — not just a coincidentally narrow
    shared scale.
    """)
    return


@app.cell
def _(
    GRID_LABELS,
    HemisphereVisualizer3D,
    add_reference_frame,
    cell_volumes,
    grids,
    mo,
):
    _volume_figs = {}
    for _t, _g in grids.items():
        _viz = HemisphereVisualizer3D(_g)
        _vols = cell_volumes[_t]
        _fig = _viz.plot_hemisphere_surface(
            data=_vols,
            title=f"{GRID_LABELS[_t]} — cell volume ({_vols.min():.1f}–{_vols.max():.1f} m³)",
            colorscale="Plasma",
            opacity=0.95,
            show_wireframe=True,
            width=650,
            height=500,
        )
        _fig = add_reference_frame(_fig, _viz)
        _volume_figs[GRID_LABELS[_t]] = _fig

    mo.ui.tabs(_volume_figs, lazy=True)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## d) 2D projection comparison — orthographic vs equidistant

    Everything above is the interactive 3D scene. `canvod-viz` also ships
    a publication-quality 2D matplotlib renderer
    (`HemisphereVisualizer2D` / `PolarPlotStyle`), and as of this section
    it supports two different **theta → rho** radial mappings via
    `PolarPlotStyle.projection`:

    - **orthographic** (`rho = sin(theta)`, the default) — mathematically
      the same view as looking straight down at the 3D hemisphere above
      from directly overhead: horizon cells compress toward the plot's
      rim, zenith cells stay spread out near the centre.
    - **equidistant** (`rho = theta / (pi/2)`) — a *true* polar plot,
      radius linear in the polar angle, so elevation rings are evenly
      spaced. This is the conventional GNSS-skyplot convention (e.g.
      RTKLIB), as opposed to a sphere-viewed-from-above projection.

    Same synthetic data as section (b), rendered both ways side by side
    for each grid type — the tessellation and the data are identical;
    only the radial mapping changes.
    """)
    return


@app.cell
def _(GRID_LABELS, grids, mo, synthetic_data):
    import matplotlib.pyplot as plt

    from canvod.viz import HemisphereVisualizer2D, PolarPlotStyle

    _proj_figs = {}
    for _t, _g in grids.items():
        _viz = HemisphereVisualizer2D(_g)
        _vals = synthetic_data[_t]
        _fig, _axes = plt.subplots(
            1, 2, figsize=(12, 6), subplot_kw={"projection": "polar"}
        )
        for _ax, _proj in zip(_axes, ["orthographic", "equidistant"]):
            _style = PolarPlotStyle(
                title=f"{GRID_LABELS[_t]} — {_proj}",
                cmap="YlGn",
                projection=_proj,
            )
            _viz.plot_grid_patches(data=_vals, style=_style, ax=_ax)
        _fig.tight_layout()
        _proj_figs[GRID_LABELS[_t]] = _fig

    mo.ui.tabs(_proj_figs, lazy=True)
    return


@app.cell
def _(mo):
    mo.md(r"""
    —

    **Previous**: [19 — Grid Exploration](./19_grid_exploration.py)

    *canVODpy — Apache 2.0*
    """)
    return


if __name__ == "__main__":
    app.run()
