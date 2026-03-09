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
    # canvodpy — Four API Levels

    canvodpy exposes the same processing pipeline at four abstraction levels,
    from one-line convenience functions to composable pure functions suitable
    for Airflow DAGs.

    | Level | Style | Best for |
    |---|---|---|
    | **L1** | Convenience functions | Quick scripts, demos |
    | **L2** | Object-oriented (`Site`, `Pipeline`) | Interactive notebooks |
    | **L3** | Fluent workflow (deferred execution) | Complex pipelines, DAG planning |
    | **L4** | Pure functions | Airflow, functional composition |

    This notebook demonstrates all four levels on the same one-hour RINEX
    dataset from Rosalia (DOY 2025-001).

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
def _(Path):
    _root = Path(__file__).resolve().parent.parent
    _test_data = _root / "packages" / "canvod-readers" / "tests" / "test_data" / "valid"
    _base = _test_data / "rinex_v3_04" / "01_Rosalia"
    CANOPY_DIR = _base / "02_canopy" / "01_GNSS" / "01_raw" / "25001"
    REFERENCE_DIR = _base / "01_reference" / "01_GNSS" / "01_raw" / "25001"
    AUX_DATA_DIR = _test_data / "aux_data"
    CANOPY_FILE = sorted(CANOPY_DIR.glob("*.rnx"))[0]
    REFERENCE_FILE = sorted(REFERENCE_DIR.glob("*.rnx"))[0]

    return AUX_DATA_DIR, CANOPY_DIR, CANOPY_FILE, REFERENCE_DIR, REFERENCE_FILE


# ===========================================================================
# Level 4 — Functional API
# ===========================================================================


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Level 4: Functional API

    Pure functions with no shared state.  Each function takes data in,
    returns data out.  Designed for Airflow XCom serialisation and
    functional composition.

    ```python
    from canvodpy.functional import (
        read_rinex,
        augment_with_ephemeris,
        calculate_vod,
    )
    ```
    """
    )


@app.cell
def _(AUX_DATA_DIR, CANOPY_FILE, REFERENCE_FILE, mo):
    from canvodpy.functional import augment_with_ephemeris, read_rinex
    from canvodpy.functional import calculate_vod as calculate_vod_fn

    # Step 1: Read
    canopy_l4 = read_rinex(CANOPY_FILE)
    reference_l4 = read_rinex(REFERENCE_FILE)

    # Step 2: Extract position & augment
    from canvod.auxiliary import ECEFPosition
    from canvod.readers import Rnxv3Obs

    _reader = Rnxv3Obs(fpath=CANOPY_FILE)
    _cp = _reader.header.approx_position
    canopy_pos = ECEFPosition(
        x=_cp[0].magnitude, y=_cp[1].magnitude, z=_cp[2].magnitude
    )

    _aug_kwargs = dict(
        receiver_position=canopy_pos,
        source="final", agency="COD", date="2025001",
        aux_data_dir=AUX_DATA_DIR,
    )
    canopy_aug_l4 = augment_with_ephemeris(canopy_l4, **_aug_kwargs)
    reference_aug_l4 = augment_with_ephemeris(reference_l4, **_aug_kwargs)

    # Step 3: VOD
    vod_l4 = calculate_vod_fn(canopy_aug_l4, reference_aug_l4)

    mo.md(f"""
### L4 Result

| Step | Output |
|---|---|
| Read | {canopy_l4.sizes['epoch']} epochs × {canopy_l4.sizes['sid']} SIDs |
| Augment | +`theta`, +`phi` ({sum(1 for v in canopy_aug_l4.data_vars if v in ('theta','phi'))} new vars) |
| VOD | {vod_l4.sizes['epoch']} epochs × {vod_l4.sizes['sid']} SIDs |

Each step is a standalone function — no classes, no config objects.
""")

    return (
        ECEFPosition, Rnxv3Obs,
        augment_with_ephemeris, calculate_vod_fn, canopy_pos,
        canopy_aug_l4, canopy_l4, read_rinex,
        reference_aug_l4, reference_l4, vod_l4,
    )


# ===========================================================================
# Level 3 — Fluent Workflow
# ===========================================================================


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Level 3: Fluent Workflow

    Chainable, deferred-execution API.  Steps are collected into a plan;
    execution happens when you call a terminal method (`.result()`,
    `.to_store()`, `.plot()`).

    ```python
    import canvodpy

    vod = (canvodpy.workflow("Rosalia")
        .read("2025001")
        .augment(source="final", agency="COD")
        .vod("canopy_01", "reference_01")
        .result())
    ```

    Use `.explain()` to inspect the plan without executing it.
    """
    )


