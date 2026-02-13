"""GNSS VOD Processing Pipeline - Timing Diagnostics Demo

This notebook demonstrates the GNSS Vegetation Optical Depth (VOD) processing pipeline
with detailed timing analysis for one day of data (2025-01-01, DOY 001).

The notebook walks through:
1. Site configuration and data loading
2. RINEX data processing per receiver
3. Timing analysis and performance metrics
4. Data visualization and quality checks

Now using the new clean canvodpy API! ✨

Author: Nicolas François Bader
Date: 2025-01-21
"""

import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")


@app.cell
def _():
    """# 🛰️ GNSS VOD Processing Pipeline - Timing Diagnostics

    This interactive notebook demonstrates the complete GNSS VOD processing workflow
    with performance timing analysis for **one day of data: 2025-001 (January 1, 2025)**.

    ## What is GNSS VOD?

    GNSS Vegetation Optical Depth (VOD) uses signal attenuation from satellite navigation
    systems to measure vegetation water content. As GNSS signals pass through vegetation
    canopies, they are attenuated proportionally to the vegetation's water content.

    ## Processing Pipeline Overview

    ```
    RINEX Files → Parse → Quality Control → Signal Processing → VOD Calculation → Storage
    ```

    ## This Demo

    We'll process data from the **Rosalia field site** with 4 receivers:
    - `canopy_01`, `canopy_02`: Under vegetation canopy
    - `reference_01`, `reference_02`: Open sky reference

    ## New Clean API ✨

    This demo uses the **new canvodpy API** - much simpler than before!

    ```python
    from canvodpy import Site, Pipeline

    # Simple, clean, Pythonic
    site = Site("Rosalia")
    pipeline = site.pipeline()
    data = pipeline.process_date("2025001")
    ```

    Let's begin! 👇
    """
    return


@app.cell
def _():
    """## 📦 Import Required Packages

    We use the new **canvodpy API** - modern, clean, and Pythonic!
    """
    import time

    import marimo as mo

    # Visualization
    import matplotlib.pyplot as plt
    import pandas as pd

    # ✨ NEW: Clean canvodpy API
    from canvodpy import Site

    mo.md("""
    ✅ Packages imported successfully!

    **Using the new canvodpy API:**
    - `Site` - Site management (receivers, stores)
    - `Pipeline` - Processing orchestration

    Much cleaner than the old gnssvodpy imports! 🎉
    """)
    return Site, mo, pd, plt, time


@app.cell
def _(mo):
    """## ⚙️ Configuration

    Set up the processing parameters for our diagnostic run.
    """
    # Target date for processing
    TARGET_DATE = "2025001"  # January 1, 2025 (Year + Day of Year)

    # Site configuration
    SITE_NAME = "Rosalia"

    # Expected receivers at this site
    EXPECTED_RECEIVERS = ["canopy_01", "reference_01"]

    config_display = mo.md(f"""
    ### Configuration Summary

    | Parameter | Value |
    |-----------|-------|
    | **Site** | {SITE_NAME} |
    | **Date** | {TARGET_DATE} (Jan 1, 2025) |
    | **Receivers** | {len(EXPECTED_RECEIVERS)} receivers |

    **Receiver List:**
    {mo.as_html(mo.tree([{r: []} for r in EXPECTED_RECEIVERS]))}
    """)

    config_display
    return SITE_NAME, TARGET_DATE


