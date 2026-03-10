import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium", css_file="canvod_nordic.css")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        r"""
    # GNSS Vegetation Optical Depth — Processing Workflow

    This notebook walks through the complete VOD retrieval pipeline, from raw
    RINEX observations to gridded Vegetation Optical Depth.  Each processing
    step is configurable — adjust the controls below to explore how settings
    affect the output.

    **Data:** Rosalia mixed-forest research site (Austria), DOY 2025-001,
    RINEX v3.04, 5 s sampling, 15-min files.

    ---

    *Nicolas F. Bader, CLIMERS — TU Wien*
    *Licensed under Apache 2.0.  Provided "as is" without warranty of any kind.*
    """
    )


@app.cell
def _():
    from pathlib import Path

    import numpy as np
    import xarray as xr

    return Path, np, xr


@app.cell
def _():
    from _paths import AUX_DATA_DIR, ROSALIA_CANOPY_DIR, ROSALIA_REFERENCE_DIR

    RINEX_CANOPY_DIR = ROSALIA_CANOPY_DIR / "25001"
    RINEX_REFERENCE_DIR = ROSALIA_REFERENCE_DIR / "25001"

    return AUX_DATA_DIR, RINEX_CANOPY_DIR, RINEX_REFERENCE_DIR


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Processing Settings

    Configure each stage of the pipeline.  Changes are applied reactively —
    downstream cells re-execute automatically.
    """
    )


@app.cell
def _(mo):
    n_files_slider = mo.ui.slider(
        start=1,
        stop=96,
        value=4,
        step=1,
        label="Files per receiver (96 = full day)",
    )
    n_files_slider

    return (n_files_slider,)


@app.cell
def _(mo):
    grid_type_dropdown = mo.ui.dropdown(
        options=["equal_area", "equal_angle", "fibonacci", "healpix", "geodesic", "HTM"],
        value="equal_area",
        label="Grid type",
    )
    angular_res_slider = mo.ui.slider(
        start=2,
        stop=30,
        value=10,
        step=1,
        label="Angular resolution (deg)",
    )
    cutoff_slider = mo.ui.slider(
        start=0,
        stop=30,
        value=5,
        step=1,
        label="Elevation cutoff (deg)",
    )

    mo.hstack(
        [grid_type_dropdown, angular_res_slider, cutoff_slider],
        justify="start",
        gap=1,
    )

    return angular_res_slider, cutoff_slider, grid_type_dropdown


# ---------------------------------------------------------------------------
# Step 1 — Read RINEX
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Step 1 — Read RINEX Observations

    The **canvod-readers** package parses RINEX v3.04 files into
    `xarray.Dataset` objects with dimensions `(epoch, sid)`.  Each signal ID
    (*sid*) encodes constellation, PRN, band, and tracking code — e.g.
    `G01_L1_C` for GPS PRN 01, L1 band, C/A code.

    The slider above controls how many 15-minute files are loaded per
    receiver.  Processing a full day (96 files) takes longer but produces
    complete diurnal coverage.
    """
    )


@app.cell
def _(RINEX_CANOPY_DIR, RINEX_REFERENCE_DIR, n_files_slider, xr):
    from canvod.auxiliary import ECEFPosition
    from canvod.readers import Rnxv3Obs

    _canopy_files = sorted(RINEX_CANOPY_DIR.glob("*.rnx"))[: n_files_slider.value]
    _reference_files = sorted(RINEX_REFERENCE_DIR.glob("*.rnx"))[: n_files_slider.value]

    # Read all files; extract receiver position from first RINEX header
    _canopy_readers = [Rnxv3Obs(fpath=f) for f in _canopy_files]
    _reference_readers = [Rnxv3Obs(fpath=f) for f in _reference_files]

    canopy_raw = xr.concat([r.to_ds() for r in _canopy_readers], dim="epoch")
    reference_raw = xr.concat([r.to_ds() for r in _reference_readers], dim="epoch")

    # ECEF position from RINEX header (approximate receiver coordinates)
    _cp = _canopy_readers[0].header.approx_position
    canopy_pos = ECEFPosition(x=_cp[0].magnitude, y=_cp[1].magnitude, z=_cp[2].magnitude)

    _rp = _reference_readers[0].header.approx_position
    reference_pos = ECEFPosition(x=_rp[0].magnitude, y=_rp[1].magnitude, z=_rp[2].magnitude)

    return ECEFPosition, Rnxv3Obs, canopy_pos, canopy_raw, reference_pos, reference_raw


@app.cell
def _(canopy_raw, mo, reference_raw):
    mo.md(
        f"""
    ### Result

    | | Canopy | Reference |
    |---|---|---|
    | Epochs | {canopy_raw.sizes['epoch']:,} | {reference_raw.sizes['epoch']:,} |
    | Signal IDs | {canopy_raw.sizes['sid']:,} | {reference_raw.sizes['sid']:,} |
    | Time span | {str(canopy_raw.epoch.values[0])[:19]} — {str(canopy_raw.epoch.values[-1])[:19]} | {str(reference_raw.epoch.values[0])[:19]} — {str(reference_raw.epoch.values[-1])[:19]} |
    | Variables | {', '.join(f'`{v}`' for v in canopy_raw.data_vars)} | {', '.join(f'`{v}`' for v in reference_raw.data_vars)} |
    """
    )


# ---------------------------------------------------------------------------
# Step 2 — Augment with Ephemeris
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Step 2 — Satellite Coordinate Augmentation

    Raw RINEX files contain only SNR values.  To compute VOD we need the
    elevation (*theta*) and azimuth (*phi*) of each satellite as seen from
    the receiver.

    The **canvod-auxiliary** package loads precise orbit (SP3) and clock
    (CLK) products, interpolates satellite positions to observation epochs
    using Hermite interpolation, then transforms ECEF coordinates to the
    local horizon frame of the receiver.

    The receiver position is extracted automatically from the RINEX header
    (approximate position in ECEF).
    """
    )


