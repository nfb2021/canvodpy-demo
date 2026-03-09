import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium", css_file="canvod_nordic.css")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        r"""
    # canVODpy Configuration Explorer

    canVODpy is driven by three YAML configuration files that control every
    aspect of the processing pipeline.  This notebook loads and displays the
    active configuration so you can inspect, understand, and validate the
    settings before running a pipeline.

    | File | Purpose |
    |---|---|
    | `config/sites.yaml` | Research sites, receivers, VOD analysis pairs |
    | `config/processing.yaml` | Metadata, credentials, auxiliary data, processing params, storage, Icechunk |
    | `config/sids.yaml` | Signal ID (SID) selection and filtering |

    ---

    *Nicolas F. Bader, CLIMERS — TU Wien*
    *Licensed under Apache 2.0.  Provided "as is" without warranty of any kind.*
    """
    )


@app.cell
def _():
    from pathlib import Path

    import yaml

    return Path, yaml


@app.cell
def _(Path):
    _root = Path(__file__).resolve().parent.parent
    CONFIG_DIR = _root / "config"

    return (CONFIG_DIR,)


# ---------------------------------------------------------------------------
# Load configuration files
# ---------------------------------------------------------------------------


@app.cell
def _(CONFIG_DIR, yaml):
    with open(CONFIG_DIR / "sites.yaml") as _f:
        sites_config = yaml.safe_load(_f)

    with open(CONFIG_DIR / "processing.yaml") as _f:
        processing_config = yaml.safe_load(_f)

    with open(CONFIG_DIR / "sids.yaml") as _f:
        sids_config = yaml.safe_load(_f)

    return processing_config, sids_config, sites_config


# ---------------------------------------------------------------------------
# Section selector
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    section = mo.ui.dropdown(
        options=[
            "Sites & Receivers",
            "Metadata & Credentials",
            "Auxiliary Data",
            "Processing Parameters",
            "Preprocessing Pipeline",
            "Storage & Icechunk",
            "Signal IDs (SIDs)",
        ],
        value="Sites & Receivers",
        label="Configuration section",
    )
    section

    return (section,)


# ---------------------------------------------------------------------------
# Sites & Receivers
# ---------------------------------------------------------------------------


@app.cell
def _(mo, section, sites_config):
    mo.stop(section.value != "Sites & Receivers")

    _sites = sites_config.get("sites", {})
    _parts = []

    for _name, _cfg in _sites.items():
        _rx_rows = ""
        for _rx_name, _rx in _cfg.get("receivers", {}).items():
            _rx_rows += (
                f"| `{_rx_name}` | {_rx.get('type', '?')} | "
                f"`{_rx.get('directory', '?')}` | {_rx.get('reader_format', '?')} | "
                f"{_rx.get('description', '')} |\n"
            )

        _vod_rows = ""
        for _v_name, _v in (_cfg.get("vod_analyses") or {}).items():
            _vod_rows += (
                f"| `{_v_name}` | `{_v.get('canopy_receiver', '?')}` | "
                f"`{_v.get('reference_receiver', '?')}` | {_v.get('description', '')} |\n"
            )

        _parts.append(f"""
### Site: {_name}

| Property | Value |
|---|---|
| Data root | `{_cfg.get('gnss_site_data_root', '?')}` |
| Description | {_cfg.get('description', '—')} |
| Country | {_cfg.get('country', '—')} |
| Latitude | {_cfg.get('latitude', '—')}° |
| Longitude | {_cfg.get('longitude', '—')}° |
| Altitude | {_cfg.get('altitude_m', '—')} m |

#### Receivers

| Name | Type | Directory | Format | Description |
|---|---|---|---|---|
{_rx_rows}

#### VOD Analyses

| Name | Canopy | Reference | Description |
|---|---|---|---|
{_vod_rows}
""")

    mo.md("## Sites & Receivers\n\n" + "\n".join(_parts))


# ---------------------------------------------------------------------------
# Metadata & Credentials
# ---------------------------------------------------------------------------


@app.cell
def _(mo, processing_config, section):
    mo.stop(section.value != "Metadata & Credentials")

    _meta = processing_config.get("metadata", {})
    _cred = processing_config.get("credentials", {})

    mo.md(f"""
## Metadata

Metadata fields are written into every processed dataset and Icechunk store
for provenance tracking.  They map to DataCite 4.5 and ACDD 1.3 standards.

| Field | Value |
|---|---|
| Author | {_meta.get('author', '—')} |
| Email | {_meta.get('email', '—')} |
| ORCID | {_meta.get('orcid') or '—'} |
| Institution | {_meta.get('institution', '—')} |
| ROR | {_meta.get('institution_ror') or '—'} |
| Department | {_meta.get('department') or '—'} |
| Research group | {_meta.get('research_group') or '—'} |
| Website | {_meta.get('website') or '—'} |
| License | {_meta.get('license') or '—'} |
| Publisher | {_meta.get('publisher') or '—'} |
| Naming authority | {_meta.get('naming_authority') or '—'} |

