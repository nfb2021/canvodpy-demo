import marimo

__generated_with = "0.19.4"
app = marimo.App(
    width="medium",
    css_file="marimo_darkmode_patch/marimo_darkmode_patch.css",
)


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # GNSS Data Augmentation Demo

    This notebook demonstrates the **complete augmentation workflow** following
    gnssvodpy's exact preprocessing pipeline:

    1. Read daily RINEX data (2025 DOY 001)
    2. Download/load auxiliary files (SP3 ephemeris + CLK clock)
    3. **Preprocess aux data with proper interpolation** (Hermite splines + piecewise linear)
    4. Compute spherical coordinates directly
    5. Export augmented dataset

    The augmentation adds:
    - **φ (phi)**: Azimuthal angle from North, clockwise [0, 2π) radians (0 = North, π/2 = East)
    - **θ (theta)**: Polar angle from zenith [0, π] radians
    - **r**: Slant range from receiver to satellite (meters)

    ## ✅ Migration Complete

    All functionality now in canvodpy monorepo - no gnssvodpy dependencies!
    """)


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 1. Setup - Data Directories
    """)


@app.cell
def _(mo):
    import os
    from datetime import date
    from pathlib import Path

    # Demo data paths
    DEMO_ROOT = Path(__file__).parent
    DEMO_DATA = DEMO_ROOT / "data"
    ROSALIA_DIR = DEMO_DATA / "01_Rosalia"
    ROSALIA_CANOPY = ROSALIA_DIR / "02_canopy/01_GNSS/01_raw"
    AUX_DIR = DEMO_DATA / "00_aux_files"

    # Output directory
    OUTPUT_DIR = DEMO_ROOT / "outputs"
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Target date
    TARGET_DATE = date(2025, 1, 1)  # 2025 DOY 001
    DOY_DIR = ROSALIA_CANOPY / "25001"

    # Check data exists
    if not DOY_DIR.exists():
        mo.md("""
        ⚠️ **Demo data not found!**

        Initialize the demo submodule:
        ```bash
        git submodule update --init demo
        ```
        """)
    else:
        rinex_count = len(list(DOY_DIR.glob("*.25o")))
        mo.md(f"""
        ✅ **Demo Data Ready**

        - **RINEX Directory**: `{DOY_DIR}`
        - **RINEX Files**: {rinex_count} files (15-minute intervals)
        - **Auxiliary Storage**: `{AUX_DIR}`
        - **Output**: `{OUTPUT_DIR}`
        - **Target Date**: {TARGET_DATE} (2025-001)
        """)
    return AUX_DIR, DOY_DIR, OUTPUT_DIR, TARGET_DATE, os


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 2. Read Daily RINEX Data

    Load all 96 files for the day using parallel processing.
    """)


@app.cell
def _(DOY_DIR, mo, os):
    from concurrent.futures import ProcessPoolExecutor, as_completed

    import xarray as xr
    from natsort import natsorted
    from tqdm import tqdm

    # Get all RINEX files for the day
    rinex_files = natsorted(DOY_DIR.glob("*.25o"))

    mo.md(f"""
    ### Reading {len(rinex_files)} RINEX Files

    Processing in parallel using {os.cpu_count()} cores...
    """)
    return ProcessPoolExecutor, as_completed, rinex_files, tqdm, xr


@app.cell
def _(ProcessPoolExecutor, as_completed, mo, rinex_files, tqdm, xr):
    from canvod_readers_parallel import read_rinex_file

    # Read in parallel
    datasets = []

    with ProcessPoolExecutor(max_workers=12) as executor:
        futures = {
            executor.submit(read_rinex_file, fpath): fpath for fpath in rinex_files
        }

        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Reading RINEX"
        ):
            fpath = futures[future]
            try:
                ds = future.result()
                datasets.append(ds)
            except Exception as e:
                print(f"❌ Failed: {fpath.name} — {e}")

    # Concatenate along epoch dimension
    daily_rinex = xr.concat(
        datasets,
        dim="epoch",
        join="outer",
        coords="different",
    )

    mo.md(f"""
    ✅ **RINEX Data Loaded**

    - **Dimensions**: {dict(daily_rinex.sizes)}
    - **Data Variables**: {list(daily_rinex.data_vars)}
    - **Time Range**: {daily_rinex.epoch.min().values} to {daily_rinex.epoch.max().values}
    - **Satellites**: {len(daily_rinex.sv)} unique SVs
    - **Signal IDs**: {len(daily_rinex.sid)} unique signals
    """)
    return daily_rinex, ds


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 3. Download/Load Auxiliary Files

    Fetch SP3 (ephemeris) and CLK (clock) files from CODE analysis center.
    """)


