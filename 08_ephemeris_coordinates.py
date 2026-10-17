# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvod-auxiliary",
#   "canvod-config",
#   "canvod-grids",
#   "canvod-ops",
#   "canvod-preflight",
#   "canvod-readers",
#   "canvod-store",
#   "canvod-store-metadata",
#   "canvod-utils",
#   "canvod-viz",
#   "canvod-vod",
#   "canvodpy",
#   "zarr>=3.1.2",
#   "marimo>=0.21.1",
#   "pyyaml==6.0.3",
#   "numpy==2.5.4",
#   "xarray==2026.9.0",
# ]
#
# [tool.uv.sources]
# canvod-auxiliary = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-auxiliary", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-config = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-config", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-grids = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-grids", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-ops = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-ops", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-preflight = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-preflight", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-readers = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-readers", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-store = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-store", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-store-metadata = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-store-metadata", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-utils = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-utils", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-viz = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-viz", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvod-vod = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-vod", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
# canvodpy = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "canvodpy", rev = "c979f38b33048852ed3c2c4c6b4ab10b5b85f654" }
#
# [tool.marimo.opengraph]
# title = "08 · Ephemeris & Coordinate Augmentation"
# description = "Augment GNSS observations with precise SP3/CLK satellite ephemeris. Transform ECEF positions to receiver-relative spherical coordinates (polar angle θ, azimuth φ)."
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium",
    app_title="Ephemeris & Coordinate Augmentation",
    css_file="canvod_nordic.css",
    html_head_file="canvod_head.html",
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

    # Ephemeris and Coordinate Augmentation

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/08_ephemeris_coordinates.py?mode=edit)

    The **canvod-auxiliary** package augments GNSS observation datasets with
    satellite geometry: the azimuth and polar angle from the receiver
    to each satellite at each epoch.

    These angles are essential for GNSS-T:

    - **Polar angle ($\theta$)** enters the VOD formula directly:
      $\text{VOD} = -\ln(T) \cdot \cos(\theta)$.  It corrects for the
      varying path length through the canopy at different satellite
      elevations.

    - **Azimuth ($\phi$)** determines which hemispheric grid cell an
      observation is assigned to, enabling spatial mapping of canopy
      properties.

    The augmentation pipeline works in two steps:

    1. **Preprocessing**: download SP3 orbit and CLK clock files for the
       observation day $n$ and for the days $n-1$ and $n+1$, interpolate
       satellite ECEF positions to the observation sampling rate (5 s), and
       cache the result as a Zarr store. The two shouldering days increase
       the interpolation accuracy at the beginning and the end of day $n$.

    2. **Augmentation**: for each observation epoch, compute the satellite
       position in the receiver's local East-North-Up (ENU) frame, then
       convert to spherical coordinates ($r$, $\theta$, $\phi$).

    ---

    **Test data**: `demo_data()` downloads the CODE final SP3/CLK products
    for DOY 2025-001; this notebook computes the auxiliary store from them.

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
    import pathlib

    import yaml

    from canvod.utils import testing

    work = pathlib.Path(tempfile.mkdtemp(prefix="canvodpy_demo_"))
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


# ---------------------------------------------------------------------------
# Imports and paths
# ---------------------------------------------------------------------------


@app.cell
def _(root, work):
    from pathlib import Path

    import numpy as np

    canopy_dir = root / "rinex_v3_04" / "01_Rosalia" / "02_canopy" / "01_GNSS" / "01_raw"
    aux_root = work / "aux_data"
    sp3_dir = aux_root / "01_SP3"

    return canopy_dir, aux_root, Path, sp3_dir, np


