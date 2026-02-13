"""GNSS VOD Analysis - Complete Workflow Demo

This is the definitive demonstration of canvodpy for processing GNSS data
and calculating Vegetation Optical Depth (VOD).

Features:
- Three-level API demonstration (convenience, OOP, low-level)
- Complete RINEX processing workflow
- VOD calculation and analysis
- Interactive visualizations
- Performance metrics

Author: Nicolas François Bader
Institution: TU Wien - CLIMERS
Date: 2025-01-22
"""

import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🛰️ GNSS Vegetation Optical Depth Analysis

    **Complete Workflow Demonstration**

    ---

    ## What is GNSS VOD?

    GNSS Vegetation Optical Depth (VOD) measures vegetation water content using
    signal attenuation from satellite navigation systems. As GNSS signals pass
    through vegetation canopies, they are attenuated proportionally to the
    vegetation's water content.

    ## The Pipeline

    ```
    RINEX Obs → Signal Processing → Aux Data Integration → VOD Calculation
    ```

    ## This Demo

    We'll process data from **Rosalia field site** in Austria:
    - 🌲 **Canopy receivers**: Under forest canopy (canopy_01, canopy_02)
    - ☀️ **Reference receivers**: Open sky (reference_01, reference_02)
    - 📅 **Date**: 2025-001 (January 1, 2025)

    ## Three API Levels ✨

    This notebook demonstrates canvodpy's three-level API design:

    **Level 1 - Convenience Functions** (for quick tasks)
    ```python
    from canvodpy import process_date, calculate_vod
    data = process_date("Rosalia", "2025001")
    vod = calculate_vod("Rosalia", "canopy_01", "reference_01", "2025001")
    ```

    **Level 2 - Object-Oriented** (for production code)
    ```python
    from canvodpy import Site, Pipeline
    site = Site("Rosalia")
    pipeline = site.pipeline()
    data = pipeline.process_date("2025001")
    ```

    **Level 3 - Low-Level Access** (for advanced control)
    ```python
    from canvodpy.orchestrator import PipelineOrchestrator
    orchestrator = PipelineOrchestrator(site, ...)
    for date, datasets, timings in orchestrator.process_by_date(...):
        # Full control over processing
    ```

    Let's explore all three! 👇
    """)


@app.cell
def _():
    """Import packages"""
    import time

    import marimo as mo

    # Visualization
    import matplotlib.pyplot as plt
    import pandas as pd

    # ✨ canvodpy - Modern GNSS processing
    from canvodpy import Site, calculate_vod, process_date

    return Site, calculate_vod, mo, pd, plt, process_date, time


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🎯 Part 1: Configuration

    Set up our processing parameters.
    """)


