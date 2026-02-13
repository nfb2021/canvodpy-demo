import marimo

__generated_with = "0.19.10"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import polars as pl
    from matplotlib.patches import Polygon as MplPolygon

    from canvod.grids import EqualAreaBuilder, create_hemigrid, grid_to_dataset
    from canvod.viz import visualize_grid_3d

    return (
        EqualAreaBuilder,
        MplPolygon,
        create_hemigrid,
        grid_to_dataset,
        mo,
        np,
        pl,
        plt,
        visualize_grid_3d,
    )


@app.cell
def _(mo):
    mo.md("""
    # canvod-grids: Hemispheric Grid Types

    The `canvod-grids` package discretises the hemisphere above a GNSS
    receiver into cells.  Seven grid implementations are available, all
    sharing the same `BaseGridBuilder` / `GridData` interface.

    This notebook builds every grid type, compares their cell counts and
    solid-angle uniformity, and visualises them side-by-side.

    ## Coordinate convention

    | Symbol | Meaning | Range |
    |--------|---------|-------|
    | **phi** | Azimuth (0 = North, pi/2 = East, clockwise) | 0 to 2 pi |
    | **theta** | Polar angle from zenith | 0 to pi/2 |
    """)
    return


@app.cell
def _(mo):
    resolution_slider = mo.ui.slider(
        2, 30, value=10, step=1, label="Angular resolution (deg)"
    )
    resolution_slider
    return (resolution_slider,)


@app.cell
def _(create_hemigrid, resolution_slider):
    _base_types = ["equal_area", "equal_angle", "equirectangular", "geodesic", "htm"]
    grids = {}
    for _gt in _base_types:
        grids[_gt] = create_hemigrid(_gt, angular_resolution=resolution_slider.value)

    try:
        grids["healpix"] = create_hemigrid(
            "healpix", angular_resolution=resolution_slider.value
        )
    except ImportError:
        pass

    try:
        grids["fibonacci"] = create_hemigrid(
            "fibonacci", angular_resolution=resolution_slider.value
        )
    except ImportError:
        pass
    return (grids,)


@app.cell
def _(mo, resolution_slider):
    mo.md(f"""
    ## 1 — Comparison table ({resolution_slider.value} deg resolution)
    """)
    return


@app.cell
def _(grids, np, pl):
    _rows = []
    for _name, _g in grids.items():
        _sa = _g.get_solid_angles()
        _cv = float(np.std(_sa) / np.mean(_sa) * 100) if np.mean(_sa) > 0 else 0.0
        _rows.append(
            {
                "Grid type": _name,
                "Cells": _g.ncells,
                "Mean solid angle [sr]": round(float(np.mean(_sa)), 6),
                "Std solid angle [sr]": round(float(np.std(_sa)), 6),
                "CV [%]": round(_cv, 2),
                "Coverage [sr]": round(float(np.sum(_sa)), 4),
            }
        )
    summary_df = pl.DataFrame(_rows).sort("Cells")
    summary_df
    return


@app.cell
def _(mo):
    mo.md("""
    **CV (coefficient of variation)** measures how uniform the cell
    solid angles are.  Lower is better: a perfect equal-area grid has
    CV = 0.  The hemisphere solid angle is 2 pi ~ 6.2832 sr.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 2 — GridData structure
    """)
    return


@app.cell
def _(grids, mo):
    ea_grid = grids["equal_area"]
    mo.md(
        f"""
        Every builder returns a frozen **`GridData`** dataclass:

        | Attribute | Value (equal_area) |
        |-----------|--------------------|
        | `grid_type` | `{ea_grid.grid_type}` |
        | `ncells` | {ea_grid.ncells} |
        | `grid.columns` | `{ea_grid.grid.columns}` |
        | `theta_lims.shape` | `{ea_grid.theta_lims.shape}` |
        | `len(phi_lims)` | {len(ea_grid.phi_lims)} |
        """
    )
    return (ea_grid,)


