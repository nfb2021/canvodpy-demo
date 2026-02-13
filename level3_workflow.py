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
        # canVODpy API — Level 3: VODWorkflow

        A **stateful orchestrator** that owns a site configuration, a
        pre-built hemisphere grid, and a structured logger. Methods execute
        eagerly and return data immediately.

        ## The Task

        Same as every notebook in this series:

        1. Read RINEX data for **Rosalia**, DOY **2025001**
        2. Preprocess (augment with auxiliary data)
        3. Assign hemisphere grid cells
        4. Calculate VOD for canopy_01 / reference_01

        ## API at a Glance

        ```python
        from canvodpy import VODWorkflow

        wf = VODWorkflow(
            site="Rosalia",
            grid="equal_area",
            grid_params={"angular_resolution": 5.0},
        )
        datasets = wf.process_date("2025001")
        vod      = wf.calculate_vod("canopy_01", "reference_01", "2025001")
        ```

        | Aspect | Detail |
        |--------|--------|
        | Import | `from canvodpy import VODWorkflow` |
        | Pattern | Stateful class with eager execution |
        | Configuration | Constructor parameters + factory system |
        | Best for | Multi-date processing, structured logging, research pipelines |
        """
    )
    return


@app.cell
def _(mo):
    mo.md("## Step 1 — Initialise the workflow")
    return


@app.cell
def _():
    from canvodpy import VODWorkflow

    return (VODWorkflow,)


@app.cell
def _(VODWorkflow, mo):
    try:
        wf = VODWorkflow(
            site="Rosalia",
            grid="equal_area",
            grid_params={"angular_resolution": 5.0},
        )
        wf_ok = True
        mo.md(
            f"""
            **Workflow ready**

            - Site: `{wf.site.name}`
            - Grid: `{wf.grid_name}` ({wf.grid.ncells} cells)
            - Reader: `{wf.reader_name}`
            - Calculator: `{wf.vod_calculator_name}`

            ```
            {wf!r}
            ```
            """
        )
    except Exception as e:
        wf = None
        wf_ok = False
        mo.md(
            f"""
            Site not available (`{type(e).__name__}`).

            ```python
            wf = VODWorkflow(
                site="Rosalia",
                grid="equal_area",
                grid_params={{"angular_resolution": 5.0}},
            )
            # VODWorkflow(site='Rosalia', grid='equal_area', reader='rinex3')
            ```
            """
        )
    return wf, wf_ok


@app.cell
def _(mo):
    mo.md(
        """
        ## Step 2 — Inspect the grid

        The grid is built eagerly at init time via `GridFactory`.
        """
    )
    return


@app.cell
def _(mo, wf, wf_ok):
    if wf_ok:
        mo.md(
            f"""
            | Property | Value |
            |----------|-------|
            | Type | `{wf.grid.definition}` |
            | Cells | {wf.grid.ncells} |
            | Bands | {wf.grid.nbands} |
            """
        )
    else:
        mo.md("_(grid inspection requires site configuration)_")
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## Step 3 — Process a date

        `process_date()` reads RINEX files, augments with auxiliary data,
        and assigns grid cells — all in one call.
        """
    )
    return


@app.cell
def _(mo, wf, wf_ok):
    if wf_ok:
        try:
            datasets = wf.process_date("2025001")
            mo.md(
                f"""
                **Receivers processed:** {", ".join(datasets.keys())}
                """
            )
        except Exception as e:
            datasets = None
            mo.md(
                f"Processing failed (`{type(e).__name__}: {e}`). Data may not be on disk."
            )
    else:
        datasets = None
        mo.md(
            """
            ```python
            datasets = wf.process_date("2025001")
            # {"canopy_01": <xr.Dataset>, "reference_01": <xr.Dataset>}
            ```
            """
        )
    return (datasets,)


@app.cell
def _(mo):
    mo.md(
        """
        ## Step 4 — Calculate VOD

        Uses `VODFactory` internally to create the calculator from the
        canopy and reference datasets.
        """
    )
    return


@app.cell
def _(mo, wf, wf_ok):
    if wf_ok:
        try:
            vod = wf.calculate_vod("canopy_01", "reference_01", "2025001")
            mo.md(f"**VOD computed** — shape: `{vod.dims}`")
        except Exception as e:
            vod = None
            mo.md(f"VOD calculation failed (`{type(e).__name__}: {e}`).")
    else:
        vod = None
        mo.md(
            """
            ```python
            vod = wf.calculate_vod("canopy_01", "reference_01", "2025001")
            # Returns xr.Dataset with VOD values per grid cell
            ```
            """
        )
    return (vod,)


@app.cell
def _(mo):
    mo.md(
        """
        ## Structured logging

        Every method call emits structured JSON logs with the site context
        bound at init time.  This makes log aggregation and LLM-assisted
        debugging straightforward.

        ```python
        wf.log.info("processing_started", date="2025001")
        # {"event": "processing_started", "date": "2025001",
        #  "site": "Rosalia", "timestamp": "..."}
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
        | Structured logging with site context | Eager execution (no plan preview) |
        | Grid built once, reused across dates | More verbose than fluent API |
        | Factory system for swappable components | Stateful — order matters |
        | `repr` shows full configuration | |

        **Next:** Open `level4_functional.py` for the stateless pure-function API.
        """
    )
    return


if __name__ == "__main__":
    app.run()
