# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvodpy>=0.2.2",
#   "marimo>=0.21.1",
# ]
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium", app_title="L1 — Convenience API", css_file="canvod_nordic.css"
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Level 1 — Convenience API

    The L1 API provides single-function entry points for the most
    common tasks.  Configuration is loaded automatically from the
    monorepo's `config/` directory.

    This notebook demonstrates how to use L1 for quick data
    exploration without constructing any objects or managing state.

    ---

    """
    )

    return (mo,)


# ---------------------------------------------------------------------------
# Section: process_date
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## `process_date()` — read and augment a day of data

    ```python
    import canvodpy

    # Process all receivers at a site for one day
    data = canvodpy.process_date("my_site", "2025001")
    # Returns: {"canopy_01": xr.Dataset, "reference_01": xr.Dataset}

    # Override defaults
    data = canvodpy.process_date(
        "my_site", "2025001",
        keep_vars=["SNR"],          # Only keep SNR variable
        aux_agency="COD",           # Use CODE final orbits
        n_workers=2,                # Limit parallelism
    )
    ```

    | Parameter | Type | Default | Description |
    |-----------|------|---------|-------------|
    | `site` | `str` | required | Site name from `sites.yaml` |
    | `date` | `str` | required | YYYYDOY format (e.g. `"2025001"`) |
    | `keep_vars` | `list[str] \| None` | `None` | Variables to retain (None = all) |
    | `aux_agency` | `str \| None` | `None` | Override ephemeris agency |
    | `n_workers` | `int \| None` | `None` | Override worker count |

    The function reads all RINEX/SBF files for the specified date,
    augments them with satellite geometry, and returns one
    `xr.Dataset` per receiver.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: calculate_vod
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## `calculate_vod()` — end-to-end VOD retrieval

    ```python
    import canvodpy

    vod = canvodpy.calculate_vod(
        "my_site",          # Site name
        "canopy_01",        # Canopy receiver
        "reference_01",     # Reference receiver
        "2025001",          # Date (YYYYDOY)
    )
    # Returns: xr.Dataset with VOD, phi, theta
    ```

    This single call performs the entire pipeline:

    1. Read RINEX/SBF files for both receivers
    2. Augment with satellite geometry (SP3/CLK or broadcast)
    3. Align datasets on shared `(epoch, sid)` pairs
    4. Compute transmittance and VOD

    The receiver names must match entries in `sites.yaml`.  The
    function uses the `vod_analyses` configuration to determine
    which receiver pair to use.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: preview_processing
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## `preview_processing()` — dry run

    ```python
    import canvodpy

    plan = canvodpy.preview_processing("my_site")
    ```

    Returns a dictionary describing what the pipeline would do:

    - Which receivers would be processed
    - How many files are available per receiver
    - Which VOD analyses are configured
    - Storage paths and strategies

    This is useful for verifying configuration before committing to
    a long-running pipeline.  No data is read or processed.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: when to use L1
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## When to use L1

    **Use L1 when:**

    - You want to quickly inspect data for a single day
    - You are writing a notebook and want minimal boilerplate
    - You trust the defaults in `config/processing.yaml`

    **Move to L2 when:**

    - You need to process a date range
    - You want to override grid type, resolution, or calculator
    - You need Dask client management (Pipeline context manager)

    **Move to L4 when:**

    - You need each step as a standalone function
    - You are building an Airflow/Prefect DAG
    - You need file-based intermediate results
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

    **Previous**: [12 — API Overview](./12_api_overview.py)
    | **Next**: [14 — L2 Fluent Workflow](./14_api_level2_fluent.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