@app.cell
def _(ea_grid):
    ea_grid.grid.head(10)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 3 — Factory function vs builder pattern

    Two ways to create grids:
    """)
    return


@app.cell
def _(EqualAreaBuilder, create_hemigrid, mo):
    grid_factory = create_hemigrid("equal_area", angular_resolution=5.0)

    builder = EqualAreaBuilder(angular_resolution=5.0, cutoff_theta=10.0)
    grid_builder = builder.build()

    mo.md(
        f"""
        | Approach | Cutoff | Cells |
        |----------|--------|-------|
        | `create_hemigrid(...)` (no cutoff) | 0 deg | {grid_factory.ncells} |
        | `EqualAreaBuilder(..., cutoff_theta=10)` | 10 deg | {grid_builder.ncells} |

        The `cutoff_theta` parameter masks low-elevation cells near the
        horizon, which is useful because GNSS signals below ~10 deg are
        heavily affected by tropospheric delay.
        """
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## 4 — Solid-angle distribution per grid type
    """)
    return


@app.cell
def _(grids, np, plt):
    _ncols = (len(grids) + 1) // 2
    _fig, _axes = plt.subplots(
        2, _ncols, figsize=(4 * _ncols, 6), constrained_layout=True
    )
    _flat = _axes.ravel()

    for _ax, (_name, _g) in zip(_flat, grids.items()):
        _sa = _g.get_solid_angles()
        _cv = float(np.std(_sa) / np.mean(_sa) * 100)
        _ax.hist(_sa, bins=20, edgecolor="black", linewidth=0.5)
        _ax.set_title(f"{_name}\n{_g.ncells} cells, CV={_cv:.1f}%", fontsize=10)
        _ax.set_xlabel("Solid angle [sr]", fontsize=8)
        _ax.set_ylabel("Count", fontsize=8)
        _ax.tick_params(labelsize=7)

    for _ax in _flat[len(grids) :]:
        _ax.set_visible(False)

    _fig.suptitle("Solid-angle uniformity", fontsize=13)
    plt.gca()
    return


@app.cell
def _(mo):
    mo.md("""
    ## 5 — 2D polar projection (all grid types)
    """)
    return


@app.cell
def _(MplPolygon, grids, np, plt):
    def _xyz_to_polar(xyz):
        """Convert unit-sphere XYZ to (phi, sin(theta)) for polar plot."""
        _th = np.arccos(np.clip(xyz[2], -1, 1))
        _ph = np.arctan2(xyz[1], xyz[0]) % (2 * np.pi)
        return (_ph, np.sin(_th))

    try:
        import healpy as _hp
    except ImportError:
        _hp = None

    def _draw_cell(_ax, _row, _grid_type, _grid_data):
        """Draw a single cell: triangle for geodesic/htm, curvilinear for healpix, rectangle otherwise."""
        if _grid_type == "geodesic" and _grid_data.vertices is not None:
            _v_idx = _row["geodesic_vertices"]
            _pts = [_xyz_to_polar(_grid_data.vertices[i]) for i in _v_idx]
        elif _grid_type == "htm" and "htm_vertex_0" in _row:
            _pts = [_xyz_to_polar(np.array(_row[f"htm_vertex_{i}"])) for i in range(3)]
        elif _grid_type == "healpix" and _hp is not None and "healpix_ipix" in _row:
            _nside = int(_row["healpix_nside"])
            _ipix = int(_row["healpix_ipix"])
            _bnd = _hp.boundaries(_nside, _ipix, step=4)
            _th = np.arccos(np.clip(_bnd[2], -1, 1))
            _ph = np.arctan2(_bnd[1], _bnd[0]) % (2 * np.pi)
            _pts = list(zip(_ph, np.sin(_th)))
        else:
            _pts = [
                (_row["phi_min"], np.sin(_row["theta_min"])),
                (_row["phi_max"], np.sin(_row["theta_min"])),
                (_row["phi_max"], np.sin(_row["theta_max"])),
                (_row["phi_min"], np.sin(_row["theta_max"])),
            ]
        _ax.add_patch(
            MplPolygon(
                _pts, closed=True, fill=False, edgecolor="steelblue", linewidth=0.4
            )
        )

    _n = len(grids)
    _nc = min(4, _n)
    _nr = (_n + _nc - 1) // _nc

    _fig, _axes = plt.subplots(
        _nr,
        _nc,
        figsize=(4 * _nc, 4 * _nr),
        subplot_kw={"projection": "polar"},
        constrained_layout=True,
    )
    _flat = np.array(_axes).ravel()

    for _ax, (_name, _g) in zip(_flat, grids.items()):
        for _row in _g.grid.iter_rows(named=True):
            _draw_cell(_ax, _row, _name, _g)
        _ax.set_ylim(0, 1)
        _ax.set_rticks([])
        _ax.set_title(f"{_name} ({_g.ncells})", fontsize=10, pad=12)

    for _ax in _flat[_n:]:
        _ax.set_visible(False)

    _fig.suptitle(
        "Hemisphere grids — polar projection",
        fontsize=13,
        y=1.02,
    )
    plt.gca()
    return