@app.cell
def _(mo):
    """Configuration"""
    # Processing parameters
    SITE_NAME = "Rosalia"
    TARGET_DATE = "2025001"  # YYYYDOY format (Jan 1, 2025)

    # Expected outputs
    EXPECTED_RECEIVERS = ["canopy_01", "canopy_02", "reference_01", "reference_02"]
    EXPECTED_ANALYSES = ["canopy_01-reference_01", "canopy_02-reference_02"]

    config_ui = mo.md(f"""
    ### 📋 Configuration

    | Parameter | Value |
    |-----------|-------|
    | **Site** | {SITE_NAME} |
    | **Date** | {TARGET_DATE} (Jan 1, 2025) |
    | **Receivers** | {len(EXPECTED_RECEIVERS)} total |
    | **VOD Analyses** | {len(EXPECTED_ANALYSES)} pairs |

    **Canopy Receivers:** canopy_01, canopy_02
    **Reference Receivers:** reference_01, reference_02
    """)

    config_ui
    return SITE_NAME, TARGET_DATE


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ Part 2: API Level 1 - Quick Processing

    The **convenience function API** - perfect for notebooks and quick analysis.

    ### Example: Process one day of data

    ```python
    from canvodpy import process_date

    # That's it! One line.
    data = process_date("Rosalia", "2025001")
    ```

    This is the simplest way to use canvodpy. Behind the scenes, it:
    1. Initializes the site
    2. Creates a pipeline
    3. Processes RINEX data
    4. Returns datasets

    Let's try it! 👇
    """)


@app.cell
def _(SITE_NAME, TARGET_DATE, mo, process_date, time):
    """Level 1 API - Convenience Function"""
    mo.md("### Running Level 1 API...")

    level1_start = time.time()

    try:
        # ✨ ONE LINE - That's the entire API!
        level1_data = process_date(SITE_NAME, TARGET_DATE)

        level1_time = time.time() - level1_start

        level1_result = mo.md(f"""
        ✅ **Level 1 API Complete!** (took {level1_time:.1f}s)

        ### Results

        **Receivers processed:** {len(level1_data)}

        {
            mo.as_html(
                mo.tree(
                    [
                        {
                            receiver: [
                                f"Epochs: {len(ds.epoch):,}",
                                f"Satellites: {len(ds.sv)}",
                                f"Variables: {len(ds.data_vars)}",
                                f"Size: {ds.nbytes / 1024 / 1024:.1f} MB",
                            ]
                        }
                        for receiver, ds in level1_data.items()
                    ]
                )
            )
        }

        ### Code Used

        ```python
        # Just one line!
        data = process_date("{SITE_NAME}", "{TARGET_DATE}")
        ```

        **Perfect for:**
        - Quick analysis in notebooks
        - One-off data processing
        - Exploratory data analysis
        """)

    except Exception as e:
        level1_result = mo.md(f"""
        ⚠️ **Level 1 processing skipped**

        This demo requires data to be present. Error: `{e!s}`

        Continue with the notebook to see other API examples.
        """)
        level1_data = {}
        level1_time = 0

    level1_result
    return level1_data, level1_time


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🔧 Part 3: API Level 2 - Object-Oriented

    The **OOP API** - recommended for production code and complex workflows.

    ### Example: Using Site and Pipeline classes

    ```python
    from canvodpy import Site, Pipeline

    # Create site object
    site = Site("Rosalia")

    # Create pipeline with options
    pipeline = site.pipeline(
        aux_agency="COD",  # CODE analysis center
        n_workers=12       # Parallel processing
    )

    # Process data
    data = pipeline.process_date("2025001")

    # Calculate VOD
    vod = pipeline.calculate_vod(
        canopy="canopy_01",
        reference="reference_01",
        date="2025001"
    )
    ```

    This gives you more control and is easier to test, debug, and maintain.
    """)


@app.cell
def _(SITE_NAME, Site, mo, time):
    """Level 2 API - Site Initialization"""
    mo.md("### Initializing Site object...")

    site_start = time.time()

    try:
        # ✨ Create Site - manages receivers and storage
        site = Site(SITE_NAME)

        site_time = time.time() - site_start

        site_info = mo.md(f"""
        ✅ **Site initialized!** (took {site_time:.2f}s)

        ### Site Information

        - **Name:** {site.name}
        - **Active Receivers:** {len(site.active_receivers)}
        - **Storage Type:** Icechunk
        - **VOD Analyses:** {len(site.vod_analyses)} configured pairs

        **Configured Receivers:**

        {
            mo.as_html(
                mo.tree(
                    [
                        {
                            receiver: [
                                f"Type: {config.get('type', 'unknown')}",
                                f"Description: {config.get('description', 'N/A')}",
                            ]
                        }
                        for receiver, config in site.active_receivers.items()
                    ]
                )
            )
        }

        ### Code Used

        ```python
        site = Site("{SITE_NAME}")

        # Access site properties
        print(site.name)                # "Rosalia"
        print(site.active_receivers)    # Dict of receivers
        print(site.vod_analyses)        # Configured VOD pairs
        ```

        **Perfect for:**
        - Production code
        - Complex workflows
        - Code that needs testing
        - Projects with multiple sites
        """)

    except Exception as e:
        site_info = mo.md(f"""
        ❌ **Site initialization failed**

        Error: `{e!s}`

        Check that the site configuration exists in `research_sites_config.py`.
        """)
        site = None
        site_time = 0

    site_info
    return (site,)


