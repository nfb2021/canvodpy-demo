import marimo

__generated_with = "0.19.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # GNSS VOD Analysis - Complete Pipeline Demo

    This notebook demonstrates the complete pipeline for GNSS Vegetation Optical Depth (VOD) analysis using the Rosalia forest site data.

    ## Pipeline Steps

    1. **Setup** - Load demo data from canvodpy-demo submodule
    2. **Read RINEX** - Load observation data from Rosalia site
    3. **Download/Load Auxiliary Data** - Get ephemeris (SP3) and clock (CLK) files
    4. **Augment Data** - Compute satellite positions and clock corrections
    5. **Complete Workflow** - End-to-end processing

    ## Demo Data

    - **Site**: Rosalia, Austria (forest research site)
    - **Receivers**: Reference (open-sky) and Canopy (below-canopy)
    - **Data**: 2025 DOY 001-002 (96 files per day, 15-minute intervals)
    - **Location**: `demo/data/01_Rosalia/`
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 1. Setup - Demo Data Paths

    Using data from the canvodpy-demo submodule.
    """)


@app.cell
def _(mo):
    from pathlib import Path

    # Demo data directory (from submodule)
    DEMO_ROOT = Path(__file__).parent
    DEMO_DATA = DEMO_ROOT / "data"

    # Rosalia site paths
    ROSALIA_DIR = DEMO_DATA / "01_Rosalia"
    ROSALIA_REFERENCE = ROSALIA_DIR / "01_reference/01_GNSS/01_raw"
    ROSALIA_CANOPY = ROSALIA_DIR / "02_canopy/01_GNSS/01_raw"
    AUX_DIR = DEMO_DATA / "00_aux_files"

    # Output directory
    OUTPUT_DIR = DEMO_ROOT / "outputs"
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Check directories exist
    if not DEMO_DATA.exists():
        mo.md("""
        ⚠️ **Demo data not found!**

        Make sure the demo submodule is initialized:
        ```bash
        git submodule update --init demo
        ```
        """)
    else:
        mo.md(f"""
        ✅ **Demo Data Located**

        - **Reference RINEX**: `{ROSALIA_REFERENCE}`
        - **Canopy RINEX**: `{ROSALIA_CANOPY}`
        - **Auxiliary Files**: `{AUX_DIR}`
        - **Output**: `{OUTPUT_DIR}`
        """)

    return AUX_DIR, OUTPUT_DIR, ROSALIA_CANOPY, ROSALIA_REFERENCE


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 2. Select Day and Receiver

    Choose which day and receiver to process.
    """)


@app.cell
def _(ROSALIA_REFERENCE, mo):
    # Day selector
    available_days = sorted([d.name for d in ROSALIA_REFERENCE.glob("*") if d.is_dir()])

    day_selector = mo.ui.dropdown(
        options=available_days,
        value=available_days[0] if available_days else None,
        label="Day (YYDDD):",
    )

    # Receiver selector
    receiver_selector = mo.ui.dropdown(
        options=["reference", "canopy"], value="reference", label="Receiver:"
    )

    mo.vstack(
        [mo.md("### Data Selection"), mo.hstack([day_selector, receiver_selector])]
    )
    return day_selector, receiver_selector


