# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvod-store",
#   "canvod-store-metadata",
#   "canvod-ops",
#   "canvodpy",
#   "pooch>=1.6",
#   "pyyaml>=6.0",
#   "marimo>=0.21.1",
# ]
#
# [tool.uv.sources]
# canvod-store = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-store", rev = "b8dfd7ace67284cc0a561f239f5cd0318bb7bd12" }
# canvod-store-metadata = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-store-metadata", rev = "b8dfd7ace67284cc0a561f239f5cd0318bb7bd12" }
# canvod-ops = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-ops", rev = "b8dfd7ace67284cc0a561f239f5cd0318bb7bd12" }
# canvodpy = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "canvodpy", rev = "b8dfd7ace67284cc0a561f239f5cd0318bb7bd12" }
#
# [tool.marimo.opengraph]
# title = "18 · Store Operations"
# description = "Read, write, branch, and query Icechunk stores. Covers temporal aggregation, store snapshots, metadata queries, and the operational pipeline layer."
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(
    width="medium",
    app_title="Store Operations",
    css_file="canvod_nordic.css",
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Store Operations

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/18_workflow_store_operations.py)

    A comprehensive, hands-on tour of everything `MyIcechunkStore`
    (`canvod-store`) and its companion `canvod-store-metadata` package can
    do to a real store: branching, writing, commit history, time travel,
    native rich rendering, and store-wide provenance metadata.

    Every operation below runs against the **same live store** built for
    notebook 08 — nothing here is illustrative-only.

    **Test data**: this notebook builds the store live, at run time, by
    running the real `canvodpy` CLI against real Rosalia RINEX v3.04 data
    for DOY 2025-001 — no pre-built store fixture is shipped (see
    `_live_store.py` for why).

    ---

    """
    )
    return (mo,)


@app.cell
def _():
    import _paths
    from _download import marimo_downloader
    _paths.ensure_data(downloader=marimo_downloader)
    return


@app.cell
def _(mo):
    from canvod.store import MyIcechunkStore

    from _live_store import build_rosalia_store, get_pipeline_command, get_pipeline_output

    store, store_path = build_rosalia_store()

    _branches = store.get_branch_names()
    _groups = store.list_groups()
    _attrs = store.get_root_attrs()

    mo.md(
        f"""
    ## Opening and inspecting a store

    ```python
    from canvod.store import MyIcechunkStore

    store = MyIcechunkStore(store_path=Path("stores/rosalia_rinex"))
    ```

    | Property | Value |
    |----------|-------|
    | **Path** | `{store_path}` |
    | **Branches** | {", ".join(f"`{b}`" for b in _branches)} |
    | **Groups** | {", ".join(f"`{g}`" for g in _groups) if _groups else "(empty)"} |
    | **Source format** | `{_attrs.get("source_format", "unknown")}` |

    The `source_format` root attribute indicates whether data
    originated from RINEX or SBF files.

    This store was built by running the real `canvodpy` CLI as a
    subprocess (marimo notebooks can't run shell commands directly) --
    here is the exact command that produced it:

    ```bash
    {get_pipeline_command()}
    ```

    <details>
    <summary>CLI output (captured after the run finished -- not live)</summary>

    ```text
    {get_pipeline_output()}
    ```

    </details>
    """
    )
    return store, store_path


@app.cell
def _(mo):
    mo.md(r"""
    ## Native rich rendering

    `MyIcechunkStore` defines `_repr_html_()` (via
    `canvod.store.viewer.add_rich_display_to_store`), so marimo (and
    Jupyter) render it as a formatted summary automatically -- no
    `print()` or manual formatting needed. Just place a bare `store`
    reference as a cell's last expression:
    """)
    return


@app.cell
def _(store):
    store
    return


@app.cell
def _(mo, store):
    import xarray as xr

    _groups = store.list_groups()

    if _groups:
        with store.readonly_session(branch="main") as _session:
            _root = xr.open_zarr(_session.store, consolidated=False)
        data_vars_table = mo.ui.table(
            [
                {"variable": _v, "dtype": str(_root[_v].dtype), "dimensions": str(_root[_v].dims)}
                for _v in _root.data_vars
            ],
            page_size=10,
            label="Root dataset variables",
        )
    else:
        data_vars_table = mo.md("Store has no groups yet.")

    mo.md(
        r"""
    ## Reading data

    ```python
    with store.readonly_session(branch="main") as session:
        ds = xr.open_zarr(session.store, group="canopy_01", consolidated=False)
    ```

    Read-only sessions provide a consistent snapshot: even if another
    process is writing to the store concurrently, your view remains
    unchanged until the session is closed.

    **Root dataset** -- a real `mo.ui.table()`, not a markdown table: sort
    any column, search across all of them, page through results:
    """
    )
    return (data_vars_table,)


@app.cell
def _(data_vars_table):
    data_vars_table
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Commit history -- before

    Every write operation creates a commit. `get_history()` returns the
    full ancestry as dicts (`snapshot_id`, `commit_msg`, `written_at`,
    `parent_ids`) -- the `snapshot_id`s are the actual coordinates used
    for branching and time travel further down.
    """)
    return