@app.cell
def _(TARGET_DATE, mo, os):
    from canvod.auxiliary import ClkFile, Sp3File

    # Configuration
    AGENCY = "COD"  # CODE Analysis Center
    PRODUCT_TYPE = "final"  # Rapid product (available within ~17 hours)
    FTP_SERVER = "ftp://gssc.esa.int/"  # ESA server (no authentication)

    # Get user email for potential NASA CDDIS fallback
    user_email = os.environ.get("CDDIS_MAIL")

    mo.md(f"""
    ### Download Configuration

    - **Agency**: {AGENCY} (CODE/Astronomical Institute, University of Bern)
    - **Product Type**: {PRODUCT_TYPE}
    - **FTP Server**: {FTP_SERVER}
    - **Target Date**: {TARGET_DATE}
    - **CDDIS Email**: {"✓ Configured" if user_email else "✗ Not set (ESA only)"}
    """)
    return AGENCY, ClkFile, FTP_SERVER, PRODUCT_TYPE, Sp3File, user_email


@app.cell
def _(
    AGENCY,
    AUX_DIR,
    ClkFile,
    FTP_SERVER,
    PRODUCT_TYPE,
    Sp3File,
    TARGET_DATE,
    mo,
    user_email,
):
    # Create auxiliary file handlers
    sp3_file = Sp3File.from_datetime_date(
        date=TARGET_DATE,
        agency=AGENCY,
        product_type=PRODUCT_TYPE,
        ftp_server=FTP_SERVER,
        local_dir=AUX_DIR / "01_SP3",
        user_email=user_email,
    )

    clk_file = ClkFile.from_datetime_date(
        date=TARGET_DATE,
        agency=AGENCY,
        product_type=PRODUCT_TYPE,
        ftp_server=FTP_SERVER,
        local_dir=AUX_DIR / "02_CLK",
        user_email=user_email,
    )

    mo.md(f"""
    ✅ **Auxiliary Files Ready**

    - **SP3 File**: `{sp3_file.fpath.name if sp3_file.fpath else "Generating..."}`
    - **CLK File**: `{clk_file.fpath.name if clk_file.fpath else "Generating..."}`

    Files will be downloaded if not already cached locally.
    """)
    return clk_file, sp3_file


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 4. Load Auxiliary Data

    Load SP3 and CLK files into xarray datasets.
    """)


@app.cell
def _(sp3_file):
    # Load data (will download if needed)
    sp3_data = sp3_file.data

    sp3_data
    return (sp3_data,)


@app.cell
def _(clk_file, mo, sp3_data):
    clk_data = clk_file.data

    mo.md(f"""
    ✅ **Auxiliary Data Loaded**

    ### SP3 (Ephemeris)
    - **Dimensions**: {dict(sp3_data.sizes)}
    - **Variables**: {list(sp3_data.data_vars)}
    - **Satellites**: {len(sp3_data.sv)}
    - **Epochs**: {len(sp3_data.epoch)}
    - **Sampling**: {sp3_data.attrs.get("sampling_rate", "N/A")}

    ### CLK (Clock)
    - **Dimensions**: {dict(clk_data.sizes)}
    - **Variables**: {list(clk_data.data_vars)}
    - **Satellites**: {len(clk_data.sv)}
    - **Epochs**: {len(clk_data.epoch)}
    """)
    return (clk_data,)


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 5. Preprocess Auxiliary Data (Following gnssvodpy Pipeline)

    This is the critical step that gnssvodpy uses:
    1. Interpolate SP3 ephemeris using **Hermite cubic splines with velocities**
    2. Interpolate CLK clock using **piecewise linear with discontinuity detection**

    **This follows the exact preprocessing steps from gnssvodpy's processor.py**
    """)