@app.cell
def _(AUX_DATA_DIR, canopy_pos, canopy_raw, reference_pos, reference_raw):
    from canvodpy.functional import augment_with_ephemeris

    canopy_aug = augment_with_ephemeris(
        canopy_raw,
        canopy_pos,
        source="final",
        agency="COD",
        date="2025001",
        aux_data_dir=AUX_DATA_DIR,
    )
    reference_aug = augment_with_ephemeris(
        reference_raw,
        reference_pos,
        source="final",
        agency="COD",
        date="2025001",
        aux_data_dir=AUX_DATA_DIR,
    )

    return augment_with_ephemeris, canopy_aug, reference_aug


@app.cell
def _(canopy_aug, mo, np):
    _theta = canopy_aug["theta"].values
    _valid = np.isfinite(_theta)
    _pct = 100 * _valid.sum() / _valid.size

    mo.md(
        f"""
    ### Result

    After augmentation the dataset has **`theta`** (elevation) and **`phi`**
    (azimuth) coordinates for every `(epoch, sid)` pair.

    - Valid satellite positions: **{_pct:.1f}%** of all observations
    - Theta range: {np.nanmin(_theta):.1f}° — {np.nanmax(_theta):.1f}°
    - New variables: {', '.join(f'`{v}`' for v in canopy_aug.data_vars)}
    """
    )


# ---------------------------------------------------------------------------
# Step 3 — VOD Calculation
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Step 3 — Vegetation Optical Depth

    The **canvod-vod** package implements the zeroth-order tau-omega model.
    VOD is derived from the ratio of canopy SNR to reference (open-sky) SNR,
    corrected for the satellite elevation angle.

    The model assumes that the GNSS signal is attenuated exponentially as it
    passes through the vegetation canopy:

    $$
    \text{SNR}_{\text{canopy}} = \text{SNR}_{\text{reference}} \cdot e^{-\tau / \cos\theta}
    $$

    Solving for the optical depth $\tau$ (VOD):

    $$
    \tau = -\cos\theta \cdot \ln\!\left(\frac{\text{SNR}_{\text{canopy}}}{\text{SNR}_{\text{reference}}}\right)
    $$
    """
    )


@app.cell
def _(canopy_aug, reference_aug):
    from canvodpy.functional import calculate_vod

    vod_ds = calculate_vod(canopy_aug, reference_aug)

    return calculate_vod, vod_ds


@app.cell
def _(mo, np, vod_ds):
    _vod = vod_ds["VOD"].values
    _valid = np.isfinite(_vod)

    mo.md(
        f"""
    ### Result

    | Metric | Value |
    |---|---|
    | Valid VOD observations | {_valid.sum():,} |
    | Mean VOD | {np.nanmean(_vod):.3f} |
    | Median VOD | {np.nanmedian(_vod):.3f} |
    | Std VOD | {np.nanstd(_vod):.3f} |
    | Range | {np.nanmin(_vod):.3f} — {np.nanmax(_vod):.3f} |
    """
    )


# ---------------------------------------------------------------------------
# Step 4 — Hemisphere Grid & Visualization
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Step 4 — Hemisphere Grid & Visualization

    The **canvod-grids** package partitions the upper hemisphere into cells.
    Each VOD observation is assigned to the grid cell it falls into based on
    its elevation and azimuth, then averaged per cell.

    The **canvod-viz** package renders the result on a polar projection
    where the centre is the zenith and the outer ring is the horizon.

    Adjust the grid settings above to see how different grid types,
    resolutions, and elevation cutoffs affect the spatial VOD pattern.
    """
    )