@app.cell
def _(SITE_NAME, Site, mo, time):
    """## 🏗️ Initialize Research Site

    Create the GNSS research site object which manages:
    - Receiver configurations
    - Data storage (Icechunk-based)
    - Processing pipelines

    ### New API Example

    ```python
    site = Site("Rosalia")  # That's it! Clean and simple.
    ```
    """
    mo.md("Initializing site... ⏳")

    init_start = time.time()

    try:
        # ✨ NEW: Clean API - just one line!
        site = Site(SITE_NAME)

        init_time = time.time() - init_start

        # Get active receivers
        active_receivers = sorted(site.active_receivers.keys())

        site_info = mo.md(f"""
        ✅ **Site initialized successfully!** (took {init_time:.2f}s)

        ### Site Information

        - **Name:** {site.name}
        - **Active Receivers:** {len(active_receivers)}
        - **Storage:** Icechunk-based (lazy loading)

        **Configured Receivers:**
        {mo.as_html(mo.tree([{r: ["Type: " + site.active_receivers[r].get("type", "unknown")]} for r in active_receivers]))}

        ### API Comparison

        **Old gnssvodpy:**
        ```python
        from gnssvodpy.icechunk_manager.manager import GnssResearchSite
        site = GnssResearchSite(site_name="Rosalia")
        ```

        **New canvodpy:**
        ```python
        from canvodpy import Site
        site = Site("Rosalia")  # So much cleaner! ✨
        ```
        """)

    except Exception as e:
        site_info = mo.md(f"""
        ❌ **Failed to initialize site!**

        Error: `{e!s}`

        Please check your site configuration in `research_sites_config.py`.
        """)
        site = None
        active_receivers = []

    site_info
    return (site,)


@app.cell
def _(mo, site, time):
    """## 🔄 Create Pipeline

    The pipeline manages the complete processing workflow:
    1. Discovers available RINEX files for each receiver
    2. Coordinates processing across multiple receivers
    3. Tracks timing and performance metrics
    4. Handles data storage and checkpointing

    ### New API Example

    ```python
    pipeline = site.pipeline()  # Create from site
    # Or directly:
    pipeline = Pipeline("Rosalia")
    ```
    """
    if site is None:
        pipeline_info = mo.md("⚠️ Cannot create pipeline - site initialization failed")
        pipeline = None
    else:
        mo.md("Creating pipeline... ⏳")

        pipeline_start = time.time()

        # try:
        # ✨ NEW: Clean API - create pipeline from site
        pipeline = site.pipeline(
            aux_agency="COD",  # Use CODE analysis center
            n_workers=12,  # Parallel processing
        )

        pipeline_time = time.time() - pipeline_start

        pipeline_info = mo.md(f"""
        ✅ **Pipeline created!** (took {pipeline_time:.2f}s)

        ### Pipeline Configuration

        - **Site:** {site.name}
        - **Receivers:** {len(site.active_receivers)}
        - **Aux Agency:** COD (Center for Orbit Determination)
        - **Workers:** 12 (parallel processing)

        The pipeline is ready to process RINEX data!

        ### API Comparison

        **Old gnssvodpy:**
        ```python
        from gnssvodpy.processor.pipeline_orchestrator import PipelineOrchestrator
        orchestrator = PipelineOrchestrator(site=site, dry_run=False)
        ```

        **New canvodpy:**
        ```python
        pipeline = site.pipeline()  # That's it! ✨
        ```
        """)

        # except Exception as e:
        #     pipeline_info = mo.md(f"""
        #     ❌ **Failed to create pipeline!**

        #     Error: `{str(e)}`
        #     """)
        #     pipeline = None

    pipeline_info
    return (pipeline,)