@app.cell
def _(mo):
    mo.md("""
    ## 6 — Detailed grid statistics
    """)
    return


@app.cell
def _(grids, mo):
    _lines = []
    for _name, _g in grids.items():
        _s = _g.get_grid_stats()
        _lines.append(f"### {_name}")
        for _k, _v in _s.items():
            _lines.append(f"- **{_k}**: `{_v}`")
        _lines.append("")
    mo.md("\n".join(_lines))
    return


@app.cell
def _(mo):
    mo.md("""
    ## 7 — 3D hemisphere visualization

    Interactive 3D view of the hemisphere grid on the unit sphere.
    Select a grid type to explore its cell geometry.
    """)
    return


@app.cell
def _(grids, mo):
    grid_3d_selector = mo.ui.dropdown(
        options=list(grids.keys()),
        value="equal_area",
        label="Grid type",
    )
    grid_3d_selector
    return (grid_3d_selector,)


@app.cell
def _(grid_3d_selector, grids, visualize_grid_3d):
    fig_3d = visualize_grid_3d(
        grids[grid_3d_selector.value],
        title=f"{grid_3d_selector.value} — 3D hemisphere",
        add_overlays=True,
    )
    fig_3d
    return


@app.cell
def _(mo):
    mo.md("""
    ## 8 — Tissot's indicatrix (cell-centre dots)

    Equal-size dots placed at each cell centre reveal projection distortion.
    On a truly equal-area grid, dots appear evenly spaced.
    Clustering or gaps indicate non-uniform cell distribution.
    """)
    return


@app.cell
def _(MplPolygon, grids, np, plt):
    def _xyz_to_polar_t(xyz):
        _th = np.arccos(np.clip(xyz[2], -1, 1))
        _ph = np.arctan2(xyz[1], xyz[0]) % (2 * np.pi)
        return (_ph, np.sin(_th))

    try:
        import healpy as _hp_t
    except ImportError:
        _hp_t = None

    _nt = len(grids)
    _nc = min(4, _nt)
    _nr = (_nt + _nc - 1) // _nc
    _fig, _axes = plt.subplots(
        _nr,
        _nc,
        figsize=(5 * _nc, 5 * _nr),
        subplot_kw={"projection": "polar"},
        constrained_layout=True,
    )
    _axes = np.array(_axes).ravel() if _nt > 1 else [_axes]

    for _ax, (_name, _g) in zip(_axes, grids.items()):
        for _row in _g.grid.iter_rows(named=True):
            if _name == "geodesic" and _g.vertices is not None:
                _v_idx = _row["geodesic_vertices"]
                _verts = [_xyz_to_polar_t(_g.vertices[i]) for i in _v_idx]
            elif _name == "htm" and "htm_vertex_0" in _row:
                _verts = [
                    _xyz_to_polar_t(np.array(_row[f"htm_vertex_{i}"])) for i in range(3)
                ]
            elif _name == "healpix" and _hp_t is not None and "healpix_ipix" in _row:
                _nside = int(_row["healpix_nside"])
                _ipix = int(_row["healpix_ipix"])
                _bnd = _hp_t.boundaries(_nside, _ipix, step=4)
                _th = np.arccos(np.clip(_bnd[2], -1, 1))
                _ph = np.arctan2(_bnd[1], _bnd[0]) % (2 * np.pi)
                _verts = list(zip(_ph, np.sin(_th)))
            elif (
                _name == "fibonacci"
                and _g.voronoi is not None
                and "voronoi_region" in _row
            ):
                _region = _row["voronoi_region"]
                _v3d = _g.voronoi.vertices[_region]
                _verts = [_xyz_to_polar_t(_v3d[_vi]) for _vi in range(len(_v3d))]
            else:
                _verts = [
                    (_row["phi_min"], np.sin(_row["theta_min"])),
                    (_row["phi_max"], np.sin(_row["theta_min"])),
                    (_row["phi_max"], np.sin(_row["theta_max"])),
                    (_row["phi_min"], np.sin(_row["theta_max"])),
                ]
            _ax.add_patch(
                MplPolygon(
                    _verts,
                    closed=True,
                    fill=False,
                    edgecolor="steelblue",
                    linewidth=0.3,
                )
            )

        _phi = _g.grid["phi"].to_numpy()
        _theta = _g.grid["theta"].to_numpy()
        _ax.scatter(
            _phi,
            np.sin(_theta),
            s=12,
            c="gold",
            edgecolors="k",
            linewidths=0.3,
            zorder=5,
            alpha=0.8,
        )

        _ax.set_ylim(0, 1)
        _ax.set_rticks([])
        _ax.set_title(_name, fontsize=10, pad=12)

    for _ax in _axes[_nt:]:
        _ax.set_visible(False)

    _fig.suptitle("Tissot's indicatrix — cell-centre dots", fontsize=13, y=1.02)
    plt.gca()
    return


