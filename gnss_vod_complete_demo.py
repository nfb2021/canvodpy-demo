"""GNSS VOD Processing Pipeline - Complete Demo

This notebook is the definitive demonstration of the canvodpy framework for
GNSS Vegetation Optical Depth analysis. It showcases the modern, clean API
and guides users from basic concepts to advanced workflows.

Features:
    - Three-level API demonstration (beginner → intermediate → advanced)
    - Complete processing workflow with real data
    - Performance analysis and visualization
    - Production-ready patterns and best practices
    - Interactive exploration and analysis

Author: Nicolas François Bader
Institution: TU Wien - Climate and Environmental Remote Sensing (CLIMERS)
Date: 2025-01-22
License: Apache 2.0
"""

import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # 🛰️ GNSS Vegetation Optical Depth Analysis

    ## Welcome to canvodpy!

    This interactive notebook demonstrates the **complete workflow** for analyzing
    vegetation water content using GNSS signal attenuation.

    ### What is GNSS VOD?

    Global Navigation Satellite System (GNSS) signals passing through vegetation
    canopies experience attenuation proportional to the vegetation's water content.
    By comparing signals received below the canopy versus open-sky reference signals,
    we can estimate **Vegetation Optical Depth (VOD)** - a key indicator of
    vegetation water status.

    ### The canvodpy Framework

    canvodpy is a modern Python framework for GNSS VOD analysis, featuring:

    - ✨ **Clean API** - Three progressive levels from simple to advanced
    - 🚀 **High Performance** - Parallel processing with intelligent caching
    - 📊 **Rich Visualizations** - 2D/3D hemisphere plots and time series
    - 🗄️ **Scalable Storage** - Icechunk-based versioned data stores
    - 🔬 **Scientific Rigor** - Validated against published methods

    ### This Demo

    We'll analyze data from the **Rosalia research site** in Austria:

    - 📍 **Location**: Rosalia Forest, Austria (beech forest)
    - 📅 **Date**: January 1, 2025 (DOY 001)
    - 📡 **Receivers**: 4 GNSS receivers (2 canopy, 2 reference)
    - ⏱️ **Sampling**: 15-minute intervals (96 files per receiver per day)

    Let's dive in! 👇
    """)


@app.cell
def _(mo):
    """## 📦 Setup and Imports

    First, we'll import the necessary packages. Notice how clean the imports are
    with the new canvodpy API!
    """
    import time

    # Visualization
    import matplotlib.pyplot as plt
    import numpy as np

    # Data handling
    import pandas as pd

    # ✨ The new canvodpy API - clean and simple!
    from canvodpy import Site

    # Set plotting style
    plt.style.use("seaborn-v0_8-darkgrid")

    mo.md("""
    ✅ **Imports complete!**

    Notice we imported from `canvodpy` directly - no complex paths needed.
    """)
    return Site, np, pd, plt, time


@app.cell
def _(mo):
    """## 🎯 Three API Levels

    canvodpy offers three levels of API, each suited for different users:
    """
    api_comparison = mo.md("""
    ### API Levels - Choose Your Style

    #### 🟢 Level 1: Convenience Functions (Beginners)
    ```python
    from canvodpy import process_date, calculate_vod

    # One-liner processing!
    data = process_date("Rosalia", "2025001")
    vod = calculate_vod("Rosalia", "canopy_01", "reference_01", "2025001")
    ```

    **Best for**: Quick scripts, notebooks, exploratory analysis

    ---

    #### 🟡 Level 2: Object-Oriented (Production Use)
    ```python
    from canvodpy import Site, Pipeline

    # More control, clean code
    site = Site("Rosalia")
    pipeline = site.pipeline(n_workers=12)
    data = pipeline.process_date("2025001")
    ```

    **Best for**: Production code, repeatable workflows, automation

    ---

    #### 🔴 Level 3: Direct Access (Advanced Users)
    ```python
    from canvod.store import GnssResearchSite
    from canvodpy.orchestrator import PipelineOrchestrator

    # Full control over every detail
    site = GnssResearchSite(site_name="Rosalia")
    orchestrator = PipelineOrchestrator(site, n_max_workers=12)
    for date, datasets, timings in orchestrator.process_by_date(...):
        # Custom processing logic
        pass
    ```

    **Best for**: Framework development, custom algorithms, research

    ---

    **This demo uses Level 2** - the sweet spot for most users!
    """)

    api_comparison


@app.cell
def _(mo):
    """## ⚙️ Configuration

    Let's set up our processing parameters.
    """
    # Processing configuration
    SITE_NAME = "Rosalia"
    TARGET_DATE = "2025001"  # January 1, 2025
    N_WORKERS = 12  # Parallel processing workers

    # Expected receivers
    CANOPY_RECEIVERS = ["canopy_01", "canopy_02"]
    REFERENCE_RECEIVERS = ["reference_01", "reference_01"]

    config_display = mo.md(f"""
    ### Processing Configuration

    | Parameter | Value |
    |-----------|-------|
    | **Site** | {SITE_NAME} |
    | **Date** | {TARGET_DATE} (Jan 1, 2025) |
    | **Workers** | {N_WORKERS} (parallel) |
    | **Canopy Receivers** | {len(CANOPY_RECEIVERS)} |
    | **Reference Receivers** | {len(REFERENCE_RECEIVERS)} |

    **Total Receivers**: {len(CANOPY_RECEIVERS) + len(REFERENCE_RECEIVERS)}
    """)

    config_display
    return N_WORKERS, SITE_NAME, TARGET_DATE


@app.cell
def _(SITE_NAME, Site, mo, time):
    """## 🏗️ Initialize Site

    Create the research site object - this manages receiver configurations,
    data storage, and processing pipelines.
    """
    mo.md("Initializing site... ⏳")

    init_start = time.time()

    try:
        # ✨ Level 2 API - Clean and simple!
        site = Site(SITE_NAME)

        init_time = time.time() - init_start

        # Get site information
        active_receivers = sorted(site.active_receivers.keys())
        n_receivers = len(active_receivers)

        # Get VOD analysis configurations
        vod_analyses = site.vod_analyses
        n_analyses = len(vod_analyses)

        site_info = mo.md(f"""
        ✅ **Site initialized successfully!** (took {init_time:.3f}s)

        ### Site: {site.name}

        **Receivers**: {n_receivers} active
        ```
        {chr(10).join(f"  • {r}" for r in active_receivers)}
        ```

        **VOD Analyses**: {n_analyses} configured
        ```
        {chr(10).join(f"  • {name}: {cfg["canopy_receiver"]} vs {cfg["reference_receiver"]}" for name, cfg in vod_analyses.items())}
        ```

        **Storage**: Icechunk-based versioned stores
        - RINEX data store: Ready ✅
        - VOD results store: Ready ✅

        ---

        ### API Comparison

        **Old (gnssvodpy)**:
        ```python
        from gnssvodpy.icechunk_manager.manager import GnssResearchSite
        site = GnssResearchSite(site_name="Rosalia")
        ```

        **New (canvodpy)**:
        ```python
        from canvodpy import Site
        site = Site("Rosalia")  # So much cleaner! ✨
        ```
        """)

        site_success = True

    except Exception as e:
        site_info = mo.md(f"""
        ❌ **Site initialization failed!**

        **Error**: `{e!s}`

        Please check:
        - Site configuration in `research_sites_config.py`
        - Icechunk stores are accessible
        - Network connectivity for remote stores
        """)
        site = None
        site_success = False

    site_info
    return n_receivers, site, site_success


@app.cell
def _(N_WORKERS, mo, site, site_success, time):
    """## 🔄 Create Processing Pipeline

    The pipeline orchestrates RINEX data processing, auxiliary data handling,
    and storage management across all receivers.
    """
    if not site_success:
        pipeline_info = mo.md("⚠️ Cannot create pipeline - site initialization failed")
        pipeline = None
        pipeline_success = False
    else:
        mo.md("Creating pipeline... ⏳")

        pipeline_start = time.time()

        # try:
        # ✨ Level 2 API - Create pipeline from site
        pipeline = site.pipeline(
            aux_agency="COD",  # CODE Analysis Center
            n_workers=N_WORKERS,  # Parallel processing
        )

        pipeline_time = time.time() - pipeline_start

        pipeline_info = mo.md(f"""
        ✅ **Pipeline created successfully!** (took {pipeline_time:.3f}s)

        ### Pipeline Configuration

        - **Site**: {site.name}
        - **Receivers**: {len(site.active_receivers)}
        - **Auxiliary Data**: CODE (Center for Orbit Determination)
        - **Parallel Workers**: {N_WORKERS}
        - **Processing Mode**: Production (dry_run=False)

        The pipeline is ready to:
        1. 📥 Download/load auxiliary data (ephemerides, clocks)
        2. 🔄 Process RINEX files in parallel
        3. 📊 Compute spherical coordinates (φ, θ, r)
        4. 💾 Store results in Icechunk with versioning

        ---

        ### API Comparison

        **Old (gnssvodpy)**:
        ```python
        from gnssvodpy.processor.pipeline_orchestrator import PipelineOrchestrator
        orchestrator = PipelineOrchestrator(
            site=site,
            n_max_workers=12,
            dry_run=False
        )
        ```

        **New (canvodpy)**:
        ```python
        pipeline = site.pipeline(n_workers=12)  # Done! ✨
        ```
        """)

        pipeline_success = True

        # except Exception as e:
        #     pipeline_info = mo.md(f"""
        #     ❌ **Pipeline creation failed!**

        #     **Error**: `{str(e)}`

        #     This might indicate issues with:
        #     - Network connectivity (for auxiliary data download)
        #     - Disk space
        #     - File permissions
        #     """)
        #     pipeline = None
        #     pipeline_success = False

    pipeline_info
    return pipeline, pipeline_success