@app.cell
def _(mo, store):
    def history_table(branch="main", limit=10):
        # A real mo.ui.table(), not a markdown string: sortable, searchable,
        # paginated -- and the message column is never truncated, unlike
        # icechunk's own `plot_commit_graph()` SVG renderer, which
        # hard-caps each node label at 60 chars
        # (icechunk/src/display/svg.rs::truncate_message), cutting
        # mid-word with no way to opt out from the Python side.
        _rows = [
            {
                "snapshot": _h.get("snapshot_id", "")[:8],
                "timestamp": str(_h.get("written_at", "---"))[:19],
                "message": _h.get("commit_msg", "---"),
            }
            for _h in store.get_history(branch=branch, limit=limit)
        ]
        return mo.ui.table(_rows, page_size=10, label=f"Commit history -- {branch}")

    table_before = history_table()

    mo.md(
        r"""
    ```python
    history = store.get_history(branch="main", limit=10)
    ```
    """
    )
    return history_table, table_before


@app.cell
def _(table_before):
    table_before
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Commit graph

    `plot_commit_graph()` delegates to icechunk's native
    `repo.ancestry_graph()` and renders as an SVG diagram directly in the
    notebook (or as colored text via `print()` in a terminal). icechunk's
    SVG renderer hard-truncates each message to 60 characters
    (`icechunk/src/display/svg.rs`), so long ones get cut mid-word -- the
    "Commit history" table above has the same commits with full,
    untruncated messages.
    """)
    return


@app.cell
def _(store):
    store.plot_commit_graph()
    return


@app.cell
def _(mo, store):
    main_tip = store.get_history(branch="main", limit=1)[0]["snapshot_id"]

    mo.md(
        f"""
    ## Creating a branch

    Branches let you experiment without touching `main` -- they share
    storage via Icechunk's copy-on-write mechanism, so creating one is
    near-instant regardless of store size. `create_branch()` accepts
    either a full snapshot ID or an 8-character prefix (as shown in the
    history table and commit graph above):

    ```python
    store.create_branch("demo/scratch", snapshot_id="{main_tip[:8]}")
    ```

    Branching from `main`'s current tip (`{main_tip[:8]}`).
    """
    )
    return (main_tip,)


@app.cell
def _(main_tip, store):
    demo_branch = "demo/scratch"
    if demo_branch in store.get_branch_names():
        store.delete_branch(demo_branch)
    store.create_branch(demo_branch, snapshot_id=main_tip)
    return (demo_branch,)


@app.cell
def _(demo_branch, mo, store):
    mo.md(f"""
    **Branches now**: {", ".join(f"`{b}`" for b in store.get_branch_names())}

    `{demo_branch}` points at the same snapshot as `main` -- no data was
    copied.

    The graph again -- `demo/scratch` now forks off `main`'s tip:
    """)
    return


@app.cell
def _(store):
    store.plot_commit_graph()
    return


@app.cell
def _(demo_branch, mo):
    mo.md(f"""
    Full, untruncated messages for `{demo_branch}` (same commits the graph
    above just showed) -- again as a real, queryable `mo.ui.table()`:
    """)
    return


@app.cell
def _(demo_branch, history_table):
    history_table(branch=demo_branch, limit=10)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Writing a new group on the branch

    A small synthetic dataset, built inline (not real GNSS data) purely
    to demonstrate `write_initial_group()` without touching any of the
    real ingested groups. Written to the `demo/scratch` branch, so
    `main` is completely unaffected.
    """)
    return