@app.cell
def _(angular_res_slider, cutoff_slider, grid_type_dropdown):
    from canvodpy.functional import create_grid

    grid = create_grid(
        grid_type_dropdown.value,
        angular_resolution=angular_res_slider.value,
        cutoff_theta=cutoff_slider.value if cutoff_slider.value > 0 else None,
    )

    return create_grid, grid


@app.cell
def _(angular_res_slider, grid, grid_type_dropdown, mo, np, vod_ds):
    from canvod.grids import add_cell_ids_to_vod_fast
    from canvod.viz import HemisphereVisualizer

    _grid_name = grid_type_dropdown.value
    _vod_gridded = add_cell_ids_to_vod_fast(vod_ds, grid, _grid_name)

    # Aggregate: mean VOD per grid cell
    _cell_var = f"cell_id_{_grid_name}"
    _vod_vals = _vod_gridded["VOD"].values.ravel()
    _cell_ids = _vod_gridded[_cell_var].values.ravel()
    _valid = ~(np.isnan(_vod_vals) | np.isnan(_cell_ids))

    _cell_mean = np.full(grid.ncells, np.nan)
    _ids = _cell_ids[_valid].astype(int)
    _vals = _vod_vals[_valid]
    for _cid in np.unique(_ids):
        _cell_mean[_cid] = np.nanmean(_vals[_ids == _cid])

    _viz = HemisphereVisualizer(grid)
    _fig, _ax = _viz.plot_2d(
        data=_cell_mean,
        title=f"Mean VOD — {_grid_name} grid, {grid.ncells} cells",
        cmap="YlGn",
    )

    mo.vstack([
        mo.md(
            f"**{grid_type_dropdown.value}** grid — **{grid.ncells}** cells at "
            f"{angular_res_slider.value}° resolution"
        ),
        mo.as_html(_fig),
    ])

    return HemisphereVisualizer, add_cell_ids_to_vod_fast


# ---------------------------------------------------------------------------
# Step 5 — Store to Icechunk
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Step 5 — Versioned Storage

    The **canvod-store** package writes the VOD dataset to a versioned
    Icechunk store (Zarr v3 with git-like branching and snapshots).  Each
    write is an immutable snapshot that can be rewound, compared, or branched.

    In a production pipeline, the orchestrator handles store creation and
    metadata automatically.  Here we write to a temporary store for
    demonstration.
    """
    )


@app.cell
def _(Path, mo, vod_ds):
    import tempfile

    from canvod.store import MyIcechunkStore

    _tmp = Path(tempfile.mkdtemp(prefix="canvodpy_demo_"))
    _store_path = _tmp / "vod_demo_store"

    _store = MyIcechunkStore(_store_path, store_type="vod_store")
    _vod_for_store = vod_ds.copy()
    _vod_for_store.attrs["File Hash"] = "demo"

    _store.write_initial_group(
        dataset=_vod_for_store,
        group_name="canopy_01_vs_reference_01",
    )

    mo.md(
        f"""
    ### Store written

    - Path: `{_store_path}`
    - Groups: `{_store.list_groups()}`
    - Snapshot: versioned and immutable
    """
    )

    return MyIcechunkStore, tempfile


@app.cell
def _(mo):
    mo.md(
        r"""
    ---

    ## Summary

    The complete GNSS-VOD pipeline:

    1. **Read** — Parse RINEX observations into xarray datasets
    2. **Augment** — Add satellite positions (theta, phi) from precise ephemerides
    3. **VOD** — Compute optical depth from canopy/reference SNR ratio
    4. **Grid** — Partition the hemisphere and average VOD per cell
    5. **Store** — Write results to a versioned Icechunk store

    Each step is an independent, composable package.
    The `canvodpy` umbrella provides convenience APIs (Levels 1–4) that
    chain these steps together.

    ---

    *canVODpy — CLIMERS, TU Wien | Apache 2.0 | No warranty*
    """
    )


if __name__ == "__main__":
    app.run()
