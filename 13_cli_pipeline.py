# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvodpy",
#   "marimo>=0.21.1",
# ]
#
# [tool.uv.sources]
# canvodpy = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "canvodpy", rev = "baa78d0abf04fc28be9f2ac68aca17a5d1da6dc5" }
#
# [tool.marimo.opengraph]
# title = "13 · Running the Pipeline (CLI)"
# description = "canvodpy run: the recommended command-line interface for production ingestion. Covers date ranges, auto-resume, multi-site runs, dry-run previews, and the ephemeris-source/VOD-calculator flags."
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium",
    app_title="Running the Pipeline (CLI)",
    css_file="canvod_nordic.css",
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Running the Pipeline — the CLI

    `canvodpy run` is the recommended way to run production ingestion. It
    wraps the exact same code path as `Site(...).pipeline().process_range()`
    (covered in the [next notebook](./14_site_pipeline.py)), adding
    resumability and a live progress display on top.

    ```bash
    uv run canvodpy run --site Rosalia --start 2025001 --end 2025007
    ```

    ---

    """
    )

    return (mo,)


# ---------------------------------------------------------------------------
# Section: basic usage
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Basic usage

    ```bash
    # Process a specific range
    uv run canvodpy run --site Rosalia --start 2025001 --end 2025007

    # Process new data only — auto-resume from the last processed date,
    # end defaults to today. This is what you want in a cron job.
    uv run canvodpy run --site Rosalia

    # Observation ingestion only, skip VOD calculation
    uv run canvodpy run --site Rosalia --no-vod

    # Preview what would be processed, without executing anything
    uv run canvodpy run --site Rosalia --dry-run
    ```

    **Auto-resume** is the reason the CLI is recommended over calling
    `Site.pipeline()` directly for scheduled runs: omit `--start` and the
    CLI queries the Icechunk store's metadata for the latest committed
    date and resumes from there. A daily cron entry needs no date-math:

    ```
    0 3 * * * cd /path/to/canvodpy && uv run canvodpy run --site Rosalia
    ```
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: multiple sites
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Multiple sites in one invocation

    `--site` accepts one or more names, processed **sequentially**:

    ```bash
    uv run canvodpy run --site Rosalia OtherSite ThirdSite
    ```

    Each site resolves its own resume point from its own store — sites
    don't share a date range. The live progress display shows one row per
    `(site, receiver-group)` pair, known upfront, so a multi-site run
    shows the full picture from the start rather than only revealing the
    next site once the previous one finishes.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: ephemeris source and VOD calculator
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Choosing ephemeris source and VOD calculator

    ```bash
    # Override the configured ephemeris source for this run
    uv run canvodpy run --site Rosalia --ephemeris-source broadcast

    # Choose a VOD calculator (choices come from VODFactory.list_available())
    uv run canvodpy run --site Rosalia --vod-calculator tau_omega
    ```

    | Flag | Choices | Default |
    |------|---------|---------|
    | `--ephemeris-source` | `final` (agency SP3/CLK), `broadcast` (SBF SatVisibility) | from `canvod-settings.yaml` |
    | `--vod-calculator` | registered in `VODFactory` (currently `tau_omega`) | `tau_omega` |

    Both flags are one-off overrides for a single invocation — they don't
    modify `canvod-settings.yaml`. Bake in a value there once you've
    settled on it for a site.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: resources
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Resource flags

    ```bash
    uv run canvodpy run --site Rosalia --workers 8 --days-per-batch 14
    ```

    | Flag | Effect |
    |------|--------|
    | `--workers` | Number of parallel workers (default: from config's `resource_mode`) |
    | `--days-per-batch` | Number of DOYs pooled into one parallel processing wave |

    `--days-per-batch` trades responsiveness for throughput: a bigger
    batch keeps the worker pool saturated longer per invocation (fewer
    sequential aux-data-prep stalls between waves), but the live progress
    display can only advance once each batch's files finish writing — so
    very large batches on a big backfill can look quiet for a while before
    a burst of progress lands. Start small (`1`–`7`) and increase once you
    have a feel for how long a batch takes on your hardware.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: config overlay
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Config overlay

    ```bash
    uv run canvodpy run --site Rosalia --config cluster-overlay.yaml
    ```

    Applies an overlay YAML on top of the main `canvod-settings.yaml` —
    only the fields present in the overlay are changed, everything else
    is read from the main file. Useful on shared/HPC machines where
    resource limits vary per job but the base configuration is
    version-controlled.

    Any configuration value can also be overridden per-invocation via
    environment variables (`CANVOD__PROCESSING__PARAMS__DAYS_PER_BATCH=7`,
    etc.) — see the Configuration guide for the full mechanism.
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
    | **Next**: [14 — Site Pipeline](./14_site_pipeline.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