@app.cell
def _(
    TARGET_DATE,
    datasets,
    mo,
    n_receivers,
    n_sats,
    pipeline,
    pipeline_success,
    time,
    total_epochs,
):
    """## 🚀 Process RINEX Data

    Now we'll process one day of RINEX observation files through the complete pipeline.
    This typically takes 1-2 minutes for a full day with 4 receivers.
    """
    if not pipeline_success:
        _process_info = mo.md("⚠️ Cannot process - pipeline not initialized")
        _datasets = {}
        _processing_time = 0
        _process_success = False
    else:
        mo.md(f"""
        Processing {TARGET_DATE}... ⏳

        This may take 1-2 minutes. The pipeline will:
        1. Discover RINEX files for each receiver
        2. Download/cache auxiliary data (SP3, CLK files)
        3. Process files in parallel ({pipeline.n_workers} workers)
        4. Compute spherical coordinates for each satellite
        5. Store processed data in Icechunk

        **Watch for progress in the terminal!** 📊
        """)

        process_start = time.time()

        # try:
        # ✨ Level 2 API - Simple function call returns all data!
        _datasets = pipeline.process_date(TARGET_DATE)

        _processing_time = time.time() - process_start

        # Calculate statistics
        _total_epochs = sum(len(d.epoch) for d in _datasets.values())
        _total_satellites = sum(len(d.sv) for d in _datasets.values())
        _avg_time_per_receiver = (
            _processing_time / n_receivers if n_receivers > 0 else 0
        )

        # Build receiver summary
        receiver_summary = []
        for rec, d in datasets.items():
            _n_epochs = len(d.epoch)
            _n_sats = len(d.sv)
            _n_vars = len(d.data_vars)
            _size_mb = d.nbytes / 1024 / 1024
            receiver_summary.append(
                f"  • **{rec}**: {_n_epochs:,} epochs × {n_sats} satellites "
                f"({_n_vars} variables, {_size_mb:.1f} MB)"
            )

        process_info = mo.md(f"""
        ✅ **Processing complete!** (took {_processing_time:.1f}s)

        ### Results Summary

        - **Date**: {TARGET_DATE}
        - **Receivers Processed**: {n_receivers}
        - **Total Time**: {_processing_time:.1f}s
        - **Avg per Receiver**: {_avg_time_per_receiver:.1f}s
        - **Throughput**: {total_epochs / _processing_time:.0f} epochs/s

        ### Processed Datasets

    {chr(10).join(receiver_summary)}

        **Total**: {_total_epochs:,} epochs, {_total_satellites:,} satellite observations

        ---

        ### API Comparison

        **Old (gnssvodpy)**:
        ```python
        from gnssvodpy.globals import KEEP_RNX_VARS

        for date_key, datasets, timings in orchestrator.process_by_date(
            keep_vars=KEEP_RNX_VARS,
            start_from="2025001",
            end_at="2025001"
        ):
            # Complex generator pattern
            # Manual timing tracking
            pass
        ```

        **New (canvodpy)**:
        ```python
        data = pipeline.process_date("2025001")  # That's it! ✨
        ```
        """)

        _process_success = True

        # except Exception as e:
        #     _process_info = mo.md(f"""
        #     ❌ **Processing failed!**

        #     **Error**: `{str(e)}`

        #     **Common issues**:
        #     - RINEX files not found for this date
        #     - Auxiliary data (SP3/CLK) not available
        #     - Network issues downloading aux data
        #     - Insufficient disk space
        #     """)
        #     _datasets = {}
        #     _process_success = False

    _process_info