@app.cell
def _(TARGET_DATE, mo, pipeline, time):
    """## 🚀 Process Target Date

    Now we'll process one day of RINEX data through the complete pipeline.
    This includes:

    1. **Data Discovery:** Find RINEX files for the target date
    2. **Parsing:** Read RINEX observation files
    3. **Quality Control:** Filter bad observations
    4. **Signal Processing:** Calculate signal metrics
    5. **Storage:** Save processed data to Icechunk store

    ### What to Expect

    Processing typically takes:
    - **Per receiver:** 10-30 seconds (depends on file size)
    - **Total for 4 receivers:** ~1-2 minutes

    ### New API Example

    ```python
    # Old way: Complex generator with manual timing
    for date, datasets, timings in orchestrator.process_by_date(...):
        ...

    # New way: Simple function call!
    data = pipeline.process_date("2025001")
    ```
    """
    if pipeline is None:
        process_info = mo.md("⚠️ Cannot process - pipeline not initialized")
        datasets = {}
        processing_time = 0
        receiver_timings = {}
    else:
        mo.md(f"Processing {TARGET_DATE}... ⏳ (this may take 1-2 minutes)")

        process_start = time.time()

        try:
            # ✨ NEW: Simple function call - returns processed data!
            datasets = pipeline.process_date(TARGET_DATE)

            processing_time = time.time() - process_start

            # Calculate per-receiver timing (estimated)
            receiver_timings = {
                receiver: processing_time / len(datasets)
                for receiver in datasets.keys()
            }

            process_info = mo.md(f"""
            ✅ **Processing complete!** (took {processing_time:.1f}s)

            ### Processing Results

            - **Date:** {TARGET_DATE}
            - **Receivers processed:** {len(datasets)}
            - **Total time:** {processing_time:.1f}s
            - **Avg per receiver:** {processing_time / len(datasets):.1f}s

            **Processed Receivers:**
            {mo.as_html(mo.tree([{r: [f"Dataset dims: {dict(ds.dims)}"]} for r, ds in datasets.items()]))}

            ### API Comparison

            **Old gnssvodpy:**
            ```python
            for date_key, datasets, timings in orchestrator.process_by_date(
                keep_vars=KEEP_RNX_VARS,
                start_from="2025001",
                end_at="2025001"
            ):
                # Complex generator pattern
                pass
            ```

            **New canvodpy:**
            ```python
            data = pipeline.process_date("2025001")  # Done! ✨
            ```
            """)

        except Exception as e:
            process_info = mo.md(f"""
            ❌ **Processing failed!**

            Error: `{e!s}`

            **Common issues:**
            - RINEX files not found for this date
            - Auxiliary data (ephemeris/clocks) not available
            - Permissions or disk space issues
            """)
            datasets = {}
            receiver_timings = {}

    process_info
    return datasets, receiver_timings


@app.cell
def _(datasets, mo, pd, receiver_timings):
    """## 📊 Timing Analysis

    Let's analyze the performance metrics for each receiver.
    """
    if not datasets:
        timing_display = mo.md("⚠️ No data to analyze - processing failed")
    else:
        # Create timing dataframe
        timing_data = []
        for receiver, timing in receiver_timings.items():
            ds = datasets[receiver]
            timing_data.append(
                {
                    "Receiver": receiver,
                    "Type": receiver.split("_")[0],
                    "Time (s)": timing,
                    "Epochs": len(ds.epoch) if "epoch" in ds.dims else 0,
                    "Satellites": len(ds.sv) if "sv" in ds.dims else 0,
                }
            )

        timing_df = pd.DataFrame(timing_data)

        # Summary statistics
        total_time = timing_df["Time (s)"].sum()
        avg_time = timing_df["Time (s)"].mean()
        total_epochs = timing_df["Epochs"].sum()

        timing_display = mo.md(f"""
        ### ⏱️ Timing Summary

        | Metric | Value |
        |--------|-------|
        | **Total Time** | {total_time:.1f}s |
        | **Average per Receiver** | {avg_time:.1f}s |
        | **Total Epochs** | {total_epochs:,} |
        | **Throughput** | {total_epochs / total_time:.0f} epochs/s |

        ### Per-Receiver Breakdown

        {mo.as_html(timing_df)}
        """)

    timing_display
    return (timing_df,)