@app.cell
def _(clk_data, daily_rinex, mo, sp3_data):
    import numpy as np
    from canvod.auxiliary.interpolation import (
        ClockConfig,
        ClockInterpolationStrategy,
        Sp3Config,
        Sp3InterpolationStrategy,
    )

    # Get target epochs from RINEX
    target_epochs = daily_rinex.epoch.values

    # 1. Interpolate ephemerides using Hermite splines
    mo.md("Interpolating ephemerides with Hermite cubic splines...")
    sp3_config = Sp3Config(use_velocities=True, fallback_method="linear")
    sp3_interpolator = Sp3InterpolationStrategy(config=sp3_config)
    sp3_interp = sp3_interpolator.interpolate(sp3_data, target_epochs)

    # Store interpolation metadata
    sp3_interp.attrs["interpolator_config"] = sp3_interpolator.to_attrs()

    # 2. Interpolate clock corrections using piecewise linear
    mo.md("Interpolating clock corrections with piecewise linear...")
    clock_config = ClockConfig(window_size=9, jump_threshold=1e-6)
    clock_interpolator = ClockInterpolationStrategy(config=clock_config)
    clk_interp = clock_interpolator.interpolate(clk_data, target_epochs)

    # Store interpolation metadata
    clk_interp.attrs["interpolator_config"] = clock_interpolator.to_attrs()

    mo.md(f"""
    ✅ **Auxiliary Data Preprocessed**

    ### Interpolated Ephemerides (Hermite Splines)
    - **Method**: Cubic Hermite with velocities
    - **Dimensions**: {dict(sp3_interp.sizes)}
    - **Epochs**: {len(sp3_interp.epoch)}
    - **Variables**: {list(sp3_interp.data_vars)}

    ### Interpolated Clock (Piecewise Linear)
    - **Method**: Discontinuity-aware piecewise linear
    - **Dimensions**: {dict(clk_interp.sizes)}
    - **Epochs**: {len(clk_interp.epoch)}
    - **Variables**: {list(clk_interp.data_vars)}

    **Now ready for coordinate computation!**
    """)
    return clk_interp, np, sp3_interp


@app.cell
def _(sp3_file):
    sp3_file.data


@app.cell
def _():
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 6. Extract Receiver Position

    Extract ECEF position from RINEX metadata.
    """)


@app.cell
def _(daily_rinex, mo):
    from canvod.auxiliary import ECEFPosition

    # Extract receiver position from RINEX metadata
    receiver_position = ECEFPosition.from_ds_metadata(daily_rinex)

    # Convert to geodetic for display
    lat, lon, alt = receiver_position.to_geodetic()

    mo.md(f"""
    ✅ **Receiver Position Extracted**

    ### ECEF (Earth-Centered, Earth-Fixed)
    - **X**: {receiver_position.x:.3f} m
    - **Y**: {receiver_position.y:.3f} m
    - **Z**: {receiver_position.z:.3f} m

    ### Geodetic (WGS84)
    - **Latitude**: {lat:.6f}°
    - **Longitude**: {lon:.6f}°
    - **Altitude**: {alt:.1f} m
    """)
    return (receiver_position,)


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 7. Compute Spherical Coordinates

    Use interpolated aux data to compute (φ, θ, r) directly.

    **This follows gnssvodpy's _compute_spherical_coords_fast() approach.**
    """)


@app.cell
def _(aux_slice, ds, receiver_position):
    ds_augmented = _compute_spherical_coords_fast(ds, aux_slice, receiver_position)


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ### 7.1 Matching of SID

    At some point, a set of desired SIDs needs to be defined. This set is then used to ensure tha both RINEX and aux data share these exacts SIDs.

    For simplicity, here we check which SIDs are common to ephemerides, clock and RINEX files and stick to these.

    First, though, aux data itself needs to be preprocessed to be of dimension `sid` instead of `sv`.
    """)


@app.cell
def _(clk_data, sp3_data, xr):
    # first_ds = datasets[0]

    # time_diff = (first_ds.epoch[1] - first_ds.epoch[0]).values
    # sampling_interval = float(time_diff / np.timedelta64(1, 's'))

    # first_epoch = first_ds.epoch.values[0]
    # day_start = np.datetime64(first_epoch.astype('datetime64[D]'))
    # day_end = day_start + np.timedelta64(1, 'D')

    # # Create uniform epoch grid for entire day
    # n_epochs = int(24 * 3600 / sampling_interval)
    # target_epochs = day_start + np.arange(n_epochs) * np.timedelta64(
    #     int(sampling_interval), 's')

    aux_processed = xr.merge([sp3_data, clk_data])
    aux_processed


@app.cell
def _(clk_interp, daily_rinex, mo, receiver_position, sp3_interp):
    from canvod.auxiliary.position import (
        add_spherical_coords_to_dataset,
        compute_spherical_coordinates,
    )

    # Get satellite positions from interpolated ephemerides
    sat_x = sp3_interp["X"].values
    sat_y = sp3_interp["Y"].values
    sat_z = sp3_interp["Z"].values

    # Compute spherical coordinates
    r, theta, phi = compute_spherical_coordinates(
        sat_x, sat_y, sat_z, receiver_position
    )

    # Add to dataset
    augmented_ds = add_spherical_coords_to_dataset(daily_rinex.copy(), r, theta, phi)

    # Optionally add clock corrections
    if "clock" in clk_interp.data_vars:
        augmented_ds = augmented_ds.assign({"clock": clk_interp["clock"]})

    mo.md(f"""
    ✅ **Spherical Coordinates Computed**

    ### New Variables Added
    - **phi (φ)**: Azimuthal angle from North, clockwise [0, 2π) radians (0 = North, π/2 = East)
    - **theta (θ)**: Polar angle from zenith [0, π] radians
    - **r**: Slant range in meters

    ### Augmented Dataset
    - **Dimensions**: {dict(augmented_ds.sizes)}
    - **Variables**: {list(augmented_ds.data_vars)}

    🎉 **Complete gnssvodpy preprocessing pipeline implemented in canvodpy!**
    """)
    return (augmented_ds,)


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 8. Visualize Spherical Coordinates

    Examine the computed coordinates for a sample satellite.
    """)


