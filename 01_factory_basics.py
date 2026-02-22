import marimo

__generated_with = "0.19.10"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # canVODpy New API: Factory Basics

    This notebook demonstrates the **factory pattern** in the redesigned canVODpy API.
    Factories provide a clean interface for registering and creating components with
    ABC enforcement and automatic validation.

    ## What You'll Learn
    1. List available components
    2. Create components with the factory
    3. Pass parameters to components
    4. Register custom components
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Setup: Import Factories
    """)
    return


@app.cell
def _():
    from canvodpy.factories import (
        GridFactory,
        ReaderFactory,
        VODFactory,
    )

    return GridFactory, ReaderFactory, VODFactory


@app.cell
def _(mo):
    mo.md("""
    ## 1. List Available Components

    Each factory maintains a registry of available implementations.
    """)
    return


@app.cell
def _(GridFactory, ReaderFactory, VODFactory, mo):
    readers = ReaderFactory.list_available()
    grids = GridFactory.list_available()
    vod_calcs = VODFactory.list_available()

    mo.md(
        f"""
        **Available Readers:** `{", ".join(readers)}`

        **Available Grids:** `{", ".join(grids)}`

        **Available VOD Calculators:** `{", ".join(vod_calcs)}`
        """
    )
    return (grids,)


@app.cell
def _(mo):
    mo.md("""
    ## 2. Create Grid Builder

    Select a grid type and parameters to create a grid builder.
    """)
    return


@app.cell
def _(grids, mo):
    grid_selector = mo.ui.dropdown(
        options=grids,
        value="equal_area",
        label="Grid Type",
    )
    angular_res = mo.ui.slider(
        1.0, 10.0, value=5.0, label="Angular Resolution (°)", step=0.5
    )
    cutoff = mo.ui.slider(0.0, 30.0, value=10.0, label="Cutoff Angle (°)", step=1.0)

    mo.hstack([grid_selector, angular_res, cutoff])
    return angular_res, cutoff, grid_selector


@app.cell
def _(GridFactory, angular_res, cutoff, grid_selector, mo):
    builder = GridFactory.create(
        grid_selector.value,
        angular_resolution=angular_res.value,
        cutoff_theta=cutoff.value,
    )

    mo.md(
        f"""
        Created `{type(builder).__name__}` with:
        - Angular resolution: {angular_res.value}°
        - Cutoff angle: {cutoff.value}°
        """
    )
    return (builder,)


@app.cell
def _(mo):
    mo.md("""
    ## 3. Build and Inspect Grid
    """)
    return


@app.cell
def _(builder, mo):
    grid = builder.build()

    mo.md(
        f"""
        **Grid Built Successfully!**

        - Total cells: {grid.ncells}
        """
    )
    return (grid,)


@app.cell
def _(grid):
    grid.__dict__
    return


@app.cell
def _(mo):
    mo.md("""
    ## 4. Visualize Grid Structure

    The grid DataFrame contains cell boundaries and metadata.
    """)
    return


@app.cell
def _(grid):
    import matplotlib.pyplot as plt
    import numpy as np

    _df = grid.grid  # polars DataFrame — correct attribute is .grid, not .df

    _phi_deg = (_df["phi"].to_numpy() * 180 / np.pi)
    _theta_deg = (_df["theta"].to_numpy() * 180 / np.pi)

    _fig, _ax = plt.subplots(
        figsize=(7, 5),
        subplot_kw={"projection": "polar"},
        constrained_layout=True,
    )
    _sc = _ax.scatter(
        np.deg2rad(_phi_deg),
        _theta_deg,
        c=_theta_deg,
        cmap="viridis_r",
        s=40,
        alpha=0.7,
    )
    _ax.set_theta_zero_location("N")
    _ax.set_theta_direction(-1)
    _ax.set_rlim(0, 90)
    _ax.set_rticks([0, 30, 60, 90])
    _ax.set_yticklabels(["0°", "30°", "60°", "90°"], fontsize=8)
    _ax.set_title("Grid Cell Centers (polar view)", pad=15)
    plt.colorbar(_sc, ax=_ax, label="Zenith angle [°]", shrink=0.7)
    plt.gcf()
    return


@app.cell
def _(mo):
    mo.md("""
    ## 5. Factory Benefits

    ### ✅ ABC Enforcement
    Components must inherit from the correct ABC or registration fails.

    ### ✅ Type Safety
    Factories are generic and type-checked.

    ### ✅ Clean API
    Single entry point for all component types.

    ### ✅ Extensible
    Register your own implementations easily!

    ---

    **Next:** See `02_workflow_usage.py` for the VODWorkflow class.
    """)
    return


if __name__ == "__main__":
    app.run()
