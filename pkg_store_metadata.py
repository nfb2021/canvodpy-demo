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
    # canvod-store-metadata — Rich Store Provenance

    The **canvod-store-metadata** package manages the full metadata lifecycle
    for Icechunk stores: schema definition, runtime collection, store I/O,
    validation against community standards, and inventory building.

    It writes ~90 metadata fields across 11 sections into the Zarr root
    attributes of every store, ensuring complete provenance tracking aligned
    with **DataCite 4.5**, **ACDD 1.3**, and **STAC 1.1**.

    ---

    *Nicolas F. Bader, CLIMERS — TU Wien*
    *Licensed under Apache 2.0.  Provided "as is" without warranty of any kind.*
    """
    )


# ---------------------------------------------------------------------------
# Schema overview
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    _sections = [
        ("Identity & Discovery", "id, title, description, store_type, source_format, keywords"),
        ("Creator", "name, email, orcid, institution, institution_ror"),
        ("Publisher & Rights", "name, type, url, license, license_uri"),
        ("Temporal Extent", "created, updated, collected_start/end, duration, resolution"),
        ("Spatial Extent & Site", "site name/description/country, lat/lon/alt, bbox, CRS"),
        ("Receivers & Instruments", "platform, per-receiver: type, format, epochs, sids, variables"),
        ("Software Provenance", "software versions, python, uv, level, lineage, facility"),
        ("Environment", "hostname, os, arch, cpu_count, memory_gb, dask config"),
        ("Config Snapshot", "processing, preprocessing, aux_data, compression, sids, config_hash"),
        ("References", "software_repository, documentation, publications, funding"),
        ("Summaries", "total_epochs, total_sids, constellations, variables, file_count, store_size_mb"),
    ]

    _rows = "\n".join(
        f"| §{i+1} | **{name}** | {fields} |"
        for i, (name, fields) in enumerate(_sections)
    )

    mo.md(f"""
## 11 Metadata Sections

| # | Section | Key fields |
|---|---|---|
{_rows}

All sections are Pydantic models — validated at construction, serialised
to JSON-compatible dicts for Zarr root attributes.
""")


# ---------------------------------------------------------------------------
# Collectors
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Runtime Collectors

    Collectors are pure functions that gather metadata from the running
    environment — no side effects, no network calls.

    ```python
    from canvod.store_metadata import collect_metadata

    meta = collect_metadata(
        config=config,
        site_name="Rosalia",
        site_config=site_config,
        store_type="rinex_store",
        source_format="rinex3",
        store_path=store_path,
    )
    ```

    The `collect_metadata()` convenience function calls all individual
    collectors and assembles a complete `StoreMetadata` object.
    """
    )


# ---------------------------------------------------------------------------
# Software versions
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvod.store_metadata.collectors import collect_software_versions

    _versions = collect_software_versions()
    _rows = "\n".join(f"| `{k}` | {v} |" for k, v in sorted(_versions.items()))

    mo.md(f"""
## Detected Software Versions

| Package | Version |
|---|---|
{_rows}

These are embedded in every store for reproducibility — you can always trace
which software versions produced a dataset.
""")

    return (collect_software_versions,)


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvod.store_metadata.collectors import collect_environment

    _env = collect_environment()
    _env_dict = _env.model_dump()
    _rows = "\n".join(f"| `{k}` | {v} |" for k, v in _env_dict.items())

    mo.md(f"""
## Environment Snapshot

| Field | Value |
|---|---|
{_rows}

Captured at metadata collection time — useful for debugging performance
differences across machines.
""")

    return (collect_environment,)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Standards Validation

    The `validate` module checks metadata completeness against three community
    standards:

    | Standard | Scope | Use case |
    |---|---|---|
    | **DataCite 4.5** | Mandatory fields for DOI registration | TU Wien Repositum publishing |
    | **ACDD 1.3** | Attribute Convention for Data Discovery | NetCDF/Zarr interop, catalog search |
    | **STAC 1.1** | SpatioTemporal Asset Catalog | Geospatial data catalogs |

    ```python
    from canvod.store_metadata import validate_all

    issues = validate_all(metadata)
    # {"datacite": [...], "acdd": [...], "stac": [...]}
    ```

    An empty list means full compliance with that standard.
    """
    )


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Store Inventory

    `scan_stores()` walks a directory tree, finds all Icechunk stores, reads
    their metadata, and returns a Polars DataFrame — one row per store.

    ```python
    from canvod.store_metadata import scan_stores

    catalog = scan_stores(Path("/data/gnss_stores/"))
    print(catalog.columns)
    # ['id', 'title', 'store_type', 'source_format', 'site',
    #  'creator', 'license', 'time_start', 'time_end', 'lat', 'lon',
    #  'total_epochs', 'store_size_mb', 'path', ...]
    ```

    This enables building dashboards and catalogs across all research sites
    and processing stages.
    """
    )


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Store I/O

    Metadata is stored in the Zarr root attributes under the `canvod_metadata`
    key — a single JSON-serializable dict.

    ```python
    from canvod.store_metadata import write_metadata, read_metadata, update_metadata

    # Write (first ingest)
    write_metadata(store_path, metadata)

    # Read back
    meta = read_metadata(store_path)

    # Incremental update (subsequent ingests)
    update_metadata(store_path, {
        "temporal.updated": "2025-01-02T00:00:00Z",
        "summaries.total_epochs": 5760,
    })
    ```

    The orchestrator calls `write_metadata` on the first ingest and
    `update_metadata` on every subsequent write to keep temporal extent
    and summaries current.
    """
    )


@app.cell
def _(mo):
    mo.md(
        r"""
    ---

    *canVODpy — CLIMERS, TU Wien | Apache 2.0 | No warranty*
    """
    )


if __name__ == "__main__":
    app.run()