@app.cell
def _(augmented_ds, mo):
    # Select a satellite to visualize
    sample_sv = augmented_ds.sv.values[0]
    sv_data = augmented_ds.sel(sv=sample_sv)

    mo.md(f"""
    ### Sample Satellite: {sample_sv}

    Examining spherical coordinate evolution over the day...
    """)
    return sample_sv, sv_data


@app.cell
def _(np, sample_sv, sv_data):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

    # Phi (azimuth)
    axes[0].plot(sv_data.epoch, sv_data.phi.sel(sid=sv_data.sid[0]), marker=".")
    axes[0].set_ylabel("φ (azimuth) [rad]")
    axes[0].set_title(f"Spherical Coordinates for {sample_sv} (Navigation Convention)")
    axes[0].grid(True, alpha=0.3)
    axes[0].axhline(y=0, color="r", linestyle="--", alpha=0.3, label="0 (North)")
    axes[0].axhline(
        y=np.pi / 2, color="g", linestyle="--", alpha=0.3, label="π/2 (East)"
    )
    axes[0].axhline(y=np.pi, color="b", linestyle="--", alpha=0.3, label="π (South)")
    axes[0].legend(loc="upper right", fontsize=8)

    # Theta (polar angle)
    axes[1].plot(
        sv_data.epoch, sv_data.theta.sel(sid=sv_data.sid[0]), marker=".", color="orange"
    )
    axes[1].set_ylabel("θ (polar angle) [rad]")
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(y=0, color="g", linestyle="--", alpha=0.3, label="0 (Zenith)")
    axes[1].axhline(
        y=np.pi / 2, color="r", linestyle="--", alpha=0.3, label="π/2 (Horizon)"
    )
    axes[1].legend(loc="upper right", fontsize=8)

    # R (distance)
    axes[2].plot(
        sv_data.epoch,
        sv_data.r.sel(sid=sv_data.sid[0]) / 1e6,
        marker=".",
        color="green",
    )
    axes[2].set_ylabel("r (distance) [Mm]")
    axes[2].set_xlabel("Epoch (UTC)")
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.gca()


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 9. Save Augmented Dataset

    Export to NetCDF for further processing.
    """)


@app.cell
def _(OUTPUT_DIR, augmented_ds, mo):
    # Save augmented dataset
    output_file = OUTPUT_DIR / "augmented_canopy_25001.nc"

    augmented_ds.to_netcdf(
        output_file,
        encoding={
            var: {"zlib": True, "complevel": 5} for var in augmented_ds.data_vars
        },
    )

    file_size_mb = output_file.stat().st_size / 1024 / 1024

    mo.md(f"""
    ✅ **Dataset Saved**

    - **File**: `{output_file.name}`
    - **Size**: {file_size_mb:.2f} MB
    - **Path**: `{output_file}`

    Ready for VOD calculation!
    """)


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## Summary

    ✅ **Loaded** 96 RINEX files (parallel processing)
    ✅ **Downloaded** SP3 and CLK auxiliary files
    ✅ **Interpolated** ephemerides (Hermite splines with velocities)
    ✅ **Interpolated** clock (piecewise linear, discontinuity-aware)
    ✅ **Extracted** receiver position (ECEF → Geodetic)
    ✅ **Computed** spherical coordinates (φ, θ, r)
    ✅ **Visualized** satellite trajectories
    ✅ **Saved** augmented dataset to NetCDF

    ### 🎉 Complete Migration!

    **All gnssvodpy preprocessing steps now in canvodpy:**

    | Component | Package | Status |
    |-----------|---------|--------|
    | RINEX Reading | canvod-readers | ✅ |
    | Auxiliary Files | canvod-aux | ✅ |
    | **Interpolation** | **canvod.auxiliary.interpolation** | **✅ NEW!** |
    | Position Classes | canvod.auxiliary.position | ✅ |
    | Spherical Coords | canvod.auxiliary.position | ✅ |

    **Preprocessing follows gnssvodpy's exact pipeline:**
    - Hermite cubic splines for ephemeris (uses satellite velocities)
    - Piecewise linear for clock (handles discontinuities)
    - Direct coordinate computation (no DatasetMatcher needed for this workflow)

    **No gnssvodpy dependencies!**
    """)


if __name__ == "__main__":
    app.run()
