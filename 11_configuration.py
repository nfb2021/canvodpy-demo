# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvod-config",
#   "canvod-utils",
#   "numpy>=1.24.0",
#   "xarray>=2024.1.0",
#   "zarr>=3.1.2",
#   "marimo>=0.21.1",
# ]
#
# [tool.uv.sources]
# canvod-config = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-config", rev = "fc3b2fe8fac9c36fa1997ad6e2d898663e0a2384" }
# canvod-utils = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-utils", rev = "fc3b2fe8fac9c36fa1997ad6e2d898663e0a2384" }
#
# [tool.marimo.opengraph]
# title = "11 · Configuration & Utilities"
# description = "Configure canVODpy processing parameters using Pydantic models. Explore site definitions, VOD analysis configs, and the shared utilities layer."
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

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/11_configuration.py)

    Two layers make every run specified and observable:

    1. **Configuration** (`canvod-config`) — Pydantic models that define
       every tuneable parameter of the canvodpy pipeline, loaded from YAML
    2. **Utilities and stage timing** (`canvod-utils`, `canvodpy.logging`)
       — date and hashing helpers, and timed pipeline stages

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

    canvodpy is configured through a single YAML file,
    `config/canvod-settings.yaml`, with three sections:

    | Section | Contents |
    |---------|----------|
    | `processing:` | Pipeline parameters, storage paths, compression, logging |
    | `sites:` | Research sites, receivers, VOD analysis definitions |
    | `sids:` | Signal ID filtering (all, preset, or custom list) |

    The `load_config()` function reads it and returns a single validated
    `CanvodConfig` object:

    ```python
    from canvod.config import load_config

    config = load_config(config_dir=Path("config/"))
    ```

    If `config_dir` is omitted, the loader checks the `CANVOD_CONFIG_DIR`
    environment variable, then uses the `config/` directory of the
    monorepo root.  An optional overlay file (`config_file`, or the
    `CANVOD_CONFIG_FILE` environment variable) is applied on top.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: configuration models overview
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvod.config.models import (
        AuxDataConfig,
        CanvodConfig,
        NetcdfCompressionConfig,
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
        ("NetcdfCompressionConfig", "NetCDF zlib compression and level (0-9)"),
        ("IcechunkConfig", "Icechunk compression, chunking, manifest settings"),
        ("StorageConfig", "Store paths and write strategies"),
        ("LoggingConfig", "Log directory and file naming"),
        ("PreprocessingConfig", "Temporal aggregation + grid assignment"),
        ("SitesConfig", "All research sites"),
        ("SiteConfig", "One site: receivers, coordinates, VOD analyses"),
        ("ReceiverConfig", "One receiver: type, directory, naming recipe"),
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
        NetcdfCompressionConfig,
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
                paired_canopies=["canopy_01"],
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
                paired_canopies=["canopy_01"],
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

    The `paired_canopies` field on the reference receiver specifies which
    canopy receiver(s) it is paired with: `"all"` or a list of canopy
    names.  It is required for reference receivers and must not be set
    for canopy receivers.
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
        ("days_per_batch", _default.days_per_batch, "Days processed per batch"),
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
# Section: stage timing
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Stage timing

    The pipeline times each stage with `stage_timer`, a context manager
    that emits one `stage_timing` log event per stage, with the stage
    name, its duration, its status (`ok` or `error`) and any extra
    context fields.  It also emits the event when the stage fails, so a
    run that crashes still has a timing record:

    ```python
    from canvodpy.logging.stage_timer import stage_timer

    with stage_timer("rinex.process_file", file=path.name):
        ...
    ```

    `canvodpy dashboard` launches a marimo dashboard that reads these
    events from a run's log files, also while the run is in progress.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: CLI
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Configuration CLI

    The `canvodpy config` commands manage the configuration file:

    ```bash
    # Initialise config/canvod-settings.yaml from the template
    canvodpy config init

    # Validate the configuration and the receiver data it points to
    canvodpy config validate
    canvodpy config validate --site <site>

    # Show the current configuration
    canvodpy config show

    # Open canvod-settings.yaml in $EDITOR
    canvodpy config edit
    ```

    `validate` catches configuration errors (missing fields, invalid
    types, broken cross-references between receivers and VOD analyses)
    and checks each receiver's files the same way `canvodpy run` finds
    them, before you run the pipeline.
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