@app.cell
def _(mo, site, time):
    """Level 2 API - Pipeline Creation"""
    if site is None:
        pipeline_info = mo.md("⚠️ Cannot create pipeline - site not initialized")
        pipeline = None
        pipeline_time = 0
    else:
        mo.md("### Creating Pipeline...")

        pipeline_start = time.time()

        try:
            # ✨ Create Pipeline from site
            pipeline = site.pipeline(
                aux_agency="COD",  # CODE analysis center
                n_workers=12,  # Parallel workers
            )

            pipeline_time = time.time() - pipeline_start

            pipeline_info = mo.md(f"""
            ✅ **Pipeline created!** (took {pipeline_time:.2f}s)

            ### Pipeline Configuration

            - **Auxiliary Agency:** CODE (Center for Orbit Determination)
            - **Workers:** 12 (parallel processing)
            - **Site:** {site.name}
            - **Receivers:** {len(site.active_receivers)}

            ### Code Used

            ```python
            # Create from site (recommended)
            pipeline = site.pipeline(
                aux_agency="COD",
                n_workers=12
            )

            # Or create directly
            pipeline = Pipeline(
                site="Rosalia",
                aux_agency="COD",
                n_workers=12
            )
            ```

            The pipeline is now ready to process RINEX data!
            """)

        except Exception as e:
            pipeline_info = mo.md(f"""
            ❌ **Pipeline creation failed**

            Error: `{e!s}`
            """)
            pipeline = None
            pipeline_time = 0

    pipeline_info
    return (pipeline,)


