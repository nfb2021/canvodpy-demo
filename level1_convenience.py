import marimo

__generated_with = "0.19.10"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # canVODpy API — Level 1: Convenience Functions

    The simplest way to use canVODpy. Two function calls cover the entire
    pipeline from raw RINEX to vegetation optical depth.

    ## The Task

    Every notebook in this series performs the **same task**:

    1. Read RINEX data for **Rosalia**, DOY **2025001**
    2. Preprocess (augment with auxiliary data)
    3. Assign hemisphere grid cells
    4. Calculate VOD for a canopy/reference receiver pair

    ## API at a Glance

    ```python
    from canvodpy import process_date, calculate_vod

    data = process_date("Rosalia", "2025001")
    vod  = calculate_vod("Rosalia", "canopy_01", "reference_01", "2025001")
    ```

    | Aspect | Detail |
    |--------|--------|
    | Import | `from canvodpy import process_date, calculate_vod` |
    | Lines of code | 2 |
    | Configuration | None (uses site defaults) |
    | Best for | Quick exploration, scripts, one-off analysis |
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 1 — Process a Date
    """)
    return


@app.cell
def _():
    from canvodpy import process_date

    return (process_date,)


@app.cell
def _(mo, process_date):
    mo.md(f"""
    `process_date` reads all active receivers for a site and date,
    applies default preprocessing, and assigns grid cells.

    **Signature:**
    ```python
    {process_date.__doc__}
    ```
    """)
    return


@app.cell
def _(mo, process_date):
    try:
        datasets = process_date("Rosalia", "2025001")
        mo.md(
            f"""
            **Processed receivers:** {", ".join(datasets.keys())}
            """
        )
    except Exception as e:
        datasets = None
        mo.md(
            f"""
            Data not available on this machine (`{type(e).__name__}`).

            When data is present, the call returns a dict of xarray Datasets:
            ```python
            datasets = process_date("Rosalia", "2025001")
            # {{"canopy_01": <xr.Dataset>, "reference_01": <xr.Dataset>, ...}}
            ```
            """
        )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 2 — Calculate VOD
    """)
    return


@app.cell
def _():
    from canvodpy import calculate_vod

    return (calculate_vod,)


@app.cell
def _(calculate_vod, mo):
    try:
        vod = calculate_vod("Rosalia", "canopy_01", "reference_01", "2025001")
        mo.md(
            f"""
            **VOD computed** — shape: `{vod.dims}`
            """
        )
    except Exception as e:
        vod = None
        mo.md(
            f"""
            Data not available on this machine (`{type(e).__name__}`).

            When data is present:
            ```python
            vod = calculate_vod("Rosalia", "canopy_01", "reference_01", "2025001")
            # Returns xarray.Dataset with VOD per grid cell
            ```
            """
        )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Summary

    | Pro | Con |
    |-----|-----|
    | Fewest lines of code | No control over grid type, resolution, reader |
    | Zero configuration | Cannot inspect intermediate results |
    | Ideal for quick checks | Hard to customise for research |

    **Next:** Open `level2_fluent.py` for the chainable deferred-execution API.
    """)
    return


if __name__ == "__main__":
    app.run()
