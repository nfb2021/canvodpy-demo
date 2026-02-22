"""Hackathon Demo — canvodpy end-to-end pipeline with Rosalia test data."""

import marimo

__generated_with = "0.19.10"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import shutil
    import numpy as np
    import xarray as xr
    from canvodpy import Site
    from canvod.grids import create_hemigrid, store_grid
    from canvod.grids.operations import add_cell_ids_to_vod_fast, store_dataset_with_cell_ids
    from canvod.vod import TauOmegaZerothOrder
    from canvod.viz import HemisphereVisualizer

    return (
        HemisphereVisualizer,
        Site,
        TauOmegaZerothOrder,
        add_cell_ids_to_vod_fast,
        create_hemigrid,
        np,
        shutil,
        store_dataset_with_cell_ids,
        store_grid,
    )


@app.cell
def _(Site, mo, shutil):
    mo.md(r"""## 1 · Site & Pipeline""")

    from pathlib import Path
    STORE_ROOT = Path("/tmp/canvodpy_demo")
    if STORE_ROOT.exists():
        shutil.rmtree(STORE_ROOT)

    site = Site("Rosalia")
    pipeline = site.pipeline(aux_agency="COD", n_workers=4)

    mo.md(f"""
    | | |
    |---|---|
    | **Site** | `{site.name}` |
    | **Receivers** | {list(site.active_receivers.keys())} |
    | **VOD analyses** | {list(site.vod_analyses.keys())} |
    | **RINEX store** | `{site.rinex_store.store_path}` |
    """)
    return Path, pipeline, site


@app.cell
def _(Path, mo, pipeline, shutil):
    mo.md(r"""## 2 · Process Date 2025-001""")
    aux_dir = Path('/Users/work/Developer/GNSS/canvodpy/packages/canvod-readers/tests/test_data/valid/aux/aux_2025001.zarr')
    if aux_dir.exists():
        shutil.rmtree(aux_dir)
    
    datasets = pipeline.process_date("2025001")

    mo.md(f"""
    | Receiver | Epochs | SIDs |
    |---|---|---|
    {"".join(f"| **{rx}** | {ds.sizes['epoch']} | {ds.sizes['sid']} |" + chr(10) for rx, ds in datasets.items())}
    """)
    return


@app.cell
def _(mo, site):
    mo.md(r"""## 3 · Explore the Store""")

    canopy_ds = site.rinex_store.read_group("canopy_01")

    with site.rinex_store.readonly_session() as _sess:
        meta_table = site.rinex_store.load_metadata(
            store=_sess.store, group_name="canopy_01"
        )
    # Available groups: canopy_01, reference_01_canopy_01

    mo.md(f"Dataset loaded — `canopy_01`  {dict(canopy_ds.sizes)}")
    return canopy_ds, meta_table


@app.cell
def _(canopy_ds):
    canopy_ds
    return


@app.cell
def _(meta_table, mo):
    mo.ui.table(meta_table, pagination=True)
    return


@app.cell
def _(mo, site):
    mo.md(r"""## 4 · Branches & Versioning""")

    from icechunk import IcechunkError

    def _create_or_replace(s, name, snapshot_id):
        try:
            s.repo.create_branch(name, snapshot_id)
        except IcechunkError:
            s.delete_branch(name)
            s.repo.create_branch(name, snapshot_id)

    with site.rinex_store.writable_session("main") as _sess:
        _latest = site.rinex_store.get_history()[0]["snapshot_id"]
        _create_or_replace(site.rinex_store, "experimental", _latest)

    hist     = site.rinex_store.get_history()
    branches = site.rinex_store.get_branch_names()

    mo.md(f"Branches: **{branches}** — latest snapshot: `{hist[0]['snapshot_id'][:12]}…`")
    return (hist,)


@app.cell
def _(site):
    site.rinex_store.plot_commit_graph()
    return


@app.cell
def _(hist, mo):
    import pandas as pd

    mo.ui.table(
        pd.DataFrame(hist)[["snapshot_id", "commit_msg", "written_at"]],
        pagination=True,
    )
    return


