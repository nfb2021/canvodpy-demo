# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvod-store>=0.2.3",
#   "marimo>=0.21.1",
# ]
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium", app_title="Icechunk Store", css_file="canvod_nordic.css"
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Versioned GNSS Data Storage with Icechunk

    The **canvod-store** package provides a versioned, transactional storage
    layer built on **Icechunk** — a Git-like version control system for
    N-dimensional arrays (Zarr v3).

    Each observation dataset is stored as a Zarr group inside an Icechunk
    repository.  The store provides:

    - **Append-only ingestion** with three-layer deduplication
      (file hash, temporal overlap, intra-batch overlap)
    - **Branching and tagging** for experimental analyses
    - **Commit history** with full audit trail
    - **Session management** (read-only and writable contexts)
    - **Metadata ledger** tracking which files have been ingested

    ---

    **Test data**: a pre-built Icechunk store for DOY 2025-001
    with canopy and reference receivers.

    """
    )

    return (mo,)


@app.cell
def _():
    from pathlib import Path

    from _paths import STORES_DIR

    return Path, STORES_DIR


# ---------------------------------------------------------------------------
# Section: opening a store
# ---------------------------------------------------------------------------


@app.cell
def _(STORES_DIR, mo):
    from canvod.store import MyIcechunkStore

    store_path = STORES_DIR / "rosalia_rinex"
    store = MyIcechunkStore(store_path=store_path)

    _branches = store.get_branch_names()
    _groups = store.list_groups()

    mo.md(
        f"""
    ## Opening a store

    ```python
    from canvod.store import MyIcechunkStore

    store = MyIcechunkStore(store_path=Path("stores/my_site_rinex"))
    ```

    | Property | Value |
    |----------|-------|
    | **Path** | `{store_path}` |
    | **Branches** | {", ".join(f"`{b}`" for b in _branches)} |
    | **Groups** | {", ".join(f"`{g}`" for g in _groups) if _groups else "(empty)"} |
    """
    )

    return MyIcechunkStore, store, store_path


# ---------------------------------------------------------------------------
# Section: reading data
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Reading data

    The `readonly_session()` context manager opens a snapshot of the store
    at a specific branch.  Within the session, groups can be opened as
    lazy `xarray.Dataset` objects backed by Dask arrays.
    """
    )

    return


@app.cell
def _(mo, store):
    import xarray as xr

    _groups = store.list_groups()

    if _groups:
        with store.readonly_session(branch="main") as _session:
            _root = xr.open_zarr(_session.store, consolidated=False)
        _info = f"Root dataset: `{dict(_root.sizes)}`"
    else:
        _info = "Store has no groups yet."

    mo.md(
        f"""
    ### Read-only session

    ```python
    with store.readonly_session(branch="main") as session:
        ds = xr.open_zarr(session.store, group="canopy_01", consolidated=False)
    ```

    {_info}
    """
    )

    return (xr,)


# ---------------------------------------------------------------------------
# Section: commit history
# ---------------------------------------------------------------------------


@app.cell
def _(mo, store):
    _history = store.get_history(branch="main", limit=5)

    if _history:
        _rows = []
        for _h in _history:
            _msg = _h.get("commit_msg", "---")[:60]
            _ts = str(_h.get("written_at", "---"))[:19]
            _rows.append(f"| `{_ts}` | {_msg} |")
        _table = f"""
    | Timestamp | Message |
    |-----------|---------|
    {chr(10).join(_rows)}
    """
    else:
        _table = "No commits found."

    mo.md(
        f"""
    ## Commit history

    Every write operation creates a commit with a message and timestamp.
    The history is navigable like Git:

    ```python
    history = store.get_history(branch="main", limit=10)
    ```

    {_table}
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: branching
# ---------------------------------------------------------------------------


@app.cell
def _(mo, store):
    _branches = store.get_branch_names()

    mo.md(
        f"""
    ## Branching

    Branches enable experimental analyses without affecting the main data:

    ```python
    # Create a branch from main
    with store.writable_session(branch="experiment_v1") as session:
        # Write experimental data ...
        session.commit("experimental VOD with different grid")
    ```

    **Current branches**: {", ".join(f"`{b}`" for b in _branches)}

    This is analogous to Git branching: the `main` branch contains the
    canonical dataset, while feature branches hold exploratory results.
    Branches can be merged or deleted without affecting `main`.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: deduplication
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
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
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: store creation
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

    ### Writing data

    ```python
    with store.writable_session(branch="main") as session:
        # First write to a group
        store.write_initial_group(ds, group_name="canopy_01")

        # Subsequent writes append along the epoch dimension
        store.append_to_group(ds_new, group_name="canopy_01", append_dim="epoch")
    ```

    The `append_to_group()` method handles all deduplication, epoch
    alignment, and SID padding automatically.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: root attributes
# ---------------------------------------------------------------------------


@app.cell
def _(mo, store):
    _attrs = store.get_root_attrs()

    _rows = []
    for _k, _v in list(_attrs.items())[:10]:
        _val = str(_v)[:80]
        _rows.append(f"| `{_k}` | `{_val}` |")

    _table = (
        f"""
    | Key | Value |
    |-----|-------|
    {chr(10).join(_rows)}
    """
        if _rows
        else "No root attributes set."
    )

    mo.md(
        f"""
    ## Root attributes

    Store-level metadata is stored in root Zarr attributes.  The
    `source_format` attribute indicates whether the data originated
    from RINEX or SBF files.

    ```python
    attrs = store.get_root_attrs()
    store.set_root_attrs({{"source_format": "rinex3"}})
    ```

    {_table}
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

    **Previous**: [07 — VOD Retrieval](./07_vod_retrieval.py)
    | **Next**: [09 — Store Metadata](./09_store_metadata.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
