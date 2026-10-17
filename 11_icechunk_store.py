# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvod-auxiliary",
#   "canvod-config",
#   "canvod-grids",
#   "canvod-ops",
#   "canvod-preflight",
#   "canvod-readers",
#   "canvod-store",
#   "canvod-store-metadata",
#   "canvod-utils",
#   "canvod-viz",
#   "canvod-vod",
#   "canvodpy",
#   "pyyaml>=6.0",
#   "marimo>=0.21.1",
#   "xarray==2026.9.0",
# ]
#
# [tool.uv.sources]
# canvod-auxiliary = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-auxiliary", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-config = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-config", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-grids = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-grids", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-ops = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-ops", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-preflight = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-preflight", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-readers = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-readers", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-store = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-store", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-store-metadata = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-store-metadata", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-utils = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-utils", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-viz = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-viz", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-vod = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-vod", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvodpy = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "canvodpy", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
#
# [tool.marimo.opengraph]
# title = "11 · Icechunk Store"
# description = "Write, read, and version GNSS-T datasets in a cloud-native Icechunk/Zarr store. Explore branching, snapshots, and deduplication guardrails."
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(
    width="medium",
    app_title="Icechunk Store",
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

    # Versioned GNSS Data Storage with Icechunk

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/11_icechunk_store.py?mode=edit)

    The **canvod-store** package provides a versioned, transactional storage
    layer built on **Icechunk**, a Git-like version control system for
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

    **Test data**: this notebook builds the store live, at run time, by
    running the site pipeline against real Rosalia RINEX v3.04 data
    for DOY 2025-001 (canopy + reference receivers); no pre-built store
    fixture is shipped.

    """
    )
    return (mo,)


@app.cell
def _():
    from canvodpy import demo_data

    root = demo_data("rinex")
    root = demo_data("aux")
    return root


@app.cell
def _(root):
    import os
    import shutil
    import tempfile
    from pathlib import Path

    import yaml

    from canvod.utils import testing

    work = Path(tempfile.mkdtemp(prefix="canvodpy_demo_"))
    config_dir = work / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    aux_data_dir = work / "aux_data"
    aux_data_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(root / "aux_data" / "01_SP3", aux_data_dir / "01_SP3")
    shutil.copytree(root / "aux_data" / "02_CLK", aux_data_dir / "02_CLK")

    settings = {
        "sites": {
            "rosalia_v3_04": {
                "store_description": (
                    "Reference GNSS-T store for the Rosalia beech forest site,"
                    " built live from real RINEX v3.04 raw data (DOY 2025-001)."
                ),
                "description": (
                    "Beech forest GNSS-T research site, reference test dataset."
                ),
                "country": "AT",
                "latitude": 47.7,
                "longitude": 16.3,
                "altitude_m": 680.0,
                "gnss_site_data_root": str(root / "rinex_v3_04" / "01_Rosalia"),
                "receivers": {
                    "reference_01": {
                        "type": "reference",
                        "directory": "01_reference/01_GNSS/01_raw",
                        "reader_format": "rinex3",
                        "paired_canopies": "all",
                        "description": "Rosalia reference receiver (test data)",
                        "metadata": {
                            "receiver_model": "Septentrio AsteRx-SB3 Pro",
                            "firmware_version": "4.14.4",
                        },
                    },
                    "canopy_01": {
                        "type": "canopy",
                        "directory": "02_canopy/01_GNSS/01_raw",
                        "reader_format": "rinex3",
                        "description": "Rosalia canopy receiver (test data)",
                        "metadata": {
                            "receiver_model": "Septentrio AsteRx-SB3 Pro",
                            "firmware_version": "4.14.4",
                        },
                    },
                },
                "vod_analyses": {
                    "canopy_01_vs_reference_01": {
                        "canopy_receiver": "canopy_01",
                        "reference_receiver": "reference_01",
                    }
                },
            }
        },
        "processing": {
            "metadata": {
                "author": testing.PERSON_NAME,
                "email": testing.PERSON_EMAIL,
                "orcid": testing.PERSON_ORCID,
                "institution": testing.INSTITUTION,
                "institution_ror": "https://ror.org/" + testing.INSTITUTION_ROR,
                "department": testing.DEPARTMENT,
                "research_group": testing.RESEARCH_GROUP,
                "website": testing.WEBSITE,
                "license": "CC-BY-4.0",
                "publisher": testing.PUBLISHER,
                "publisher_url": testing.WEBSITE,
                "naming_authority": testing.NAMING_AUTHORITY,
            },
            "references": {
                "software_repository": "https://github.com/nfb2021/canvodpy",
                "documentation": "https://github.com/nfb2021/canvodpy/tree/main/docs",
                "publications": [],
                "funding": [],
            },
            "storage": {
                "stores_root_dir": str(work / "stores"),
                "aux_data_dir": str(aux_data_dir),
                "shared_aux_cache_dir": None,
            },
            "logging": {"log_dir": str(work / "logs")},
        },
    }
    (config_dir / "canvod-settings.yaml").write_text(
        yaml.safe_dump(settings, sort_keys=False)
    )
    os.environ["CANVOD_CONFIG_DIR"] = str(config_dir)
    return work, config_dir


@app.cell
def _(mo, config_dir, root):
    from canvodpy import Site

    site = Site("rosalia_v3_04")
    data = site.pipeline(n_workers=2).process_date("2025001")
    site.vod.compute_day(data, "canopy_01_vs_reference_01", write=True)

    store = site.gnss_store
    store_path = site.gnss_store_path

    _branches = store.get_branch_names()
    _groups = store.list_groups()

    mo.md(
        f"""
    ## Opening a store

    ```python
    from canvodpy import Site

    site = Site("rosalia_v3_04")
    data = site.pipeline().process_date("2025001")
    ```

    The site pipeline ran on the demo data that `demo_data()` downloaded,
    and wrote the store into a fresh temporary folder. Each notebook run
    uses its own temporary folder, so the stores are throwaway and the
    demo cache is only ever read, never written to.

    | Property | Value |
    |----------|-------|
    | **Path** | `{store_path}` |
    | **Site** | `{store.site_name}` |
    | **Branches** | {", ".join(f"`{b}`" for b in _branches)} |
    | **Groups** | {", ".join(f"`{g}`" for g in _groups) if _groups else "(empty)"} |

    The store knows its site from its own metadata, not from the folder
    it sits in, so moving or renaming the folder doesn't change it.

    A normal `canvodpy run` (or `site.pipeline()`) writes to both the GNSS
    and the VOD store in the same pipeline pass whenever the site config
    defines `vod_analyses` -- no separate VOD computation step is needed.
    """
    )
    return site, store


@app.cell
def _(store):
    store
    return


@app.cell
def _(site, mo):
    vod_store = site.vod_store
    vod_store_path = site.vod_store_path

    _vod_branches = vod_store.get_branch_names()
    _vod_groups = vod_store.list_groups()

    mo.md(
        f"""
    ## The VOD store

    VOD products live in a **separate** Icechunk store, sibling to the GNSS
    store above -- same `MyIcechunkStore` class, but groups are
    nested `{{calculator_name}}/{{analysis_name}}` rather than flat
    per-receiver names, since one VOD store can hold output from multiple
    retrieval algorithms.

    ```python
    vod_store = MyIcechunkStore(store_path=Path("stores/my_site_vod"), store_type="vod_store")
    ```

    | Property | Value |
    |----------|-------|
    | **Path** | `{vod_store_path}` |
    | **Branches** | {", ".join(f"`{b}`" for b in _vod_branches)} |
    | **Groups** | {", ".join(f"`{g}`" for g in _vod_groups) if _vod_groups else "(empty)"} |

    A normal `canvodpy run` writes to both stores in the same pipeline pass
    whenever the site config defines `vod_analyses` -- no separate VOD
    computation step is needed.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Reading data

    The `readonly_session()` context manager opens a snapshot of the store
    at a specific branch.  Within the session, groups can be opened as
    lazy `xarray.Dataset` objects backed by Dask arrays.
    """)
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
    return


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


@app.cell
def _(mo):
    mo.md(r"""
    ## Three-layer deduplication

    The store prevents duplicate data from entering the repository through
    three independent checks:

    1. **File hash match**: the SHA-256 hash of each RINEX/SBF file is
       recorded in the metadata ledger.  If the same file is ingested
       again, it is skipped, and the ledger records the skip.

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

    You don't create a store yourself: `canvodpy run` creates a site's
    stores when it first writes data, together with their metadata and
    the Icechunk settings in `processing.icechunk`. Opening a store never
    creates one, so a mistyped path fails with a `FileNotFoundError`
    instead of leaving an empty store behind:

    ```python
    from canvod.store import open_gnss_store, open_vod_store

    # Raw observation data
    gnss_store = open_gnss_store(Path("/data/my_site/rinex"))

    # VOD products
    vod_store = open_vod_store(Path("/data/my_site/vod"))
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

    `canvodpy run` does not append. In a new GNSS store each processing
    day gets one block of empty epoch slots, and every file is written
    into its own slots, so writing a file again replaces it.
    `append_to_group()` refuses a group made of day blocks; use it only on
    groups you create yourself with `write_initial_group()`.
    """)
    return


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


@app.cell
def _(mo):
    mo.md(r"""
    ---

    **Previous**: [10 · VOD Retrieval](./10_vod_retrieval.py)
    | **Next**: [12 · Store Metadata](./12_store_metadata.py)

    *canVODpy · Apache 2.0*
    """)
    return


if __name__ == "__main__":
    app.run()