@app.cell
def _(demo_branch, store):
    import numpy as np
    import xarray as _xr

    def _make_demo_dataset():
        sids = ["G01|L1|C", "G02|L1|C", "E01|L1|C"]
        epochs = np.datetime64("2025-01-01T00:00:00") + np.arange(60) * np.timedelta64(
            5, "s"
        )
        rng = np.random.default_rng(42)
        snr = rng.uniform(30.0, 50.0, (60, len(sids))).astype(np.float32)
        ds = _xr.Dataset(
            {"S1C": (("epoch", "sid"), snr)},
            coords={"epoch": epochs, "sid": sids},
        )
        ds.attrs["File Hash"] = "demo0000deadbeef"
        return ds

    demo_group = "demo_scratch_group"
    if not store.group_exists(demo_group, branch=demo_branch):
        store.write_initial_group(
            _make_demo_dataset(), group_name=demo_group, branch=demo_branch
        )
    return (demo_group,)


@app.cell
def _(demo_branch, demo_group, mo, store):
    mo.md(f"""
    **Groups on `{demo_branch}`**: {
        ", ".join(f"`{g}`" for g in store.get_group_names(branch=demo_branch)[demo_branch])
    }

    **Groups on `main`**: {
        ", ".join(f"`{g}`" for g in store.list_groups(branch="main"))
    } -- unchanged, `write_initial_group()` on a branch never touches `main`.

    (`{demo_group}` on `{demo_branch}` is a small synthetic dataset built
    inline purely to demonstrate the write path -- not real GNSS data.)

    And the graph once more -- `demo/scratch` now has one extra commit
    that `main` doesn't:
    """)
    return


@app.cell
def _(store):
    store.plot_commit_graph()
    return


@app.cell
def _(demo_branch, mo):
    mo.md(f"""
    ## Commit history -- after

    `{demo_branch}`'s history now has one more commit than `main`'s (the
    write we just did); `main`'s own history (shown further up) is
    completely unchanged -- branch isolation, not just naming.

    ```python
    store.get_history(branch="{demo_branch}", limit=10)
    ```
    """)
    return


@app.cell
def _(demo_branch, history_table):
    history_table(branch=demo_branch, limit=10)
    return


@app.cell
def _(mo, store):
    _history = store.get_history(branch="main", limit=None)
    # history[-1] is always icechunk's own reserved empty "genesis" commit
    # (snapshot_id "1CECHNKREP0F1RSTCMT0"), created before any group exists --
    # not a useful "first commit" to time-travel to. The oldest *real* write
    # is one step in from that, when present.
    first_commit = _history[-2] if len(_history) > 1 else _history[-1]
    latest_commit = _history[0]

    mo.md(
        f"""
    ## Time travel

    Every snapshot ID is a permanent coordinate you can reopen directly --
    not just branch tips. `store.repo` exposes the full icechunk
    `Repository`, so `repo.readonly_session(snapshot_id=...)` opens the
    store exactly as it looked at that commit (`MyIcechunkStore`'s own
    `readonly_session()` wrapper only takes a branch name, so this drops
    to the icechunk API directly):

    ```python
    session = store.repo.readonly_session(snapshot_id="{first_commit["snapshot_id"][:8]}")
    root = zarr.open(session.store, mode="r")
    ```

    Comparing the very first commit on `main` (`{first_commit["snapshot_id"][:8]}`,
    "{first_commit["commit_msg"][:40]}") against the latest
    (`{latest_commit["snapshot_id"][:8]}`):
    """
    )
    return first_commit, latest_commit


@app.cell
def _(first_commit, latest_commit, store):
    _diff = store.compare_snapshots(
        first_commit["snapshot_id"], latest_commit["snapshot_id"]
    )
    _diff
    return


@app.cell
def _(first_commit, mo, store):
    import zarr as _zarr

    _session = store.repo.readonly_session(snapshot_id=first_commit["snapshot_id"])
    _root = _zarr.open(_session.store, mode="r")

    mo.md(
        f"""
    Opening the store *at* that first commit directly (not through
    `main`'s current tip):

    **Groups at `{first_commit["snapshot_id"][:8]}`**: {
        ", ".join(f"`{g}`" for g in _root.group_keys()) or "(none)"
    }
    """
    )
    return


