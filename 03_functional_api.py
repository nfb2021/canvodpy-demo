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
        # canVODpy New API: Functional API

        The **functional API** provides pure functions for VOD processing.
        Each function is stateless and deterministic.

        ## Two Versions
        - **Data-returning**: For notebooks and interactive use
        - **Path-returning**: For Airflow XCom serialization

        ## What You'll Learn
        1. Read RINEX data
        2. Create grids
        3. Assign grid cells
        4. Calculate VOD
        5. Airflow integration pattern
        """
    )
    return


@app.cell
def _(mo):
    mo.md("## Setup: Import Functions")
    return


@app.cell
def _():
    from canvodpy.functional import (
        assign_grid_cells,
        calculate_vod,
        create_grid,
        read_rinex,
    )
    return assign_grid_cells, calculate_vod, create_grid, read_rinex


@app.cell
def _(mo):
    mo.md(
        """
        ## 1. Create Grid (Data-Returning)

        Pure function to create a grid with specified parameters.
        """
    )
    return


@app.cell
def _(mo):
    grid_type = mo.ui.dropdown(
        options=["equal_area", "equal_angle", "healpix"],
        value="equal_area",
        label="Grid Type",
    )
    angular_res = mo.ui.slider(
        2.0, 10.0, value=5.0, label="Angular Resolution (°)", step=1.0
    )

    mo.hstack([grid_type, angular_res])
    return angular_res, grid_type


@app.cell
def _(angular_res, create_grid, grid_type, mo):
    grid = create_grid(
        grid_type=grid_type.value,
        angular_resolution=angular_res.value,
    )

    mo.md(
        f"""
        **Grid Created!**

        - Type: {grid.definition}
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
        ## 2. Read RINEX (Demo - Requires File)

        ```python
        # Read RINEX file
        ds = read_rinex(
            path="path/to/data.rnx",
            reader="rinex3",
            keep_vars=["C1C", "L1C", "S1C"]
        )

        # Returns xarray.Dataset with RINEX data
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 3. Assign Grid Cells (Demo)

        ```python
        # Assign observations to grid cells
        gridded_ds = assign_grid_cells(
            data=ds,
            grid=grid,
        )

        # Returns Dataset with 'cell_id' coordinate
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 4. Calculate VOD (Demo)

        ```python
        # Calculate VOD from gridded data
        vod_ds = calculate_vod(
            data=gridded_ds,
            method="dual_polarization",
        )

        # Returns Dataset with VOD values per cell
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 5. Airflow Integration

        For Airflow DAGs, use the `*_to_file()` variants that return paths.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        '''
        ```python
        from airflow import DAG
        from airflow.operators.python import PythonOperator
        from canvodpy.functional_airflow import (
            create_grid_to_file,
            read_rinex_to_file,
            assign_grid_cells_to_file,
            calculate_vod_to_file,
        )

        with DAG("vod_processing", ...) as dag:

            # Task 1: Create grid
            create_grid_task = PythonOperator(
                task_id="create_grid",
                python_callable=create_grid_to_file,
                op_kwargs={
                    "grid_type": "equal_area",
                    "angular_resolution": 5.0,
                    "output_path": "/tmp/grid.zarr",
                },
            )

            # Task 2: Read RINEX
            read_rinex_task = PythonOperator(
                task_id="read_rinex",
                python_callable=read_rinex_to_file,
                op_kwargs={
                    "path": "/data/rinex/2025001.rnx",
                    "output_path": "/tmp/rinex.nc",
                },
            )

            # Task 3: Assign cells
            assign_cells_task = PythonOperator(
                task_id="assign_cells",
                python_callable=assign_grid_cells_to_file,
                op_kwargs={
                    "data_path": "{{ ti.xcom_pull(task_ids='read_rinex') }}",
                    "grid_path": "{{ ti.xcom_pull(task_ids='create_grid') }}",
                    "output_path": "/tmp/gridded.nc",
                },
            )

            # Task 4: Calculate VOD
            calc_vod_task = PythonOperator(
                task_id="calculate_vod",
                python_callable=calculate_vod_to_file,
                op_kwargs={
                    "data_path": "{{ ti.xcom_pull(task_ids='assign_cells') }}",
                    "output_path": "/tmp/vod.nc",
                },
            )

            create_grid_task >> assign_cells_task
            read_rinex_task >> assign_cells_task
            assign_cells_task >> calc_vod_task
        ```
        '''
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 6. Functional API Benefits

        ### ✅ Pure Functions
        No side effects, deterministic output.

        ### ✅ Stateless
        No configuration to manage between calls.

        ### ✅ Composable
        Easy to chain and combine.

        ### ✅ Airflow-Ready
        Path-returning variants for XCom serialization.

        ### ✅ Type Safe
        Full type hints for all functions.

        ---

        **Next:** See `04_custom_components.py` for extending the API.
        """
    )
    return


if __name__ == "__main__":
    app.run()