@app.cell
def _(ROSALIA_CANOPY, ROSALIA_REFERENCE, day_selector, mo, receiver_selector):
    # Get selected directory
    if day_selector.value and receiver_selector.value:
        if receiver_selector.value == "reference":
            _selected_dir = ROSALIA_REFERENCE / day_selector.value
        else:
            _selected_dir = ROSALIA_CANOPY / day_selector.value

        # List RINEX files
        _rinex_files = sorted(_selected_dir.glob("*.[0-9][0-9]o"))

        if _rinex_files:
            mo.md(f"""
            ✅ **Found {len(_rinex_files)} RINEX files**

            - Directory: `{_selected_dir}`
            - Pattern: 15-minute observation files
            - First file: `{_rinex_files[0].name}`
            - Last file: `{_rinex_files[-1].name}`
            """)
        else:
            mo.md(f"⚠️ No RINEX files found in `{_selected_dir}`")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 3. Load RINEX Data

    Read RINEX observation files.
    """)


@app.cell
def _(mo):
    # File count selector
    file_count_selector = mo.ui.dropdown(
        options=[1, 4, 8, 24, 96],
        value=4,
        label="Number of files to load (1 file = 15 minutes):",
    )

    load_button = mo.ui.run_button(label="Load RINEX Files")

    mo.vstack([file_count_selector, load_button])
    return file_count_selector, load_button


@app.cell
def _(
    ROSALIA_CANOPY,
    ROSALIA_REFERENCE,
    day_selector,
    file_count_selector,
    load_button,
    mo,
    receiver_selector,
):
    _rinex_datasets = None
    _load_output = None

    if load_button.value and day_selector.value:
        import xarray as xr
        from canvod.readers import Rnxv3Obs

        # Get directory
        if receiver_selector.value == "reference":
            _dir = ROSALIA_REFERENCE / day_selector.value
        else:
            _dir = ROSALIA_CANOPY / day_selector.value

        # Get files
        _files = sorted(_dir.glob("*.[0-9][0-9]o"))[: file_count_selector.value]

        # Load datasets
        _datasets = []
        for _f in _files:
            try:
                obs = Rnxv3Obs(fpath=_f)
                ds = obs.to_ds()
                _datasets.append(ds)
            except Exception as e:
                print(f"Error loading {_f.name}: {e}")

        if _datasets:
            # Concatenate along epoch dimension
            _rinex_datasets = xr.concat(_datasets, dim="epoch")

            _load_output = mo.md(f"""
            ✅ **RINEX Data Loaded**

            - **Files loaded**: {len(_datasets)}
            - **Receiver**: {receiver_selector.value}
            - **Day**: {day_selector.value}
            - **Total epochs**: {len(_rinex_datasets.epoch)}
            - **Satellites**: {len(_rinex_datasets.sv)}
            - **Dimensions**: {dict(_rinex_datasets.sizes)}
            """)
        else:
            _load_output = mo.md("❌ Failed to load RINEX files")
    else:
        _load_output = load_button

    _load_output


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 4. Auxiliary Data

    Load or download ephemeris (SP3) and clock (CLK) files.
    """)


@app.cell
def _(AUX_DIR, mo):
    # Check if auxiliary files exist in demo
    if _rinex_datasets is not None:
        # Extract date from first epoch
        import datetime

        _first_epoch = _rinex_datasets.epoch.min().values
        _dt = datetime.datetime.utcfromtimestamp(
            _first_epoch.astype("datetime64[s]").astype(int)
        )
        _obs_date = _dt.date()

        # Check for existing files
        _sp3_dir = AUX_DIR / "01_SP3"
        _clk_dir = AUX_DIR / "02_CLK"

        _sp3_files = (
            list(_sp3_dir.glob("*.SP3")) + list(_sp3_dir.glob("*.sp3"))
            if _sp3_dir.exists()
            else []
        )
        _clk_files = (
            list(_clk_dir.glob("*.CLK")) + list(_clk_dir.glob("*.clk"))
            if _clk_dir.exists()
            else []
        )

        mo.md(f"""
        ### Observation Date: {_obs_date}

        **Auxiliary Files in Demo:**
        - SP3 files: {len(_sp3_files)}
        - CLK files: {len(_clk_files)}

        *If files are missing, they can be downloaded using canvod-aux package.*
        """)


@app.cell
def _(mo):
    # Agency and product selectors
    agency_selector = mo.ui.dropdown(
        options=["COD", "GFZ", "ESA", "JPL", "IGS"],
        value="COD",
        label="Analysis Center:",
    )

    product_selector = mo.ui.dropdown(
        options=["final", "rapid"], value="rapid", label="Product Type:"
    )

    download_aux_button = mo.ui.run_button(label="Download Auxiliary Data")

    mo.vstack(
        [
            mo.md("### Download Options"),
            mo.hstack([agency_selector, product_selector]),
            download_aux_button,
        ]
    )
    return agency_selector, download_aux_button, product_selector