@app.cell
def _(demo_branch, mo, store):
    store.delete_branch(demo_branch)

    mo.md(
        f"""
    ## Deleting a branch

    ```python
    store.delete_branch("{demo_branch}")
    ```

    **Branches now**: {", ".join(f"`{b}`" for b in store.get_branch_names())}
    -- `{demo_branch}` (and the `demo_scratch_group` written to it) is
    gone; `main` was never touched.

    **Deleting a group** is deliberately *not* shown here: unlike
    branches and tags, `MyIcechunkStore` exposes no `delete_group()` --
    there's no supported store-level operation for it (confirmed by
    reading `store.py`'s full method list). Removing a group means
    deleting the branch it lives on, or dropping to raw zarr/icechunk
    group deletion, which bypasses the metadata-ledger guardrails this
    store is built around.

    One last look at the graph -- `demo/scratch`'s fork and its commit
    are both gone; `main`'s own history is untouched throughout:
    """
    )
    return


@app.cell
def _(store):
    store.plot_commit_graph()
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Three-layer deduplication

    The store prevents duplicate data from entering the repository through
    three independent checks:

    1. **File hash match**: the SHA-256 hash of each RINEX/SBF file is
       recorded in the metadata ledger.  If the same file is ingested
       again, it is silently skipped.

    2. **Temporal overlap**: the start and end timestamps of each ingested
       file are compared against the existing data.  Files that overlap
       with previously ingested data are rejected.

    3. **Intra-batch overlap**: within a single batch of files being
       ingested, overlapping files are detected before any writes occur.

    ```python
    # Check which files are already in the store
    existing = store.batch_check_existing(
        group_name="canopy_01",
        file_hashes=["abc123...", "def456...", "ghi789..."],
    )
    # Returns: {"abc123..."} (set of hashes already present)
    ```

    This design ensures that re-running the pipeline on the same data
    is safe and idempotent.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Creating a new store

    The `create_rinex_store()` and `create_vod_store()` factory functions
    initialise new Icechunk repositories with the appropriate configuration:

    ```python
    from canvod.store import create_rinex_store, create_vod_store

    # For raw observation data
    obs_store = create_rinex_store(Path("/data/my_site/observations.icechunk"))

    # For VOD products
    vod_store = create_vod_store(Path("/data/my_site/vod.icechunk"))
    ```

    The store opened at the top of this notebook was created this way
    internally, by the `canvodpy` CLI pipeline.
    """)
    return


@app.cell
def _(mo, store):
    _groups = store.list_groups()
    ledger_group = _groups[0] if _groups else None
    ledger_table = None

    if ledger_group is not None:
        try:
            with store.readonly_session() as _session:
                ledger_table = mo.ui.table(
                    store.read_metadata_table(_session, ledger_group),
                    page_size=10,
                    label=f"Metadata ledger -- {ledger_group}",
                )
        except (KeyError, FileNotFoundError):
            ledger_table = None

    mo.md(
        r"""
    ## Metadata ledger

    Each group maintains a metadata ledger recording which files have
    been ingested -- this is the foundation of the three-layer
    deduplication system: before writing, the pipeline checks the ledger
    for hash matches and temporal overlaps.

    ```python
    with store.readonly_session() as session:
        meta = store.read_metadata_table(session, "canopy_01")
    # Returns: Polars DataFrame with rinex_hash, start, end, fname, etc.
    ```

    Returned directly to `mo.ui.table()` (it accepts a Polars DataFrame
    natively) -- sort by `start`/`end` to check temporal ordering, search
    `rinex_hash` for a specific file, or page through everything ingested
    so far:
    """
    )
    return ledger_group, ledger_table


@app.cell
def _(ledger_group, ledger_table, mo):
    (
        ledger_table
        if ledger_table is not None
        else mo.md(
            f"Group `{ledger_group}` exists but has no metadata ledger "
            "(store was not created via the full pipeline)."
            if ledger_group is not None
            else "No groups with metadata ledger found."
        )
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    The ledger stores:

    | Field | Description |
    |-------|-------------|
    | `rinex_hash` | SHA-256 hash (16-char truncation) |
    | `start` / `end` | Temporal extent of the file |
    | `fname` | Original filename |
    | `canonical_name` | Standardised name via `FilenameMapper` |
    | `written_at` | Ingestion timestamp |
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Store-wide metadata -- full schema, by standard

    Distinct from the per-file metadata ledger above: `canvod-store-metadata`
    attaches rich provenance to the *store itself* across **11 sections**
    (identity, creator, publisher, temporal, spatial, instruments,
    processing, environment, config, references, summaries -- see
    `schema.py` for the full ~90-field Pydantic model). The `canvodpy` CLI
    writes this automatically on every run.

    Every row below is this **live store's actual metadata** -- real values
    written by `collect_metadata()` from the `rosalia_v3_04` recipe, not a
    synthetic example. A field showing `(not set)` means the schema
    supports it but nothing in the current recipe/collector populates it
    yet -- that gap is real, not hidden.

    ### How to read the "Standard" column

    Most fields serve more than one external standard at once:

    | Tag | Standard | Scope |
    |-----|----------|-------|
    | **DataCite** | DataCite Metadata Schema 4.5 | Citation/identifier metadata: creator, title, publisher, funding, related identifiers |
    | **ACDD** | Attribute Convention for Dataset Discovery 1.3 | NetCDF/CF-style discovery attributes: summary, keywords, coverage, platform |
    | **STAC** | SpatioTemporal Asset Catalog 1.1 | Web-catalog fields: id, bbox, temporal extent, license |
    | **FAIR** | FAIR data principles (sub-principles `F1`-`F4`, `A1`-`A2`, `I1`-`I3`, `R1.1`-`R1.3`) | Cross-cutting findability/accessibility/interoperability/reusability -- see `validate_fair()` |
    | **W3C PROV** | W3C PROV-O | Provenance: what produced this store, when, from what config |
    | **Internal** | canvodpy-specific | No external standard; operational/debugging value only |

    ```python
    from canvod.store_metadata import metadata_exists, read_metadata

    if metadata_exists(store_path):
        meta = read_metadata(store_path)
    ```
    """)
    return


