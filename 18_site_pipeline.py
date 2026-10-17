# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvodpy",
#   "marimo>=0.21.1",
#   "pyyaml==6.0.3",
# ]
#
# [tool.uv.sources]
# canvodpy = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "canvodpy", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
#
# [tool.marimo.opengraph]
# title = "18 · Site Pipeline"
# description = "Process a full GNSS-T site with Site().pipeline().process_range() -- the same code path the canvodpy CLI runs. Combines configuration, file discovery, storage, and VOD retrieval in a production-ready workflow."
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium", app_title="Site Pipeline", css_file="canvod_nordic.css",
    html_head_file="canvod_head.html"
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

    # Site Pipeline

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/18_site_pipeline.py?mode=edit)

    `Site(...).pipeline()` is canvodpy's Python-native surface for running
    the pipeline, the exact same code path the `canvodpy run` CLI wraps
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
    `(date_key, datasets)` pair per processed day; this is what the CLI's
    reporter loop consumes to show live progress.

    The first run creates the site's stores. Before that,
    `site.gnss_store` and `site.vod_store` raise a `FileNotFoundError`;
    `site.gnss_store_path` and `site.vod_store_path` say where the run
    puts them.

    Once data is ingested, `site.vod` (a `VodComputer`) gives finer-grained
    control over VOD computation as a separate stage, covered below.

    ---

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

    mo.md(
        f"""
    ## A real run on the demo data

    This cell runs the site pipeline on the Rosalia demo data that
    `demo_data()` downloaded (DOY 2025-001, canopy + reference), using the
    settings written above. It writes the site's GNSS store into a fresh
    temporary folder, not the demo cache.

    ```python
    from canvodpy import Site

    site = Site("rosalia_v3_04")
    data = site.pipeline(n_workers=2).process_date("2025001")
    ```

    | Property | Value |
    |----------|-------|
    | **Site** | `{site}` |
    | **GNSS store** | `{site.gnss_store_path}` |
    | **Receivers** | {", ".join(f"`{r}`" for r in site.receivers)} |
    | **Analyses** | {", ".join(f"`{a}`" for a in site.vod_analyses)} |
    """
    )
    return site


# ---------------------------------------------------------------------------
# Section: VodComputer
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## VodComputer: VOD as a separate stage

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

    ### Strategy 1: `compute_day()`, inline

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

    ### Strategy 2: `compute_bulk()`, from store

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
    GNSS store for the specified date range, then computes VOD.  This
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

    The `vod_analyses` entry of each site in `config/canvod-settings.yaml`
    defines receiver pairs for VOD computation:

    ```yaml
    sites:
      my_site:
        receivers:
          canopy_01:
            type: canopy
            directory: 02_canopy
          canopy_02:
            type: canopy
            directory: 03_canopy
          reference_01:
            type: reference
            directory: 01_reference
            paired_canopies: all
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

    Multiple analyses can share the same reference receiver,
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
            pass  # data is now in the GNSS store

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
    ---

    **Previous**: [17 · API Overview](./17_api_overview.py)
    | **Next**: [19 · Single-Day Workflow](./19_workflow_single_day.py)

    *canVODpy · Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
