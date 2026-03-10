import marimo

__generated_with = "0.20.2"
app = marimo.App(
    width="medium",
    css_file="canvod_nordic.css",
)


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from pathlib import Path

    from canvod.store import MyIcechunkStore

    return MyIcechunkStore, Path


@app.cell
def _(Path):
    from _paths import STORES_DIR

    data_root = STORES_DIR / "rosalia_rinex"
    data_root.exists()
    return (data_root,)


@app.cell
def _(MyIcechunkStore, data_root):
    mystore = MyIcechunkStore(store_path=data_root)
    mystore
    return (mystore,)


@app.cell
def _(create_hemigrid, mystore):
    from canvod.grids import store_grid

    grid = create_hemigrid("equal_area", angular_resolution=2)
    store_grid(grid, mystore, "equal_area_2deg")  # overwrites with correct attrs
    return


@app.cell
def _(mystore):
    mystore.tree
    return


@app.cell
def _(mystore):
    mystore.get_history()
    return


@app.cell
def _():
    return


@app.cell
def _(mystore):
    from icechunk import IcechunkError


    def create_or_replace_branch(mystore, branch_name: str, snapshot_id: str):
        """Create branch at snapshot_id. If it exists, delete and recreate."""
        try:
            mystore.repo.create_branch(branch_name, snapshot_id)
        except IcechunkError:
            # Prefer catching a more specific error if Icechunk provides one (e.g. BranchAlreadyExistsError)
            mystore.delete_branch(branch_name)
            mystore.repo.create_branch(branch_name, snapshot_id)

        return branch_name  # or return whatever create_branch returns, if needed


    with mystore.writable_session() as _session:
        latest_commit = mystore.get_history()[0]["snapshot_id"]
        print(latest_commit)
        new_branch = create_or_replace_branch(mystore, "experimental_branch", latest_commit)

    mystore
    return


@app.cell
def _(mystore):
    reference_rinex_ds = mystore.read_group(branch="main", group_name="canopy_01")
    # canopy_rinex_metadata_ds = mystore.read_group(
    #     branch="main", group_name="canopy_02/metadata/sbf_obs"
    # )

    reference_rinex_ds
    return (reference_rinex_ds,)


@app.cell
def _(mystore):
    canopy_rinex_ds = mystore.read_group(branch="main", group_name="reference_01_canopy_01")
    # canopy_rinex_metadata_ds = mystore.read_group(
    #     branch="main", group_name="canopy_02/metadata/sbf_obs"
    # )

    canopy_rinex_ds
    return (canopy_rinex_ds,)


@app.cell
def _(canopy_rinex_ds, reference_rinex_ds):
    delta_rec = canopy_rinex_ds - reference_rinex_ds
    delta_rec
    return (delta_rec,)


@app.cell
def _():
    # import xarray as xr

    # _rinex_ds = mystore.read_group(branch="main", group_name="canopy_01")
    # _rinex_metadata_ds = mystore.read_group(
    #     branch="main", group_name="canopy_02/metadata/sbf_obs"
    # )

    # _ds = xr.combine_by_coords([_rinex_ds, _rinex_metadata_ds], compat="override")
    # _ds
    return


@app.cell
def _(canopy_rinex_ds, np):
    snr_can = canopy_rinex_ds["SNR"].values
    mean_can = snr_can[~np.isnan(snr_can)].mean()
    mean_can
    return


@app.cell
def _(np, reference_rinex_ds):
    snr_ref = reference_rinex_ds["SNR"].values
    mean_ref = snr_ref[~np.isnan(snr_ref)].mean()
    mean_ref
    return


@app.cell
def _(mystore):
    with mystore.readonly_session() as session:
        canopy_rinex_metadata = mystore.load_metadata(
            store=session.store, group_name="reference_01_canopy_01"
        )

    canopy_rinex_metadata
    return (canopy_rinex_metadata,)


@app.cell
def _(mystore):
    commit_history_main = mystore.get_history(branch="main")
    commit_history_main
    return


@app.cell
def _(mystore):
    commit_history_exp = mystore.get_history(branch="experimental_branch")
    commit_history_exp
    return


@app.cell
def _(mystore):
    # mystore.delete_branch('experimental_branch')
    mystore.plot_commit_graph()
    return


@app.cell
def _(canopy_rinex_metadata, mo):
    table = mo.ui.table(data=canopy_rinex_metadata, pagination=True)
    return (table,)


@app.cell
def _(table):
    table
    return


