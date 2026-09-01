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
# canvod-store = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-store", rev = "baa78d0abf04fc28be9f2ac68aca17a5d1da6dc5" }
# canvod-store-metadata = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-store-metadata", rev = "baa78d0abf04fc28be9f2ac68aca17a5d1da6dc5" }
# canvod-ops = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-ops", rev = "baa78d0abf04fc28be9f2ac68aca17a5d1da6dc5" }
# canvodpy = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "canvodpy", rev = "baa78d0abf04fc28be9f2ac68aca17a5d1da6dc5" }
#
# [tool.marimo.opengraph]
# title = "18 · Store Operations"
# description = "Read, write, branch, and query Icechunk stores. Covers temporal aggregation, store snapshots, metadata queries, and the operational pipeline layer."
# ///

import marimo

__generated_with = "0.21.1"
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
    return (store, store_path)


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Native rich rendering

    `MyIcechunkStore` defines `_repr_html_()` (via
    `canvod.store.viewer.add_rich_display_to_store`), so marimo (and
    Jupyter) render it as a formatted summary automatically -- no
    `print()` or manual formatting needed. Just place a bare `store`
    reference as a cell's last expression:
    """
    )
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

        _info_rows = []
        for _v in list(_root.data_vars)[:5]:
            _da = _root[_v]
            _info_rows.append(f"| `{_v}` | `{_da.dtype}` | `{_da.dims}` |")

        _table = f"""
    | Variable | Dtype | Dimensions |
    |----------|-------|------------|
    {chr(10).join(_info_rows)}
    """
    else:
        _table = "Store has no groups yet."

    mo.md(
        f"""
    ## Reading data

    ```python
    with store.readonly_session(branch="main") as session:
        ds = xr.open_zarr(session.store, group="canopy_01", consolidated=False)
    ```

    Read-only sessions provide a consistent snapshot: even if another
    process is writing to the store concurrently, your view remains
    unchanged until the session is closed.

    **Root dataset**:

    {_table}
    """
    )
    return


# ---------------------------------------------------------------------------
# Section: commit history, before
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Commit history -- before

    Every write operation creates a commit. `get_history()` returns the
    full ancestry as dicts (`snapshot_id`, `commit_msg`, `written_at`,
    `parent_ids`) -- the `snapshot_id`s are the actual coordinates used
    for branching and time travel further down.
    """
    )
    return


@app.cell
def _(mo, store):
    def history_table(branch="main", limit=10):
        _rows = []
        for _h in store.get_history(branch=branch, limit=limit):
            _msg = _h.get("commit_msg", "---")[:50]
            _ts = str(_h.get("written_at", "---"))[:19]
            _sid = _h.get("snapshot_id", "")[:8]
            _rows.append(f"| `{_sid}` | `{_ts}` | {_msg} |")
        if not _rows:
            return "No commits found."
        return f"""
| Snapshot | Timestamp | Message |
|----------|-----------|---------|
{chr(10).join(_rows)}
"""

    _table_before = history_table()

    mo.md(
        f"""
    ```python
    history = store.get_history(branch="main", limit=10)
    ```

    {_table_before}
    """
    )
    return (history_table,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Commit graph

    `plot_commit_graph()` delegates to icechunk's native
    `repo.ancestry_graph()` and renders as an SVG diagram directly in the
    notebook (or as colored text via `print()` in a terminal).
    """
    )
    return


@app.cell
def _(store):
    store.plot_commit_graph()
    return


# ---------------------------------------------------------------------------
# Section: branching, hands-on
# ---------------------------------------------------------------------------


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
    mo.md(
        f"""
    **Branches now**: {", ".join(f"`{b}`" for b in store.get_branch_names())}

    `{demo_branch}` points at the same snapshot as `main` -- no data was
    copied.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Writing a new group on the branch

    A small synthetic dataset, built inline (not real GNSS data) purely
    to demonstrate `write_initial_group()` without touching any of the
    real ingested groups. Written to the `demo/scratch` branch, so
    `main` is completely unaffected.
    """
    )
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
    mo.md(
        f"""
    **Groups on `{demo_branch}`**: {
        ", ".join(f"`{g}`" for g in store.get_group_names(branch=demo_branch)[demo_branch])
    }

    **Groups on `main`**: {
        ", ".join(f"`{g}`" for g in store.list_groups(branch="main"))
    } -- unchanged, `write_initial_group()` on a branch never touches `main`.

    (`{demo_group}` on `{demo_branch}` is a small synthetic dataset built
    inline purely to demonstrate the write path -- not real GNSS data.)
    """
    )
    return


# ---------------------------------------------------------------------------
# Section: commit history, after
# ---------------------------------------------------------------------------


@app.cell
def _(demo_branch, history_table, mo):
    _table_after = history_table(branch=demo_branch, limit=10)

    mo.md(
        f"""
    ## Commit history -- after

    `{demo_branch}`'s history now has one more commit than `main`'s (the
    write we just did); `main`'s own history (shown further up) is
    completely unchanged -- branch isolation, not just naming.

    ```python
    store.get_history(branch="{demo_branch}", limit=10)
    ```

    {_table_after}
    """
    )
    return


# ---------------------------------------------------------------------------
# Section: time travel
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Section: deleting a branch
# ---------------------------------------------------------------------------


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
    """
    )
    return


