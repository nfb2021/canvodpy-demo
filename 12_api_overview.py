import marimo

__generated_with = "0.12.0"
app = marimo.App(
    width="medium", app_title="API Levels Overview", css_file="canvod_nordic.css"
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # canvodpy API Levels

    canvodpy exposes **four API levels**, each designed for a different
    use case and user profile.  All levels produce the same scientific
    results — the same VOD values from the same input data — but
    differ in verbosity, control, and composability.

    | Level | Style | Entry point | Use case |
    |-------|-------|-------------|----------|
    | **L1** | Convenience | `process_date()`, `calculate_vod()` | Quick exploration, notebooks |
    | **L2** | Object-oriented / fluent | `Site()`, `Pipeline()`, `workflow()` | Interactive workflows |
    | **L3** | Site pipeline | `site.vod.compute_day()` | Full site processing with config |
    | **L4** | Functional | `read_rinex()`, `calculate_vod()` | Airflow DAGs, custom pipelines |

    The levels form a **progressive disclosure** hierarchy: L1 hides
    all complexity behind single function calls; L4 exposes every
    component as a standalone function suitable for workflow orchestrators.

    ---

    """
    )

    return (mo,)


# ---------------------------------------------------------------------------
# Section: L1 convenience
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Level 1 — Convenience functions

    L1 provides the simplest possible interface: one function call per
    task.  Configuration is loaded automatically from the monorepo's
    `config/` directory.

    ```python
    import canvodpy

    # Process a single day for all receivers at a site
    data = canvodpy.process_date("my_site", "2025001")

    # Calculate VOD for a specific receiver pair
    vod = canvodpy.calculate_vod(
        "my_site", "canopy_01", "reference_01", "2025001",
    )

    # Preview what would happen without running
    plan = canvodpy.preview_processing("my_site")
    ```

    L1 is ideal for **notebooks and quick exploration**: no imports
    beyond `canvodpy`, no configuration objects, no state management.
    The trade-off is limited control — you cannot change compression
    settings, grid parameters, or worker allocation without editing
    the YAML config files.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: L2 object-oriented
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Level 2 — Object-oriented API

    L2 introduces stateful objects that provide more control while
    remaining concise.

    ### Site and Pipeline

    ```python
    from canvodpy import Site, Pipeline

    # Inspect a site
    site = Site("my_site")
    print(site.receivers)       # All configured receivers
    print(site.vod_analyses)    # All VOD pair definitions

    # Create a pipeline with custom settings
    with site.pipeline(
        aux_agency="COD",
        n_workers=4,
        batch_hours=24.0,
    ) as pipe:
        data = pipe.process_date("2025001")
        vod = pipe.calculate_vod("canopy_01", "reference_01", "2025001")

        # Process a date range (yields results as generator)
        for date, result in pipe.process_range("2025001", "2025010"):
            print(f"{date}: {len(result)} receivers")
    ```

    The `Pipeline` context manager manages Dask client lifecycle
    and cleans up resources on exit.

    ### Fluent workflow

    ```python
    from canvodpy import workflow

    result = (workflow("my_site")
        .read("2025001")
        .augment(source="final", agency="COD")
        .grid("equal_area", angular_resolution=2.0)
        .vod("canopy_01", "reference_01")
        .result())
    ```

    The fluent API uses **deferred execution**: steps are recorded but
    not executed until `.result()` is called.  The `.explain()` method
    returns the execution plan without running it.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: L3 site pipeline
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Level 3 — Site pipeline

    L3 provides direct access to the `VodComputer`, which implements
    two computation strategies:

    - **`compute_day()`**: takes pre-loaded datasets (already in memory),
      computes VOD inline
    - **`compute_bulk()`**: loads data from the Icechunk store, computes
      VOD for a date range, optionally writes results back

    ```python
    from canvodpy import Site

    site = Site("my_site")
    vod = site.vod  # VodComputer instance

    # Strategy 1: inline computation from loaded data
    datasets = pipe.process_date("2025001")
    result = vod.compute_day(datasets, "main")

    # Strategy 2: bulk computation from store
    result = vod.compute_bulk(
        "main",
        start=datetime(2025, 1, 1),
        end=datetime(2025, 1, 31),
        write=True,
    )
    ```

    L3 is designed for **production workflows** where the processing
    pipeline and VOD computation run as separate stages — for
    example, when RINEX data is ingested nightly and VOD is computed
    weekly from the store.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: L4 functional
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Level 4 — Functional API

    L4 exposes every pipeline step as a standalone pure function.
    Each function has two variants:

    - **In-memory**: takes and returns `xr.Dataset`
    - **File-based**: takes and returns file paths (for Airflow XCom)

    ```python
    from canvodpy.functional import (
        read_rinex,           # → xr.Dataset
        read_rinex_to_file,   # → str (path)
        augment_with_ephemeris,
        create_grid,
        assign_grid_cells,
        calculate_vod,
        calculate_vod_to_file,
    )

    # In-memory pipeline
    ds = read_rinex("observation.rnx")
    ds = augment_with_ephemeris(ds, rx_pos, source="final", agency="COD")
    grid = create_grid("equal_area", angular_resolution=2.0)
    ds = assign_grid_cells(ds, grid)
    vod = calculate_vod(canopy_ds, sky_ds)

    # File-based pipeline (for Airflow)
    c = read_rinex_to_file("c.rnx", "/tmp/c.nc")
    s = read_rinex_to_file("s.rnx", "/tmp/s.nc")
    v = calculate_vod_to_file(c, s, "/tmp/vod.nc")
    ```

    L4 is designed for **workflow orchestrators** (Airflow, Prefect,
    Dagster) where each step runs in a separate process or container.
    The file-based variants serialise intermediate results to NetCDF,
    allowing steps to run on different machines.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: factory system
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvodpy.factories import GridFactory, ReaderFactory, VODFactory

    _readers = ReaderFactory.list_available()
    _grids = GridFactory.list_available()
    _vods = VODFactory.list_available()

    mo.md(
        f"""
    ## Factory system

    All pipeline components are registered in factory classes, enabling
    extensibility without modifying core code:

    ```python
    from canvodpy.factories import ReaderFactory, GridFactory, VODFactory

    # List available components
    ReaderFactory.list_available()   # {_readers}
    GridFactory.list_available()     # {_grids}
    VODFactory.list_available()      # {_vods}

    # Register a custom component
    from my_package import MyCustomCalculator
    VODFactory.register("my_calculator", MyCustomCalculator)
    ```

    | Factory | Registered components |
    |---------|-----------------------|
    | `ReaderFactory` | {", ".join(f"`{r}`" for r in _readers)} |
    | `GridFactory` | {", ".join(f"`{g}`" for g in _grids)} |
    | `VODFactory` | {", ".join(f"`{v}`" for v in _vods)} |

    Custom components must implement the corresponding abstract base
    class (`GNSSDataReader`, `GridBuilder`, or `VODCalculator`).
    """
    )

    return GridFactory, ReaderFactory, VODFactory


# ---------------------------------------------------------------------------
# Section: choosing an API level
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Choosing an API level

    | If you want to... | Use |
    |-------------------|-----|
    | Quickly inspect data in a notebook | L1: `process_date()` |
    | Run an interactive analysis session | L2: `Site()` + `Pipeline()` |
    | Build a composable, testable pipeline | L2: `workflow()` (fluent) |
    | Run nightly production ingestion | L3: `site.vod.compute_bulk()` |
    | Orchestrate with Airflow/Prefect | L4: `*_to_file()` functions |
    | Extend with custom algorithms | Factories: `VODFactory.register()` |

    All levels share the same underlying implementations.  You can mix
    levels freely — for example, use L1 to explore data in a notebook,
    then switch to L2 for a scripted workflow, then deploy the same
    logic via L4 in Airflow.

    ---

    The following notebooks demonstrate each level in detail:

    - [13 — L1 Convenience](./13_api_level1_convenience.py)
    - [14 — L2 Fluent Workflow](./14_api_level2_fluent.py)
    - [15 — L3 Site Pipeline](./15_api_level3_site_pipeline.py)
    - [16 — L4 Functional](./16_api_level4_functional.py)
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

    **Previous**: [11 — Configuration](./11_configuration.py)
    | **Next**: [13 — L1 Convenience](./13_api_level1_convenience.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
