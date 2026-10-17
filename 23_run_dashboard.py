# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvodpy",
#   "marimo>=0.23.13",
# ]
#
# [tool.uv.sources]
# canvodpy = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "canvodpy", rev = "caddb63b88618cde329b126e036cf0f5c05c1c7e" }
#
# [tool.marimo.opengraph]
# title = "23 · Run Dashboard"
# description = "canVODpy's run dashboard on an example run history: nine runs of the same week with 1 to 126 workers, their progress, time per stage and per day, CPU, memory and disk, problems, and the comparison by label."
# ///

import marimo

__generated_with = "0.23.13"
app = marimo.App(
    width="medium", app_title="Run Dashboard", css_file="canvod_nordic.css",
    html_head_file="canvod_head.html"
)


# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    <p align="center" class="canvod-logo">
      <img class="canvod-logo-light" src="https://raw.githubusercontent.com/nfb2021/canvodpy/main/docs/assets/logo/canvodpy_logo_bright_mode.svg" alt="canVODpy logo" width="280">
      <img class="canvod-logo-dark" src="https://raw.githubusercontent.com/nfb2021/canvodpy/main/docs/assets/logo/canvodpy_logo_dark_mode.svg" alt="canVODpy logo" width="280">
    </p>

    # Run Dashboard

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/23_run_dashboard.py?mode=edit)

    Every `canvodpy run` records what it does in a **run history**, a
    SQLite file in the log folder: when each run started and ended, which
    receiver-days it wrote, how long each stage took, the CPU, memory and
    free disk during the run, and every warning and error. The **run
    dashboard** shows it. On your own runs you open it with

    ```bash
    canvodpy dashboard                  # the log folder of canvod-settings.yaml
    canvodpy dashboard --logs-dir logs  # or any log folder
    canvodpy run --dashboard            # or next to a run, live
    ```

    Below is the same dashboard, not a copy, on an example run history:
    nine runs of the same seven days of two receivers, processed with 1, 2,
    4, 8, 16, 32, 64 and 126 worker processes, labeled `pilot-w001` to
    `pilot-w126`, plus a warm-up run whose orbit download failed for three
    days (its problems are listed). The history is anonymized: the person
    and site are canVODpy's test persona, and the machine is an example
    machine.

    ---
    """
    )
    return (mo,)


# ---------------------------------------------------------------------------
# Example run history
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvodpy import demo_data

    # Downloaded on first use, then read from the cache.
    log_dir = demo_data("run_history") / "run_history"
    mo.md(f"The example log folder: `{log_dir}`")
    return (log_dir,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ## The dashboard

    Pick a run in the list to see its page. **Compare runs by label** at the
    end groups the runs by label; with one run per label here, it compares
    the worker counts stage by stage. The **Time axis** switch shows the
    durations on a logarithmic axis, which spreads short and long stages
    apart. **Download** gives the data behind the page as a zip of CSV
    files.
    """
    )
    return


@app.cell
def _(log_dir):
    import os

    from canvodpy.cli.dashboards import performance

    # The dashboard reads its log folder from this variable, the one
    # `canvodpy dashboard --logs-dir` sets.
    os.environ["CANVODPY_PERF_LOG_DIR"] = str(log_dir)
    return (performance,)


@app.cell
async def _(performance):
    dashboard = await performance.app.embed()
    dashboard.output
    return


if __name__ == "__main__":
    app.run()