# ---------------------------------------------------------------------------
# Section: three-layer deduplication
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Section: store creation (concept reference)
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
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
    """
    )
    return


# ---------------------------------------------------------------------------
# Section: metadata ledger
# ---------------------------------------------------------------------------


@app.cell
def _(mo, store):
    _groups = store.list_groups()
    _meta_info = "No groups with metadata ledger found."

    if _groups:
        _group = _groups[0]
        try:
            with store.readonly_session() as _session:
                _meta = store.read_metadata_table(_session, _group)
            _n_files = len(_meta)
            _meta_info = (
                f"Group `{_group}` has **{_n_files}** files in its metadata ledger."
            )
        except (KeyError, FileNotFoundError):
            _meta_info = f"Group `{_group}` exists but has no metadata ledger (store was not created via the full pipeline)."

    mo.md(
        f"""
    ## Metadata ledger

    Each group maintains a metadata ledger recording which files have
    been ingested:

    ```python
    with store.readonly_session() as session:
        meta = store.read_metadata_table(session, "canopy_01")
    # Returns: Polars DataFrame with rinex_hash, start, end, fname, etc.
    ```

    {_meta_info}

    The ledger stores:

    | Field | Description |
    |-------|-------------|
    | `rinex_hash` | SHA-256 hash (16-char truncation) |
    | `start` / `end` | Temporal extent of the file |
    | `fname` | Original filename |
    | `canonical_name` | Standardised name via `FilenameMapper` |
    | `written_at` | Ingestion timestamp |

    This is the foundation of the three-layer deduplication system:
    before writing, the pipeline checks the ledger for hash matches
    and temporal overlaps.
    """
    )
    return


# ---------------------------------------------------------------------------
# Section: store-wide metadata (canvod-store-metadata)
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Store-wide metadata

    Distinct from the per-file metadata ledger above: `canvod-store-metadata`
    attaches rich DataCite/ACDD/STAC provenance to the *store itself*
    (identity, creator, environment, software versions, processing
    parameters -- see notebook 09 for the full schema). The `canvodpy`
    CLI writes this automatically on every run; reading it back from our
    live store:
    """
    )
    return


@app.cell
def _(mo, store_path):
    from canvod.store_metadata import format_metadata, metadata_exists, read_metadata

    _exists = metadata_exists(store_path)
    _report = (
        "No store metadata found."
        if not _exists
        else format_metadata(read_metadata(store_path), section="identity")
    )

    mo.md(
        f"""
    ```python
    from canvod.store_metadata import metadata_exists, read_metadata, format_metadata

    if metadata_exists(store_path):
        meta = read_metadata(store_path)
        print(format_metadata(meta, section="identity"))
    ```

    **Metadata present**: `{_exists}`

    ```text
    {_report}
    ```

    See notebook 09 for the full 11-section schema and multi-standard
    validation (`validate_all()`).
    """
    )
    return


# ---------------------------------------------------------------------------
# Section: store stats and tree
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Section: per-SID temporal aggregation
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Section: exporting data
# ---------------------------------------------------------------------------


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
