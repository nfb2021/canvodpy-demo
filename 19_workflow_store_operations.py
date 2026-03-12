import marimo

__generated_with = "0.12.0"
app = marimo.App(width="medium", app_title="Store Operations", css_file="canvod_nordic.css")


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Store Operations

    This notebook demonstrates common Icechunk store operations beyond
    basic read/write: branching, history navigation, metadata inspection,
    and data export.

    These operations use the `MyIcechunkStore` API from `canvod-store`
    directly, providing low-level access to the versioned storage layer.

    ---

    """
    )

    return (mo,)


@app.cell
def _():
    from pathlib import Path

    from _paths import STORES_DIR

    return Path, STORES_DIR


# ---------------------------------------------------------------------------
# Section: opening and inspecting
# ---------------------------------------------------------------------------


@app.cell
def _(STORES_DIR, mo):
    from canvod.store import MyIcechunkStore

    store_path = STORES_DIR / "rosalia_rinex"
    store = MyIcechunkStore(store_path=store_path)

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
    | **Branches** | {', '.join(f'`{b}`' for b in _branches)} |
    | **Groups** | {', '.join(f'`{g}`' for g in _groups) if _groups else '(empty)'} |
    | **Source format** | `{_attrs.get('source_format', 'unknown')}` |

    The `source_format` root attribute indicates whether data
    originated from RINEX or SBF files.
    """
    )

    return MyIcechunkStore, store, store_path


# ---------------------------------------------------------------------------
# Section: reading data from store
# ---------------------------------------------------------------------------


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

    return (xr,)


# ---------------------------------------------------------------------------
# Section: commit history
# ---------------------------------------------------------------------------


@app.cell
def _(mo, store):
    _history = store.get_history(branch="main", limit=10)

    _rows = []
    for _h in _history:
        _msg = _h.get("message", "---")[:50]
        _ts = str(_h.get("timestamp", "---"))[:19]
        _rows.append(f"| `{_ts}` | {_msg} |")

    _table = f"""
    | Timestamp | Message |
    |-----------|---------|
    {chr(10).join(_rows)}
    """ if _rows else "No commits found."

    mo.md(
        f"""
    ## Commit history

    Every write operation creates a commit.  The history is navigable
    like Git:

    ```python
    history = store.get_history(branch="main", limit=10)
    for commit in history:
        print(f"{{commit['timestamp']}}: {{commit['message']}}")
    ```

    {_table}
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: branching
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Branching for experiments

    Branches enable experimental analyses without affecting the main
    data:

    ```python
    # Create a branch and write experimental data
    with store.writable_session(branch="experiment_v1") as session:
        # Write data ...
        session.commit("experimental VOD with 5-degree grid")

    # Read from the experiment branch
    with store.readonly_session(branch="experiment_v1") as session:
        ds = xr.open_zarr(session.store, consolidated=False)

    # List all branches
    branches = store.get_branch_names()

    # Delete when done
    # store.delete_branch("experiment_v1")
    ```

    Branches share storage with `main` through Icechunk's
    copy-on-write mechanism: only modified chunks are duplicated.
    Creating a branch is nearly instant regardless of store size.
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
            _meta_info = f"Group `{_group}` has **{_n_files}** files in its metadata ledger."
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
# Section: exporting data
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
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

    **Previous**: [18 — Batch Processing](./18_workflow_batch_processing.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
