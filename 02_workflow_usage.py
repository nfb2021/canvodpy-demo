import marimo

__generated_with = "0.19.5"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # canVODpy New API: VODWorkflow Usage

        The **VODWorkflow** class provides stateful orchestration for the complete
        VOD processing pipeline with structured logging and factory integration.

        ## What You'll Learn
        1. Initialize workflow with site configuration
        2. Process RINEX data for a date
        3. Calculate VOD from processed data
        4. Access structured logging context
        """
    )
    return


@app.cell
def _(mo):
    mo.md("## Setup: Import Workflow")
    return


@app.cell
def _():
    from canvodpy import VODWorkflow
    from datetime import date
    return VODWorkflow, date


@app.cell
def _(mo):
    mo.md(
        """
        ## 1. Initialize Workflow

        Create a workflow for a specific research site with custom parameters.
        """
    )
    return


@app.cell
def _(mo):
    site_input = mo.ui.text(
        value="Rosalia",
        label="Site Name",
        full_width=False,
    )
    grid_type = mo.ui.dropdown(
        options=["equal_area", "equal_angle", "healpix", "geodesic"],
        value="equal_area",
        label="Grid Type",
    )
    angular_res = mo.ui.slider(
        1.0, 10.0, value=5.0, label="Angular Resolution (°)", step=0.5
    )

    mo.hstack([site_input, grid_type, angular_res])
    return angular_res, grid_type, site_input


@app.cell
def _(VODWorkflow, angular_res, grid_type, mo, site_input):
    try:
        workflow = VODWorkflow(
            site=site_input.value,
            grid=grid_type.value,
            grid_params={"angular_resolution": angular_res.value},
        )

        mo.md(
            f"""
            **Workflow Initialized!**

            - Site: {workflow.site.name}
            - Grid: {grid_type.value}
            - Resolution: {angular_res.value}°
            - Total cells: {workflow.grid.ncells}
            """
        )
    except Exception as e:
        mo.md(f"⚠️ **Error:** {e}")
        mo.stop(True)
    return (workflow,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 2. Workflow Representation

        The workflow provides a clean repr showing its configuration.
        """
    )
    return


@app.cell
def _(workflow):
    workflow
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 3. Structured Logging Context

        The workflow has a context-bound logger that includes site information.
        """
    )
    return


@app.cell
def _(mo, workflow):
    mo.md(
        f"""
        Logger: `{workflow.log}`

        The logger automatically includes:
        - Site name: `{workflow.site.name}`
        - Grid type: `{workflow.grid.definition}`

        All log messages are structured JSON for LLM-assisted debugging!
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 4. Process Date (Demo - Requires Data)

        **Note:** This requires actual RINEX data files. 
        The demo shows the API structure.

        ```python
        # Process a specific date
        result = workflow.process_date(
            date(2025, 1, 15),
            receivers=["all"],  # or specific receivers
            augmentation_steps=["filter", "interpolate"]
        )

        # Returns dict with processed datasets
        {
            'rinex': xr.Dataset,      # Raw RINEX data
            'augmented': xr.Dataset,  # After augmentation
            'gridded': xr.Dataset,    # With grid assignments
        }
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 5. Calculate VOD (Demo - Requires Data)

        ```python
        # Calculate VOD from gridded data
        vod_ds = workflow.calculate_vod(
            gridded_data=result['gridded'],
            method="dual_polarization"
        )

        # Returns xarray.Dataset with VOD values per grid cell
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 6. Workflow Benefits

        ### ✅ Stateful Configuration
        Set site, grid, and parameters once, reuse for multiple dates.

        ### ✅ Structured Logging
        Context-bound logger with site/grid info for debugging.

        ### ✅ Factory Integration
        Uses ReaderFactory, GridFactory, VODFactory internally.

        ### ✅ Clean API
        Simple method calls: `process_date()` and `calculate_vod()`.

        ### ✅ Type Hints
        Full type annotations for IDE support.

        ---

        **Next:** See `03_functional_api.py` for pure functions.
        """
    )
    return


if __name__ == "__main__":
    app.run()