@app.cell
def _(TARGET_DATE, mo, pipeline, time):
    """Level 2 API - Data Processing"""
    if pipeline is None:
        process_info = mo.md("⚠️ Cannot process - pipeline not initialized")
        level2_data = {}
        process_time = 0
    else:
        mo.md(f"### Processing {TARGET_DATE}...")

        process_start = time.time()

        try:
            # ✨ Process date using pipeline
            level2_data = pipeline.process_date(TARGET_DATE)

            process_time = time.time() - process_start

            process_info = mo.md(f"""
            ✅ **Processing complete!** (took {process_time:.1f}s)

            ### Processing Results

            **Receivers processed:** {len(level2_data)}
            **Average time per receiver:** {process_time / len(level2_data):.1f}s

            {
                mo.as_html(
                    mo.tree(
                        [
                            {
                                receiver: [
                                    f"Epochs: {len(ds.epoch):,}",
                                    f"Satellites: {len(ds.sv)}",
                                    f"Variables: {len(ds.data_vars)}",
                                    f"Coverage: {ds.epoch[0].values} to {ds.epoch[-1].values}",
                                ]
                            }
                            for receiver, ds in level2_data.items()
                        ]
                    )
                )
            }

            ### Code Used

            ```python
            # Process data
            data = pipeline.process_date("{TARGET_DATE}")

            # Access results
            for receiver, dataset in data.items():
                print(f"{{receiver}}: {{len(dataset.epoch)}} epochs")
            ```

            Data is now stored in Icechunk and ready for VOD calculation!
            """)

        except Exception as e:
            process_info = mo.md(f"""
            ⚠️ **Processing encountered an issue**

            Error: `{e!s}`

            **Common causes:**
            - RINEX files not found for this date
            - Auxiliary data (ephemeris/clocks) unavailable
            - Network issues downloading aux data
            """)
            level2_data = {}
            process_time = 0

    process_info
    return level2_data, process_time


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 📊 Part 4: Data Analysis

    Let's analyze the processed data.
    """)


@app.cell
def _(level1_data, level1_time, level2_data, mo, pd, process_time):
    """Data Analysis Summary"""
    # Use whichever dataset is available
    data_to_analyze = level2_data if level2_data else level1_data
    processing_seconds = process_time if process_time > 0 else level1_time

    if not data_to_analyze:
        analysis_summary = mo.md("⚠️ No data available for analysis")
    else:
        # Create summary DataFrame
        summary_data = []
        for receiver, ds in data_to_analyze.items():
            summary_data.append(
                {
                    "Receiver": receiver,
                    "Type": receiver.split("_")[0],
                    "Epochs": len(ds.epoch),
                    "Satellites": len(ds.sv),
                    "Variables": len(ds.data_vars),
                    "Size (MB)": ds.nbytes / 1024 / 1024,
                    "First Epoch": str(ds.epoch[0].values)[:19],
                    "Last Epoch": str(ds.epoch[-1].values)[:19],
                }
            )

        summary_df = pd.DataFrame(summary_data)

        # Calculate statistics
        total_epochs = summary_df["Epochs"].sum()
        total_size = summary_df["Size (MB)"].sum()
        avg_satellites = summary_df["Satellites"].mean()

        analysis_summary = mo.md(f"""
        ### 📈 Processing Summary

        | Metric | Value |
        |--------|-------|
        | **Total Processing Time** | {processing_seconds:.1f}s |
        | **Receivers Processed** | {len(data_to_analyze)} |
        | **Total Epochs** | {total_epochs:,} |
        | **Total Data Size** | {total_size:.1f} MB |
        | **Avg Satellites** | {avg_satellites:.1f} |
        | **Throughput** | {total_epochs / processing_seconds:.0f} epochs/s |

        ### 📋 Per-Receiver Details

        {mo.as_html(summary_df)}

        ### 🔍 Key Observations

        - **Canopy receivers** typically see fewer satellites (due to obstruction)
        - **Reference receivers** have full sky view (more satellites)
        - **All receivers** processed in parallel for efficiency
        - **Data stored** in Icechunk for permanent access
        """)

    analysis_summary
    return (summary_df,)


@app.cell
def _(mo, plt, summary_df):
    """Visualization - Processing Statistics"""
    if "summary_df" not in dir() or summary_df.empty:
        stats_plot = mo.md("⚠️ No data to visualize")
    else:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Plot 1: Epochs per receiver
        colors = [
            "#2ecc71" if "canopy" in r.lower() else "#3498db"
            for r in summary_df["Receiver"]
        ]

        ax1.barh(summary_df["Receiver"], summary_df["Epochs"], color=colors)
        ax1.set_xlabel("Number of Epochs", fontsize=11)
        ax1.set_ylabel("Receiver", fontsize=11)
        ax1.set_title("Epochs Processed per Receiver", fontsize=12, fontweight="bold")
        ax1.grid(axis="x", alpha=0.3)

        # Add value labels
        for i, (receiver, epochs) in enumerate(
            zip(summary_df["Receiver"], summary_df["Epochs"])
        ):
            ax1.text(epochs, i, f"  {epochs:,}", va="center", fontsize=9)

        # Plot 2: Satellites per receiver
        ax2.barh(summary_df["Receiver"], summary_df["Satellites"], color=colors)
        ax2.set_xlabel("Number of Satellites", fontsize=11)
        ax2.set_ylabel("Receiver", fontsize=11)
        ax2.set_title("Satellites Tracked per Receiver", fontsize=12, fontweight="bold")
        ax2.grid(axis="x", alpha=0.3)

        # Add value labels
        for i, (receiver, sats) in enumerate(
            zip(summary_df["Receiver"], summary_df["Satellites"])
        ):
            ax2.text(sats, i, f"  {sats}", va="center", fontsize=9)

        plt.tight_layout()

        stats_plot = mo.md(f"""
        ### 📊 Processing Statistics

        {mo.as_html(fig)}

        **Legend:**
        - 🟢 **Green:** Canopy receivers (under vegetation)
        - 🔵 **Blue:** Reference receivers (open sky)

        **Note:** Canopy receivers typically track fewer satellites due to obstruction.
        """)

        plt.close(fig)

    stats_plot


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🌲 Part 5: VOD Calculation

    Calculate Vegetation Optical Depth by comparing canopy and reference receivers.

    ### The VOD Equation

    VOD (τ) is derived from the signal attenuation:

    $$
    \\tau = -\\frac{1}{2} \\ln\\left(\\frac{P_{canopy}}{P_{reference}}\\right)
    $$

    Where:
    - $P_{canopy}$ = Signal power under canopy
    - $P_{reference}$ = Signal power in open sky
    - $τ$ = Vegetation optical depth (dimensionless)

    Let's calculate it! 👇
    """)