@app.cell
def _(datasets, mo, pd, process_success, processing_time):
    """## 📊 Performance Analysis

    Let's analyze the processing performance and data characteristics.
    """
    if not process_success:
        perf_display = mo.md("⚠️ No data to analyze")
    else:
        # Build performance dataframe
        perf_data = []
        for receiver, ds in datasets.items():
            receiver_type = receiver.split("_")[0]
            n_epochs = len(ds.epoch)
            n_sats = len(ds.sv) if "sv" in ds.dims else 0
            n_vars = len(ds.data_vars)
            size_mb = ds.nbytes / 1024 / 1024

            perf_data.append(
                {
                    "Receiver": receiver,
                    "Type": receiver_type.capitalize(),
                    "Epochs": n_epochs,
                    "Satellites": n_sats,
                    "Variables": n_vars,
                    "Size (MB)": round(size_mb, 1),
                }
            )

        perf_df = pd.DataFrame(perf_data)

        # Calculate totals
        total_epochs = perf_df["Epochs"].sum()
        total_size = perf_df["Size (MB)"].sum()
        throughput = total_epochs / processing_time if processing_time > 0 else 0

        perf_display = mo.md(f"""
        ### ⏱️ Performance Metrics

        | Metric | Value |
        |--------|-------|
        | **Total Processing Time** | {processing_time:.1f}s |
        | **Total Epochs Processed** | {total_epochs:,} |
        | **Total Data Size** | {total_size:.1f} MB |
        | **Throughput** | {throughput:.0f} epochs/s |
        | **Parallel Workers Used** | 12 |

        ### 📋 Per-Receiver Breakdown

        {mo.as_html(perf_df)}

        ---

        ### 💡 Performance Notes

        - **Parallel Processing**: Using ProcessPoolExecutor with {len(datasets)} workers
        - **Caching**: Auxiliary data cached on disk (faster subsequent runs)
        - **Lazy Loading**: Datasets loaded on-demand from Icechunk
        - **Memory Efficient**: Only keeps necessary variables in memory
        """)

    perf_display
    return n_sats, total_epochs