@app.cell
def _(mo):
    mo.md("""
    ## 9 — Convert to xarray Dataset

    `grid_to_dataset()` converts a `GridData` to an `xr.Dataset` for
    interoperability with the rest of the pipeline.
    """)
    return


@app.cell
def _(grid_to_dataset, grids):
    xr_ds = grid_to_dataset(grids["equal_area"])
    xr_ds
    return


@app.cell
def _(mo):
    mo.md("""
    ## 10 — Resolution sweep

    How does angular resolution affect cell count?
    """)
    return


@app.cell
def _(create_hemigrid, pl, plt):
    _resolutions = [2.0, 5.0, 10.0, 15.0, 20.0, 30.0]
    _sweep_types = ["equal_area", "equirectangular", "geodesic", "htm"]

    _rows = []
    for _gt in _sweep_types:
        for _res in _resolutions:
            _g = create_hemigrid(_gt, angular_resolution=_res)
            _rows.append({"Grid": _gt, "Resolution [deg]": _res, "Cells": _g.ncells})
    sweep_df = pl.DataFrame(_rows)

    _fig, _ax = plt.subplots(figsize=(8, 4), constrained_layout=True)
    for _gt in _sweep_types:
        _sub = sweep_df.filter(pl.col("Grid") == _gt)
        _ax.plot(
            _sub["Resolution [deg]"].to_numpy(),
            _sub["Cells"].to_numpy(),
            marker="o",
            label=_gt,
        )
    _ax.set_xlabel("Angular resolution [deg]")
    _ax.set_ylabel("Number of cells")
    _ax.set_yscale("log")
    _ax.legend(fontsize=9)
    _ax.set_title("Cell count vs angular resolution")
    _ax.grid(True, alpha=0.3)
    plt.gca()
    return (sweep_df,)


@app.cell
def _(sweep_df):
    sweep_df
    return


@app.cell
def _(mo):
    mo.md("""
    ## Summary

    | Grid | Cell shape | Equal area? | Extra dependency |
    |------|-----------|-------------|------------------|
    | `equal_area` | Rectangular | Approximately | None |
    | `equal_angle` | Rectangular | No (zenith bias) | None |
    | `equirectangular` | Rectangular | No (zenith bias) | None |
    | `healpix` | Curvilinear | Yes (by construction) | `healpy` |
    | `geodesic` | Triangular | Near-uniform | None |
    | `fibonacci` | Voronoi | Near-uniform | `scipy` |
    | `htm` | Triangular | Near-uniform | None |

    For most GNSS-T analyses, **`equal_area`** at 5 deg resolution is
    the recommended default.
    """)
    return


if __name__ == "__main__":
    app.run()
