import marimo

__generated_with = "0.19.10"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # canVODpy API — Level 2: Fluent Workflow

    A **chainable, deferred-execution** pipeline. Steps are recorded when
    you call them; nothing runs until you invoke a terminal method like
    `.result()` or `.plot()`.

    ## The Task

    Same as every notebook in this series:

    1. Read RINEX data for **Rosalia**, DOY **2025001**
    2. Preprocess (augment with auxiliary data)
    3. Assign hemisphere grid cells
    4. Calculate VOD for canopy_01 / reference_01

    ## API at a Glance

    ```python
    import canvodpy

    result = (canvodpy.workflow("Rosalia")
        .read("2025001")
        .preprocess()
        .grid("equal_area", angular_resolution=5.0)
        .vod("canopy_01", "reference_01")
        .result())
    ```

    | Aspect | Detail |
    |--------|--------|
    | Import | `import canvodpy` |
    | Pattern | Builder / method chaining with deferred execution |
    | Configuration | Per-step overrides via keyword arguments |
    | Best for | Interactive notebooks, exploratory analysis |
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 0 — Create the workflow
    """)
    return


@app.cell
def _():
    import canvodpy

    return (canvodpy,)


@app.cell
def _(mo):
    mo.md("""
    `canvodpy.workflow()` returns a `FluentWorkflow` with an empty
    execution plan.
    """)
    return


@app.cell
def _(canvodpy, mo):
    try:
        fw = canvodpy.workflow("Rosalia")
        site_ok = True
        mo.md(f"**Workflow created:** `{fw!r}`")
    except Exception as e:
        site_ok = False
        fw = None
        mo.md(
            f"""
            Site configuration not available (`{type(e).__name__}`).
            The examples below show the API structure.
            """
        )
    return fw, site_ok


@app.cell
def _(mo):
    mo.md("""
    ## Step 1 — Chain the pipeline

    Each method records a step in the plan **without executing it**.
    The chain returns `self`, so calls compose naturally.
    """)
    return


@app.cell
def _(fw, mo, site_ok):
    if site_ok:
        fw.read("2025001").preprocess().grid("equal_area", angular_resolution=5.0).vod(
            "canopy_01", "reference_01"
        )
        mo.md(f"**Plan recorded:** `{fw!r}`")
    else:
        mo.md(
            """
            ```python
            fw = canvodpy.workflow("Rosalia")
            fw.read("2025001")\\
              .preprocess()\\
              .grid("equal_area", angular_resolution=5.0)\\
              .vod("canopy_01", "reference_01")
            # FluentWorkflow(site='Rosalia', pending_steps=4)
            ```
            """
        )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 2 — Inspect the plan (without executing)

    `.explain()` returns the recorded steps as a list of dicts.
    Nothing is executed — no data is read, no computation happens.
    """)
    return


@app.cell
def _(fw, mo, site_ok):
    if site_ok:
        plan = fw.explain()
        mo.md(
            "\n".join(
                [
                    f"- **{s['step']}** — args={s['args']}, kwargs={s['kwargs']}"
                    for s in plan
                ]
            )
        )
    else:
        mo.md(
            """
            ```python
            plan = fw.explain()
            # [
            #   {"step": "read",       "args": ("2025001",), "kwargs": {}},
            #   {"step": "preprocess", "args": (),           "kwargs": {}},
            #   {"step": "grid",       "args": ("equal_area",), "kwargs": {"angular_resolution": 5.0}},
            #   {"step": "vod",        "args": ("canopy_01", "reference_01"), "kwargs": {}},
            # ]
            ```
            """
        )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 3 — Execute with a terminal method

    `.result()` runs all recorded steps in order, then returns the final
    data.  The plan is cleared afterwards so the workflow can be reused.

    Other terminals: `.to_store()`, `.plot()`.
    """)
    return


@app.cell
def _(fw, mo, site_ok):
    if site_ok:
        try:
            result = fw.result()
            mo.md(f"**Result type:** `{type(result).__name__}`")
        except Exception as e:
            result = None
            mo.md(
                f"Execution failed (`{type(e).__name__}: {e}`). Data may not be on disk."
            )
    else:
        result = None
        mo.md(
            """
            ```python
            result = fw.result()
            # Returns xr.Dataset (VOD) if .vod() was in the plan,
            # otherwise dict[str, xr.Dataset] of per-receiver datasets.
            ```
            """
        )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Decorator mechanics

    The fluent pattern is powered by two decorators defined in
    `canvodpy.fluent`:

    | Decorator | Effect |
    |-----------|--------|
    | `@step` | Records `(method, args, kwargs)` in `self._plan`, returns `self` |
    | `@terminal` | Replays every recorded step, clears the plan, runs the terminal |

    This means **zero computation happens during chaining** — the plan is
    just a list of tuples.  Execution is a single sequential pass triggered
    by the terminal.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Summary

    | Pro | Con |
    |-----|-----|
    | Readable, chainable one-liner | Implicit execution order |
    | `.explain()` previews without running | Less granular than functional API |
    | Reusable workflow object | Mutable internal state |
    | Per-step configuration | |

    **Next:** Open `level3_workflow.py` for the stateful VODWorkflow class.
    """)
    return


if __name__ == "__main__":
    app.run()