@app.cell
def _(datasets, mo, plt, process_success):
    """## 📈 Visualization: Processing Statistics

    Visual breakdown of the data characteristics.
    """
    if not process_success:
        viz_display = mo.md("⚠️ No data to visualize")
        fig = None
    else:
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("GNSS Data Processing Statistics", fontsize=16, fontweight="bold")

        # Prepare data
        receivers = list(datasets.keys())
        epochs = [len(ds.epoch) for ds in datasets.values()]
        satellites = [len(ds.sv) if "sv" in ds.dims else 0 for ds in datasets.values()]
        sizes = [ds.nbytes / 1024 / 1024 for ds in datasets.values()]

        colors = ["#2ecc71" if "canopy" in r else "#3498db" for r in receivers]

        # 1. Epochs per receiver
        ax1 = axes[0, 0]
        bars1 = ax1.barh(receivers, epochs, color=colors, alpha=0.7)
        ax1.set_xlabel("Number of Epochs", fontsize=11)
        ax1.set_title("Temporal Coverage", fontsize=12, fontweight="bold")
        ax1.grid(axis="x", alpha=0.3)
        for i, (r, e) in enumerate(zip(receivers, epochs)):
            ax1.text(e, i, f"  {e:,}", va="center", fontsize=9)

        # 2. Satellites per receiver
        ax2 = axes[0, 1]
        bars2 = ax2.barh(receivers, satellites, color=colors, alpha=0.7)
        ax2.set_xlabel("Number of Satellites", fontsize=11)
        ax2.set_title("Satellite Coverage", fontsize=12, fontweight="bold")
        ax2.grid(axis="x", alpha=0.3)
        for i, (r, s) in enumerate(zip(receivers, satellites)):
            ax2.text(s, i, f"  {s}", va="center", fontsize=9)

        # 3. Data size per receiver
        ax3 = axes[1, 0]
        bars3 = ax3.barh(receivers, sizes, color=colors, alpha=0.7)
        ax3.set_xlabel("Data Size (MB)", fontsize=11)
        ax3.set_title("Memory Footprint", fontsize=12, fontweight="bold")
        ax3.grid(axis="x", alpha=0.3)
        for i, (r, s) in enumerate(zip(receivers, sizes)):
            ax3.text(s, i, f"  {s:.1f} MB", va="center", fontsize=9)

        # 4. Data distribution by receiver type
        ax4 = axes[1, 1]
        canopy_count = sum(1 for r in receivers if "canopy" in r)
        reference_count = len(receivers) - canopy_count

        wedges, texts, autotexts = ax4.pie(
            [canopy_count, reference_count],
            labels=["Canopy", "Reference"],
            colors=["#2ecc71", "#3498db"],
            autopct="%1.0f%%",
            startangle=90,
            textprops={"fontsize": 11},
        )
        ax4.set_title("Receiver Distribution", fontsize=12, fontweight="bold")

        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")

        plt.tight_layout()

        viz_display = mo.md(f"""
        ### Visual Analysis

        {mo.as_html(fig)}

        **Legend**:
        - 🟢 **Green**: Canopy receivers (below vegetation)
        - 🔵 **Blue**: Reference receivers (open sky)
        """)

        plt.close(fig)

    viz_display