@app.cell
def _(TARGET_DATE, calculate_vod, mo, pd, site, time):
    """VOD Calculation"""
    if site is None:
        vod_result = mo.md("⚠️ Cannot calculate VOD - site not initialized")
        vod_datasets = {}
        vod_time = 0
    else:
        mo.md("### Calculating VOD for all receiver pairs...")

        vod_start = time.time()
        vod_datasets = {}

        try:
            # Calculate VOD for each configured pair
            for analysis_name, config in site.vod_analyses.items():
                canopy_rx = config["canopy_receiver"]
                reference_rx = config["reference_receiver"]

                # ✨ Calculate VOD - simple function call
                vod_ds = calculate_vod(
                    site=site.name,
                    canopy_receiver=canopy_rx,
                    reference_receiver=reference_rx,
                    date=TARGET_DATE,
                )

                vod_datasets[analysis_name] = vod_ds

            vod_time = time.time() - vod_start

            # Create summary
            vod_summary = []
            for analysis, vod_ds in vod_datasets.items():
                vod_summary.append(
                    {
                        "Analysis": analysis,
                        "Mean VOD": float(vod_ds.tau.mean()),
                        "Std VOD": float(vod_ds.tau.std()),
                        "Min VOD": float(vod_ds.tau.min()),
                        "Max VOD": float(vod_ds.tau.max()),
                        "Data Points": int(vod_ds.tau.count()),
                    }
                )

            vod_df = pd.DataFrame(vod_summary)

            vod_result = mo.md(f"""
            ✅ **VOD calculation complete!** (took {vod_time:.1f}s)

            ### Results

            **Analyses completed:** {len(vod_datasets)}

            {mo.as_html(vod_df)}

            ### Code Used

            ```python
            # Calculate VOD for one pair
            vod = calculate_vod(
                site="Rosalia",
                canopy_receiver="canopy_01",
                reference_receiver="reference_01",
                date="2025001"
            )

            # Or using pipeline
            vod = pipeline.calculate_vod(
                canopy="canopy_01",
                reference="reference_01",
                date="2025001"
            )
            ```

            ### Interpretation

            - **Higher VOD** = More vegetation water content
            - **Lower VOD** = Less vegetation water content
            - **Typical values**: 0.1 - 2.0 for forests
            """)

        except Exception as e:
            vod_result = mo.md(f"""
            ⚠️ **VOD calculation encountered an issue**

            Error: `{e!s}`

            **Common causes:**
            - Data not processed yet for this date
            - Missing receiver data
            - Insufficient overlap between canopy/reference
            """)
            vod_datasets = {}
            vod_time = 0

    vod_result


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🎓 Part 6: API Comparison

    Let's review what we learned about the three API levels.
    """)


@app.cell(hide_code=True)
def _(mo):
    comparison = mo.md(r"""
    ### 🔄 API Level Comparison

    | Feature | Level 1: Convenience | Level 2: OOP | Level 3: Low-Level |
    |---------|---------------------|--------------|-------------------|
    | **Lines of code** | 1-2 | 3-5 | 10+ |
    | **Control** | Low | Medium | High |
    | **Use case** | Quick analysis | Production | Advanced workflows |
    | **Testing** | Hard | Easy | Very Easy |
    | **Debugging** | Hard | Easy | Very Easy |
    | **Customization** | Limited | Moderate | Full |

    ### 📝 When to Use Each Level

    **Level 1 - Convenience Functions** (`process_date`, `calculate_vod`)
    - ✅ Jupyter notebooks / quick analysis
    - ✅ One-off data processing
    - ✅ Prototyping
    - ❌ Production code
    - ❌ Complex workflows

    **Level 2 - Object-Oriented** (`Site`, `Pipeline`)
    - ✅ Production code
    - ✅ Automated workflows
    - ✅ Code that needs testing
    - ✅ Projects with multiple sites
    - ✅ **Recommended for most users**

    **Level 3 - Low-Level** (`PipelineOrchestrator`, etc.)
    - ✅ Advanced customization
    - ✅ Research & development
    - ✅ Performance optimization
    - ✅ Contributing to canvodpy
    - ❌ Not needed for typical use

    ### 🎯 Recommendation

    **Start with Level 2** (Site/Pipeline) for most projects. It offers the best
    balance of simplicity, control, and maintainability.

    Only drop to Level 1 for quick notebook experiments, or Level 3 when you need
    to modify the processing pipeline itself.
    """)

    comparison


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🚀 Part 7: Next Steps

    Where to go from here?
    """)