# ---------------------------------------------------------------------------
# Section: receiver position
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Receiver position

    The receiver's ECEF (Earth-Centered, Earth-Fixed) position is the
    reference point for computing satellite azimuth and elevation.  In
    canvodpy, this position is always extracted from the RINEX header
    (`APPROX POSITION XYZ` record), never from configuration files.

    ECEF coordinates express the receiver location in a Cartesian frame
    fixed to the rotating Earth, with the origin at the Earth's centre of
    mass.
    """
    )

    return


@app.cell
def _(canopy_dir, mo):
    from canvod.auxiliary import ECEFPosition
    from canvod.readers import Rnxv3Obs

    _file = sorted(canopy_dir.glob("25001/*.rnx"))[0]
    _reader = Rnxv3Obs(fpath=_file)
    ds_single = _reader.to_ds(keep_data_vars=["SNR"], write_global_attrs=True)

    rx_pos = ECEFPosition.from_ds_metadata(ds_single)

    _lat, _lon, _alt = rx_pos.to_geodetic()

    mo.md(
        f"""
    ### Canopy receiver

    ```python
    from canvod.auxiliary import ECEFPosition

    rx_pos = ECEFPosition.from_ds_metadata(ds)
    ```

    | Coordinate | Value |
    |------------|-------|
    | **X** | {rx_pos.x:,.3f} m |
    | **Y** | {rx_pos.y:,.3f} m |
    | **Z** | {rx_pos.z:,.3f} m |
    | **Latitude** | {_lat:.6f} deg |
    | **Longitude** | {_lon:.6f} deg |
    | **Altitude** | {_alt:.1f} m |

    `ECEFPosition.from_ds_metadata(ds)` reads the `APPROX POSITION X/Y/Z`
    attributes that the RINEX reader stores in the dataset.  The
    `to_geodetic()` method converts to WGS-84 latitude, longitude, and
    ellipsoidal height.
    """
    )

    return ECEFPosition, Rnxv3Obs, ds_single, rx_pos


# ---------------------------------------------------------------------------
# Section: ephemeris products
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvod.auxiliary import list_agencies, list_products

    _agencies = list_agencies()
    _products = list_products()

    _rows = []
    for _a, _t in _products[:12]:
        _rows.append(f"| `{_a}` | `{_t}` |")

    mo.md(
        f"""
    ## Ephemeris products

    Satellite orbits are distributed as **SP3** files (precise positions
    at 5--15 minute intervals) and **CLK** files (satellite clock
    corrections at 5--30 second intervals).  Multiple analysis centres
    produce these products with varying latency and accuracy.

    | Agency | Product type |
    |--------|-------------|
    {chr(10).join(_rows)}
    | ... | ({len(_products)} products from {len(_agencies)} agencies total) |

    | Product tier | Latency | Orbit accuracy | Use case |
    |-------------|---------|----------------|----------|
    | **Final** | 12--18 days | ~2 cm | Archival analysis |
    | **Rapid** | 17--41 hours | ~2--3 cm | Near-real-time |
    | **Ultra-rapid** | 3--9 hours | ~5 cm | Not supported: refused in the settings |
    | **Broadcast** | Real-time | ~1--2 m | SBF fast path |

    For GNSS-T at 2-degree grid resolution, even broadcast ephemeris is
    sufficient: the angular difference between broadcast and final orbits
    is approximately 0.1 degrees, which is 20x smaller than the grid cell
    size.
    """
    )

    return list_agencies, list_products


# ---------------------------------------------------------------------------
# Section: pre-computed auxiliary data
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Auxiliary data computed from SP3/CLK

    The auxiliary store is not shipped pre-computed.  The next cell uses the
    `AgencyEphemerisProvider` to build it from the CODE final SP3/CLK products
    that `demo_data()` downloads for DOY 2025-001, using Hermite cubic spline
    interpolation to the observation sampling rate.
    """
    )

    return


@app.cell
def _(aux_root, ds_single, mo, np, rx_pos):
    import xarray as xr

    from canvod.auxiliary.ephemeris.provider import AgencyEphemerisProvider
    from canvod.auxiliary.interpolation import sampling_interval_from_epochs

    provider = AgencyEphemerisProvider(
        agency="COD", product_type="final", aux_data_dir=aux_root, fetch_clock=True
    )
    provider.preprocess_day("2025001", None)

    # Write the interpolated store for this file's sampling rate, then read it back
    provider.augment_dataset(ds_single, rx_pos)

    _interval = sampling_interval_from_epochs(ds_single.epoch.values)
    ds_aux = xr.open_zarr(
        str(aux_root / f"aux_2025001_{_interval:g}s.zarr"),
        decode_timedelta=False,
        consolidated=False,
    )

    _var_rows = []
    for _v in ds_aux.data_vars:
        _arr = ds_aux[_v]
        _valid_pct = (
            np.isfinite(_arr.values).sum() / _arr.values.size * 100
            if _arr.values.dtype.kind == "f"
            else 100.0
        )
        _unit = _arr.attrs.get("units", "---")
        _var_rows.append(f"| `{_v}` | `{_arr.dtype}` | {_unit} | {_valid_pct:.0f}% |")

    mo.md(
        f"""
    ### Auxiliary Zarr store contents

    **Source**: CODE final SP3/CLK products for DOY 2025-001, downloaded by
    `demo_data()` and interpolated to the observation sampling rate.
    **Path**: `aux_data/aux_2025001_{_interval:g}s.zarr`
    **Dimensions**: `{dict(ds_aux.sizes)}`

    | Variable | Dtype | Units | Valid |
    |----------|-------|-------|-------|
    {chr(10).join(_var_rows)}

    The `X`, `Y`, `Z` variables are satellite ECEF coordinates in meters,
    interpolated from the 5-minute SP3 samples to the 5-second observation grid.
    `Vx`, `Vy`, `Vz` are velocity components computed by central differencing
    of the position time series.  `clock_offset` is the satellite clock
    correction interpolated from CLK 30-second samples.

    The store contains **{ds_aux.sizes["sid"]}** SIDs across all
    constellations and **{ds_aux.sizes["epoch"]:,}** epochs.
    """
    )

    return ds_aux, xr


