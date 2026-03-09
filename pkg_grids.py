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
    # canvod-grids — Hemispheric Grid Types

    The **canvod-grids** package partitions the upper hemisphere into cells
    for spatially resolved VOD analysis.  Seven grid types are available,
    each with different trade-offs in cell uniformity, computation cost, and
    angular resolution.

    Use the controls below to compare grid types interactively.

    ---

    *Nicolas F. Bader, CLIMERS — TU Wien*
    *Licensed under Apache 2.0.  Provided "as is" without warranty of any kind.*
    """
    )


@app.cell
def _(mo):
    grid_type = mo.ui.dropdown(
        options=["equal_area", "equal_angle", "fibonacci", "healpix", "geodesic", "HTM"],
        value="equal_area",
        label="Grid type",
    )
    resolution = mo.ui.slider(
        start=2, stop=30, value=10, step=1,
        label="Angular resolution (deg)",
    )
    mo.hstack([grid_type, resolution], justify="start", gap=1)

    return grid_type, resolution


@app.cell
def _(grid_type, resolution):
    from canvod.grids import create_hemigrid

    grid = create_hemigrid(grid_type.value, angular_resolution=resolution.value)

    return create_hemigrid, grid


@app.cell
def _(grid, grid_type, mo, resolution):
    mo.md(f"""
## {grid_type.value} — {grid.ncells} cells at {resolution.value}°

| Property | Value |
|---|---|
| Grid type | `{grid_type.value}` |
| Cell count | {grid.ncells} |
| Resolution | {resolution.value}° |
""")


@app.cell
def _(grid, grid_type, mo):
    from canvod.viz import HemisphereVisualizer

    import numpy as np

    _viz = HemisphereVisualizer(grid)
    _fig, _ax = _viz.plot_2d(
        data=None,
        title=f"{grid_type.value} grid — {grid.ncells} cells",
    )

    mo.as_html(_fig)

    return HemisphereVisualizer, np


# ---------------------------------------------------------------------------
# Grid comparison table
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Grid Type Comparison

    The table below shows the cell count for each grid type at the selected
    resolution.
    """
    )


@app.cell
def _(create_hemigrid, mo, resolution):
    _types = ["equal_area", "equal_angle", "fibonacci", "healpix", "geodesic", "HTM"]
    _rows = []
    for _t in _types:
        try:
            _g = create_hemigrid(_t, angular_resolution=resolution.value)
            _rows.append(f"| `{_t}` | {_g.ncells} |")
        except Exception as _e:
            _rows.append(f"| `{_t}` | Error: {_e} |")

    mo.md(f"""
| Grid type | Cells at {resolution.value}° |
|---|---|
""" + "\n".join(_rows) + """

**equal_area** — Cells have approximately equal solid angle (best for
unbiased spatial averaging).
**equal_angle** — Regular phi/theta grid (simple but cells shrink near zenith).
**fibonacci** — Fibonacci spiral placement (near-uniform, non-hierarchical).
**healpix** — Hierarchical Equal Area isoLatitude Pixelisation (widely used in
astrophysics).
**geodesic** — Icosahedron subdivision (good uniformity).
**HTM** — Hierarchical Triangular Mesh (recursive triangle subdivision).
""")


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
