import marimo

__generated_with = "0.12.0"
app = marimo.App(width="medium", app_title="Batch Processing Workflows", css_file="canvod_nordic.css")


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Batch Processing Workflows

    This notebook demonstrates various batch processing patterns:

    - Processing **multiple days** for a single site
    - Using different **ephemeris agencies** (CODE, GFZ, IGS)
    - Configuring **temporal aggregation** and grid parameters
    - **Resource management** for long-running pipelines

    All examples use the L2 API (`Site`, `Pipeline`, `workflow`)
    which provides the right balance of control and convenience for
    batch operations.

    —

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

    The generator pattern means that only one day's data is in memory
    at a time.  After each iteration, the datasets are committed to
    the Icechunk store and released.
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
        # Set ephemeris_source in processing.yaml to "broadcast"
        data = pipe.process_date("2025001")
    ```

    For GNSS-T at 2-degree grid resolution, the choice of agency
    has **negligible impact** on VOD values.  The angular difference
    between agencies is approximately 0.001° — three orders of
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

    The preprocessing step can aggregate observations to a coarser
    time resolution before VOD computation:

    ```python
    # In processing.yaml:
    preprocessing:
      temporal_aggregation:
        enabled: true
        freq: "1min"      # Pandas offset alias
        method: "mean"    # or "median"
    ```

    | Frequency | Epochs per day | Use case |
    |-----------|---------------|----------|
    | `"5s"` | 17,280 | Full resolution (no aggregation) |
    | `"30s"` | 2,880 | Reduced noise, moderate resolution |
    | `"1min"` | 1,440 | Standard for daily VOD maps |
    | `"5min"` | 288 | Coarse monitoring |
    | `"15min"` | 96 | Matches file boundaries |

    Temporal aggregation reduces noise by averaging multiple
    observations within each time window.  The trade-off is loss
    of temporal resolution for rapid vegetation dynamics (e.g.
    rain interception, dew formation).

    The `method` parameter controls how observations within each
    window are combined:

    - **`mean`**: arithmetic mean (default, lower noise)
    - **`median`**: more robust to outliers (multipath spikes)
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

    Grid assignment can be configured globally or per-workflow:

    ```python
    # In processing.yaml:
    preprocessing:
      grid_assignment:
        enabled: true
        grid_type: "equal_area"
        angular_resolution: 2.0  # degrees

    # Or override in code:
    result = (workflow("my_site")
        .read("2025001")
        .augment()
        .grid("equal_area", angular_resolution=5.0)  # Override to 5°
        .vod("canopy_01", "reference_01")
        .result())
    ```

    | Resolution | Cells | Obs per cell (1 day) | Best for |
    |------------|-------|---------------------|----------|
    | 1° | ~10,300 | ~2 | Maximum spatial detail |
    | 2° | ~2,600 | ~7 | Standard analysis |
    | 5° | ~400 | ~45 | Robust averages |
    | 10° | ~100 | ~180 | Coarse monitoring |

    The observation count per cell assumes ~18,000 valid observations
    per day from ~100 visible satellites across GPS and Galileo.
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

    For long-running batch jobs, resource parameters prevent the
    pipeline from overwhelming the system:

    ```python
    with site.pipeline(
        n_workers=4,              # Dask workers
        batch_hours=6.0,          # Process in 6-hour batches
        max_memory_gb=16.0,       # Soft RAM limit per worker
        cpu_affinity=[0, 1, 2, 3],# Pin to specific cores
        nice_priority=10,         # Lower scheduling priority
        threads_per_worker=2,     # Threads per Dask worker
    ) as pipe:
        for date, data in pipe.process_range("2025001", "2025365"):
            pass
    ```

    | Parameter | Default | Description |
    |-----------|---------|-------------|
    | `n_workers` | auto | Number of Dask workers |
    | `batch_hours` | 24.0 | File grouping window |
    | `max_memory_gb` | auto | Soft RAM limit per worker |
    | `cpu_affinity` | None | Pin workers to CPU cores |
    | `nice_priority` | 0 | Unix nice value (0-19) |
    | `threads_per_worker` | auto | Threads within each worker |

    The `batch_hours` parameter controls how files are grouped for
    processing.  With `batch_hours=6.0`, a 24-hour day is processed
    in four batches of ~24 files each, reducing peak memory usage.
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

    Use the diagnostics system to track progress and identify
    bottlenecks:

    ```python
    from canvod.utils.diagnostics import (
        BatchTracker,
        track_time,
        bottlenecks,
        configure_db,
    )

    # Persist metrics across sessions
    configure_db("~/.canvod/metrics.db")

    tracker = BatchTracker(name="january_2025")

    with site.pipeline(n_workers=4) as pipe:
        for date, data in pipe.process_range("2025001", "2025031"):
            with tracker.step(date):
                pass  # Pipeline already ran

    # After completion
    print(tracker.summary())  # Polars DataFrame with per-day timings
    print(bottlenecks(top_n=5))  # Slowest operations
    ```

    The SQLite database allows comparing performance across runs —
    useful for detecting regressions after code changes.
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
    —

    **Previous**: [17 — Single-Day Workflow](./17_workflow_single_day.py)
    | **Next**: [19 — Store Operations](./19_workflow_store_operations.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
