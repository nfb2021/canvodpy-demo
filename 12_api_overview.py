# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvod-auxiliary",
#   "canvod-config",
#   "canvod-grids",
#   "canvod-ops",
#   "canvod-preflight",
#   "canvod-readers",
#   "canvod-store",
#   "canvod-store-metadata",
#   "canvod-utils",
#   "canvod-viz",
#   "canvod-vod",
#   "canvodpy",
#   "marimo>=0.21.1",
# ]
#
# [tool.uv.sources]
# canvod-auxiliary = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-auxiliary", rev = "fc3b2fe8fac9c36fa1997ad6e2d898663e0a2384" }
# canvod-config = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-config", rev = "fc3b2fe8fac9c36fa1997ad6e2d898663e0a2384" }
# canvod-grids = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-grids", rev = "fc3b2fe8fac9c36fa1997ad6e2d898663e0a2384" }
# canvod-ops = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-ops", rev = "fc3b2fe8fac9c36fa1997ad6e2d898663e0a2384" }
# canvod-preflight = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-preflight", rev = "fc3b2fe8fac9c36fa1997ad6e2d898663e0a2384" }
# canvod-readers = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-readers", rev = "fc3b2fe8fac9c36fa1997ad6e2d898663e0a2384" }
# canvod-store = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-store", rev = "fc3b2fe8fac9c36fa1997ad6e2d898663e0a2384" }
# canvod-store-metadata = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-store-metadata", rev = "fc3b2fe8fac9c36fa1997ad6e2d898663e0a2384" }
# canvod-utils = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-utils", rev = "fc3b2fe8fac9c36fa1997ad6e2d898663e0a2384" }
# canvod-viz = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-viz", rev = "fc3b2fe8fac9c36fa1997ad6e2d898663e0a2384" }
# canvod-vod = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-vod", rev = "fc3b2fe8fac9c36fa1997ad6e2d898663e0a2384" }
# canvodpy = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "canvodpy", rev = "fc3b2fe8fac9c36fa1997ad6e2d898663e0a2384" }
#
# [tool.marimo.opengraph]
# title = "12 · API Overview"
# description = "Survey canVODpy's supported surfaces: the canvodpy run CLI for production use and Site.pipeline(), the Python entry point it wraps."
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium", app_title="API Overview", css_file="canvod_nordic.css"
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # canvodpy API Overview

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/12_api_overview.py)

    canvodpy has **two supported ways to run or script the pipeline**.
    Both produce the same scientific results — the same VOD values from
    the same input data — but differ in where you invoke them from.

    | Surface | Style | Entry point | Use case |
    |---------|-------|-------------|----------|
    | **CLI** | Command-line | `canvodpy run --site ...` | Running production ingestion — recommended |
    | **Site pipeline** | Python, object-oriented | `Site(...).pipeline()` | Python-native scripting; what the CLI wraps internally |

    Earlier versions of canvodpy exposed four numbered "API levels"
    (L1 convenience one-liners, L2 fluent method chaining, L3 site
    pipelines, L4 functional). L1 and L2 are now deprecated — L1 was a
    thin wrapper around exactly what `Site.pipeline()` already does, and
    L2's fluent chain was superfluous alongside it. L4,
    `canvodpy.functional`, is no longer maintained and gives different
    results than `canvodpy run`. All three are deprecated: they still work
    (with a `FutureWarning`) until the next major version, but are no
    longer documented or taught. This notebook covers what replaced them.

    ---

    """
    )

    return (mo,)


# ---------------------------------------------------------------------------
# Section: CLI
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## CLI — running the pipeline

    The recommended way to run canvodpy in production: a single command,
    resumable, no Python required.

    ```bash
    # Process a range
    uv run canvodpy run --site Rosalia --start 2025001 --end 2025007

    # Resume automatically from the last processed date
    uv run canvodpy run --site Rosalia

    # Multiple sites in one invocation (processed sequentially)
    uv run canvodpy run --site Rosalia OtherSite

    # Preview without executing
    uv run canvodpy run --site Rosalia --dry-run
    ```

    The CLI is a thin wrapper around `Site(...).pipeline().process_range()`
    — same code path, same guarantees. It adds resumability (auto-detects
    the last committed date in the store), a live progress display, and a
    few production-oriented flags (`--ephemeris-source`, `--vod-calculator`,
    `--workers`, `--days-per-batch`).

    See [13 — Running the Pipeline (CLI)](./13_cli_pipeline.py) for a full
    walkthrough of the flags.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: Site pipeline
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Site pipeline — Python-native scripting

    `Site(...).pipeline()` is what the CLI calls internally. Use it
    directly when you need scripted control from Python: looping over
    sites, embedding a run inside a notebook, or customising resources
    per invocation.

    ```python
    from canvodpy import Site

    site = Site("my_site")

    with site.pipeline(n_workers=4) as pipe:
        for date_key, datasets in pipe.process_range("2025001", "2025010"):
            print(f"{date_key}: {list(datasets)}")
    ```

    Once data is ingested, `site.vod` (a `VodComputer`) gives finer control
    over VOD computation as a separate stage — useful for production
    deployments that ingest nightly and recompute VOD on a different
    schedule.

    See [14 — Site Pipeline](./14_site_pipeline.py) for the full walkthrough.
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
    class (`GNSSDataReader`, `GridBuilder`, or `VODCalculator`). The
    `canvodpy run --vod-calculator` CLI flag reads its choices directly
    from `VODFactory.list_available()`.
    """
    )

    return GridFactory, ReaderFactory, VODFactory


# ---------------------------------------------------------------------------
# Section: choosing a surface
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Choosing a surface

    | If you want to... | Use |
    |-------------------|-----|
    | Run production ingestion, resumable, from a shell/cron | CLI: `canvodpy run` |
    | Script a run in Python — loop over sites, embed in a notebook | `Site(...).pipeline()` |
    | Recompute VOD separately from ingestion | `Site(...).vod` (`VodComputer`) |
    | Orchestrate with Airflow | The optional `canvod-airflow` extension (`canvodpy.workflows.tasks`) |
    | Inspect or modify an intermediate step for research | The `canvod-*` packages directly, see [16 — Single-Day Workflow](./16_workflow_single_day.py) |
    | Extend with a custom reader/grid/calculator | Factories: `VODFactory.register()` |

    The CLI and `Site(...).pipeline()` share the same implementation — you
    can mix them freely. A common pattern: use the CLI for scheduled
    production runs, and `Site(...)` in an analysis notebook to open the
    stores the CLI wrote.

    ---

    The following notebooks demonstrate each surface in detail:

    - [13 — Running the Pipeline (CLI)](./13_cli_pipeline.py)
    - [14 — Site Pipeline](./14_site_pipeline.py)
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
    | **Next**: [13 — Running the Pipeline (CLI)](./13_cli_pipeline.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