## Credentials

| Field | Value |
|---|---|
| NASA Earthdata email | {_cred.get('nasa_earthdata_acc_mail') or '*(not set — ESA only)*'} |

If the NASA Earthdata email is set, the pipeline uses CDDIS as the primary
FTP source with ESA as fallback.  Otherwise, ESA is used exclusively (no
authentication required).
""")


# ---------------------------------------------------------------------------
# Auxiliary Data
# ---------------------------------------------------------------------------


@app.cell
def _(mo, processing_config, section):
    mo.stop(section.value != "Auxiliary Data")

    _aux = processing_config.get("aux_data", {})

    mo.md(f"""
## Auxiliary Data

Precise satellite orbits (SP3) and clock corrections (CLK) are downloaded
from analysis centres before processing.

| Setting | Value | Description |
|---|---|---|
| Agency | `{_aux.get('agency', '?')}` | Analysis centre (COD, GFZ, IGS, ESA, ...) |
| Product type | `{_aux.get('product_type', '?')}` | `final` (best, ~2 week latency), `rapid` (~1 day), `ultra-rapid` (predicted) |

The agency determines which orbit products are used for satellite coordinate
computation.  CODE (`COD`) final products are recommended for research — they
provide the highest accuracy (~2 cm orbit, ~0.1 ns clock).
""")


# ---------------------------------------------------------------------------
# Processing Parameters
# ---------------------------------------------------------------------------


@app.cell
def _(mo, processing_config, section):
    mo.stop(section.value != "Processing Parameters")

    _proc = processing_config.get("processing", {})

    _keep_vars = _proc.get("keep_rnx_vars", ["SNR"])
    _keep_str = ", ".join(f"`{v}`" for v in _keep_vars)

    mo.md(f"""
## Processing Parameters

These settings control how RINEX/SBF data is read, augmented, and batched.

### Observation Settings

| Setting | Value | Description |
|---|---|---|
| Keep RINEX variables | {_keep_str} | Observation types preserved from RINEX files |
| Aggregate GLONASS FDMA | `{_proc.get('aggregate_glonass_fdma', True)}` | Merge GLONASS FDMA sub-bands into effective G1*/G2* |
| Store radial distance | `{_proc.get('store_radial_distance', False)}` | Keep satellite-receiver distance alongside phi/theta |
| Receiver position mode | `{_proc.get('receiver_position_mode', 'shared')}` | `shared`: all receivers use canopy position; `per_receiver`: each uses own |
| File pairing | `{_proc.get('file_pairing', 'complete')}` | `complete`: per-receiver; `paired`: only dates with both receivers |
| Ephemeris source | `{_proc.get('ephemeris_source', 'final')}` | `final`: SP3/CLK products; `broadcast`: from SBF file (SBF only) |

### Batch & Resource Settings

| Setting | Value | Description |
|---|---|---|
| Batch hours | `{_proc.get('batch_hours', 24)}` | Hours per processing batch (24 = one day) |
| Resource mode | `{_proc.get('resource_mode', 'auto')}` | `auto`: Dask auto-detects; `manual`: use caps below |
| Max threads | `{_proc.get('n_max_threads', '*(auto)*')}` | Worker processes (manual mode only) |
| Max memory | `{_proc.get('max_memory_gb', '*(auto)*')}` | RAM budget in GB (manual mode only) |
""")


# ---------------------------------------------------------------------------
# Preprocessing Pipeline
# ---------------------------------------------------------------------------


@app.cell
def _(mo, processing_config, section):
    mo.stop(section.value != "Preprocessing Pipeline")

    _pre = processing_config.get("preprocessing", {})
    _ta = _pre.get("temporal_aggregation", {})
    _ga = _pre.get("grid_assignment", {})

    mo.md(f"""
## Preprocessing Pipeline

Optional operations applied automatically during ingestion, after
satellite coordinate augmentation.

### Temporal Aggregation

| Setting | Value | Description |
|---|---|---|
| Enabled | `{_ta.get('enabled', False)}` | Resample observations to coarser time grid |
| Frequency | `{_ta.get('freq', '1min')}` | Target interval (pandas offset: `30s`, `1min`, `5min`) |
| Method | `{_ta.get('method', 'mean')}` | Aggregation function (`mean` or `median`) |

Temporal aggregation reduces data volume and noise.  A 5 s dataset
aggregated to 1 min is 12x smaller.

### Grid Assignment