# ---------------------------------------------------------------------------
# Section: coordinate computation
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Coordinate computation

    The `compute_spherical_coordinates()` function converts satellite ECEF
    positions to spherical coordinates in the receiver's local ENU frame.

    The transformation chain is:

    1. **ECEF to ENU**: rotate the satellite-receiver vector into the local
       East-North-Up frame at the receiver location
    2. **ENU to spherical**: compute range ($r$), polar angle ($\theta$),
       and azimuth ($\phi$)

    ### Coordinate conventions

    | Coordinate | Symbol | Range | Convention |
    |-----------|--------|-------|------------|
    | **Range** | $r$ | > 0 | Distance in meters |
    | **Polar angle** | $\theta$ | [0, $\pi$] | 0 = overhead, $\pi/2$ = horizon |
    | **Azimuth** | $\phi$ | [0, $2\pi$) | 0 = North, $\pi/2$ = East (navigation) |

    Observations below the horizon ($\theta > \pi/2$) are masked to NaN.
    This follows the navigation convention where $\phi$ increases clockwise
    from North, consistent with the geographic azimuth used in hemispheric
    grid definitions.
    """
    )

    return


@app.cell
def _(ds_aux, ds_single, mo, np, rx_pos):
    from canvod.auxiliary import compute_spherical_coordinates

    _shared_sids = np.intersect1d(ds_single.sid.values, ds_aux.sid.values)
    _shared_epochs = np.intersect1d(ds_single.epoch.values, ds_aux.epoch.values)

    _aux_sel = ds_aux.sel(sid=_shared_sids, epoch=_shared_epochs)

    _r, _theta, _phi = compute_spherical_coordinates(
        _aux_sel["X"].values,
        _aux_sel["Y"].values,
        _aux_sel["Z"].values,
        rx_pos,
    )

    _valid_theta = np.isfinite(_theta)

    mo.md(
        f"""
    ### Computed angles for one 15-minute file

    Aligning observation epochs with auxiliary data and computing coordinates:

    ```python
    from canvod.auxiliary import compute_spherical_coordinates

    r, theta, phi = compute_spherical_coordinates(
        aux["X"].values, aux["Y"].values, aux["Z"].values,
        rx_pos,
    )
    ```

    | Statistic | $\\theta$ (polar) | $\\phi$ (azimuth) |
    |-----------|-------------------|-------------------|
    | **Valid values** | {_valid_theta.sum():,} | {np.isfinite(_phi).sum():,} |
    | **Min** | {np.nanmin(_theta):.4f} rad ({np.rad2deg(np.nanmin(_theta)):.2f} deg) | {np.nanmin(_phi):.4f} rad |
    | **Max** | {np.nanmax(_theta):.4f} rad ({np.rad2deg(np.nanmax(_theta)):.2f} deg) | {np.nanmax(_phi):.4f} rad |
    | **Mean** | {np.nanmean(_theta):.4f} rad ({np.rad2deg(np.nanmean(_theta)):.2f} deg) | {np.nanmean(_phi):.4f} rad |

    Polar angles cluster around 0.4--1.4 rad (23--80 degrees from zenith),
    reflecting the typical elevation range of visible GNSS satellites.
    Values near $\\pi/2$ (1.57 rad, 90 degrees) correspond to satellites
    close to the horizon, which are typically excluded from VOD analysis
    due to long, oblique signal paths through the canopy.
    """
    )

    return (compute_spherical_coordinates,)


# ---------------------------------------------------------------------------
# Section: augmenting a dataset
# ---------------------------------------------------------------------------


@app.cell
def _(ds_aux, ds_single, mo, np, rx_pos):
    from canvod.auxiliary import add_spherical_coords_to_dataset
    from canvod.auxiliary import compute_spherical_coordinates as _csc

    _shared_sids = np.intersect1d(ds_single.sid.values, ds_aux.sid.values)
    _shared_epochs = np.intersect1d(ds_single.epoch.values, ds_aux.epoch.values)

    _aux_sel = ds_aux.sel(sid=_shared_sids, epoch=_shared_epochs)
    _ds_sel = ds_single.sel(sid=_shared_sids, epoch=_shared_epochs)

    _r, _theta, _phi = _csc(
        _aux_sel["X"].values,
        _aux_sel["Y"].values,
        _aux_sel["Z"].values,
        rx_pos,
    )

    ds_augmented = add_spherical_coords_to_dataset(_ds_sel, _r, _theta, _phi)

    mo.md(
        f"""
    ## Augmented dataset

    `add_spherical_coords_to_dataset()` attaches the computed coordinates
    as new data variables with CF-compliant metadata:

    ```python
    ds_augmented = add_spherical_coords_to_dataset(ds, r, theta, phi)
    ```

    **New variables**:

    | Variable | Shape | Units | Description |
    |----------|-------|-------|-------------|
    | `theta` | (epoch, sid) | radians | Polar angle |
    | `phi` | (epoch, sid) | radians | Azimuth |
    | `r` | (epoch, sid) | meters | Range to satellite |

    **Dataset dimensions**: `{dict(ds_augmented.sizes)}`
    **Data variables**: {list(ds_augmented.data_vars)}

    The augmented dataset now contains everything needed for VOD retrieval:
    SNR observations and satellite geometry.
    """
    )

    return (ds_augmented,)


@app.cell
def _(ds_augmented):
    ds_augmented

    return


# ---------------------------------------------------------------------------
# Section: ephemeris provider abstraction
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Ephemeris providers

    The `EphemerisProvider` abstract base class defines a two-step interface
    for augmenting datasets with satellite geometry:

    ```python
    class EphemerisProvider(ABC):
        def preprocess_day(date, site_config) -> Path | None
        def augment_dataset(ds, receiver_position) -> xr.Dataset
    ```

    Two concrete implementations exist:

    ### AgencyEphemerisProvider (SP3/CLK)

    Downloads post-processed precise orbits from an analysis centre, then
    interpolates satellite positions using **Hermite cubic splines** (which
    use both SP3 positions and velocities for continuity).

    ```python
    from canvod.auxiliary.ephemeris.provider import AgencyEphemerisProvider

    provider = AgencyEphemerisProvider(
        agency="COD",           # CODE (Bern)
        product_type="final",   # ~2 cm orbit accuracy
        aux_data_dir=aux_dir,   # Cache directory
    )
    provider.preprocess_day("2025001", site_config)
    ds = provider.augment_dataset(ds, rx_pos)
    ```

    ### SbfBroadcastProvider

    Extracts satellite geometry directly from the SBF `SatVisibility` block;
    the receiver firmware computes azimuth and elevation in real time
    using the broadcast navigation message.

    ```python
    from canvod.auxiliary.ephemeris.provider import SbfBroadcastProvider

    provider = SbfBroadcastProvider()
    ds = provider.augment_dataset(ds, rx_pos, aux_datasets={"sbf_obs": meta_ds})
    ```

    No preprocessing step is needed: the geometry is already embedded in
    the SBF file.  This path is faster but less accurate (~1--2 m orbit
    error vs ~2 cm for final products).
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: interpolation details
# ---------------------------------------------------------------------------


@app.cell
def _(sp3_dir, mo):
    _sp3_files = sorted(sp3_dir.glob("*.SP3"))

    _sp3_info = ""
    if _sp3_files:
        _sp3_info = "<br>".join(f"`{_f.name}`" for _f in _sp3_files)
    else:
        _sp3_info = "(no SP3 files in test data)"

    mo.md(
        f"""
    ## Interpolation method

    The auxiliary Zarr store is produced by interpolating SP3 positions
    (typically at 5-minute intervals) to the observation sampling rate
    (5 seconds).

    | Property | Value |
    |----------|-------|
    | **SP3 files** | {_sp3_info} |
    | **Days** | $n-1$, $n$, $n+1$ (1 h of each neighboring day) |
    | **SP3 interval** | 5 minutes (289 positions per daily file, 00:00 to 24:00) |
    | **Target interval** | 5 seconds (17,280 positions per day) |
    | **Method** | `scipy.CubicHermiteSpline` (piecewise cubic) |
    | **Velocities** | Computed from the SP3 positions (central differences), used as Hermite derivatives |
    | **Clock method** | Piecewise linear with jump detection |

    The orbits and clocks of the two shouldering days, $n-1$ and $n+1$,
    are fetched as well, and one hour of each is joined to day $n$. This
    increases the interpolation accuracy at the beginning and the end of
    the day: from a single daily file, no samples would be available
    beyond the day's edges, and the spline would not fit as well there.

    The Hermite spline uses both SP3 positions and velocities as boundary
    conditions for each cubic segment.  This produces C1-continuous
    trajectories (continuous position and velocity) without the Runge
    phenomenon that affects high-degree polynomial fits.
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

    **Previous**: [07 · Satellite Catalog](./07_satellite_catalog.py)
    | **Next**: [09 · Hemispheric Grids](./09_hemispheric_grids.py)

    *canVODpy · Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
