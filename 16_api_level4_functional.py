# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvodpy>=0.2.2",
#   "marimo>=0.21.1",
# ]
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium", app_title="L4 — Functional API", css_file="canvod_nordic.css"
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Level 4 — Functional API

    The L4 API exposes every pipeline step as a **standalone pure
    function**.  Each function has two variants:

    - **In-memory**: accepts and returns `xr.Dataset`
    - **File-based**: accepts and returns file paths (`str`)

    The file-based variants serialise intermediate results to NetCDF,
    making them compatible with workflow orchestrators like Airflow,
    Prefect, and Dagster where each task runs in a separate process.

    ---

    """
    )

    return (mo,)


# ---------------------------------------------------------------------------
# Section: in-memory pipeline
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## In-memory pipeline

    ```python
    from canvodpy.functional import (
        read_rinex,
        augment_with_ephemeris,
        create_grid,
        assign_grid_cells,
        calculate_vod,
    )
    from canvod.auxiliary import ECEFPosition

    # Step 1: read
    ds_canopy = read_rinex("canopy.rnx", reader="rinex3")
    ds_reference = read_rinex("reference.rnx")

    # Step 2: augment with satellite geometry
    rx_pos = ECEFPosition.from_ds_metadata(ds_canopy)
    ds_canopy = augment_with_ephemeris(
        ds_canopy, rx_pos,
        source="final", agency="COD", date="2025001",
    )

    # Step 3: create grid and assign cells
    grid = create_grid("equal_area", angular_resolution=2.0)
    ds_canopy = assign_grid_cells(ds_canopy, grid)

    # Step 4: compute VOD
    vod = calculate_vod(ds_canopy, ds_reference)
    ```

    Each function is self-contained: it accepts all required inputs
    as parameters and returns its output without side effects.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: function reference
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    _funcs = [
        (
            "read_rinex",
            "path, reader='rinex3'",
            "xr.Dataset",
            "Read one RINEX/SBF file",
        ),
        (
            "augment_with_ephemeris",
            "ds, rx_pos, source, agency, date",
            "xr.Dataset",
            "Add θ, φ, r coordinates",
        ),
        ("create_grid", "grid_type, **params", "GridData", "Create hemispheric grid"),
        ("assign_grid_cells", "ds, grid", "xr.Dataset", "Add cell_id variable"),
        ("calculate_vod", "canopy_ds, sky_ds, calculator", "xr.Dataset", "Compute VOD"),
    ]

    _rows = "\n".join(f"| `{n}` | `{p}` | `{r}` | {d} |" for n, p, r, d in _funcs)

    mo.md(
        f"""
    ### Function reference

    | Function | Key parameters | Returns | Description |
    |----------|---------------|---------|-------------|
    {_rows}

    All functions accept additional `**kwargs` that are forwarded to
    the underlying component constructors.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: file-based pipeline
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## File-based pipeline (Airflow)

    The `_to_file` variants write results to disk and return the path
    as a string — suitable for Airflow XCom:

    ```python
    from canvodpy.functional import (
        read_rinex_to_file,
        create_grid_to_file,
        assign_grid_cells_to_file,
        calculate_vod_to_file,
    )

    # Each step reads inputs from disk and writes outputs to disk
    canopy = read_rinex_to_file("canopy.rnx", "/tmp/canopy.nc")
    sky = read_rinex_to_file("reference.rnx", "/tmp/reference.nc")
    grid = create_grid_to_file("/tmp/grid.nc", "equal_area", angular_resolution=2.0)
    canopy = assign_grid_cells_to_file(canopy, grid, "/tmp/canopy_gridded.nc")
    vod = calculate_vod_to_file(canopy, sky, "/tmp/vod.nc")
    ```

    ### Airflow DAG example

    ```python
    from airflow.decorators import dag, task

    @dag(schedule="@daily")
    def gnss_pipeline():
        @task
        def read_canopy():
            return read_rinex_to_file(
                "s3://gnss/canopy/2025001.rnx",
                "/tmp/canopy.nc",
            )

        @task
        def read_reference():
            return read_rinex_to_file(
                "s3://gnss/reference/2025001.rnx",
                "/tmp/reference.nc",
            )

        @task
        def compute_vod(canopy_path, reference_path):
            return calculate_vod_to_file(
                canopy_path, reference_path, "/tmp/vod.nc",
            )

        c = read_canopy()
        r = read_reference()
        compute_vod(c, r)
    ```

    Airflow automatically passes return values between tasks via XCom.
    Since each `_to_file` function returns a path string, the
    downstream task knows where to find its input.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: mixing levels
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Mixing API levels

    L4 functions use the same underlying components as all other levels.
    You can freely mix levels in a single script:

    ```python
    from canvodpy import Site
    from canvodpy.functional import read_rinex, calculate_vod

    # Use L2 for site configuration
    site = Site("my_site")

    # Use L4 for explicit step control
    ds_c = read_rinex(site_canopy_path, reader="rinex3")
    ds_r = read_rinex(site_reference_path)

    # Use the VodComputer from L3
    vod_result = calculate_vod(ds_c, ds_r, calculator="tau_omega")
    ```

    This flexibility is by design: the API levels are not mutually
    exclusive but complementary views of the same pipeline.
    """
    )

    return


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ---

    **Previous**: [15 — L3 Site Pipeline](./15_api_level3_site_pipeline.py)
    | **Next**: [17 — Single-Day Workflow](./17_workflow_single_day.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