| Setting | Value | Description |
|---|---|---|
| Enabled | `{_ga.get('enabled', False)}` | Assign hemisphere grid cells during ingestion |
| Grid type | `{_ga.get('grid_type', 'equal_area')}` | Grid geometry for cell assignment |
| Angular resolution | `{_ga.get('angular_resolution', 2.0)}`° | Cell size |

When enabled, a `cell_id` coordinate is added to each observation at
ingestion time, avoiding the need to recompute it later.
""")


# ---------------------------------------------------------------------------
# Storage & Icechunk
# ---------------------------------------------------------------------------


@app.cell
def _(mo, processing_config, section):
    mo.stop(section.value != "Storage & Icechunk")

    _storage = processing_config.get("storage", {})
    _ice = processing_config.get("icechunk", {})
    _comp = processing_config.get("compression", {})
    _chunks = _ice.get("chunk_strategies", {})

    _chunk_rows = ""
    for _store_type, _dims in _chunks.items():
        _dim_str = ", ".join(f"{k}={v}" for k, v in _dims.items())
        _chunk_rows += f"| `{_store_type}` | {_dim_str} |\n"

    mo.md(f"""
## Storage

| Setting | Value |
|---|---|
| Stores root | `{_storage.get('stores_root_dir', '?')}` |
| RINEX store name | `{_storage.get('rinex_store_name', 'rinex')}` |
| VOD store name | `{_storage.get('vod_store_name', 'vod')}` |
| RINEX strategy | `{_storage.get('rinex_store_strategy', 'skip')}` |
| VOD strategy | `{_storage.get('vod_store_strategy', 'overwrite')}` |
| Aux data dir | `{_storage.get('aux_data_dir', '*(system temp)*')}` |

Strategies: `skip` (don't overwrite), `overwrite` (replace), `append` (add new epochs).

## Icechunk Settings

Icechunk provides git-like versioning for Zarr v3 stores.

| Setting | Value |
|---|---|
| Compression | `{_ice.get('compression_algorithm', 'zstd')}` level {_ice.get('compression_level', 5)} |
| Inline threshold | {_ice.get('inline_threshold', 512)} bytes |
| Get concurrency | {_ice.get('get_concurrency', 1)} |

### Chunk Strategies

| Store type | Dimensions |
|---|---|
{_chunk_rows}

Chunking controls how data is split for parallel I/O.  `epoch=34560`
means ~2 days of 5 s data per chunk; `sid=-1` keeps all signal IDs in
one chunk (they are always accessed together).
""")


# ---------------------------------------------------------------------------
# Signal IDs (SIDs)
# ---------------------------------------------------------------------------


@app.cell
def _(mo, section, sids_config):
    mo.stop(section.value != "Signal IDs (SIDs)")

    _mode = sids_config.get("mode", "all")
    _preset = sids_config.get("preset", "—")
    _custom = sids_config.get("custom_sids", [])

    # Count by constellation
    _counts = {}
    for _sid in _custom:
        _const = _sid[0]
        _counts[_const] = _counts.get(_const, 0) + 1

    _count_str = ", ".join(
        f"**{_prefixes.get(k, k)}**: {v}"
        for k, v in sorted(_counts.items())
    ) if (_prefixes := {"G": "GPS", "E": "Galileo", "R": "GLONASS", "C": "BeiDou", "I": "IRNSS", "S": "SBAS", "J": "QZSS"}) and _counts else "—"

    mo.md(f"""
## Signal IDs (SIDs)

Signal IDs identify individual GNSS signals.  Format: `PRN|Band|Code`
(e.g. `G01|L1|C` = GPS PRN 01, L1 band, C/A code).

| Setting | Value |
|---|---|
| Mode | `{_mode}` |
| Preset | `{_preset}` |
| Custom SIDs | {len(_custom)} signals |

### Constellation breakdown

{_count_str}

### Modes

- **`all`** — Keep every SID found in the file (no filtering)
- **`preset`** — Use a named preset (`gps_galileo`, `multi_gnss`, `gps_only`)
- **`custom`** — Keep only the SIDs listed in `custom_sids`

Custom mode gives full control over which satellites and frequency bands
enter the pipeline.  This is useful for constellation-specific analyses
(e.g. BeiDou-only VOD) or for excluding noisy signals.
""")


@app.cell
def _(mo):
    mo.md(
        r"""
    ---

    ## Configuration Commands

    ```bash
    just config-show              # Display current config
    just config-validate          # Validate sites.yaml
    just config-check-data SITE   # Pre-flight data directory check
    just config-edit FILE         # Open config file in editor
    just config-init              # Initialize from template
    ```

    ---

    *canVODpy — CLIMERS, TU Wien | Apache 2.0 | No warranty*
    """
    )


if __name__ == "__main__":
    app.run()
