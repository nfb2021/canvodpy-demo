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
    width="medium", app_title="Configuration & Utilities", css_file="canvod_nordic.css"
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Configuration and Utilities

    The **canvod-utils** package provides two core subsystems:

    1. **Configuration** — Pydantic models that define every tuneable
       parameter of the canvodpy pipeline, loaded from YAML files
    2. **Diagnostics** — decorators and context managers for timing,
       memory tracking, dataset inspection, and retry logic

    Together they ensure that the pipeline is both reproducible
    (every run is fully specified by its config) and observable
    (every step can be profiled without modifying scientific code).

    —

    """
    )

    return (mo,)


# ---------------------------------------------------------------------------
# Section: configuration loading
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Configuration system

    canvodpy uses a layered YAML configuration split across three files:

    | File | Contents |
    |------|----------|
    | `processing.yaml` | Pipeline parameters, storage paths, compression, logging |
    | `sites.yaml` | Research sites, receivers, VOD analysis definitions |
    | `sids.yaml` | Signal ID filtering (all, preset, or custom list) |

    The `load_config()` function reads all three and returns a single
    validated `CanvodConfig` object:

    ```python
    from canvod.utils.config import load_config

    config = load_config(config_dir=Path("config/"))
    ```

    If `config_dir` is omitted, the loader checks the
    `CANVOD_CONFIG_DIR` environment variable, then searches for a
    `config/` directory relative to the monorepo root.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: configuration models overview
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvod.utils.config.models import (
        AuxDataConfig,
        CanvodConfig,
        CompressionConfig,
        IcechunkConfig,
        LoggingConfig,
        MetadataConfig,
        PreprocessingConfig,
        ProcessingConfig,
        ProcessingParams,
        ReceiverConfig,
        SidsConfig,
        SiteConfig,
        SitesConfig,
        StorageConfig,
        VodAnalysisConfig,
    )

    _models = [
        ("CanvodConfig", "Top-level container (processing + sites + sids)"),
        ("ProcessingConfig", "Pipeline parameters, storage, compression, logging"),
        ("MetadataConfig", "Author ORCID, institution ROR, publisher"),
        ("AuxDataConfig", "Ephemeris agency and product type"),
        ("ProcessingParams", "Thread count, resource mode, ephemeris source"),
        ("CompressionConfig", "zlib level (0-9)"),
        ("IcechunkConfig", "Icechunk compression, chunking, manifest settings"),
        ("StorageConfig", "Store paths and write strategies"),
        ("LoggingConfig", "Log directory and file naming"),
        ("PreprocessingConfig", "Temporal aggregation + grid assignment"),
        ("SitesConfig", "All research sites"),
        ("SiteConfig", "One site: receivers, coordinates, VOD analyses"),
        ("ReceiverConfig", "One receiver: type, directory, naming"),
        ("VodAnalysisConfig", "One VOD pair: canopy + reference receiver"),
        ("SidsConfig", "Signal ID filter mode (all/preset/custom)"),
    ]

    _rows = "\n".join(f"| `{n}` | {d} |" for n, d in _models)

    mo.md(
        f"""
    ### Configuration model hierarchy

    The configuration is built from **15 nested Pydantic models**,
    each responsible for a well-defined concern:

    | Model | Purpose |
    |-------|---------|
    {_rows}

    Every field has a type annotation, a default value (where
    sensible), and validation logic.  Invalid YAML produces a clear
    Pydantic `ValidationError` with the exact field and constraint
    that failed.
    """
    )

    return (
        AuxDataConfig,
        CanvodConfig,
        CompressionConfig,
        IcechunkConfig,
        LoggingConfig,
        MetadataConfig,
        PreprocessingConfig,
        ProcessingConfig,
        ProcessingParams,
        ReceiverConfig,
        SidsConfig,
        SiteConfig,
        SitesConfig,
        StorageConfig,
        VodAnalysisConfig,
    )


# ---------------------------------------------------------------------------
# Section: building config programmatically
# ---------------------------------------------------------------------------


@app.cell
def _(
    AuxDataConfig,
    MetadataConfig,
    ProcessingParams,
    ReceiverConfig,
    SiteConfig,
    SitesConfig,
    StorageConfig,
    VodAnalysisConfig,
    mo,
):
    _site = SiteConfig(
        gnss_site_data_root="/data/gnss/my_site",
        description="Example GNSS-T station",
        country="AT",
        latitude=48.0,
        longitude=16.0,
        altitude_m=400.0,
        receivers={
            "canopy_01": ReceiverConfig(
                type="canopy",
                directory="02_canopy",
            ),
            "reference_01": ReceiverConfig(
                type="reference",
                directory="01_reference",
                scs_from="canopy_01",
            ),
        },
        vod_analyses={
            "main": VodAnalysisConfig(
                canopy_receiver="canopy_01",
                reference_receiver="reference_01",
                description="Primary canopy-reference pair",
            ),
        },
    )

    _n_receivers = len(_site.receivers)
    _canopy_names = _site.get_canopy_receiver_names()
    _pairs = _site.get_reference_canopy_pairs()

    mo.md(
        f"""
    ## Building configuration programmatically

    Configuration objects can be created in Python without YAML files
    — useful for notebooks and testing:

    ```python
    site = SiteConfig(
        gnss_site_data_root="/data/gnss/my_site",
        country="AT",
        latitude=48.0, longitude=16.0, altitude_m=400.0,
        receivers={{
            "canopy_01": ReceiverConfig(type="canopy", directory="02_canopy"),
            "reference_01": ReceiverConfig(
                type="reference", directory="01_reference",
                scs_from="canopy_01",
            ),
        }},
        vod_analyses={{
            "main": VodAnalysisConfig(
                canopy_receiver="canopy_01",
                reference_receiver="reference_01",
            ),
        }},
    )
    ```

    | Property | Value |
    |----------|-------|
    | **Receivers** | {_n_receivers} |
    | **Canopy receivers** | {_canopy_names} |
    | **Reference–canopy pairs** | {_pairs} |

    The `scs_from` field on the reference receiver specifies which
    canopy receiver(s) it provides sky-condition subtraction for.
    This is validated at construction time: the target must exist
    in the same site's receiver dictionary.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: auxiliary data config