@app.cell
def _(mo):
    mo.md(
        r"""
    ### Plan Inspection

    The fluent API lets you build and inspect execution plans before running
    them — useful for debugging complex pipelines.

    ```python
    plan = (canvodpy.workflow("Rosalia")
        .read("2025001")
        .augment()
        .vod("canopy_01", "reference_01")
        .explain())

    # Returns list of step dicts:
    # [{"step": "read", "args": {"date": "2025001"}},
    #  {"step": "augment", "args": {"source": "final"}},
    #  {"step": "vod", "args": {"canopy": "canopy_01", ...}}]
    ```
    """
    )


# ===========================================================================
# Level 2 — Object-Oriented
# ===========================================================================


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Level 2: Object-Oriented API

    The `Site` and `Pipeline` classes wrap configuration and resource
    management.  They read from `config/sites.yaml` automatically.

    ```python
    from canvodpy import Site, Pipeline

    site = Site("Rosalia")
    print(site.receivers)       # Configured receivers
    print(site.vod_analyses)    # VOD analysis pairs

    pipeline = site.pipeline(n_workers=4)
    data = pipeline.process_date("2025001")
    vod = pipeline.calculate_vod("canopy_01", "reference_01", "2025001")
    ```

    The `Site` object provides access to stores, receivers, and the
    `VodComputer` for bulk processing.
    """
    )


@app.cell
def _(mo):
    mo.md(
        r"""
    ### Site Properties

    ```python
    site = Site("Rosalia")

    site.receivers          # dict of all receivers
    site.active_receivers   # only active receivers
    site.vod_analyses       # configured VOD pairs
    site.rinex_store        # Icechunk store for RINEX data
    site.vod_store          # Icechunk store for VOD results
    site.vod                # VodComputer for bulk processing
    ```
    """
    )


# ===========================================================================
# Level 1 — Convenience
# ===========================================================================


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Level 1: Convenience Functions

    One-liner functions for common tasks.  They read config, set up
    resources, process, and return results — all in one call.

    ```python
    from canvodpy import process_date, calculate_vod, preview_processing

    # Process all receivers for a date
    data = process_date("Rosalia", "2025001")

    # Compute VOD for a specific pair
    vod = calculate_vod("Rosalia", "canopy_01", "reference_01", "2025001")

    # Preview what would happen (no execution)
    plan = preview_processing("Rosalia")
    ```

    These are wrappers around L2 — they create a `Site` and `Pipeline`
    internally, process, and clean up.
    """
    )


# ===========================================================================
# Comparison
# ===========================================================================


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Level Comparison

    | Aspect | L1 | L2 | L3 | L4 |
    |---|---|---|---|---|
    | **Lines of code** | 1 | 3–5 | 5–8 | 10–15 |
    | **Config required** | Yes | Yes | Yes | No |
    | **State management** | Automatic | Per-site | Deferred plan | None |
    | **Parallelism** | Auto (Dask) | Configurable | Configurable | Manual |
    | **Airflow-ready** | No | No | No | Yes |
    | **Plan inspection** | No | Preview only | Full `.explain()` | N/A |
    | **Store integration** | Auto | Via `site.rinex_store` | `.to_store()` | Manual |

    ### When to use which level

    - **L1** — Quick exploration, demos, teaching
    - **L2** — Interactive notebooks, iterative research
    - **L3** — Production pipelines with plan inspection
    - **L4** — Airflow/Prefect DAGs, unit testing, functional composition
    """
    )


# ===========================================================================
# L4 File-based API (Airflow)
# ===========================================================================


@app.cell
def _(mo):
    mo.md(
        r"""
    ## L4 Bonus: File-Based API for Airflow

    Every L4 function has a `_to_file` variant that serialises results to
    disk, returning the file path as a string — compatible with Airflow XCom.

    ```python
    from canvodpy.functional import (
        read_rinex_to_file,
        calculate_vod_to_file,
    )

    # Each task writes to a file and returns the path
    canopy_path = read_rinex_to_file("canopy.rnx", "/tmp/canopy.nc")
    sky_path = read_rinex_to_file("sky.rnx", "/tmp/sky.nc")
    vod_path = calculate_vod_to_file(canopy_path, sky_path, "/tmp/vod.nc")
    ```

    This enables building Airflow DAGs where each task is a pure function
    with file-based I/O — no shared memory between workers.
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
