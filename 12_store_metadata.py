# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvod-config",
#   "canvod-store-metadata",
#   "canvod-utils",
#   "marimo>=0.21.1",
# ]
#
# [tool.uv.sources]
# canvod-config = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-config", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-store-metadata = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-store-metadata", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-utils = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-utils", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
#
# [tool.marimo.opengraph]
# title = "12 · Store Metadata & FAIR Compliance"
# description = "How a canVODpy store describes itself: repository metadata, snapshot summary and commit metadata, checked against the zarr conventions, ACDD, DataCite and STAC."
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium",
    app_title="Store Metadata & FAIR Compliance",
    css_file="canvod_nordic.css",
    html_head_file="canvod_head.html",
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

    # Store Metadata and FAIR Compliance

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/12_store_metadata.py?mode=edit)

    Every canVODpy store describes itself: who made it, with which
    software and settings, for which site and receivers, and which period
    it covers. The package **canvod-store-metadata** writes this
    description and checks it against the metadata standards, so the
    stores are findable, accessible, interoperable, and reusable (FAIR).

    The field names follow three standards:

    - **DataCite 4.5**: identifier and citation metadata
    - **ACDD 1.3**: the Attribute Convention for Data Discovery
    - **STAC 1.1**: the SpatioTemporal Asset Catalog

    ---

    """
    )
    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    ## Three parts, each where it belongs

    A store's metadata has three parts:

    | Part | Where | What it holds | Changes |
    |---|---|---|---|
    | **Repository metadata** | Icechunk's repository metadata, on no branch and in no snapshot | What describes the store as a whole: identity, creator, publisher and license, site and position, receivers, references | Fixed fields never; the others only by amendment |
    | **Snapshot summary** | Root attributes of each snapshot | What the snapshot holds: time coverage, per-receiver counts, time range and position | Written by every commit |
    | **Commit metadata** | Icechunk's metadata of each commit | How the commit was made: software versions, environment, settings | Written by every commit |

    The **fixed fields** say which store this is: the store id, UUID,
    store type, source format, naming authority, catalog link, and
    creation date. The store id is `{site}-{gnss|vod}`, from the site
    name in lowercase.

    Every commit writes the snapshot summary in the same commit as the
    data, so it can't disagree with the data. Every commit also copies
    the repository metadata into the root attributes as CF and ACDD
    global attributes, so tools that read only the root group, such as
    xarray, see it.
    """)
    return


@app.cell
def _(mo):
    from canvod.store_metadata import StoreMetadata

    _sections = [
        (
            "identity",
            "Store id, UUID, naming authority, title, description, keywords",
            "Repository metadata",
        ),
        (
            "creator",
            "Name, email, ORCID, institution and its ROR ID",
            "Repository metadata",
        ),
        ("publisher", "Publisher name and URL, license", "Repository metadata"),
        (
            "temporal",
            "Created; updated, first and last stored epoch",
            "Created: repository metadata; the rest: snapshot summary",
        ),
        (
            "spatial",
            "Site, latitude, longitude, altitude; bounding box",
            "Site and position: repository metadata; bounding box: snapshot summary",
        ),
        (
            "instruments",
            "Receivers: type, directory, hardware; epochs, signals, position",
            "Receivers: repository metadata; counts and position: snapshot summary",
        ),
        ("references", "Publications, funding, related stores", "Repository metadata"),
        (
            "summaries",
            "Number of epochs and signals, constellations, variables",
            "Snapshot summary",
        ),
        ("processing", "Software versions", "Commit metadata"),
        (
            "environment",
            "Host, operating system, hash and text of uv.lock",
            "Commit metadata",
        ),
        ("config", "The settings and their hash", "Commit metadata"),
    ]

    _rows = "\n".join(f"| `{s}` | {d} | {p} |" for s, d, p in _sections)

    mo.md(
        f"""
    ## Sections

    `read_metadata()` combines the three parts of one snapshot into one
    `StoreMetadata`:

    | Section | Contents | Part |
    |---------|----------|------|
    {_rows}

    Each section is a Pydantic model.
    """
    )
    return (StoreMetadata,)


