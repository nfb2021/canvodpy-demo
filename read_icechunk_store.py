import marimo

__generated_with = "0.19.7"
app = marimo.App(
    width="medium",
    css_file="./marimo_darkmode_patch/marimo_darkmode_patch.css",
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
    # data_root = Path('/Users/work/Developer/GNSS/canvodpy-test-data/valid/01_Rosalia/03_Rinex_Testing')
    # data_root = Path('/Volumes/SanDisk/GNSS/ComparedStores/Rosalia/rinex')
    data_root = Path("/Volumes/SanDisk/GNSS/Rosalia/rinex")
    data_root.exists()
    return (data_root,)


@app.cell
def _(MyIcechunkStore, data_root):
    mystore = MyIcechunkStore(store_path=data_root)
    mystore
    return (mystore,)


@app.cell
def _(mystore):
    mystore.tree


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
        new_branch = create_or_replace_branch(
            mystore, "experimental_branch", latest_commit
        )

    mystore


@app.cell
def _(mystore):
    canopy_rinex_ds = mystore.read_group(branch="main", group_name="canopy_01")
    canopy_rinex_ds


@app.cell
def _(mystore):
    with mystore.readonly_session() as session:
        canopy_rinex_metadata = mystore.load_metadata(
            store=session.store, group_name="canopy_01"
        )

    canopy_rinex_metadata
    return (canopy_rinex_metadata,)


@app.cell
def _(mystore):
    commit_history_main = mystore.get_history(branch="main")
    commit_history_main


@app.cell
def _(mystore):
    commit_history_exp = mystore.get_history(branch="experimental_branch")
    commit_history_exp


@app.cell
def _(mystore):
    # mystore.delete_branch('experimental_branch')
    mystore.plot_commit_graph()


@app.cell
def _(canopy_rinex_metadata, mo):
    table = mo.ui.table(data=canopy_rinex_metadata, pagination=True)
    return (table,)


@app.cell
def _(table):
    table


@app.cell
def _(canopy_rinex_metadata, mo):
    df = mo.ui.dataframe(canopy_rinex_metadata)
    df


@app.cell
def _():
    from canvod.grids.workflows import AdaptedVODWorkflow

    return (AdaptedVODWorkflow,)


@app.cell
def _(AdaptedVODWorkflow, data_root):
    wf = AdaptedVODWorkflow(vod_store_path=data_root)
    wf


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


@app.cell
def _(mystore):
    mystore


@app.cell
def _():
    import numpy as np

    def generate_zenith_data(grid):
        theta = grid.grid["theta"].to_numpy()
        data = np.exp(-3 * theta)
        data += 0.05 * np.random.randn(len(data))
        return data

    return (generate_zenith_data,)


@app.cell
def _(create_hemigrid, generate_zenith_data):
    import matplotlib.pyplot as plt
    from canvod.viz import HemisphereVisualizer

    grid_htm = create_hemigrid(angular_resolution=4, grid_type="equal_area")
    data_htm = generate_zenith_data(grid_htm)

    # Create unified visualizer
    viz = HemisphereVisualizer(grid_htm)

    # 2D visualization
    fig_2d, ax_2d = viz.plot_2d(data=data_htm)
    plt.gca()

    return data_htm, viz


@app.cell
def _(data_htm, viz):
    # 3D visualization
    fig_3d = viz.plot_3d(data=data_htm)
    fig_3d.show()


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