@app.cell
def _(mo, store_path):
    from canvod.store_metadata import metadata_exists, read_metadata

    _STANDARD_MAP: dict[str, str] = {
        # identity
        "identity.id": "DataCite (identifier) · STAC (id) · FAIR F1",
        "identity.title": "DataCite (title) · ACDD (title) · STAC (title)",
        "identity.description": "ACDD (summary) · STAC (description) · FAIR F2",
        "identity.store_type": "Internal",
        "identity.source_format": "Internal",
        "identity.keywords": "ACDD (keywords) · FAIR F2",
        "identity.conventions": "ACDD (Conventions) · FAIR I2",
        "identity.naming_authority": "ACDD (naming_authority)",
        "identity.persistent_identifier": "DataCite (identifier/DOI) · FAIR F1",
        "identity.standard_name_vocabulary": "ACDD (standard_name_vocabulary)",
        # creator
        "creator.name": "DataCite (creator.name) · ACDD (creator_name)",
        "creator.email": "ACDD (creator_email)",
        "creator.orcid": "DataCite (nameIdentifier) · FAIR",
        "creator.type": "DataCite (creatorType)",
        "creator.institution": "DataCite (creator.affiliation) · ACDD (institution)",
        "creator.institution_ror": "DataCite (affiliationIdentifier) · FAIR",
        "creator.department": "Internal",
        "creator.research_group": "Internal",
        "creator.website": "ACDD (creator_url)",
        # publisher
        "publisher.name": "DataCite (publisher)",
        "publisher.type": "DataCite (publisherType)",
        "publisher.url": "ACDD (publisher_url)",
        "publisher.license": "ACDD (license) · STAC (license) · FAIR R1.1",
        "publisher.license_uri": "STAC (license link)",
        # temporal
        "temporal.created": "DataCite (date: Created) · ACDD (date_created)",
        "temporal.updated": "ACDD (date_modified)",
        "temporal.collected_start": "ACDD (time_coverage_start) · FAIR F2",
        "temporal.collected_end": "ACDD (time_coverage_end) · FAIR F2",
        "temporal.time_coverage_start": "ACDD/STAC (temporal extent)",
        "temporal.time_coverage_end": "ACDD/STAC (temporal extent)",
        "temporal.time_coverage_duration": "ACDD (time_coverage_duration)",
        "temporal.time_coverage_resolution": "ACDD (time_coverage_resolution)",
        # spatial
        "spatial.site.name": "Internal",
        "spatial.site.description": "ACDD (summary, per-site)",
        "spatial.site.country": "Internal",
        "spatial.geospatial_lat": "ACDD (geospatial_lat_min/max) · FAIR F2",
        "spatial.geospatial_lon": "ACDD (geospatial_lon_min/max) · FAIR F2",
        "spatial.geospatial_alt_m": "ACDD (geospatial_vertical_min/max)",
        "spatial.geospatial_lat_min": "ACDD (geospatial_lat_min)",
        "spatial.geospatial_lat_max": "ACDD (geospatial_lat_max)",
        "spatial.geospatial_lon_min": "ACDD (geospatial_lon_min)",
        "spatial.geospatial_lon_max": "ACDD (geospatial_lon_max)",
        "spatial.geospatial_vertical_crs": "ACDD (geospatial_bounds_crs)",
        "spatial.bbox": "STAC (bbox) · FAIR F4",
        "spatial.extent_temporal_interval": "STAC (temporal extent)",
        # instruments
        "instruments.platform": "ACDD (platform)",
        "instruments.instruments": "ACDD (instrument)",
        "instruments.receivers": "Internal (canvodpy-specific)",
        # processing
        "processing.software": "W3C PROV (wasGeneratedBy) · FAIR R1.2",
        "processing.python": "Internal · FAIR R1.2",
        "processing.uv_version": "Internal · FAIR R1.2",
        "processing.level": "Internal (canvodpy API level)",
        "processing.lineage": "ACDD (source) · W3C PROV",
        "processing.facility": "ACDD (institution)",
        "processing.datetime": "W3C PROV (generatedAtTime)",
        # environment
        "environment.hostname": "Internal · FAIR R1.2",
        "environment.os": "Internal · FAIR R1.2",
        "environment.arch": "Internal · FAIR R1.2",
        "environment.cpu_count": "Internal",
        "environment.memory_gb": "Internal",
        "environment.disk_free_gb": "Internal",
        "environment.dask_workers": "Internal",
        "environment.dask_threads_per_worker": "Internal",
        "environment.uv_lock_hash": "FAIR R1.2 (reproducibility)",
        "environment.pyproject_toml_text": "FAIR R1.2 (reproducibility)",
        "environment.uv_lock_text": "FAIR R1.2 (reproducibility)",
        # config
        "config.processing": "W3C PROV (frozen config) · Internal",
        "config.preprocessing": "W3C PROV (frozen config) · Internal",
        "config.aux_data": "W3C PROV (frozen config) · Internal",
        "config.compression": "W3C PROV (frozen config) · Internal",
        "config.icechunk": "W3C PROV (frozen config) · Internal",
        "config.sids": "W3C PROV (frozen config) · Internal",
        "config.config_hash": "W3C PROV (checksum) · Internal",
        # references
        "references.software_repository": "FAIR R1.2 · Internal",
        "references.documentation": "Internal",
        "references.access_url": "FAIR A1",
        "references.related_stores": "FAIR I3",
        "references.publications": "DataCite (relatedIdentifiers) · FAIR I3",
        "references.funding": "DataCite (fundingReferences)",
        # summaries
        "summaries.total_epochs": "ACDD (summary statistics) · Internal",
        "summaries.total_sids": "ACDD (summary statistics) · Internal",
        "summaries.constellations": "ACDD (summary statistics) · Internal",
        "summaries.variables": "ACDD (summary statistics) · Internal",
        "summaries.temporal_resolution_s": "ACDD (summary statistics) · Internal",
        "summaries.file_count": "ACDD (summary statistics) · Internal",
        "summaries.store_size_mb": "ACDD (summary statistics) · Internal",
        "summaries.history": "W3C PROV (activity log)",
    }

    def _fmt_value(v):
        if v is None:
            return "(not set)"
        if isinstance(v, str):
            if len(v) > 200:
                return f"(stored -- {len(v):,} chars)"
            return v
        if isinstance(v, list):
            if not v:
                return "(empty)"
            if len(v) > 5 or any(isinstance(x, dict) for x in v):
                return f"[{len(v)} items]"
            return str(v)
        if isinstance(v, dict):
            if not v:
                return "(empty)"
            if len(v) > 4 or any(isinstance(x, dict | list) for x in v.values()):
                _keys = ", ".join(list(v)[:5])
                _more = "" if len(v) <= 5 else f", … +{len(v) - 5} more"
                return f"({len(v)} keys: {_keys}{_more})"
            return ", ".join(f"{k}={vv}" for k, vv in v.items())
        return str(v)

    def _rows_for(section_name, section_dict, prefix=None):
        _out = []
        prefix = prefix or section_name
        for k, v in section_dict.items():
            path = f"{prefix}.{k}"
            if k == "site" and isinstance(v, dict):
                _out.extend(_rows_for(section_name, v, prefix=path))
                continue
            if k == "receivers" and isinstance(v, dict):
                if not v:
                    _out.append(
                        {
                            "section": section_name,
                            "field": path,
                            "value": "(no receivers)",
                            "standard": _STANDARD_MAP.get(path, "—"),
                        }
                    )
                for rcv_name, rcv in v.items():
                    for rk, rv in rcv.items():
                        _out.append(
                            {
                                "section": section_name,
                                "field": f"{path}.{rcv_name}.{rk}",
                                "value": _fmt_value(rv),
                                "standard": "Internal (canvodpy-specific)",
                            }
                        )
                continue
            if k in ("publications", "funding") and isinstance(v, list):
                if not v:
                    _out.append(
                        {
                            "section": section_name,
                            "field": path,
                            "value": "(none)",
                            "standard": _STANDARD_MAP.get(path, "—"),
                        }
                    )
                for i, item in enumerate(v):
                    for ik, iv in item.items():
                        _out.append(
                            {
                                "section": section_name,
                                "field": f"{path}[{i}].{ik}",
                                "value": _fmt_value(iv),
                                "standard": _STANDARD_MAP.get(path, "—"),
                            }
                        )
                continue
            _out.append(
                {
                    "section": section_name,
                    "field": path,
                    "value": _fmt_value(v),
                    "standard": _STANDARD_MAP.get(path, "—"),
                }
            )
        return _out

    _exists = metadata_exists(store_path)
    if _exists:
        store_metadata = read_metadata(store_path)
        _all_rows = []
        for _sec in (
            "identity",
            "creator",
            "publisher",
            "temporal",
            "spatial",
            "instruments",
            "processing",
            "environment",
            "config",
            "references",
            "summaries",
        ):
            _all_rows.extend(
                _rows_for(_sec, getattr(store_metadata, _sec).model_dump(mode="json"))
            )
        full_metadata_table = mo.ui.table(
            _all_rows,
            page_size=20,
            label=f"{len(_all_rows)} populated metadata fields across all 11 sections",
        )
    else:
        store_metadata = None
        full_metadata_table = mo.md("No store metadata found.")
    return full_metadata_table, store_metadata


