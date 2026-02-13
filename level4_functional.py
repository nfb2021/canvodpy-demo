import marimo

__generated_with = "0.19.7"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # canVODpy API — Level 4: Functional API

        **Pure, stateless functions** that each do exactly one thing.
        No shared state, no side effects — ideal for Airflow DAGs,
        unit testing, and composition.

        ## The Task

        Same as every notebook in this series:

        1. Read RINEX data for **Rosalia**, DOY **2025001**
        2. Preprocess (augment with auxiliary data)
        3. Assign hemisphere grid cells
        4. Calculate VOD for canopy_01 / reference_01

        ## API at a Glance

        ```python
        from canvodpy import (
            read_rinex, create_grid, assign_grid_cells, calculate_vod_to_file
        )

        ds   = read_rinex(path, reader="rinex3")
        grid = create_grid(grid_type="equal_area", angular_resolution=5.0)
        ds   = assign_grid_cells(ds, grid)
        path = calculate_vod_to_file(canopy_path, ref_path, output_path)
        ```

        Each function returns **data** (xarray Dataset, GridData) or a
        **file path** (the `*_to_file` variants for Airflow XCom).

        | Aspect | Detail |
        |--------|--------|
        | Import | `from canvodpy import read_rinex, create_grid, ...` |
        | Pattern | Pure functions, no shared state |
        | Configuration | Explicit parameters on every call |
        | Best for | Airflow DAGs, testing, reproducible scripts |
        """
    )
    return


@app.cell
def _(mo):
    mo.md("## Step 1 — Create a hemisphere grid")
    return


@app.cell
def _():
    from canvodpy import create_grid

    return (create_grid,)


@app.cell
def _(create_grid, mo):
    grid = create_grid(grid_type="equal_area", angular_resolution=5.0)

    mo.md(
        f"""
        **Grid built**

        - Type: `{grid.definition}`
        - Cells: {grid.ncells}
        - Bands: {grid.nbands}
        """
    )
    return (grid,)


@app.cell
def _(grid):
    grid.df.head(10)
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## Step 2 — Read RINEX data

        `read_rinex` takes a file path and returns an xarray Dataset.
        """
    )
    return


@app.cell
def _():
    from canvodpy import read_rinex

    return (read_rinex,)


@app.cell
def _(mo, read_rinex):
    try:
        from pathlib import Path

        # Locate a RINEX file from demo data
        demo_dir = Path(__file__).parent / "data" / "01_Rosalia"
        ref_dir = demo_dir / "01_reference" / "01_GNSS" / "01_raw" / "25001"
        rinex_file = next(ref_dir.glob("*.25o"))

        ds = read_rinex(path=rinex_file, reader="rinex3")
        data_ok = True
        mo.md(
            f"""
            **RINEX loaded** — `{rinex_file.name}`

            - Dimensions: `{dict(ds.dims)}`
            - Variables: {len(ds.data_vars)}
            """
        )
    except Exception as e:
        ds = None
        data_ok = False
        mo.md(
            f"""
            Demo data not available (`{type(e).__name__}`).

            ```python
            ds = read_rinex(path="path/to/file.rnx", reader="rinex3")
            ```
            """
        )
    return data_ok, ds


@app.cell
def _(mo):
    mo.md(
        """
        ## Step 3 — Assign grid cells

        `assign_grid_cells` adds a `cell_id` coordinate to the dataset.
        """
    )
    return


@app.cell
def _():
    from canvodpy import assign_grid_cells

    return (assign_grid_cells,)


@app.cell
def _(assign_grid_cells, data_ok, ds, grid, mo):
    if data_ok:
        try:
            gridded = assign_grid_cells(ds, grid)
            mo.md(
                f"""
                **Grid cells assigned**

                - `cell_id` now in coordinates: `{"cell_id" in gridded.coords}`
                """
            )
        except Exception as e:
            gridded = None
            mo.md(f"Grid assignment failed (`{type(e).__name__}: {e}`).")
    else:
        gridded = None
        mo.md(
            """
            ```python
            gridded = assign_grid_cells(ds, grid)
            # Dataset now has a 'cell_id' coordinate
            ```
            """
        )
    return (gridded,)


@app.cell
def _(mo):
    mo.md(
        """
        ## Step 4 — Calculate VOD

        The functional API calculates VOD from a canopy and reference
        dataset pair.

        ```python
        from canvodpy.functional import calculate_vod

        vod = calculate_vod(
            canopy_ds=gridded_canopy,
            reference_ds=gridded_reference,
            calculator="tau_omega",
        )
        ```

        For Airflow, use the path-returning variant:

        ```python
        from canvodpy import calculate_vod_to_file

        output_path = calculate_vod_to_file(
            canopy_path="/tmp/canopy.nc",
            reference_path="/tmp/reference.nc",
            output_path="/tmp/vod.nc",
        )
        # Returns the output path string (XCom-serialisable)
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## Airflow DAG Pattern

        The `*_to_file` functions return **path strings** that serialize
        cleanly through Airflow XCom.

        ```python
        from airflow import DAG
        from airflow.operators.python import PythonOperator
        from canvodpy import (
            create_grid_to_file,
            read_rinex_to_file,
            assign_grid_cells_to_file,
            calculate_vod_to_file,
        )

        with DAG("vod_pipeline", ...) as dag:

            t_grid = PythonOperator(
                task_id="create_grid",
                python_callable=create_grid_to_file,
                op_kwargs={"grid_type": "equal_area",
                           "angular_resolution": 5.0,
                           "output_path": "/tmp/grid.zarr"},
            )

            t_read = PythonOperator(
                task_id="read_rinex",
                python_callable=read_rinex_to_file,
                op_kwargs={"path": "/data/2025001.rnx",
                           "output_path": "/tmp/rinex.nc"},
            )

            t_assign = PythonOperator(
                task_id="assign_cells",
                python_callable=assign_grid_cells_to_file,
                op_kwargs={
                    "data_path": "{{ ti.xcom_pull('read_rinex') }}",
                    "grid_path": "{{ ti.xcom_pull('create_grid') }}",
                    "output_path": "/tmp/gridded.nc",
                },
            )

            t_vod = PythonOperator(
                task_id="calculate_vod",
                python_callable=calculate_vod_to_file,
                op_kwargs={
                    "canopy_path": "{{ ti.xcom_pull('assign_cells') }}",
                    "reference_path": "/tmp/gridded_ref.nc",
                    "output_path": "/tmp/vod.nc",
                },
            )

            [t_grid, t_read] >> t_assign >> t_vod
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## Summary

        | Pro | Con |
        |-----|-----|
        | Pure functions — easy to test and reason about | Most verbose API level |
        | Airflow-ready (`*_to_file` variants) | Must wire steps manually |
        | Full control over every parameter | No shared configuration |
        | Composable and parallelisable | No structured logging built in |

        ## Series Overview

        | Notebook | API | Lines | State | Execution |
        |----------|-----|-------|-------|-----------|
        | `level1_convenience.py` | `process_date`, `calculate_vod` | 2 | None | Eager |
        | `level2_fluent.py` | `workflow().read().vod().result()` | 5-6 | Builder plan | Deferred |
        | `level3_workflow.py` | `VODWorkflow.process_date()` | 8-10 | Site + grid | Eager |
        | **`level4_functional.py`** | `read_rinex`, `create_grid`, ... | 10-15 | None | Eager |
        """
    )
    return


if __name__ == "__main__":
    app.run()
