# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvodpy",
#   "marimo>=0.21.1",
# ]
#
# [tool.uv.sources]
# canvodpy = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "canvodpy", rev = "6aa534fb8d78251c5640857361505d98a9b7dfb9" }
#
# [tool.marimo.opengraph]
# title = "14 · Site Pipeline"
# description = "Process a full GNSS-T site with Site().pipeline().process_range() -- the same code path the canvodpy CLI runs. Combines configuration, file discovery, storage, and VOD retrieval in a production-ready workflow."
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium", app_title="Site Pipeline", css_file="canvod_nordic.css"
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Site Pipeline

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/14_site_pipeline.py)

    `Site(...).pipeline()` is canvodpy's Python-native surface for running
    the pipeline — the exact same code path the `canvodpy run` CLI wraps
    internally. Use it directly when you need scripted control: looping
    over sites, embedding a run inside a notebook, or customising resource
    limits per invocation.

    ```python
    from canvodpy import Site

    site = Site("my_site")

    with site.pipeline(n_workers=4) as pipe:
        for date_key, datasets in pipe.process_range("2025001", "2025010"):
            print(f"{date_key}: {list(datasets)}")
    ```

    `process_range()` is a generator: it discovers files, augments with
    ephemeris, writes to the Icechunk store, and yields one
    `(date_key, datasets)` pair per processed day — this is what the CLI's
    reporter loop consumes to show live progress.

    Once data is ingested, `site.vod` (a `VodComputer`) gives finer-grained
    control over VOD computation as a separate stage — covered below.

    ---

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
    ## VodComputer — VOD as a separate stage

    `site.vod` offers two computation strategies for when VOD retrieval is
    decoupled from ingestion (e.g. ingest nightly, recompute VOD weekly):

    ```python
    from canvodpy import Site

    site = Site("my_site")
    vod = site.vod  # VodComputer instance
    ```

    | Property | Description |
    |----------|-------------|
    | `site` | Parent `Site` object |
    | `calculator` | VOD calculator type (default: `"tau_omega"`) |
    | `rechunk` | Optional rechunk parameters for store reads |

    ### Strategy 1: `compute_day()` — inline

    ```python
    # Load data first, e.g. via pipe.process_range()
    for date_key, datasets in pipe.process_range("2025001", "2025001"):
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

    # Stage 1: nightly ingestion (runs via cron or Airflow --
    # or just `canvodpy run --site my_site` on a schedule)
    with site.pipeline(n_workers=4) as pipe:
        for date_key, datasets in pipe.process_range("2025032", "2025032"):
            pass  # data is now in the Icechunk RINEX store

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

    **Previous**: [13 — Running the Pipeline (CLI)](./13_cli_pipeline.py)
    | **Next**: [15 — Functional API](./15_functional_api.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