@app.cell
def _(AUX_DIR, agency_selector, download_aux_button, mo, product_selector):
    _aux_files = None
    _download_output = None

    if download_aux_button.value and _obs_date:
        import os

        from canvod.auxiliary.clock.reader import ClkFile
        from canvod.auxiliary.core.downloader import FtpDownloader
        from canvod.auxiliary.ephemeris.reader import Sp3File

        results = {}

        # Setup downloader
        user_email = os.environ.get("CDDIS_MAIL")
        downloader = FtpDownloader(user_email=user_email)
        ftp_server = "ftp://ftp.aiub.unibe.ch"

        try:
            sp3_file = Sp3File.from_datetime_date(
                date=_obs_date,
                agency=agency_selector.value,
                product_type=product_selector.value,
                ftp_server=ftp_server,
                local_dir=AUX_DIR,
                downloader=downloader,
            )
            results["sp3"] = sp3_file
            results["sp3_error"] = None
        except Exception as e:
            results["sp3"] = None
            results["sp3_error"] = str(e)

        try:
            clk_file = ClkFile.from_datetime_date(
                date=_obs_date,
                agency=agency_selector.value,
                product_type=product_selector.value,
                ftp_server=ftp_server,
                local_dir=AUX_DIR,
                downloader=downloader,
            )
            results["clk"] = clk_file
            results["clk_error"] = None
        except Exception as e:
            results["clk"] = None
            results["clk_error"] = str(e)

        _aux_files = results

        messages = []
        if results["sp3"]:
            messages.append(f"✅ SP3: `{results['sp3'].fpath.name}`")
        elif results["sp3_error"]:
            messages.append(f"❌ SP3 Error: {results['sp3_error'][:200]}")

        if results["clk"]:
            messages.append(f"✅ CLK: `{results['clk'].fpath.name}`")
        elif results["clk_error"]:
            messages.append(f"❌ CLK Error: {results['clk_error'][:200]}")

        _download_output = mo.md("\n\n".join(messages))
    else:
        _download_output = download_aux_button

    _download_output


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 5. Augment Data

    Add satellite positions and clock corrections to RINEX observations.
    """)


@app.cell
def _(mo, receiver_selector):
    # Receiver position (Rosalia site ECEF coordinates)
    # Reference receiver (open-sky)
    REF_POSITION = {"x": 4194354.123, "y": 1162180.456, "z": 4647290.789}

    # Canopy receiver (below canopy)
    CANOPY_POSITION = {"x": 4194304.678, "y": 1162205.267, "z": 4647245.201}

    _pos = REF_POSITION if receiver_selector.value == "reference" else CANOPY_POSITION

    receiver_x = mo.ui.number(value=_pos["x"], label="X (m):", step=0.001)
    receiver_y = mo.ui.number(value=_pos["y"], label="Y (m):", step=0.001)
    receiver_z = mo.ui.number(value=_pos["z"], label="Z (m):", step=0.001)

    mo.vstack(
        [
            mo.md(f"### Receiver Position ({receiver_selector.value})"),
            mo.hstack([receiver_x, receiver_y, receiver_z]),
        ]
    )
    return receiver_x, receiver_y, receiver_z


@app.cell
def _(mo):
    augment_button = mo.ui.run_button(label="Augment Data")
    augment_button
    return (augment_button,)


@app.cell
def _(augment_button, mo, receiver_x, receiver_y, receiver_z):
    _augmented_ds = None
    _augment_output = None

    if augment_button.value and _rinex_datasets is not None and _aux_files:
        from dataclasses import dataclass

        from canvod.auxiliary.augmentation import AugmentationContext, AuxDataAugmenter

        @dataclass
        class ECEFPosition:
            x: float
            y: float
            z: float

        if _aux_files["sp3"] and _aux_files["clk"]:
            try:
                # Create receiver position
                ecef_pos = ECEFPosition(
                    x=receiver_x.value, y=receiver_y.value, z=receiver_z.value
                )

                # Create augmentation context
                context = AugmentationContext(
                    receiver_position=ecef_pos,
                    receiver_type="demo",
                    matched_datasets={
                        "ephemeris": _aux_files["sp3"].data,
                        "clock": _aux_files["clk"].data,
                    },
                )

                # Augment
                augmenter = AuxDataAugmenter()
                _augmented_ds = augmenter.augment(_rinex_datasets, context)

                new_vars = set(_augmented_ds.data_vars) - set(_rinex_datasets.data_vars)

                _augment_output = mo.md(f"""
                ✅ **Augmentation Complete**

                **New Variables:**
                {chr(10).join(f"- `{var}`" for var in sorted(new_vars))}

                **Dataset:**
                - Dimensions: {dict(_augmented_ds.sizes)}
                - Total variables: {len(_augmented_ds.data_vars)}
                """)
            except Exception as e:
                _augment_output = mo.md(f"❌ **Error:** {str(e)[:500]}")
        else:
            _augment_output = mo.md("⚠️ Missing auxiliary files")
    else:
        _augment_output = augment_button

    _augment_output


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 6. Visualize

    Explore the augmented dataset.
    """)