@app.cell
def _(mo, plt, timing_df):
    """## 📈 Visualization: Processing Time by Receiver"""
    if "timing_df" not in dir() or timing_df.empty:
        viz_display = mo.md("⚠️ No data to visualize")
    else:
        fig, ax = plt.subplots(figsize=(10, 6))

        colors = [
            "#2ecc71" if "canopy" in r.lower() else "#3498db"
            for r in timing_df["Receiver"]
        ]

        ax.barh(timing_df["Receiver"], timing_df["Time (s)"], color=colors)
        ax.set_xlabel("Processing Time (seconds)", fontsize=12)
        ax.set_ylabel("Receiver", fontsize=12)
        ax.set_title("Processing Time by Receiver", fontsize=14, fontweight="bold")
        ax.grid(axis="x", alpha=0.3)

        # Add value labels
        for i, (receiver, time_val) in enumerate(
            zip(timing_df["Receiver"], timing_df["Time (s)"])
        ):
            ax.text(time_val, i, f"  {time_val:.1f}s", va="center", fontsize=10)

        plt.tight_layout()

        viz_display = mo.md(f"""
        ### Processing Time Comparison

        - 🟢 **Green:** Canopy receivers (under vegetation)
        - 🔵 **Blue:** Reference receivers (open sky)

        {mo.as_html(fig)}
        """)

        plt.close(fig)

    viz_display


@app.cell
def _(datasets, mo):
    """## 📊 Data Quality Summary

    Quick check of the processed datasets.
    """
    if not datasets:
        quality_display = mo.md("⚠️ No data to check")
    else:
        quality_info = []

        for receiver, ds in datasets.items():
            quality_info.append(
                {
                    "receiver": receiver,
                    "epochs": len(ds.epoch) if "epoch" in ds.dims else 0,
                    "satellites": len(ds.sv) if "sv" in ds.dims else 0,
                    "variables": len(ds.data_vars),
                    "size_mb": ds.nbytes / 1024 / 1024,
                }
            )

        quality_display = mo.md(f"""
        ### Dataset Summary

        {
            mo.as_html(
                mo.tree(
                    [
                        {
                            q["receiver"]: [
                                f"Epochs: {q['epochs']:,}",
                                f"Satellites: {q['satellites']}",
                                f"Variables: {q['variables']}",
                                f"Size: {q['size_mb']:.1f} MB",
                            ]
                        }
                        for q in quality_info
                    ]
                )
            )
        }

        ### Next Steps

        Now that data is processed and stored in Icechunk, you can:

        1. **Calculate VOD:** Use `pipeline.calculate_vod()` to compute vegetation optical depth
        2. **Visualize:** Use `canvod.viz` tools for 2D/3D hemisphere plots
        3. **Analyze:** Extract time series, compare receivers, quality filtering
        4. **Export:** Save results for external analysis
        """)

    quality_display


@app.cell
def _(mo):
    """## 🎯 Summary

    This demo showed the complete GNSS VOD processing workflow using
    the **new clean canvodpy API**.
    """
    mo.md("""
    ### ✨ API Improvements

    **Before (gnssvodpy):**
    ```python
    from gnssvodpy.icechunk_manager.manager import GnssResearchSite
    from gnssvodpy.processor.pipeline_orchestrator import PipelineOrchestrator
    from gnssvodpy.globals import KEEP_RNX_VARS

    site = GnssResearchSite(site_name="Rosalia")
    orchestrator = PipelineOrchestrator(site=site, dry_run=False)

    for date_key, datasets, timings in orchestrator.process_by_date(
        keep_vars=KEEP_RNX_VARS, start_from="2025001", end_at="2025001"
    ):
        # Process data...
        pass
    ```

    **After (canvodpy):**
    ```python
    from canvodpy import Site, Pipeline

    site = Site("Rosalia")
    pipeline = site.pipeline()
    data = pipeline.process_date("2025001")
    ```

    ### Key Benefits

    ✅ **Simpler** - 3 lines instead of 10+
    ✅ **Cleaner** - No long import paths
    ✅ **More Pythonic** - Follows pandas/requests style
    ✅ **Same Performance** - Uses proven gnssvodpy logic internally
    ✅ **Better Documentation** - Type hints, docstrings

    ### Learn More

    - **API Levels:** Use `process_date()` for quick tasks, or `Site`/`Pipeline` for more control
    - **Documentation:** Check the API reference and examples
    - **Migration Guide:** Converting from gnssvodpy to canvodpy

    **Happy processing! 🛰️**
    """)


if __name__ == "__main__":
    app.run()
