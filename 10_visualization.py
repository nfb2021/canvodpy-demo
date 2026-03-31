import marimo

__generated_with = "0.12.0"
app = marimo.App(
    width="medium", app_title="Visualization", css_file="canvod_nordic.css"
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Hemispheric Visualization

    The **canvod-viz** package provides 2D and 3D visualization of
    hemispheric grids and the data mapped onto them.  Two rendering
    backends are available:

    - **Matplotlib** (2D): polar-projection plots suitable for
      publication figures and quick inspection
    - **Plotly** (3D): interactive 3D hemisphere surfaces that can be
      rotated, zoomed, and exported to HTML

    The unified `HemisphereVisualizer` class wraps both backends behind
    a single API.  Lower-level access is available through
    `HemisphereVisualizer2D` and `HemisphereVisualizer3D`.

    —

    """
    )

    return (mo,)


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------


@app.cell
def _():
    import numpy as np

    return (np,)


# ---------------------------------------------------------------------------
# Section: creating a grid to visualize
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvod.grids import create_hemigrid

    grid = create_hemigrid("equal_area", angular_resolution=5.0)

    mo.md(
        f"""
    ## Setting up a grid

    All visualization functions accept a `HemiGrid` object.  We create
    a 5-degree equal-area grid (a good balance between cell count and
    visual clarity for demonstration purposes).

    ```python
    from canvod.grids import create_hemigrid

    grid = create_hemigrid("equal_area", angular_resolution=5.0)
    ```

    | Property | Value |
    |----------|-------|
    | **Grid type** | `{grid.grid_type}` |
    | **Cells** | {grid.ncells:,} |
    | **Resolution** | 5.0 degrees |
    """
    )

    return create_hemigrid, grid


# ---------------------------------------------------------------------------
# Section: 2D polar plot — empty grid
# ---------------------------------------------------------------------------


@app.cell
def _(grid, mo):
    from canvod.viz import HemisphereVisualizer, PolarPlotStyle

    viz = HemisphereVisualizer(grid)

    _style = PolarPlotStyle(
        title="Equal-Area Grid (5°)",
        figsize=(8, 8),
        edgecolor="steelblue",
        linewidth=0.3,
        alpha=0.4,
        cmap="Blues",
    )

    fig_empty, ax_empty = viz.plot_2d(style=_style)

    mo.md(
        r"""
    ## 2D polar projection — empty grid

    `plot_2d()` renders the grid cells as patches on a polar axis.
    When no data array is provided, all cells are drawn with the same
    fill colour — useful for inspecting grid geometry.

    ```python
    from canvod.viz import HemisphereVisualizer, PolarPlotStyle

    viz = HemisphereVisualizer(grid)
    fig, ax = viz.plot_2d(style=PolarPlotStyle(title="Grid", figsize=(8, 8)))
    ```

    The polar axis convention matches the hemispheric grid definition:

    - **Radial axis**: polar angle $\theta$ (0° at centre = overhead,
      90° at edge = horizon)
    - **Angular axis**: azimuth $\phi$ (0° = North, clockwise)
    """
    )

    return HemisphereVisualizer, PolarPlotStyle, ax_empty, fig_empty, viz


@app.cell
def _(fig_empty):
    fig_empty

    return


# ---------------------------------------------------------------------------
# Section: 2D polar plot — with data
# ---------------------------------------------------------------------------


@app.cell
def _(grid, mo, np, viz):
    # Simulate data: a smooth gradient based on polar angle (theta)
    _theta_centres = grid.grid["theta"].to_numpy()
    _data = np.cos(_theta_centres)  # cos(theta): 1 at zenith, 0 at horizon

    _style_data = PolarPlotStyle(  # type: ignore[unresolved-reference]
        title="Simulated VOD — cos(θ) gradient",
        figsize=(8, 8),
        cmap="YlGn",
        edgecolor="gray",
        linewidth=0.3,
        alpha=0.9,
        colorbar_label="VOD (simulated)",
    )

    fig_data, ax_data = viz.plot_2d(data=_data, style=_style_data)

    mo.md(
        f"""
    ## 2D polar plot with data

    When a 1-D array of length `ncells` is provided, each cell is
    colour-mapped to its data value.  Here we simulate a polar-angle-dependent
    VOD field using $\\cos(\\theta)$, which produces maximum attenuation
    overhead and zero at the horizon.

    ```python
    data = np.cos(grid.grid["theta"].to_numpy())
    fig, ax = viz.plot_2d(data=data, style=style)
    ```

    The colourbar label, limits, and colourmap are all configurable
    through `PolarPlotStyle`.

    **Data shape**: {_data.shape[0]} values (one per cell)
    """
    )

    return ax_data, fig_data


@app.cell
def _(fig_data):
    fig_data

    return


# ---------------------------------------------------------------------------
# Section: Tissot indicatrix
# ---------------------------------------------------------------------------


@app.cell
def _(ax_empty, fig_empty, grid, mo):
    from canvod.viz import add_tissot_indicatrix

    _fig_tissot, _ax_tissot = fig_empty, ax_empty
    add_tissot_indicatrix(_ax_tissot, grid, facecolor="gold", alpha=0.5)

    mo.md(
        r"""
    ## Tissot indicatrix

    The **Tissot indicatrix** places identical circles at grid cell
    centres and lets the projection distort them.  On an equal-area
    grid, the circles have constant area (though their shape may vary);
    on an equal-angle grid, areas shrink toward the zenith.

    ```python
    from canvod.viz import add_tissot_indicatrix

    fig, ax = viz.plot_2d(style=style)
    add_tissot_indicatrix(ax, grid, facecolor="gold", alpha=0.5)
    ```

    This is a standard cartographic tool for assessing projection
    distortion.  For GNSS-T, it confirms that the equal-area grid
    gives equal weight to observations at all elevations.
    """
    )

    return (add_tissot_indicatrix,)


# ---------------------------------------------------------------------------
# Section: 3D hemisphere
# ---------------------------------------------------------------------------


@app.cell
def _(grid, mo, np, viz):
    _theta_centres = grid.grid["theta"].to_numpy()
    _data_3d = np.cos(_theta_centres)

    fig_3d = viz.plot_3d(
        data=_data_3d,
        title="3D Hemisphere — cos(θ) gradient",
        colorscale="YlGn",
        opacity=0.85,
    )

    mo.md(
        r"""
    ## 3D interactive hemisphere

    `plot_3d()` renders each grid cell as a coloured surface element on a
    unit hemisphere using Plotly.  The result is interactive: rotate by
    dragging, zoom with scroll, hover for cell values.

    ```python
    fig = viz.plot_3d(
        data=data,
        title="3D Hemisphere",
        colorscale="YlGn",
        opacity=0.85,
    )
    ```

    The 3D view is particularly useful for inspecting spatial patterns
    that are hard to see in polar projection (e.g. directional gaps in
    satellite coverage, asymmetric canopy structure).
    """
    )

    return (fig_3d,)


@app.cell
def _(fig_3d):
    fig_3d

    return


# ---------------------------------------------------------------------------
# Section: 3D overlays
# ---------------------------------------------------------------------------


@app.cell
def _(mo, viz):
    from canvod.viz import HemisphereVisualizer3D

    _viz3d = HemisphereVisualizer3D(viz.viz_3d.grid)

    fig_overlay = _viz3d.plot_hemisphere_surface(
        title="3D with elevation rings and meridians",
        colorscale="Blues",
        opacity=0.6,
    )
    fig_overlay = _viz3d.add_spherical_overlays(
        fig_overlay,
        elevation_rings=[15, 30, 45, 60, 75],
        meridians_deg=[0, 45, 90, 135, 180, 225, 270, 315],
    )
    fig_overlay = _viz3d.add_custom_axes(fig_overlay)

    mo.md(
        r"""
    ## 3D overlays: elevation rings and meridians

    `add_spherical_overlays()` draws elevation rings (constant $\theta$)
    and meridian lines (constant $\phi$) over the hemisphere surface.
    `add_custom_axes()` adds labelled E/N/Up axes for orientation.

    ```python
    from canvod.viz import HemisphereVisualizer3D

    viz3d = HemisphereVisualizer3D(grid)
    fig = viz3d.plot_hemisphere_surface()
    fig = viz3d.add_spherical_overlays(
        fig, elevation_rings=[15, 30, 45, 60, 75],
    )
    fig = viz3d.add_custom_axes(fig)
    ```

    These overlays help interpret the 3D view by providing angular
    reference lines — the same role that grid lines play on a
    2D polar plot.
    """
    )

    return HemisphereVisualizer3D, fig_overlay


@app.cell
def _(fig_overlay):
    fig_overlay

    return


# ---------------------------------------------------------------------------
# Section: style presets
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvod.viz import PlotStyle, create_interactive_style, create_publication_style

    _pub = create_publication_style()
    _inter = create_interactive_style(dark_mode=True)

    _rows = []
    for _name, _s in [("publication", _pub), ("interactive", _inter)]:
        _rows.append(
            f"| `{_name}` | `{_s.colorscale}` | `{_s.background_color}` | "
            f"`{_s.font_size}` | `{_s.dark_mode}` |"
        )

    mo.md(
        f"""
    ## Style presets

    Two factory functions create pre-configured `PlotStyle` objects:

    ```python
    from canvod.viz import create_publication_style, create_interactive_style

    pub_style = create_publication_style()       # White bg, high DPI
    dark_style = create_interactive_style(True)  # Dark bg, larger fonts
    ```

    | Preset | Colorscale | Background | Font size | Dark mode |
    |--------|-----------|------------|-----------|-----------|
    {chr(10).join(_rows)}

    `PlotStyle` can be converted to a `PolarPlotStyle` for 2D plots
    via `.to_polar_style()`, or to a Plotly layout dict via
    `.to_plotly_layout()`.
    """
    )

    return PlotStyle, create_interactive_style, create_publication_style


# ---------------------------------------------------------------------------
# Section: convenience functions
# ---------------------------------------------------------------------------


@app.cell
def _(grid, mo, np):
    from canvod.viz import visualize_grid, visualize_grid_3d

    _data_conv = np.random.default_rng(42).uniform(0, 1, grid.ncells)

    fig2d, _ax2d = visualize_grid(
        grid,
        data=_data_conv,
        title="visualize_grid() — one-liner 2D",
        cmap="plasma",
    )

    fig3d_conv = visualize_grid_3d(
        grid,
        data=_data_conv,
        title="visualize_grid_3d() — one-liner 3D",
        colorscale="Plasma",
    )

    mo.md(
        r"""
    ## Convenience functions

    For quick one-off plots without constructing a `HemisphereVisualizer`,
    two module-level functions are available:

    ```python
    from canvod.viz import visualize_grid, visualize_grid_3d

    fig, ax = visualize_grid(grid, data=data, title="2D", cmap="plasma")
    fig3d = visualize_grid_3d(grid, data=data, title="3D")
    ```

    These accept the same keyword arguments as the class methods and
    return the same figure objects.
    """
    )

    return visualize_grid, visualize_grid_3d, fig2d, fig3d_conv


@app.cell
def _(fig2d):
    fig2d

    return


@app.cell
def _(fig3d_conv):
    fig3d_conv

    return


# ---------------------------------------------------------------------------
# Section: comparing grid types visually
# ---------------------------------------------------------------------------


@app.cell
def _(PolarPlotStyle, create_hemigrid, mo, np):
    import matplotlib.pyplot as plt

    from canvod.viz import HemisphereVisualizer2D

    _all_types = ["equal_area", "equal_angle", "fibonacci", "healpix"]
    _types = []
    for _t in _all_types:
        try:
            create_hemigrid(_t, angular_resolution=10.0)
            _types.append(_t)
        except Exception:
            pass  # skip unavailable grid types (e.g. healpix requires healpy)

    fig_comp, _axes = plt.subplots(
        1, len(_types), figsize=(6 * len(_types), 6), subplot_kw={"projection": "polar"}
    )
    if len(_types) == 1:
        _axes = [_axes]

    for _i, _gtype in enumerate(_types):
        _g = create_hemigrid(_gtype, angular_resolution=10.0)
        _v = HemisphereVisualizer2D(_g)
        _style = PolarPlotStyle(
            title=_gtype.replace("_", " ").title(),
            edgecolor="steelblue",
            linewidth=0.4,
            alpha=0.5,
            cmap="Blues",
            figsize=(6, 6),
        )
        _v.plot_grid_patches(style=_style, ax=_axes[_i])

    fig_comp.suptitle("Grid type comparison (10° resolution)", fontsize=14, y=1.02)
    plt.tight_layout()

    mo.md(
        r"""
    ## Comparing grid types

    Different grid types produce visibly different tessellations of
    the hemisphere.  The equal-area grid has bands of varying azimuthal
    resolution (more sectors near the horizon), while the equal-angle
    grid has uniform angular spacing but cells that shrink toward the
    zenith.

    ```python
    for grid_type in ["equal_area", "equal_angle", "fibonacci", "healpix"]:
        grid = create_hemigrid(grid_type, angular_resolution=10.0)
        viz = HemisphereVisualizer2D(grid)
        viz.plot_grid_patches(ax=ax, style=style)
    ```
    """
    )

    return HemisphereVisualizer2D, plt, fig_comp


@app.cell
def _(fig_comp):
    fig_comp

    return


# ---------------------------------------------------------------------------
# Section: publication figure
# ---------------------------------------------------------------------------


@app.cell
def _(grid, mo, np, viz):
    _data_pub = np.cos(grid.grid["theta"].to_numpy())

    fig_pub, ax_pub = viz.create_publication_figure(
        data=_data_pub,
        title="Hemispheric VOD Distribution",
        dpi=150,
    )

    mo.md(
        r"""
    ## Publication-quality figure

    `create_publication_figure()` applies high-DPI settings, clean
    styling, and appropriate font sizes for journal submissions:

    ```python
    fig, ax = viz.create_publication_figure(
        data=data,
        title="Hemispheric VOD Distribution",
        dpi=300,
        save_path="figure_1.png",
    )
    ```

    The optional `save_path` parameter writes the figure directly to
    disk at the specified DPI.
    """
    )

    return ax_pub, fig_pub


@app.cell
def _(fig_pub):
    fig_pub

    return


# ---------------------------------------------------------------------------
# Section: interactive explorer
# ---------------------------------------------------------------------------


@app.cell
def _(grid, mo, np, viz):
    _data_expl = np.cos(grid.grid["theta"].to_numpy())

    fig_explorer = viz.create_interactive_explorer(
        data=_data_expl,
        title="Interactive Data Explorer",
        dark_mode=False,
    )

    mo.md(
        r"""
    ## Interactive explorer

    `create_interactive_explorer()` creates a Plotly figure with
    hover tooltips showing cell ID, coordinates, and data value.
    It can optionally be saved as a standalone HTML file:

    ```python
    fig = viz.create_interactive_explorer(
        data=data,
        title="Explorer",
        dark_mode=True,
        save_html="explorer.html",
    )
    ```

    Dark mode uses a black background with lighter grid lines —
    useful for presentations and screen-based analysis.
    """
    )

    return (fig_explorer,)


@app.cell
def _(fig_explorer):
    fig_explorer

    return


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    —

    **Previous**: [09 — Store Metadata](./09_store_metadata.py)
    | **Next**: [11 — Configuration](./11_configuration.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