@app.cell
def _():
    if _augmented_ds is not None:
        print("Augmented Dataset:")
        print(_augmented_ds)


@app.cell
def _(mo):
    if _augmented_ds is not None:
        plot_var_selector = mo.ui.dropdown(
            options=sorted([str(v) for v in _augmented_ds.data_vars]),
            label="Variable to plot:",
        )
        plot_var_selector
    return (plot_var_selector,)


@app.cell
def _(plot_var_selector):
    if _augmented_ds is not None and plot_var_selector.value:
        import matplotlib.pyplot as plt

        var = plot_var_selector.value
        data = _augmented_ds[var]

        fig, ax = plt.subplots(figsize=(12, 6))

        if "sv" in data.sizes or "sid" in data.sizes:
            sv_dim = "sv" if "sv" in data.sizes else "sid"
            first_sv = data[sv_dim].values[0]
            subset = data.sel({sv_dim: first_sv})

            ax.plot(subset.epoch.values, subset.values, marker=".")
            ax.set_xlabel("Epoch")
            ax.set_ylabel(var)
            ax.set_title(f"{var} for {first_sv}")
            ax.grid(True, alpha=0.3)
        else:
            ax.plot(data.epoch.values, data.values, marker=".")
            ax.set_xlabel("Epoch")
            ax.set_ylabel(var)
            ax.set_title(var)
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.gca()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 7. Save

    Export the augmented dataset.
    """)


@app.cell
def _(mo):
    save_button = mo.ui.run_button(label="Save Dataset")
    save_button
    return (save_button,)


@app.cell
def _(OUTPUT_DIR, day_selector, mo, receiver_selector, save_button):
    if save_button.value and _augmented_ds is not None:
        output_file = (
            OUTPUT_DIR / f"augmented_{receiver_selector.value}_{day_selector.value}.nc"
        )
        _augmented_ds.to_netcdf(output_file)

        mo.md(f"""
        ✅ **Saved**

        File: `{output_file}`  
        Size: {output_file.stat().st_size / 1024 / 1024:.2f} MB
        """)
    else:
        save_button


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Summary

    This demo showed the complete GNSS VOD pipeline using real Rosalia forest site data:

    ✅ **Load RINEX** - Read 15-minute observation files
    ✅ **Auxiliary Data** - Get ephemeris and clock corrections
    ✅ **Augment** - Add satellite positions and timing
    ✅ **Visualize** - Explore augmented variables
    ✅ **Save** - Export to NetCDF

    ### Next Steps

    - Process full day (96 files) for complete coverage
    - Compare reference vs canopy receivers
    - Calculate vegetation optical depth (VOD)
    - Generate spatial grids and visualizations

    ### Resources

    - [canvodpy Documentation](https://canvodpy.readthedocs.io)
    - [Demo Data Repository](https://github.com/nfb2021/canvodpy-demo)
    - [Rosalia Site Info](../data/01_Rosalia/README.md)
    """)


if __name__ == "__main__":
    app.run()
