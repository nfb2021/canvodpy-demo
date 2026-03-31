import marimo

__generated_with = "0.12.0"
app = marimo.App(
    width="medium", app_title="L2 — Fluent Workflow", css_file="canvod_nordic.css"
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Level 2 — Fluent Workflow API

    The L2 fluent API provides a **chainable, deferred-execution**
    pipeline.  Steps are recorded as a plan and executed only when
    a terminal method (`.result()`, `.to_store()`, `.plot()`) is called.

    This design enables:

    - **Composability**: build pipelines by chaining `.read().augment().vod()`
    - **Introspection**: call `.explain()` to see the plan before executing
    - **Reusability**: store a partially-built workflow and complete it later

    ---

    """
    )

    return (mo,)


# ---------------------------------------------------------------------------
# Section: basic workflow
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Building a workflow

    ```python
    from canvodpy import workflow

    result = (workflow("my_site")
        .read("2025001")
        .augment(source="final", agency="COD")
        .grid("equal_area", angular_resolution=2.0)
        .vod("canopy_01", "reference_01")
        .result())
    ```

    Each step returns `self`, so calls chain naturally.  The
    `workflow()` factory function creates a `FluentWorkflow` instance
    bound to a site.

    ### Step reference

    | Step | Parameters | Description |
    |------|-----------|-------------|
    | `.read(date)` | `date`, `receivers` | Read RINEX/SBF files for a day |
    | `.preprocess(agency)` | `agency` | Download and cache ephemeris products |
    | `.augment(source, agency)` | `source`, `agency`, `date` | Add satellite geometry |
    | `.grid(kind)` | `kind`, `**params` | Create hemispheric grid |
    | `.vod(canopy, reference)` | `canopy`, `reference` | Compute VOD |
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: terminal methods
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Terminal methods

    Terminal methods trigger execution of the accumulated plan:

    | Method | Returns | Description |
    |--------|---------|-------------|
    | `.result()` | `xr.Dataset` or `dict` | Execute and return data |
    | `.to_store()` | `FluentWorkflow` | Execute and write to Icechunk |
    | `.plot()` | figure | Execute and visualize |

    ### Deferred execution example

    ```python
    # Build plan (no execution yet)
    wf = (workflow("my_site")
        .read("2025001")
        .augment(source="final", agency="COD")
        .vod("canopy_01", "reference_01"))

    # Inspect the plan
    plan = wf.explain()
    for step in plan:
        print(f"{step['name']}: {step}")

    # Now execute
    result = wf.result()
    ```

    The `.explain()` method returns a list of dictionaries describing
    each step, its parameters, and its expected inputs/outputs.  This
    is useful for debugging and documentation.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: Site and Pipeline
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Site and Pipeline objects

    For workflows that require a managed Dask client or multi-date
    processing, L2 also provides `Site` and `Pipeline`:

    ```python
    from canvodpy import Site

    site = Site("my_site")

    # Access site properties
    print(site.receivers)       # Dict of ReceiverConfig
    print(site.vod_analyses)    # Dict of VodAnalysisConfig
    print(site.rinex_store)     # MyIcechunkStore for observations
    print(site.vod_store)       # MyIcechunkStore for VOD products

    # Create a pipeline with resource management
    with site.pipeline(n_workers=4, batch_hours=24.0) as pipe:
        # Process single day
        data = pipe.process_date("2025001")

        # Process date range (generator for memory efficiency)
        for date, result in pipe.process_range("2025001", "2025031"):
            print(f"{date}: {list(result.keys())}")

        # Calculate VOD within the pipeline context
        vod = pipe.calculate_vod("canopy_01", "reference_01", "2025001")
    ```

    The `Pipeline` context manager:

    - Creates a Dask `LocalCluster` with the specified worker count
    - Manages the cluster lifecycle (shutdown on exit)
    - Provides `.preview()` for dry-run inspection
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: customization
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Customization options

    The `FluentWorkflow` constructor accepts component overrides:

    ```python
    from canvodpy import FluentWorkflow

    wf = FluentWorkflow(
        site="my_site",
        reader="rinex3",           # or "sbf"
        grid_type="equal_area",    # or "equal_angle", "fibonacci", ...
        vod_calculator="tau_omega",
        keep_vars=["SNR"],         # Only retain SNR
    )
    ```

    And `Pipeline` accepts resource parameters:

    ```python
    pipe = site.pipeline(
        aux_agency="GFZ",          # Use GFZ instead of CODE
        n_workers=8,
        batch_hours=6.0,           # Process in 6-hour batches
        max_memory_gb=32.0,
        cpu_affinity=[0, 1, 2, 3], # Pin to specific cores
        nice_priority=10,          # Lower scheduling priority
    )
    ```

    These overrides take precedence over `processing.yaml` defaults
    for the duration of the pipeline.
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

    **Previous**: [13 — L1 Convenience](./13_api_level1_convenience.py)
    | **Next**: [15 — L3 Site Pipeline](./15_api_level3_site_pipeline.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