# ---------------------------------------------------------------------------


@app.cell
def _(AuxDataConfig, mo):
    _agencies = [
        ("COD", "final", "CODE (Bern), ~2 cm, 12-18 days"),
        ("GFZ", "final", "GFZ Potsdam, ~2 cm, 12-18 days"),
        ("COD", "rapid", "CODE rapid, ~2-3 cm, 17-41 hours"),
        ("IGS", "final", "IGS combined, ~2 cm, 12-18 days"),
    ]

    _rows = "\n".join(f"| `{a}` | `{p}` | {d} |" for a, p, d in _agencies)

    _default = AuxDataConfig()

    mo.md(
        f"""
    ## Ephemeris source configuration

    The `AuxDataConfig` model controls which analysis centre and
    product type to use for satellite orbit data:

    ```python
    aux = AuxDataConfig(agency="COD", product_type="final")
    ```

    | Agency | Product | Description |
    |--------|---------|-------------|
    {_rows}

    **Default**: agency=`{_default.agency}`, product_type=`{_default.product_type}`

    For most GNSS-T applications at 2-degree grid resolution, the choice
    of ephemeris product has negligible impact on VOD results.  The angular
    difference between broadcast and final orbits is approximately 0.1°
    — 20 times smaller than the grid cell size.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: processing parameters
# ---------------------------------------------------------------------------


@app.cell
def _(ProcessingParams, mo):
    _default = ProcessingParams()

    _fields = [
        ("resource_mode", _default.resource_mode, "auto or manual worker allocation"),
        (
            "ephemeris_source",
            _default.ephemeris_source,
            "final (SP3/CLK) or broadcast (SBF)",
        ),
        ("batch_hours", _default.batch_hours, "Hours per processing batch"),
        (
            "aggregate_glonass_fdma",
            _default.aggregate_glonass_fdma,
            "Merge FDMA frequency channels",
        ),
        (
            "store_radial_distance",
            _default.store_radial_distance,
            "Include range (r) in store",
        ),
        ("file_pairing", _default.file_pairing, "complete or paired file discovery"),
    ]

    _rows = "\n".join(f"| `{f}` | `{v}` | {d} |" for f, v, d in _fields)

    mo.md(
        f"""
    ## Processing parameters

    `ProcessingParams` controls pipeline behaviour:

    | Parameter | Default | Description |
    |-----------|---------|-------------|
    {_rows}

    The `resource_mode` setting determines how Dask workers are
    allocated:

    - **`auto`**: the pipeline inspects available CPU cores and RAM,
      then chooses worker count and memory limits automatically
    - **`manual`**: the user specifies `n_max_threads`,
      `max_memory_gb`, and optionally `cpu_affinity`

    ```python
    params = ProcessingParams(
        resource_mode="manual",
        n_max_threads=4,
        max_memory_gb=16.0,
        ephemeris_source="broadcast",
    )
    ```
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: storage strategies
# ---------------------------------------------------------------------------


@app.cell
def _(StorageConfig, mo):
    mo.md(
        r"""
    ## Storage strategies

    The `StorageConfig` model defines how the pipeline handles
    pre-existing data in Icechunk stores:

    | Strategy | Behaviour |
    |----------|-----------|
    | `skip` | If the store already has data for this day, skip entirely |
    | `append` | Append new epochs; deduplication guards prevent duplicates |
    | `overwrite` | Delete existing data for the day, then write fresh |

    ```python
    storage = StorageConfig(
        stores_root_dir=Path("/data/stores"),
        rinex_store_strategy="append",
        vod_store_strategy="overwrite",
    )
    ```

    The **append** strategy is the recommended default for production:
    it is idempotent (re-running the same day is safe) and preserves
    previously ingested data.  The three-layer deduplication system
    in `canvod-store` ensures that no duplicate epochs enter the store.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: SID filtering
# ---------------------------------------------------------------------------


@app.cell
def _(SidsConfig, mo):
    _all = SidsConfig(mode="all")
    _preset = SidsConfig(mode="preset", preset="gps_galileo_l1")

    mo.md(
        """
    ## Signal ID filtering

    The `SidsConfig` model controls which satellite signals are
    processed.  Three modes are available:

    | Mode | Description |
    |------|-------------|
    | `all` | Process all SIDs present in the data |
    | `preset` | Use a named preset (e.g. `gps_galileo_l1`) |
    | `custom` | Provide an explicit list of SID strings |

    ```python
    # Process everything
    sids = SidsConfig(mode="all")
    effective = sids.get_sids()  # Returns None (= no filter)

    # Use a preset
    sids = SidsConfig(mode="preset", preset="gps_galileo_l1")
    effective = sids.get_sids()  # Returns ["G01|L1|C", "G02|L1|C", ...]

    # Custom list
    sids = SidsConfig(
        mode="custom",
        custom_sids=["G01|L1|C", "G02|L1|C", "E01|L1|C"],
    )
    ```

    Filtering by SID (rather than by constellation or PRN) gives
    fine-grained control: you can select specific frequencies and
    tracking codes while excluding others from the same satellite.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: date utilities
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    import datetime

    from canvod.utils.tools import YYYYDOY

    _d1 = YYYYDOY.from_str("2025001")
    _d2 = YYYYDOY.from_date(datetime.date(2025, 6, 15))

    mo.md(
        f"""
    ## Date utilities

    GNSS data is organised by **Day of Year (DOY)**.  The `YYYYDOY`
    dataclass converts between calendar dates, DOY strings, and GPS
    week numbers:

    ```python
    from canvod.utils.tools import YYYYDOY

    d = YYYYDOY.from_str("2025001")       # January 1, 2025
    d = YYYYDOY.from_date(date(2025, 6, 15))  # DOY 166
    d = YYYYDOY.from_yydoy_str("25001")   # Short format
    ```

    | Input | Year | DOY | Date | GPS week | GPS day |
    |-------|------|-----|------|----------|---------|
    | `"2025001"` | {_d1.year} | {_d1.doy} | {_d1.date} | {_d1.gps_week} | {_d1.gps_day_of_week} |
    | `2025-06-15` | {_d2.year} | {_d2.doy} | {_d2.date} | {_d2.gps_week} | {_d2.gps_day_of_week} |

    GPS week numbers are used extensively in ephemeris product file
    names (e.g. `COD0OPSFIN_20250010000_01D_05M_ORB.SP3` is also
    week 2347, day 3).
    """
    )

    return YYYYDOY, datetime


# ---------------------------------------------------------------------------
# Section: file hashing
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvod.utils.tools import file_hash

    mo.md(
        r"""
    ## File hashing

    The `file_hash()` function computes a truncated SHA-256 hash for
    deduplication in the store metadata ledger:

    ```python
    from canvod.utils.tools import file_hash

    h = file_hash(Path("observation.rnx"))
    # Returns: "a1b2c3d4e5f6g7h8" (16-character hex string)
    ```

    The 16-character truncation provides 64 bits of entropy —
    sufficient for deduplication within a single site (collision
    probability < $10^{-15}$ for 10,000 files).  The truncation
    keeps metadata compact in the Zarr store.
    """
    )

    return (file_hash,)


# ---------------------------------------------------------------------------
# Section: timing diagnostics
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    import time

    from canvod.utils.diagnostics import BatchTracker, track_time

    # Demonstrate track_time as context manager
    with track_time("demo.sleep") as _t:
        time.sleep(0.05)

    # Demonstrate BatchTracker
    _tracker = BatchTracker(name="demo_batch")
    for _i in range(5):
        with _tracker.step(f"step_{_i}"):
            time.sleep(0.01)

    _summary = _tracker.summary()

    mo.md(
        f"""
    ## Timing diagnostics

    `track_time` works as both a decorator and a context manager.
    It records elapsed time to a global in-memory store (and
    optionally to a SQLite database):

    ```python
    from canvod.utils.diagnostics import track_time

    # As decorator
    @track_time("rinex.read")
    def read_file(path): ...

    # As context manager
    with track_time("store.write") as t:
        ds.to_zarr(store)
    print(f"Elapsed: {{t.elapsed:.3f}} s")
    ```

    **Context manager result**: {_t.elapsed:.4f} s

    ### Batch tracking

    `BatchTracker` times multiple steps and produces a summary:

    ```python
    tracker = BatchTracker(name="daily_batch")
    for day in days:
        with tracker.step(f"day_{{day}}"):
            process(day)
    tracker.summary()  # Polars DataFrame
    ```

    **Batch summary** ({_tracker.total:.4f} s total, {_tracker.mean:.4f} s mean):

    {_summary.to_pandas().to_markdown(index=False)}
    """
    )

    return BatchTracker, time, track_time


# ---------------------------------------------------------------------------
# Section: memory tracking
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    import numpy as _np

    from canvod.utils.diagnostics import track_memory

    with track_memory("demo.allocate") as _m:
        _big = _np.zeros((1000, 1000))

    mo.md(
        f"""
    ## Memory diagnostics

    `track_memory` measures peak and current RSS memory usage:

    ```python
    from canvod.utils.diagnostics import track_memory

    with track_memory("vod.compute") as m:
        result = compute_vod(ds)
    print(f"Peak: {{m.peak_mb:.1f}} MB")
    ```

    | Metric | Value |
    |--------|-------|
    | **Peak RSS** | {_m.peak_mb:.1f} MB |
    | **Current RSS** | {_m.current_mb:.1f} MB |

    Memory tracking uses `resource.getrusage()` on Unix systems.
    It adds negligible overhead and is safe to leave enabled in
    production.
    """
    )

    return (track_memory,)


# ---------------------------------------------------------------------------
# Section: dataset diagnostics
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    import numpy as _np
    import xarray as _xr

    from canvod.utils.diagnostics import track_dataset

    # Create a small test dataset
    _ds = _xr.Dataset(
        {
            "SNR": (
                ["epoch", "sid"],
                _np.random.default_rng(42).normal(40, 5, (100, 20)),
            ),
        },
        coords={
            "epoch": _np.arange(100),
            "sid": [f"G{i:02d}|L1|C" for i in range(1, 21)],
        },
    )
    # Inject some NaNs
    _ds["SNR"].values[0:10, 0:5] = _np.nan

    _report = track_dataset("demo.inspect", _ds, log=False)

    mo.md(
        f"""
    ## Dataset diagnostics

    `track_dataset()` inspects an xarray Dataset and returns a
    `DatasetReport` with shape, NaN ratios, epoch gaps, and size:

    ```python
    from canvod.utils.diagnostics import track_dataset

    report = track_dataset("pipeline.step3", ds)
    ```

    | Property | Value |
    |----------|-------|
    | **Epochs** | {_report.n_epochs} |
    | **SIDs** | {_report.n_sids} |
    | **Variables** | {_report.variables} |
    | **NaN ratios** | {_report.nan_ratios} |
    | **Size** | {_report.size_mb:.3f} MB |

    The `warn_nan_threshold` parameter (default 0.5) triggers a
    warning when any variable exceeds that NaN fraction — useful
    for catching data quality issues early in the pipeline.
    """
    )

    return track_dataset, xr  # type: ignore[unresolved-reference]


# ---------------------------------------------------------------------------
# Section: retry decorator
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvod.utils.diagnostics import retry

    mo.md(
        r"""
    ## Retry decorator

    Network operations (FTP downloads of SP3/CLK files) can fail
    transiently.  The `retry` decorator adds exponential backoff:

    ```python
    from canvod.utils.diagnostics import retry

    @retry(attempts=3, delay=1.0, backoff=2.0, exceptions=(IOError,))
    def download_sp3(url):
        ...
    ```

    | Parameter | Default | Description |
    |-----------|---------|-------------|
    | `attempts` | 3 | Maximum number of tries |
    | `delay` | 1.0 s | Initial wait between retries |
    | `backoff` | 2.0 | Multiplier per retry (1 s → 2 s → 4 s) |
    | `exceptions` | `(Exception,)` | Exception types that trigger retry |

    Only the specified exception types trigger a retry; all others
    propagate immediately.
    """
    )

    return (retry,)


# ---------------------------------------------------------------------------
# Section: global metrics store
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvod.utils.diagnostics import bottlenecks, get_timings, reset_timings

    _df = get_timings()

    mo.md(
        f"""
    ## Global metrics store

    All timing and memory measurements are recorded in a global
    in-memory store.  For persistence across sessions, an optional
    SQLite database can be configured:

    ```python
    from canvod.utils.diagnostics import (
        configure_db,    # Set SQLite path (None = in-memory only)
        get_timings,     # Current session as Polars DataFrame
        bottlenecks,     # Top-N slowest operations
        reset_timings,   # Clear in-memory store
        query_db,        # Query persistent DB
    )

    configure_db("~/.canvod/metrics.db")

    # After a pipeline run:
    df = get_timings()
    slow = bottlenecks(top_n=5)
    ```

    **Current session** has {len(_df)} recorded metrics.

    The `bottlenecks()` function aggregates by operation name and
    returns total time, mean time, count, and percentage — making
    it straightforward to identify where the pipeline spends most of
    its time.
    """
    )

    return bottlenecks, get_timings, reset_timings


# ---------------------------------------------------------------------------
# Section: CLI
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Configuration CLI

    The `canvod-utils` package includes a Typer CLI for managing
    configuration files:

    ```bash
    # Initialise config directory with templates
    uv run canvod-config init --config-dir ./config/

    # Validate configuration
    uv run canvod-config validate

    # Show current configuration
    uv run canvod-config show
    uv run canvod-config show --section sites

    # Open in editor
    uv run canvod-config edit sites
    ```

    The `validate` command catches common errors (missing fields,
    invalid types, broken cross-references between receivers and
    VOD analyses) before running the pipeline.
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

    **Previous**: [10 — Visualization](./10_visualization.py)
    | **Next**: [12 — API Overview](./12_api_overview.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