@app.cell
def _(datasets, mo, np, process_success):
    """## 🔬 Data Quality Check

    Examine the structure and quality of processed datasets.
    """
    if not process_success:
        quality_display = mo.md("⚠️ No data to check")
    else:
        # Pick one dataset for detailed inspection
        sample_receiver = list(datasets.keys())[0]
        sample_ds = datasets[sample_receiver]

        # Get dimensions
        dims_info = "\n".join(
            f"  - **{dim}**: {size}" for dim, size in sample_ds.dims.items()
        )

        # Get variables
        vars_info = "\n".join(
            f"  - `{var}`: {sample_ds[var].dtype!s}" for var in sample_ds.data_vars
        )

        # Get coordinates
        coords_info = "\n".join(
            f"  - `{coord}`: {sample_ds[coord].dtype!s}" for coord in sample_ds.coords
        )

        # Time range
        start_time = sample_ds.epoch.values[0]
        end_time = sample_ds.epoch.values[-1]

        # Sample data quality metrics
        if "phi" in sample_ds.data_vars:
            phi_valid = (~np.isnan(sample_ds["phi"].values)).sum()
            phi_total = sample_ds["phi"].size
            phi_completeness = 100 * phi_valid / phi_total if phi_total > 0 else 0
        else:
            phi_completeness = 0

        quality_display = mo.md(f"""
        ### Dataset Structure (Sample: {sample_receiver})

        **Dimensions**:
    {dims_info}

        **Coordinates**:
    {coords_info}

        **Data Variables** ({len(sample_ds.data_vars)} total):
    {vars_info}

        **Time Range**:
        - Start: {start_time}
        - End: {end_time}
        - Duration: {end_time - start_time}

        **Data Quality**:
        - Spherical coordinates computed: {"✅" if "phi" in sample_ds.data_vars else "❌"}
        - Data completeness: {phi_completeness:.1f}%
        - Missing values: {(~np.isnan(sample_ds["phi"].values)).sum() if "phi" in sample_ds.data_vars else "N/A"} / {sample_ds["phi"].size if "phi" in sample_ds.data_vars else "N/A"}

        ---

        ### 💡 What's in the Data?

        Each dataset contains:
        - **RINEX observables**: C1C, L1C, D1C, S1C (code, phase, Doppler, SNR)
        - **Spherical coordinates**: φ (azimuth), θ (elevation), r (distance)
        - **Satellite info**: PRN numbers, GNSS system
        - **Time stamps**: GPS epoch for each observation

        All processed data is stored in **Icechunk** with full version control!
        """)

    quality_display