@app.cell
def _(TauOmegaZerothOrder, mo, site):
    mo.md(r"""## 5 · VOD Calculation — Tau-Omega Zeroth Order""")

    canopy_ds_vod = site.rinex_store.read_group("canopy_01")
    ref_ds_vod    = site.rinex_store.read_group("reference_01_canopy_01")

    vod_ds = TauOmegaZerothOrder.from_datasets(
        canopy_ds=canopy_ds_vod,
        sky_ds=ref_ds_vod,
        align=True,
    )
    vod_ds = vod_ds.unify_chunks().chunk({"epoch": 34560, "sid": -1})
    for _var in vod_ds.data_vars:
        vod_ds[_var].encoding = {}

    mo.md(f"""
    | | |
    |---|---|
    | Epochs | {vod_ds.sizes['epoch']:,} |
    | SIDs | {vod_ds.sizes['sid']} |
    """)
    return (vod_ds,)


@app.cell
def _(vod_ds):
    vod_ds
    return


@app.cell
def _(create_hemigrid, mo, site, store_grid):
    mo.md(r"""## 6 · Equal-Area Hemisphere Grid (2°)""")

    ea_grid   = create_hemigrid("equal_area", angular_resolution=2)
    snap_grid = store_grid(ea_grid, site.rinex_store, "equal_area_2deg")

    mo.md(f"""
    | | |
    |---|---|
    | Cells | {ea_grid.ncells} |
    | Snapshot | `{snap_grid[:12]}…` |
    """)
    return (ea_grid,)


@app.cell
def _(
    add_cell_ids_to_vod_fast,
    ea_grid,
    mo,
    np,
    site,
    store_dataset_with_cell_ids,
    vod_ds,
):
    mo.md(r"""## 7 · Assign Grid Cells to VOD Observations""")

    GRID_NAME   = "equal_area_2deg"
    vod_gridded = add_cell_ids_to_vod_fast(vod_ds, ea_grid, GRID_NAME)
    snap_vod    = store_dataset_with_cell_ids(vod_gridded, site.rinex_store, "vod_rosalia")

    _n = int((~np.isnan(vod_gridded[f"cell_id_{GRID_NAME}"].values)).sum())
    mo.md(f"**{_n:,}** observations assigned — snapshot `{snap_vod[:12]}…`")
    return GRID_NAME, vod_gridded


@app.cell
def _(GRID_NAME, ea_grid, np, vod_gridded):
    _vod_vals = vod_gridded["VOD"].values.ravel()
    _cell_ids = vod_gridded[f"cell_id_{GRID_NAME}"].values.ravel()
    _valid    = ~(np.isnan(_vod_vals) | np.isnan(_cell_ids))

    cell_mean_vod = np.full(ea_grid.ncells, np.nan)
    _ids  = _cell_ids[_valid].astype(int)
    _vals = _vod_vals[_valid]
    for _cid in np.unique(_ids):
        cell_mean_vod[_cid] = np.nanmean(_vals[_ids == _cid])

    cell_mean_vod
    return (cell_mean_vod,)


@app.cell
def _(HemisphereVisualizer, cell_mean_vod, ea_grid, mo):
    mo.md(r"""## 8 · Hemisphere Visualisation""")

    viz = HemisphereVisualizer(ea_grid)
    fig_2d, _ax = viz.plot_2d(
        data=cell_mean_vod,
        title="Mean VOD — Rosalia 2025-001",
        cmap="YlGn",
        vmin=0,
        vmax=1,
    )
    return (fig_2d,)


@app.cell
def _(fig_2d, mo):
    mo.md(r"""### 2-D polar hemisphere plot""")
    fig_2d
    return


@app.cell
def _(cell_mean_vod, ea_grid, mo):
    mo.md(r"""### 3-D interactive hemisphere plot""")
    from canvod.viz import visualize_grid_3d

    fig_3d = visualize_grid_3d(
        ea_grid,
        data=cell_mean_vod,
        title="Mean VOD — Rosalia 2025-001",
        colorscale="YlGn",
        add_overlays=True,
        add_axes=True,
    )
    return (fig_3d,)


@app.cell
def _(fig_3d):
    fig_3d
    return


if __name__ == "__main__":
    app.run()
