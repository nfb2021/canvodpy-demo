# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "marimo>=0.21.1",
# ]
#
# [tool.marimo.opengraph]
# title = "20 · Batch Processing Workflows"
# description = "Process multiple days of GNSS-T data in parallel worker processes. Covers date-range iteration, store appends, and strategies for large-scale canopy monitoring."
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium", app_title="Batch Processing Workflows", css_file="canvod_nordic.css",
    html_head_file="canvod_head.html"
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    <p align="center" class="canvod-logo">
      <img class="canvod-logo-light" src="https://raw.githubusercontent.com/nfb2021/canvodpy/main/docs/assets/logo/canvodpy_logo_bright_mode.svg" alt="canVODpy logo" width="280">
      <img class="canvod-logo-dark" src="https://raw.githubusercontent.com/nfb2021/canvodpy/main/docs/assets/logo/canvodpy_logo_dark_mode.svg" alt="canVODpy logo" width="280">
    </p>

    # Batch Processing Workflows

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/20_workflow_batch_processing.py?mode=edit)

    This notebook demonstrates various batch processing patterns:

    - Processing **multiple days** for a single site
    - Using different **ephemeris agencies** (CODE, GFZ, IGS)
    - Configuring **temporal aggregation** and grid parameters
    - **Resource management** for long-running pipelines

    All examples use `Site` and `Pipeline`, the Python counterpart of
    `canvodpy run`.

    ---

    """
    )

    return (mo,)


# ---------------------------------------------------------------------------
# Section: multi-day processing
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Multi-day processing

    The `Pipeline.process_range()` method iterates over a date range
    and yields results as a generator, keeping memory usage constant:

    ```python
    from canvodpy import Site

    site = Site("my_site")

    with site.pipeline(n_workers=4) as pipe:
        for date, data in pipe.process_range("2025001", "2025031"):
            # data: dict[str, xr.Dataset] (one per receiver)
            print(f"{date}: {list(data.keys())}")
            # Data is written to the Icechunk store automatically
    ```

    | Parameter | Description |
    |-----------|-------------|
    | `start` | First date (YYYYDOY format) |
    | `end` | Last date (YYYYDOY format, inclusive) |

    The pipeline writes each day to the Icechunk store itself and
    yields the days of a batch once the whole batch is written.  While
    your loop works on a batch, it reads the next one, so it holds the
    days of two batches in memory at a time; `days_per_batch` sets
    their number (default 1).
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: ephemeris agencies
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Choosing ephemeris agencies

    Different analysis centres produce orbit products with varying
    latency and accuracy:

    | Agency | Code | Latency | Orbit accuracy |
    |--------|------|---------|----------------|
    | **CODE** (Bern) | `COD` | 12-18 days | ~2 cm |
    | **GFZ** (Potsdam) | `GFZ` | 12-18 days | ~2 cm |
    | **IGS** (combined) | `IGS` | 12-18 days | ~2 cm |
    | **ESA** | `ESA` | 12-18 days | ~2 cm |
    | **JPL** | `JPL` | 12-18 days | ~2 cm |

    ```python
    # Use CODE final products (default)
    with site.pipeline(aux_agency="COD") as pipe:
        data = pipe.process_date("2025001")

    # Use GFZ final products
    with site.pipeline(aux_agency="GFZ") as pipe:
        data = pipe.process_date("2025001")

    # Use broadcast ephemeris (from SBF SatVisibility block)
    # Only available when source format is SBF
    with site.pipeline() as pipe:
        # Set processing.params.ephemeris_source to "broadcast"
        # in config/canvod-settings.yaml
        data = pipe.process_date("2025001")
    ```

    For GNSS-T at 2-degree grid resolution, the choice of agency
    has **negligible impact** on VOD values.  The angular difference
    between agencies is approximately 0.001°, three orders of
    magnitude smaller than the grid cell size.

    The practical difference is **availability**: if one agency's FTP
    server is down, switch to another.  All final products use the
    same satellite laser ranging and VLBI calibration data.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: temporal aggregation
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Temporal aggregation

    `canvodpy run`, `Site(...).pipeline()` and Airflow store observations
    at the receiver's sampling interval, unless the optional
    `processing.preprocessing` section of `canvod-settings.yaml` sets a
    temporal aggregation. Then each receiver's observations of a day are
    aggregated into time bins before they are written to the GNSS store.
    Nothing is aggregated unless it is set:

    ```yaml
    processing:
      preprocessing:
        temporal_aggregation:
          freq: "1min"             # whole number + "s", "min" or "h"; divides one day
          method: "mean"           # "mean" or "median" (floating-point variables)
          integer_method: "first"  # "first", "last" or "middle" (integer flags)
    ```

    All three settings are required. Bins start at 00:00 and are labeled
    with their start; a bin that spans two files is aggregated from both.
    Keep the setting for the life of a store: writing differently
    aggregated data into an existing store stops with an error.

    To aggregate a dataset yourself, apply a `canvod-ops` pipeline to it:

    ```python
    from canvod.ops import Pipeline, TemporalAggregate

    ops = Pipeline(
        [TemporalAggregate(freq="1min", method="mean", integer_method="first")]
    )
    ds_aggregated, result = ops(ds)
    ```

    | Frequency | Epochs per day | Use case |
    |-----------|---------------|----------|
    | `"5s"` | 17,280 | Full resolution of the test data (no aggregation) |
    | `"30s"` | 2,880 | Reduced noise, moderate resolution |
    | `"1min"` | 1,440 | Daily VOD maps |
    | `"5min"` | 288 | Coarse monitoring |
    | `"15min"` | 96 | Matches file boundaries |

    Temporal aggregation reduces noise by combining the observations
    within each bin.  The trade-off is loss of temporal resolution for
    rapid vegetation dynamics (e.g. rain interception, dew formation).

    `method` sets how the floating-point variables of a bin are combined:

    - **`mean`**: arithmetic mean (lower noise)
    - **`median`**: more robust to outliers (multipath spikes)

    Integer variables such as LLI and SSI are flags and codes, which
    cannot be averaged: each bin takes their `first`, `last` or `middle`
    value in time order, as `integer_method` sets.

    The settings are recorded in the log book of the GNSS store. A store
    group never mixes data preprocessed with different settings: `canvodpy
    run` compares the settings with the stores before it processes any
    data and stops on a mismatch. Keep the setting for the life of a store,
    or write to a new store.

    To aggregate a dataset yourself in Python:

    ```python
    from canvod.ops import TemporalAggregate

    op = TemporalAggregate(freq="1min", method="mean", integer_method="first")
    ds_aggregated, result = op(ds)
    ```
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: grid configuration
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Grid configuration

    `canvodpy run` assigns grid cells only if `processing.preprocessing`
    sets a grid. The cells are then added to the observations, after the
    temporal aggregation, before they are written to the GNSS store:

    ```yaml
    processing:
      preprocessing:
        grid_assignment:
          grid_type: "equal_area"
          angular_resolution: 5.0  # degrees (0 < value <= 90)
    ```

    Alternatively, assign cells to a dataset yourself, at the resolution
    you choose (see [19 · Single-Day Workflow](./19_workflow_single_day.py)):

    ```python
    from canvod.grids import add_cell_ids_to_ds_fast, create_hemigrid

    grid = create_hemigrid("equal_area", angular_resolution=5.0)
    ds = add_cell_ids_to_ds_fast(ds_vod, grid, grid_name="equal_area_5deg")
    ```

    Each observation goes to the cell that contains it.

    | Resolution | Cells (`equal_area`) | Best for |
    |------------|-------|----------|
    | 1° | 26,263 | Maximum spatial detail |
    | 2° | 6,563 | Standard analysis |
    | 5° | 1,051 | Robust averages |
    | 10° | 263 | Coarse monitoring |
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: resource management
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Resource management

    For long-running batch jobs, these arguments limit how much of
    the machine the pipeline uses:

    ```python
    with site.pipeline(
        n_workers=4,           # worker processes
        days_per_batch=2,      # days the workers process together
        max_memory_gb=8,       # memory budget of the run
        threads_per_worker=1,  # threads of numerical libraries per worker
    ) as pipe:
        for date, data in pipe.process_range("2025001", "2025365"):
            pass
    ```

    | Argument | Default | Description |
    |----------|---------|-------------|
    | `n_workers` | from the settings | Most worker processes |
    | `days_per_batch` | from the settings (1) | Days the workers process together |
    | `max_memory_gb` | from the settings (the available memory) | Memory budget: fewer workers or days per batch if they do not fit |
    | `threads_per_worker` | from the settings (1) | Threads that numerical libraries use in each worker |

    The CPU cores and the priority of the workers come from
    `cpu_affinity` and `nice_priority` under `processing.params` in
    `canvod-settings.yaml`.  `n_workers` is the most workers; the run
    starts fewer, or lowers `days_per_batch`, if they do not fit in
    `max_memory_gb`, and stops before reading a file, saying how much
    memory it needs, if not even one worker fits.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: monitoring
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Monitoring long-running batches

    Every pipeline stage writes a timing event to the run's
    performance log (`machine/performance*.json` in the log directory),
    with the stage name, its duration and its status.  The dashboard
    reads these logs, also while a run is still in progress, so you can
    follow a multi-day batch and find its slowest stages:

    ```bash
    canvodpy dashboard                      # log directory from canvod-settings.yaml
    canvodpy dashboard --logs-dir /path/to/logs   # or an explicit one
    ```
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

    **Previous**: [19 · Single-Day Workflow](./19_workflow_single_day.py)
    | **Next**: [21 · Your Own VOD Calculator](./21_plugins.py)

    *canVODpy · Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
