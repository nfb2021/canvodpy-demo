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
    # canvod-store — Versioned GNSS Data Storage

    The **canvod-store** package manages GNSS observation and VOD datasets
    in **Icechunk** stores — a git-like versioned storage layer built on
    Zarr v3.  Every write is an atomic commit with a snapshot ID, enabling
    full reproducibility and rollback.

    This notebook demonstrates creating a store, writing RINEX data,
    reading it back, and inspecting the metadata ledger.

    ---

    *Nicolas F. Bader, CLIMERS — TU Wien*
    *Licensed under Apache 2.0.  Provided "as is" without warranty of any kind.*
    """
    )


@app.cell
def _():
    from pathlib import Path

    return (Path,)


@app.cell
def _():
    from _paths import ROSALIA_CANOPY_DIR

    RINEX_DIR = ROSALIA_CANOPY_DIR / "25001"
    RINEX_FILES = sorted(RINEX_DIR.glob("*.rnx"))[:4]

    return RINEX_DIR, RINEX_FILES


# ---------------------------------------------------------------------------
# Parse files
# ---------------------------------------------------------------------------


@app.cell
def _(RINEX_FILES):
    import xarray as xr

    from canvod.readers import Rnxv3Obs

    _readers = [Rnxv3Obs(fpath=f) for f in RINEX_FILES]
    datasets = [r.to_ds() for r in _readers]

    return Rnxv3Obs, datasets, xr


@app.cell
def _(RINEX_FILES, datasets, mo):
    mo.md(f"""
## Parsed {len(datasets)} RINEX Files

| # | File | Epochs | SIDs |
|---|---|---|---|
""" + "\n".join(
        f"| {i+1} | `{f.name}` | {ds.sizes['epoch']:,} | {ds.sizes['sid']:,} |"
        for i, (f, ds) in enumerate(zip(RINEX_FILES, datasets))
    ))


# ---------------------------------------------------------------------------
# Create store
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Creating an Icechunk Store

    `create_rinex_store()` initialises a new Icechunk repository with
    compression and chunking settings optimised for GNSS observation data.

    ```python
    from canvod.store import create_rinex_store

    store = create_rinex_store(Path("/tmp/demo_store"))
    ```
    """
    )


@app.cell
def _(Path):
    import tempfile

    from canvod.store import create_rinex_store

    _store_dir = Path(tempfile.mkdtemp()) / "demo_rinex_store"
    store = create_rinex_store(_store_dir)

    return create_rinex_store, store, tempfile


# ---------------------------------------------------------------------------
# Write data
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Writing Data

    Each RINEX file is written as a separate operation.  The first write
    creates the group; subsequent writes append along the `epoch` dimension.

    The store tracks every ingested file in a **metadata ledger** — a Zarr
    group storing file hashes, temporal ranges, and commit IDs.
    """
    )


@app.cell
def _(datasets, store, xr):
    _combined = xr.concat(datasets, dim="epoch")

    store.write_initial_group(
        dataset=_combined,
        group_name="canopy_01",
    )


@app.cell
def _(mo, store):
    _groups = store.list_groups()
    _info = store.get_group_info("canopy_01")

    mo.md(f"""
## Store Contents

| Property | Value |
|---|---|
| Groups | {', '.join(f'`{g}`' for g in _groups)} |
| Dimensions | {_info.get('dimensions', '?')} |
| Variables | {', '.join(f'`{v}`' for v in _info.get('variables', []))} |
| Temporal range | {_info.get('temporal_info', {}).get('start', '?')} — {_info.get('temporal_info', {}).get('end', '?')} |
| Epoch count | {_info.get('temporal_info', {}).get('count', '?'):,} |
""")


# ---------------------------------------------------------------------------
# Read back
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Reading Data

    `read_group()` returns a lazy (Dask-backed) xarray Dataset — data is
    only loaded into memory when accessed.  For deduplication-aware reads,
    use `read_group_deduplicated()`.
    """
    )


@app.cell
def _(mo, store):
    ds_read = store.read_group("canopy_01")
    mo.md(f"""
Read back: **{ds_read.sizes['epoch']:,}** epochs × **{ds_read.sizes['sid']:,}** SIDs
(Dask-backed: `{type(ds_read['SNR'].data).__name__}`)
""")

    return (ds_read,)


# ---------------------------------------------------------------------------
# Store tree
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Store Structure

    The store is a Zarr v3 hierarchy managed by Icechunk.  Use `print_tree()`
    or the rich HTML viewer to inspect the structure.

    ```
    /                          ← root (store-level attrs)
    └── canopy_01/             ← receiver group
        ├── SNR                ← observation variable
        ├── epoch              ← time coordinate
        ├── sid                ← signal ID coordinate
        ├── sv, system, band…  ← derived coordinates
        └── metadata/
            └── table/         ← ingest ledger (hashes, ranges)
    ```
    """
    )


# ---------------------------------------------------------------------------
# Root attributes
# ---------------------------------------------------------------------------


@app.cell
def _(mo, store):
    _attrs = store.get_root_attrs()
    _rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in _attrs.items()) if _attrs else "| *(none)* | |"

    mo.md(f"""
## Root Attributes

Store-level attributes are set on the Zarr root group.

| Key | Value |
|---|---|
{_rows}
""")


# ---------------------------------------------------------------------------
# Versioning
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Git-Like Versioning

    Every `commit()` creates an immutable snapshot.  You can:

    - **Branch** — create parallel timelines
    - **Tag** — name important snapshots (e.g. releases)
    - **Time-travel** — read any historical snapshot by ID

    ```python
    # List branches
    store.get_branch_names()

    # Read from a specific branch
    ds = store.read_group("canopy_01", branch="experiment_v2")
    ```

    This makes GNSS data processing fully reproducible — every pipeline run
    is traceable to a specific store state.
    """
    )


# ---------------------------------------------------------------------------
# Guardrails
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Ingest Guardrails

    The store prevents duplicate or overlapping data through a three-layer
    deduplication system:

    1. **Hash match** — skip files already ingested (same file hash)
    2. **Temporal overlap** — reject files whose time range overlaps existing data
    3. **Intra-batch overlap** — detect overlaps within a single batch

    This ensures data integrity even when reprocessing or resuming interrupted
    pipelines.
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