@app.cell(hide_code=True)
def _(mo):
    next_steps = mo.md(r"""
    ### 🎯 What You've Learned

    ✅ **Three API levels** - convenience, OOP, low-level
    ✅ **Complete workflow** - RINEX → processing → VOD
    ✅ **Site management** - receivers, storage, configuration
    ✅ **Pipeline processing** - parallel, efficient, robust
    ✅ **VOD calculation** - canopy vs reference analysis

    ### 📚 Further Resources

    **Documentation:**
    - API Reference: Full documentation of all classes and functions
    - User Guide: Step-by-step tutorials and examples
    - Migration Guide: Moving from gnssvodpy to canvodpy

    **Examples:**
    - `examples/01_quick_start.py` - Get started in 5 minutes
    - `examples/02_multi_site.py` - Process multiple sites
    - `examples/03_custom_workflow.py` - Advanced customization
    - `examples/04_airflow_integration.py` - Production automation

    **Code Structure:**
    ```
    canvodpy/
    ├── packages/          # Low-level building blocks
    │   ├── canvod-readers/   # RINEX parsing
    │   ├── canvod-aux/       # Auxiliary data
    │   ├── canvod-store/     # Icechunk storage
    │   └── canvod-vod/       # VOD calculations
    │
    └── canvodpy/          # High-level framework
        └── src/canvodpy/
            ├── api.py            # User-facing API
            ├── orchestrator/     # Processing pipeline
            ├── workflows/        # Airflow integration
            └── diagnostics/      # Monitoring & logging
    ```

    ### 🔬 Advanced Topics

    **For Production Use:**
    - Apache Airflow integration for multi-site automation
    - Monitoring and diagnostics
    - Performance optimization
    - Error handling and recovery

    **For Researchers:**
    - Custom VOD algorithms
    - Signal processing modifications
    - Multi-frequency analysis
    - Time series analysis

    ### 💡 Tips

    1. **Start simple** - Use Level 2 API (Site/Pipeline) for most tasks
    2. **Read the docs** - Comprehensive documentation with examples
    3. **Check the tests** - Test files show how to use each component
    4. **Ask questions** - Open issues on GitHub for help
    5. **Contribute** - PRs welcome for improvements!

    ### 🎓 Best Practices

    **Code Organization:**
    ```python
    # Good: Clear, testable, maintainable
    from canvodpy import Site, Pipeline

    def process_site(site_name: str, date: str):
        site = Site(site_name)
        pipeline = site.pipeline()
        return pipeline.process_date(date)

    # Test-friendly, can mock Site, easy to debug
    ```

    **Error Handling:**
    ```python
    try:
        data = process_date("Rosalia", "2025001")
    except FileNotFoundError:
        print("RINEX files not found - check data directory")
    except RuntimeError as e:
        if "auxiliary" in str(e).lower():
            print("Auxiliary data unavailable - check network")
        else:
            raise
    ```

    **Configuration:**
    ```python
    # Use site configuration files for flexibility
    # See: canvodpy/src/canvodpy/research_sites_config.py

    RESEARCH_SITES = {
        'Rosalia': {
            'active_receivers': {...},
            'vod_analyses': {...},
        }
    }
    ```

    ---

    ## 🎉 Congratulations!

    You've completed the canvodpy workflow demo. You now know how to:

    - ✅ Process GNSS data with canvodpy
    - ✅ Calculate vegetation optical depth
    - ✅ Use all three API levels
    - ✅ Understand the architecture
    - ✅ Follow best practices

    **Happy processing!** 🛰️
    """)

    next_steps


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