@app.cell
def _(canopy_rinex_metadata, mo):
    df = mo.ui.dataframe(canopy_rinex_metadata)
    df
    return


@app.cell
def _():
    from canvod.grids.workflows import AdaptedVODWorkflow

    return (AdaptedVODWorkflow,)


@app.cell
def _(AdaptedVODWorkflow, data_root):
    wf = AdaptedVODWorkflow(vod_store_path=data_root)
    wf
    return


@app.cell
def _():
    from canvod.grids import create_hemigrid
    from canvod.grids.operations import add_cell_ids_to_ds_fast

    return add_cell_ids_to_ds_fast, create_hemigrid


@app.cell
def _(create_hemigrid):
    ea_grid = create_hemigrid(grid_type="equal_area", angular_resolution=2)
    ea_grid
    return (ea_grid,)


@app.cell
def _(add_cell_ids_to_ds_fast, ea_grid, mystore):
    canopy_rinex_ds_exp = mystore.read_group(
        branch="experimental_branch", group_name="canopy_01"
    )

    canopy_rinex_grid_ds = add_cell_ids_to_ds_fast(
        canopy_rinex_ds_exp, ea_grid, grid_name="equal_area_2deg", data_var="SNR"
    )
    return (canopy_rinex_grid_ds,)


@app.cell
def _(canopy_rinex_grid_ds):
    canopy_rinex_grid_ds
    return


@app.cell
def _(mystore):
    mystore
    return


@app.cell
def _():
    import numpy as np


    def generate_zenith_data(grid):
        theta = grid.grid["theta"].to_numpy()
        data = np.exp(-3 * theta)
        data += 0.05 * np.random.randn(len(data))
        return data

    return generate_zenith_data, np


@app.cell
def _(create_hemigrid, generate_zenith_data):
    import matplotlib.pyplot as plt

    from canvod.viz import HemisphereVisualizer

    grid_htm = create_hemigrid(angular_resolution=2, grid_type="equal_area")
    data_htm = generate_zenith_data(grid_htm)

    # Create unified visualizer
    viz = HemisphereVisualizer(grid_htm)

    # 2D visualization
    fig_2d, ax_2d = viz.plot_2d(data=data_htm)
    plt.gca()
    return HemisphereVisualizer, data_htm, viz


@app.cell
def _(data_htm, viz):
    # 3D visualization
    fig_3d = viz.plot_3d(data=data_htm)
    fig_3d.show()
    return


@app.cell
def _(delta_rec):
    delta_rec["VOD"] = delta_rec["SNR"]
    return


@app.cell
def _(delta_rec, ea_grid, mo, np):
    mo.md(r"""## 7 · Assign Grid Cells to VOD Observations""")
    from canvod.grids.operations import (
        add_cell_ids_to_vod_fast,
        store_dataset_with_cell_ids,
    )

    GRID_NAME = "equal_area_2deg"
    vod_gridded = add_cell_ids_to_vod_fast(delta_rec, ea_grid, GRID_NAME)
    _vod_vals = vod_gridded["SNR"].values.ravel()
    _cell_ids = vod_gridded[f"cell_id_{GRID_NAME}"].values.ravel()
    _valid = ~(np.isnan(_vod_vals) | np.isnan(_cell_ids))

    cell_mean_vod = np.full(ea_grid.ncells, np.nan)
    _ids = _cell_ids[_valid].astype(int)
    _vals = _vod_vals[_valid]
    for _cid in np.unique(_ids):
        cell_mean_vod[_cid] = np.nanmean(_vals[_ids == _cid])

    cell_mean_vod
    _n = int((~np.isnan(vod_gridded[f"cell_id_{GRID_NAME}"].values)).sum())
    return (cell_mean_vod,)


@app.cell
def _(cell_mean_vod):
    cell_mean_vod
    return


@app.cell
def _(HemisphereVisualizer, cell_mean_vod, ea_grid, mo, np):
    mo.md(r"""## 8 · Hemisphere Visualisation""")

    _viz = HemisphereVisualizer(ea_grid)
    _vmin = float(np.nanmin(cell_mean_vod))
    _vmax = float(np.nanmax(cell_mean_vod))

    print(f"VOD value range for visualization: vmin={_vmin}, vmax={_vmax}")
    _fig_2d, _ax = _viz.plot_2d(
        data=cell_mean_vod,
        title="Mean VOD — Rosalia 2025-001",
        cmap="YlGn",
        vmin=_vmin,
        vmax=_vmax,
    )
    _fig_2d
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