@app.cell
def _(StoreMetadata, mo):
    from canvod.store_metadata import validate_all
    from canvod.store_metadata.schema import (
        Creator,
        Publisher,
        SiteInfo,
        SpatialExtent,
        StoreIdentity,
        TemporalExtent,
    )

    _example = StoreMetadata(
        identity=StoreIdentity(
            id="examplesite-gnss",
            uuid="00000000-0000-4000-8000-000000000001",
            naming_authority="edu.example",
            stac_link=(
                "../../gnss-observations/edu.example.examplesite-gnss/"
                "edu.example.examplesite-gnss.json"
            ),
            title="Example GNSS-T Observations",
            description="L-band SNR observations from paired GNSS receivers",
            store_type="gnss_store",
            source_format="rinex3",
            keywords=["GNSS", "VOD", "forest"],
        ),
        creator=Creator(
            name="J. Doe",
            email="j.doe@example.edu",
            institution="Example University",
        ),
        publisher=Publisher(name="Example University", license="CC-BY-4.0"),
        temporal=TemporalExtent(
            created="2025-01-01T00:00:00Z",
            updated="2025-01-01T23:59:55Z",
        ),
        spatial=SpatialExtent(
            site=SiteInfo(name="ExampleSite"),
            geospatial_lat=48.0,
            geospatial_lon=16.0,
            geospatial_alt_m=400.0,
            bbox=[16.0, 48.0, 16.0, 48.0],
            extent_temporal_interval=[["2025-01-01T00:00:00Z", "2025-01-01T23:59:55Z"]],
        ),
    )

    _failures = validate_all(_example, recommended=False)
    _all = validate_all(_example)
    _rows = []
    for _standard, _issues in _all.items():
        _failed = len(_failures[_standard])
        _status = "PASS" if not _failed else f"{_failed} failures"
        _advice = len(_issues) - _failed
        if _advice:
            _status += f", {_advice} recommendations"
        _rows.append(f"| `{_standard}` | {_status} |")

    mo.md(
        f"""
    ## Checking against the standards

    `validate_all()` returns a list of messages per standard. With
    `recommended=False` it lists only failures: what a standard
    requires, or what ACDD 1.3 highly recommends. A store created by
    canVODpy has none. Without it, the lists also hold the ACDD
    recommendations, marked `[recommended]`, and the FAIR advice:

    ```python
    from canvod.store_metadata import validate_all

    failures = validate_all(metadata, recommended=False)
    # {{"zarr_conventions": [], "acdd": [], "datacite": [], "stac": [], "fair": []}}
    ```

    The example metadata, built by hand:

    | Standard | Result |
    |----------|--------|
    {chr(10).join(_rows)}

    Runs never build the metadata by hand. `collect_metadata()` builds it
    from the settings, and a store is not created without a naming
    authority, a description of the site's stores, a publisher, and a
    license.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Reading the metadata

    Runs write the metadata themselves: the repository metadata before
    the first write to a store, the snapshot summary and the commit
    metadata with every commit.

    ```python
    from canvod.store_metadata import metadata_exists, read_metadata, show_metadata

    if metadata_exists(store_path):
        meta = read_metadata(store_path)                          # tip of main
        old = read_metadata(store_path, snapshot_id=snapshot_id)  # one snapshot

    show_metadata(store_path)  # all sections, amendments, and the commit log
    ```

    The history of a store is its commit log; `show_metadata()` lists it.

    ## Stores on S3

    The metadata functions also take an `s3://bucket/prefix` URL, so you
    can read the metadata of a shared store without copying it:

    ```python
    show_metadata("s3://example-bucket/stores/ExampleSite/gnss")
    ```

    Credentials, region and endpoint come only from the environment
    (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` or `AWS_PROFILE`,
    `AWS_REGION`, and `AWS_ENDPOINT_URL` for storage that isn't AWS) or
    from `~/.aws/credentials`, never from the settings or the store.
    Runs write stores on S3 too: [22 · Stores on S3](./22_s3_stores.py).

    ## Changing the description

    Amendable fields change only by amendment, with a reason. Each
    changed field is recorded with its old and new value, the reason,
    who, and when:

    ```bash
    canvodpy store amend ExampleSite --store gnss \
      --set identity.title="Example site GNSS-T observations" \
      --reason "Clearer title"
    ```

    A store written before the repository metadata is moved to the
    current form once, with `canvodpy store migrate-metadata`; runs refuse
    it until then.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Listing the stores of a directory

    `scan_stores()` finds the Icechunk stores in a directory tree and
    lists their metadata, one row per store:

    ```python
    from pathlib import Path

    from canvod.store_metadata import scan_stores, write_stac_catalog

    inventory = scan_stores(Path("/data/stores/"))

    # STAC catalog at /data/stores/catalog.json, a collection next to each store
    write_stac_catalog(Path("/data/stores/"))
    ```

    STAC is a widely used standard for finding geospatial data; any STAC
    browser or STAC API can read the catalog.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    **Previous**: [11 · Icechunk Store](./11_icechunk_store.py)
    | **Next**: [13 · Store Operations](./13_workflow_store_operations.py)

    *canVODpy · Apache 2.0*
    """)
    return


if __name__ == "__main__":
    app.run()
