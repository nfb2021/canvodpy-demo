import marimo

__generated_with = "0.12.0"
app = marimo.App(
    width="medium",
    app_title="Store Metadata & FAIR Compliance",
    css_file="canvod_nordic.css",
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Store Metadata and FAIR Compliance

    The **canvod-store-metadata** package attaches rich, standards-compliant
    provenance metadata to every Icechunk store.  This metadata enables
    **FAIR** (Findable, Accessible, Interoperable, Reusable) data
    management and supports automated cataloguing via STAC (SpatioTemporal
    Asset Catalog).

    The metadata schema comprises **11 sections** with approximately
    **90 fields**, validated against three international standards:

    - **DataCite 4.5** — persistent identifier and citation metadata
    - **ACDD 1.3** — Attribute Convention for Dataset Discovery
    - **STAC 1.1** — SpatioTemporal Asset Catalog

    ---

    """
    )

    return (mo,)


# ---------------------------------------------------------------------------
# Section: metadata schema
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvod.store_metadata import StoreMetadata

    _sections = [
        ("identity", "Store title, DOI, version, description"),
        ("creator", "Author ORCID, institution, ROR, email"),
        ("publisher", "Publisher name, URL, contact"),
        ("temporal", "Start/end dates, processing timestamp"),
        ("spatial", "Site coordinates, country, bounding box"),
        ("instruments", "Receiver model, antenna, firmware"),
        ("processing", "Software versions, pipeline parameters"),
        ("environment", "Python version, OS, dependencies"),
        ("config", "Frozen snapshot of processing configuration"),
        ("references", "Publications, URLs, related datasets"),
        ("summaries", "Statistics, quality indicators, data volume"),
    ]

    _rows = "\n".join(f"| `{s}` | {d} |" for s, d in _sections)

    mo.md(
        f"""
    ## Metadata sections

    The `StoreMetadata` Pydantic model organises metadata into 11 sections:

    | Section | Contents |
    |---------|----------|
    {_rows}

    Each section is a nested Pydantic model with field-level validation,
    defaults, and documentation.
    """
    )

    return (StoreMetadata,)


# ---------------------------------------------------------------------------
# Section: building metadata
# ---------------------------------------------------------------------------


@app.cell
def _(StoreMetadata, mo):
    from canvod.store_metadata.schema import (
        Creator,
        SiteInfo,
        SpatialExtent,
        StoreIdentity,
        TemporalExtent,
    )

    _example = StoreMetadata(
        identity=StoreIdentity(
            id="example_site/rinex_store",
            title="Example GNSS-T Observations",
            store_type="rinex_store",
            source_format="rinex3",
            description="L-band SNR observations from paired GNSS receivers",
        ),
        creator=Creator(
            name="J. Doe",
            email="j.doe@example.edu",
            institution="Example University",
        ),
        temporal=TemporalExtent(
            created="2025-01-01T00:00:00Z",
            updated="2025-01-01T23:59:55Z",
        ),
        spatial=SpatialExtent(
            site=SiteInfo(name="Example Site"),
            geospatial_lat=48.0,
            geospatial_lon=16.0,
            geospatial_alt_m=400.0,
        ),
    )

    _dict = _example.model_dump(exclude_none=True)
    _n_fields = sum(len(v) if isinstance(v, dict) else 1 for v in _dict.values())

    mo.md(
        f"""
    ## Building metadata

    ```python
    from canvod.store_metadata import StoreMetadata
    from canvod.store_metadata.schema import (
        StoreIdentity, Creator, TemporalExtent, SpatialExtent,
    )

    metadata = StoreMetadata(
        identity=StoreIdentity(id="my_site/rinex_store", title="My GNSS-T Store", store_type="rinex_store", source_format="rinex3", ...),
        creator=Creator(name="J. Doe", email="j.doe@example.edu", institution="My University", ...),
        temporal=TemporalExtent(created="2025-01-01T00:00:00Z", updated="2025-01-01T00:00:00Z", ...),
        spatial=SpatialExtent(site="My Site", geospatial_lat=48.0, ...),
    )
    ```

    The example above populates {_n_fields} fields.  Optional sections
    (instruments, processing, environment, etc.) are auto-populated by
    collector functions when available.
    """
    )

    return Creator, SpatialExtent, StoreIdentity, TemporalExtent


# ---------------------------------------------------------------------------
# Section: validation
# ---------------------------------------------------------------------------


@app.cell
def _(StoreMetadata, mo):
    from canvod.store_metadata import validate_all
    from canvod.store_metadata.schema import (
        Creator as _C,
    )
    from canvod.store_metadata.schema import (
        SiteInfo as _Si,
    )
    from canvod.store_metadata.schema import (
        SpatialExtent as _Sp,
    )
    from canvod.store_metadata.schema import (
        StoreIdentity as _Id,
    )
    from canvod.store_metadata.schema import (
        TemporalExtent as _Te,
    )

    _meta = StoreMetadata(
        identity=_Id(
            id="test_site/rinex_store",
            title="Test",
            store_type="rinex_store",
            source_format="rinex3",
        ),
        creator=_C(name="Test", email="test@example.com", institution="Test"),
        temporal=_Te(created="2025-01-01T00:00:00Z", updated="2025-01-01T00:00:00Z"),
        spatial=_Sp(site=_Si(name="Test")),
    )

    _results = validate_all(_meta)

    _rows = []
    for _standard, _errors in _results.items():
        _status = "PASS" if not _errors else f"{len(_errors)} issues"
        _rows.append(f"| `{_standard}` | {_status} |")

    mo.md(
        f"""
    ## Multi-standard validation

    `validate_all()` checks metadata against all supported standards
    and returns a dictionary of results:

    ```python
    from canvod.store_metadata import validate_all

    results = validate_all(metadata)
    # {{"datacite": [...], "acdd": [...], "stac": [...], "fair": [...]}}
    ```

    | Standard | Result |
    |----------|--------|
    {chr(10).join(_rows)}

    Missing optional fields are reported as warnings, not errors.
    The validators are designed to guide users toward complete metadata
    without blocking data ingestion.
    """
    )

    return (validate_all,)


# ---------------------------------------------------------------------------
# Section: I/O
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Store I/O

    Metadata is stored in the Zarr root attributes under the key
    `canvod_metadata`.  The I/O functions handle serialisation and
    deserialisation:

    ```python
    from canvod.store_metadata import (
        write_metadata,   # Write to store
        read_metadata,    # Read from store
        update_metadata,  # Merge updates
        metadata_exists,  # Check presence
    )

    # Write
    write_metadata(store_path, metadata, branch="main")

    # Read back
    meta = read_metadata(store_path, branch="main")

    # Update specific fields (dotted keys supported)
    update_metadata(store_path, {"temporal.end": "2025-12-31"})

    # Check
    if metadata_exists(store_path):
        ...
    ```

    ### Automatic collection

    The `collect_metadata()` function auto-populates as many fields as
    possible from the processing environment:

    - Python version, OS, installed packages (environment section)
    - canvodpy version, pipeline parameters (processing section)
    - Site configuration (spatial, instruments sections)
    - Current timestamp (temporal section)

    ```python
    from canvod.store_metadata import collect_metadata

    metadata = collect_metadata(
        config=site_config,
        datasets={"canopy": ds_canopy, "reference": ds_reference},
    )
    ```
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: STAC integration
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## STAC catalog integration

    For multi-site deployments, `scan_stores()` discovers all Icechunk
    stores in a directory tree and extracts their metadata into a
    catalogue:

    ```python
    from canvod.store_metadata import scan_stores, write_stac_catalog

    # Scan all stores under a root directory
    inventory = scan_stores(Path("/data/gnss_stores/"))

    # Write STAC catalog for web-based discovery
    write_stac_catalog(inventory, Path("/data/stac_catalog/"))
    ```

    STAC (SpatioTemporal Asset Catalog) is a widely adopted standard
    for geospatial data discovery.  The generated catalog can be served
    by any STAC API implementation (e.g. stac-fastapi) for web-based
    search and access.
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

    **Previous**: [08 — Icechunk Store](./08_icechunk_store.py)
    | **Next**: [10 — Visualization](./10_visualization.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