@app.cell
def _(full_metadata_table):
    full_metadata_table
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Exporting as STAC, inline

    All of the above is `canvod-store-metadata`'s own display format. For
    interop with STAC-based tooling (catalog browsers, `stac-fastapi`,
    `pystac`), `to_stac_collection()` converts the same metadata into a
    STAC 1.1 Collection dict **in memory** -- no file write required. A
    JSON-string convenience wrapper, `to_stac_collection_json()`, is also
    available for cases that want the serialized form directly (display,
    hashing, sending over the wire).

    ```python
    from canvod.store_metadata import to_stac_collection, to_stac_collection_json

    collection = to_stac_collection(meta)          # dict
    as_json = to_stac_collection_json(meta)         # str

    # To persist it to disk instead: write_stac_collection(store_path)
    ```
    """)
    return


@app.cell
def _(mo, store_metadata):
    from canvod.store_metadata import to_stac_collection_json

    _stac_json = (
        "No store metadata found."
        if store_metadata is None
        else to_stac_collection_json(store_metadata)
    )

    mo.md(
        f"""
    ```json
    {_stac_json}
    ```
    """
    )
    return


@app.cell
def _(mo, store):
    import contextlib
    import io

    _stats = store.get_store_stats()
    _stats_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in _stats.items())

    _buf = io.StringIO()
    with contextlib.redirect_stdout(_buf):
        store.print_tree(max_depth=2)

    mo.md(
        f"""
    ## Store stats and tree

    ```python
    stats = store.get_store_stats()
    store.print_tree(max_depth=2)
    ```

    | Stat | Value |
    |------|-------|
    {_stats_rows}

    ```text
    {_buf.getvalue()}
    ```

    `store.py` also exposes maintenance-oriented operations not
    demonstrated here since they're destructive/scheduled rather than
    exploratory: `garbage_collect()`, `expire_old_snapshots()`,
    `compact_manifests()`, `rechunk_group()`, and tag helpers
    (`create_release_tag()`, `list_tags()`, `delete_tag()`) for pinning
    permanent named snapshots.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Per-SID temporal aggregation

    When aggregating GNSS-T observations, it is essential to aggregate
    **per satellite independently**.  Each SID (satellite + band + code)
    observes the canopy from a different sky position ($\theta$, $\phi$).
    Mixing VOD or SNR values across satellites within a time bin conflates
    **spatial** variability (different view angles through the canopy)
    with **temporal** variability — producing a physically meaningless
    average.

    #### Why geometry must also be averaged

    When you average VOD over a time bin, the contributing observations
    came from many sky positions as the satellite moved.  The aggregated
    geometry ($\theta$, $\phi$) should be the **centroid** (mean) of those
    positions — not the first observation's position, which is an arbitrary
    pick that doesn't represent the average.

    #### Recommended: `TemporalAggregate`

    The `TemporalAggregate` operation (from `canvod-ops`) handles all of
    this correctly — it groups by `(time_bin, sid)` before computing the
    mean or median, and averages geometry coords per-SID:

    ```python
    from canvod.ops import TemporalAggregate

    op = TemporalAggregate(freq="1min", method="mean")
    ds_agg, result = op(ds)
    # Each SID is aggregated independently within each 1-minute bin.
    # Coordinates (phi, theta) are also averaged per-SID (centroid).
    # sid-only coords (e.g. sv, band) are preserved unchanged.
    ```

    #### Quick-look: `store.safe_temporal_aggregate()`

    For interactive exploration, the store provides a convenience method:

    ```python
    ds_agg = store.safe_temporal_aggregate("canopy_01", freq="1D")
    ```

    This uses xarray's `.resample()` which preserves the `sid` dimension
    (each satellite is aggregated independently).  For production
    analyses, prefer `TemporalAggregate`.

    #### Anti-pattern: naive resampling

    A plain `ds.resample(epoch="1D").mean()` is correct only when
    variables are already spatial averages (e.g. hemispheric mean VOD).
    It should **not** be used on raw per-satellite observations.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Exporting data

    Data can be exported from Icechunk to standard formats:

    ```python
    # Export to NetCDF
    with store.readonly_session(branch="main") as session:
        ds = xr.open_zarr(session.store, group="canopy_01", consolidated=False)
        ds.load()  # Load into memory
    ds.to_netcdf("canopy_01.nc")

    # Export to CSV (small datasets)
    df = ds["SNR"].to_dataframe()
    df.to_csv("snr_values.csv")

    # Export to Parquet (via Polars)
    import polars as pl
    df = pl.from_pandas(ds.to_dataframe().reset_index())
    df.write_parquet("observations.parquet")
    ```

    For large datasets, use Dask-backed lazy loading to avoid
    memory issues:

    ```python
    with store.readonly_session(branch="main") as session:
        ds = xr.open_zarr(session.store, group="canopy_01",
                          consolidated=False, chunks={"epoch": 10000})
        # Process in chunks without loading everything
        daily_mean = ds.resample(epoch="1D").mean().compute()
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    **Previous**: [17 — Batch Processing](./17_workflow_batch_processing.py)
    | **Next**: [19 — Grid Exploration](./19_grid_exploration.py)

    *canVODpy — Apache 2.0*
    """)
    return


if __name__ == "__main__":
    app.run()