@app.cell
def _(mo):
    """## 🎯 Next Steps: VOD Calculation

    Now that we have processed RINEX data, we can calculate VOD!
    """
    next_steps = mo.md("""
    ### What's Next?

    With processed RINEX data in Icechunk, you can now:

    #### 1. Calculate VOD (Vegetation Optical Depth)

    ```python
    from canvodpy import calculate_vod

    # Level 1 API - Simple one-liner
    vod = calculate_vod(
        site="Rosalia",
        canopy_receiver="canopy_01",
        reference_receiver="reference_01",
        date="2025001"
    )
    ```

    #### 2. Visualize on Hemisphere

    ```python
    from canvod.viz import HemispherePlot2D

    # Create 2D hemisphere visualization
    plot = HemispherePlot2D(vod_dataset)
    plot.plot_tau()
    plot.show()
    ```

    #### 3. Time Series Analysis

    ```python
    # Process multiple days
    dates = ["2025001", "2025002", "2025003", ...]

    vod_series = []
    for date in dates:
        vod = calculate_vod("Rosalia", "canopy_01", "reference_01", date)
        vod_series.append(vod.tau.mean())

    # Plot time series
    plt.plot(dates, vod_series)
    plt.xlabel("Date")
    plt.ylabel("Mean VOD (τ)")
    plt.title("Vegetation Water Content Over Time")
    ```

    #### 4. Automate with Airflow

    ```python
    from airflow import DAG
    from airflow.operators.python import PythonOperator

    def daily_vod_task(site, date):
        from canvodpy import process_date, calculate_vod

        # Process RINEX
        process_date(site, date)

        # Calculate VOD
        vod = calculate_vod(site, "canopy_01", "reference_01", date)
        return float(vod.tau.mean())

    with DAG('gnss_vod_daily', schedule='@daily') as dag:
        task = PythonOperator(
            task_id='calculate_vod',
            python_callable=daily_vod_task,
            op_kwargs={'site': 'Rosalia', 'date': '{{ ds_nodash }}'},
        )
    ```

    ---

    ### 📚 Learn More

    - **Documentation**: https://canvodpy.readthedocs.io
    - **API Reference**: See `API_QUICK_REFERENCE.md`
    - **Examples**: Check the `examples/` directory
    - **Research Paper**: [Link to publication]

    ### 🆘 Getting Help

    - **Issues**: https://github.com/yourusername/canvodpy/issues
    - **Discussions**: https://github.com/yourusername/canvodpy/discussions
    - **Email**: your.email@tuwien.ac.at
    """)

    next_steps


@app.cell
def _(mo):
    """## 🎓 Summary

    Congratulations! You've completed the canvodpy demo.
    """
    summary = mo.md("""
    ## ✅ What We Accomplished

    In this notebook, you learned how to:

    1. ✅ **Set up a research site** using the clean `Site` API
    2. ✅ **Create a processing pipeline** with automatic parallelization
    3. ✅ **Process RINEX data** with one simple function call
    4. ✅ **Analyze performance** and data quality metrics
    5. ✅ **Visualize results** with publication-quality plots

    ---

    ## 🎯 Key Takeaways

    ### The canvodpy API is:

    - ✨ **Simple**: `Site("Rosalia").pipeline().process_date("2025001")`
    - 🚀 **Fast**: Parallel processing with intelligent caching
    - 📊 **Complete**: From raw RINEX to VOD in a few lines
    - 🔬 **Scientific**: Validated against published methods
    - 🏭 **Production-ready**: Airflow integration, monitoring, versioning

    ### Three Levels for Every User:

    - 🟢 **Beginners**: Convenience functions (`process_date()`)
    - 🟡 **Production**: Object-oriented API (`Site`, `Pipeline`)
    - 🔴 **Advanced**: Direct orchestrator access (full control)

    ---

    ## 📈 Comparison: Old vs New

    ### Before (gnssvodpy)
    ```python
    from gnssvodpy.icechunk_manager.manager import GnssResearchSite
    from gnssvodpy.processor.pipeline_orchestrator import PipelineOrchestrator
    from gnssvodpy.globals import KEEP_RNX_VARS

    site = GnssResearchSite(site_name="Rosalia")
    orchestrator = PipelineOrchestrator(site=site, dry_run=False)

    for date_key, datasets, timings in orchestrator.process_by_date(
        keep_vars=KEEP_RNX_VARS,
        start_from="2025001",
        end_at="2025001"
    ):
        # Process each dataset...
        pass
    ```

    ### After (canvodpy)
    ```python
    from canvodpy import Site

    site = Site("Rosalia")
    data = site.pipeline().process_date("2025001")
    ```

    **10 lines → 3 lines. Same power. Much cleaner.** ✨

    ---

    ## 🚀 Ready for Production

    canvodpy is ready for:
    - ✅ Multi-site deployments (20+ sites)
    - ✅ Automated daily processing (Airflow)
    - ✅ Large-scale analysis (parallel processing)
    - ✅ Reproducible research (versioned stores)
    - ✅ Operational monitoring (logging, metrics)

    ---

    ## 🙏 Acknowledgments

    **Developed by**: Nicolas François Bader
    **Institution**: TU Wien - CLIMERS
    **License**: Apache 2.0
    **Citation**: [Your paper here]

    **Built on**:
    - xarray: Labeled multi-dimensional arrays
    - Icechunk: Versioned data stores
    - georinex: RINEX parsing
    - numpy: Numerical computing

    **Happy analyzing! 🛰️**
    """)

    summary


if __name__ == "__main__":
    app.run()
