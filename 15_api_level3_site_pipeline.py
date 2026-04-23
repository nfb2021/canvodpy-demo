# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvodpy>=0.2.2",
#   "marimo>=0.21.1",
# ]
#
# [tool.marimo.opengraph]
# title = "15 · L3 — Site Pipeline"
# description = "Process a full GNSS-T site with Site().pipeline().process_range(). Combines configuration, file discovery, storage, and VOD retrieval in a production-ready workflow."
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium", app_title="L3 — Site Pipeline", css_file="canvod_nordic.css"
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Level 3 — Site Pipeline

    The L3 API provides direct access to the `VodComputer` for
    fine-grained control over VOD computation.  It is designed for
    **production workflows** where data ingestion and VOD retrieval
    run as separate stages.

    The key abstraction is `VodComputer`, accessible via `site.vod`.
    It offers two computation strategies:

    - **`compute_day()`**: inline computation from pre-loaded datasets
    - **`compute_bulk()`**: batch computation from the Icechunk store

    —

    """
    )

    return (mo,)


# ---------------------------------------------------------------------------
# Section: VodComputer
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## VodComputer

    ```python
    from canvodpy import Site

    site = Site("my_site")
    vod = site.vod  # VodComputer instance
    ```

    | Property | Description |
    |----------|-------------|
    | `site` | Parent `Site` object |
    | `calculator` | VOD calculator type (default: `"tau_omega_zeroth"`) |
    | `rechunk` | Optional rechunk parameters for store reads |

    ### Strategy 1: `compute_day()` — inline

    ```python
    # Load data first (via Pipeline or L4 functions)
    datasets = pipe.process_date("2025001")

    # Compute VOD from loaded datasets
    result = vod.compute_day(
        datasets,               # Dict of receiver datasets
        "main",                 # Analysis name from vod_analyses config
        write=True,             # Write result to VOD store
    )
    ```

    `compute_day()` calls `.load()` on the Dask-backed datasets to
    bring them into memory, then runs the VOD calculation.  This is
    the fastest path for single-day processing.

    ### Strategy 2: `compute_bulk()` — from store

    ```python
    from datetime import datetime

    result = vod.compute_bulk(
        "main",
        start=datetime(2025, 1, 1),
        end=datetime(2025, 1, 31),
        write=True,
    )
    ```

    `compute_bulk()` reads canopy and reference data from the Icechunk
    RINEX store for the specified date range, then computes VOD.  This
    decouples ingestion from retrieval: data can be ingested nightly,
    and VOD recomputed weekly or on demand.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: VOD analyses configuration
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## VOD analyses configuration

    The `vod_analyses` section in `sites.yaml` defines receiver pairs
    for VOD computation:

    ```yaml
    sites:
      my_site:
        receivers:
          canopy_01:
            type: canopy
            directory: 02_canopy
          reference_01:
            type: reference
            directory: 01_reference
            scs_from: canopy_01
        vod_analyses:
          main:
            canopy_receiver: canopy_01
            reference_receiver: reference_01
            description: "Primary canopy-reference pair"
          secondary:
            canopy_receiver: canopy_02
            reference_receiver: reference_01
            description: "Second canopy at different location"
    ```

    Each analysis is a `VodAnalysisConfig` with three fields:

    | Field | Description |
    |-------|-------------|
    | `canopy_receiver` | Name of the canopy receiver (must exist in `receivers`) |
    | `reference_receiver` | Name of the reference receiver |
    | `description` | Human-readable description |

    Multiple analyses can share the same reference receiver —
    a common setup when one open-sky receiver serves several
    below-canopy stations.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: production workflow
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Production workflow pattern

    A typical production deployment separates ingestion from retrieval:

    ```python
    from canvodpy import Site

    site = Site("my_site")

    # Stage 1: nightly ingestion (runs via cron or Airflow)
    with site.pipeline(n_workers=4) as pipe:
        data = pipe.process_date("2025032")
        # Data is now in the Icechunk RINEX store

    # Stage 2: weekly VOD computation (triggered separately)
    result = site.vod.compute_bulk(
        "main",
        start=datetime(2025, 1, 27),
        end=datetime(2025, 2, 2),
        write=True,  # Write to VOD store
    )
    ```

    This pattern has several advantages:

    - **Idempotent ingestion**: re-running a day is safe (deduplication guards)
    - **Recomputable VOD**: if the algorithm changes, VOD can be recomputed
      from the store without re-reading raw files
    - **Independent scheduling**: ingestion and retrieval can run on
      different schedules and different machines
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
    —

    **Previous**: [14 — L2 Fluent Workflow](./14_api_level2_fluent.py)
    | **Next**: [16 — L4 Functional](./16_api_level4_functional.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
