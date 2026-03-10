"""Hackathon Demo — canvodpy end-to-end pipeline with Rosalia test data."""

import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium", css_file="canvod_nordic.css")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import shutil

    import numpy as np
    import xarray as xr

    from canvod.grids import create_hemigrid, store_grid
    from canvod.grids.operations import (
        add_cell_ids_to_vod_fast,
        store_dataset_with_cell_ids,
    )
    from canvod.viz import HemisphereVisualizer
    from canvodpy import Site

    return (
        HemisphereVisualizer,
        Site,
        add_cell_ids_to_vod_fast,
        create_hemigrid,
        np,
        shutil,
        store_dataset_with_cell_ids,
        store_grid,
        xr,
    )


@app.cell
def _(Site, mo, shutil):
    mo.md(r"""## 1 · Site & Pipeline""")

    from pathlib import Path

    STORE_ROOT = Path("/tmp/canvodpy_demo")
    if STORE_ROOT.exists():
        shutil.rmtree(STORE_ROOT)

    site = Site("Rosalia")
    pipeline = site.pipeline(n_workers=8)

    mo.md(f"""
    | | |
    |---|---|
    | **Site** | `{site.name}` |
    | **Receivers** | {list(site.active_receivers.keys())} |
    | **VOD analyses** | {list(site.vod_analyses.keys())} |
    | **RINEX store** | `{site.rinex_store.store_path}` |
    """)
    return Path, pipeline, site


@app.cell
def _(site):
    site
    return


@app.cell
def _(Path, mo, pipeline, shutil):
    mo.md(r"""## 2 · Process Date 2025-001""")
    from _paths import AUX_DATA_DIR

    aux_dir = AUX_DATA_DIR / "aux" / "aux_2025001.zarr"
    if aux_dir.exists():
        shutil.rmtree(aux_dir)

    datasets = pipeline.process_date("2025001")

    mo.md(f"""
    | Receiver | Epochs | SIDs |
    |---|---|---|
    {"".join(f"| **{rx}** | {ds.sizes['epoch']} | {ds.sizes['sid']} |" + chr(10) for rx, ds in datasets.items())}
    """)
    return


@app.cell
def _(mo, site):
    mo.md(r"""## 3 · Explore the Store""")

    site.rinex_store
    return


@app.cell
def _(mo, site):
    canopy_ds = site.rinex_store.read_group("canopy_01")
    # Available groups: canopy_01, reference_01_canopy_01

    mo.md(f"Dataset loaded — `canopy_01`  {dict(canopy_ds.sizes)}")
    return (canopy_ds,)


@app.cell
def _(canopy_ds):
    canopy_ds
    return


@app.cell
def _(mo, site):
    with site.rinex_store.readonly_session() as _sess:
        meta_table = site.rinex_store.load_metadata(
            store=_sess.store, group_name="canopy_01"
        )

    mo.ui.table(meta_table, pagination=True)
    return (meta_table,)


@app.cell
def _(meta_table):
    meta_table
    return


@app.cell
def _(mo, site):
    mo.md(r"""## 4 · Branches & Versioning""")

    from icechunk import IcechunkError

    def _create_or_replace(s, name, snapshot_id):
        try:
            s.repo.create_branch(name, snapshot_id)
        except IcechunkError:
            s.delete_branch(name)
            s.repo.create_branch(name, snapshot_id)

    with site.rinex_store.writable_session("main") as _sess:
        _latest = site.rinex_store.get_history()[0]["snapshot_id"]
        _create_or_replace(site.rinex_store, "experimental", _latest)

    _hist = site.rinex_store.get_history()
    branches = site.rinex_store.get_branch_names()

    mo.md(
        f"Branches: **{branches}** — latest snapshot: `{_hist[0]['snapshot_id'][:12]}…`"
    )
    return


@app.cell
def _(site):
    site.rinex_store
    return


@app.cell
def _(site):
    experimental_canopy_ds = site.rinex_store.read_group(
        branch="experimental", group_name="canopy_01"
    )
    experimental_canopy_ds
    return (experimental_canopy_ds,)


@app.cell
def _(site):
    site.rinex_store.plot_commit_graph()
    return


@app.cell
def _(experimental_canopy_ds, np, xr):
    from datetime import datetime, timezone

    rng = np.random.default_rng(42)

    # ── dimensions ──────────────────────────────────────────────────────────────
    # copy sid structure directly from the real dataset
    n_sid = experimental_canopy_ds.sizes["sid"]

    # 15 min at 5 s cadence = 180 epochs
    t0 = np.datetime64("2025-01-01T12:00:00", "ns")
    epochs = t0 + np.arange(180) * np.timedelta64(5, "s")

    # ── per-epoch, per-sid signals ───────────────────────────────────────────────
    shape = (180, n_sid)

    # SNR: 20–50 dB-Hz, masked where satellite below horizon (theta > π/2 → NaN)
    snr = rng.uniform(20.0, 50.0, shape).astype(np.float32)

    # theta: zenith angle 0 (overhead) – π/2 (horizon); satellites vary over time
    theta_base = rng.uniform(0.05, np.pi / 2, n_sid)  # per-sid mean
    theta_drift = rng.normal(0, 0.02, shape)  # small epoch noise
    theta = np.clip(theta_base[None, :] + theta_drift, 0.0, np.pi / 2)

    # mask low-elevation satellites (theta > 75° ≈ 1.31 rad) with NaN
    below_horizon = theta > 1.31
    snr[below_horizon] = np.nan

    # phi: azimuth 0–2π, also drifts slowly
    phi_base = rng.uniform(0.0, 2 * np.pi, n_sid)
    phi_drift = rng.normal(0, 0.01, shape)
    phi = (phi_base[None, :] + phi_drift) % (2 * np.pi)

    # r: satellite–receiver range ~20 000–40 000 km (MEO / GEO range in metres)
    r_base = rng.uniform(20_000_000.0, 40_000_000.0, n_sid)
    r_noise = rng.normal(0, 1000.0, shape)
    r = r_base[None, :] + r_noise

    # ── build dataset ────────────────────────────────────────────────────────────
    sid_coords = {
        coord: experimental_canopy_ds[coord]
        for coord in [
            "sid",
            "sv",
            "system",
            "band",
            "code",
            "freq_center",
            "freq_min",
            "freq_max",
        ]
    }

    synthetic_ds = xr.Dataset(
        {
            "SNR": xr.Variable(
                ("epoch", "sid"),
                snr,
                attrs=experimental_canopy_ds["SNR"].attrs,
            ),
            "r": xr.Variable(
                ("epoch", "sid"),
                r,
                attrs=experimental_canopy_ds["r"].attrs,
            ),
            "phi": xr.Variable(
                ("epoch", "sid"),
                phi,
                attrs=experimental_canopy_ds["phi"].attrs,
            ),
            "theta": xr.Variable(
                ("epoch", "sid"),
                theta,
                attrs=experimental_canopy_ds["theta"].attrs,
            ),
        },
        coords={
            "epoch": xr.Variable(
                "epoch",
                epochs,
                attrs=experimental_canopy_ds["epoch"].attrs,
            ),
            **sid_coords,
        },
        attrs=experimental_canopy_ds.attrs
        | {
            "Note": "Synthetic dataset — generated for testing",
        },
    )

    synthetic_ds
    return datetime, synthetic_ds, timezone


@app.cell
def _(datetime, site, synthetic_ds, timezone):
    import hashlib
    import json

    from icechunk.xarray import to_icechunk

    # ── 1. write the dataset ────────────────────────────────────────────────────

    # give the synthetic dataset a unique hash so the store doesn't deduplicate it
    synthetic_hash = hashlib.sha256(b"synthetic-15min-test").hexdigest()[:16]
    synthetic_ds.attrs["File Hash"] = synthetic_hash

    # Session 1: write data
    with site.rinex_store.writable_session(branch="main") as _sess:
        to_icechunk(synthetic_ds, _sess, group="canopy_01", append_dim="epoch")
        snapshot_id = _sess.commit("Add synthetic 15-min dataset")

    # Session 2: write metadata row (append_metadata_bulk opens its own clean session)
    site.rinex_store.append_metadata_bulk(
        group_name="canopy_01",
        rows=[
            {
                "rinex_hash": synthetic_ds.attrs["File Hash"],
                "start": synthetic_ds.epoch.values[0],
                "end": synthetic_ds.epoch.values[-1],
                "snapshot_id": snapshot_id,
                "action": "insert",
                "commit_msg": "Add synthetic 15-min dataset",
                "written_at": datetime.now(timezone.utc).isoformat(),
                "write_strategy": "append",
                "attrs": json.dumps(dict(synthetic_ds.attrs), default=str),
            }
        ],
    )

    site.rinex_store
    return snapshot_id, to_icechunk


@app.cell
def _(mo, site, snapshot_id):
    import pandas as pd

    _ = snapshot_id  # depend on snapshot_id so this re-runs after each write
    main_hist = site.rinex_store.get_history()
    mo.ui.table(
        pd.DataFrame(main_hist)[["snapshot_id", "commit_msg", "written_at"]],
        pagination=True,
    )
    return (pd,)


@app.cell
def _(mo, pd, site, snapshot_id):
    _ = snapshot_id
    experimental_hist = site.rinex_store.get_history(branch="experimental")
    mo.ui.table(
        pd.DataFrame(experimental_hist)[["snapshot_id", "commit_msg", "written_at"]],
        pagination=True,
    )
    return


@app.cell
def _(site, snapshot_id):
    _ = snapshot_id  # re-run graph whenever a new commit lands
    site.rinex_store.plot_commit_graph()
    return


@app.cell
def _(mo, np, site, to_icechunk, xr):
    from canvod.store import MyIcechunkStore, create_vod_store
    from canvod.vod import TauOmegaZerothOrder

    mo.md(r"""## 5 · VOD Calculation — Tau-Omega Zeroth Order""")

    rinex_store = MyIcechunkStore(site.rinex_store.store_path)

    with rinex_store.readonly_session(branch="experimental") as session:
        _canopy_ds = xr.open_zarr(store=session.store, group="canopy_01")
        _reference_ds = xr.open_zarr(
            store=session.store, group="reference_01_canopy_01"
        )

        c_anopy_ds = _canopy_ds.sortby("epoch")
        _, index = np.unique(_canopy_ds["epoch"], return_index=True)
        _canopy_ds = _canopy_ds.isel(epoch=index)

        _reference_ds = _reference_ds.sortby("epoch")
        _, index = np.unique(_reference_ds["epoch"], return_index=True)
        _reference_ds = _reference_ds.isel(epoch=index)

    vod_ds = TauOmegaZerothOrder.from_datasets(
        canopy_ds=_canopy_ds, sky_ds=_reference_ds, align=True
    )

    vod_ds = vod_ds.unify_chunks()

    vod_ds = vod_ds.chunk({"epoch": 34560, "sid": -1})

    for var in vod_ds.data_vars:
        vod_ds[var].encoding = {}

    vod_store = create_vod_store(site.vod_store.store_path)

    with vod_store.writable_session() as session:
        to_icechunk(
            vod_ds, session, group="reference_01_canopy_01", mode="w", safe_chunks=False
        )
        _snapshot_id = session.commit("Initial VOD calculation")
    vod_store
    return (vod_ds,)


@app.cell
def _(mo, vod_ds):
    mo.md(f"""
    | | |
    |---|---|
    | Epochs | {vod_ds.sizes["epoch"]:,} |
    | SIDs | {vod_ds.sizes["sid"]} |
    """)
    return


@app.cell
def _(create_hemigrid, mo, site, store_grid):
    mo.md(r"""## 6 · Equal-Area Hemisphere Grid (2°)""")

    ea_grid = create_hemigrid("equal_area", angular_resolution=2)
    snap_grid = store_grid(ea_grid, site.vod_store, "equal_area_2deg")

    mo.md(f"""
    | | |
    |---|---|
    | Cells | {ea_grid.ncells} |
    | Snapshot | `{snap_grid[:12]}…` |
    """)
    return (ea_grid,)


@app.cell
def _(
    add_cell_ids_to_vod_fast,
    ea_grid,
    mo,
    np,
    site,
    store_dataset_with_cell_ids,
    vod_ds,
):
    mo.md(r"""## 7 · Assign Grid Cells to VOD Observations""")

    GRID_NAME = "equal_area_2deg"
    vod_gridded = add_cell_ids_to_vod_fast(vod_ds, ea_grid, GRID_NAME)
    snap_vod = store_dataset_with_cell_ids(vod_gridded, site.rinex_store, "vod_rosalia")

    _n = int((~np.isnan(vod_gridded[f"cell_id_{GRID_NAME}"].values)).sum())
    mo.md(f"**{_n:,}** observations assigned — snapshot `{snap_vod[:12]}…`")
    return GRID_NAME, vod_gridded


@app.cell
def _(GRID_NAME, ea_grid, np, vod_gridded):
    _vod_vals = vod_gridded["VOD"].values.ravel()
    _cell_ids = vod_gridded[f"cell_id_{GRID_NAME}"].values.ravel()
    _valid = ~(np.isnan(_vod_vals) | np.isnan(_cell_ids))

    cell_mean_vod = np.full(ea_grid.ncells, np.nan)
    _ids = _cell_ids[_valid].astype(int)
    _vals = _vod_vals[_valid]
    for _cid in np.unique(_ids):
        cell_mean_vod[_cid] = np.nanmean(_vals[_ids == _cid])

    cell_mean_vod
    return (cell_mean_vod,)


@app.cell
def _(HemisphereVisualizer, cell_mean_vod, ea_grid, mo, np):
    mo.md(r"""## 8 · Hemisphere Visualisation""")

    viz = HemisphereVisualizer(ea_grid)
    _vmin = float(np.nanmin(cell_mean_vod))
    _vmax = float(np.nanmax(cell_mean_vod))

    fig_2d, _ax = viz.plot_2d(
        data=cell_mean_vod,
        title="Mean VOD — Rosalia 2025-001",
        cmap="YlGn",
        vmin=_vmin,
        vmax=_vmax,
    )
    return (fig_2d,)


@app.cell
def _(fig_2d, mo):
    mo.md(r"""### 2-D polar hemisphere plot""")
    fig_2d
    return


@app.cell
def _(cell_mean_vod, ea_grid, mo):
    mo.md(r"""### 3-D interactive hemisphere plot""")
    from canvod.viz import visualize_grid_3d

    fig_3d = visualize_grid_3d(
        ea_grid,
        data=cell_mean_vod,
        title="Mean VOD — Rosalia 2025-001",
        colorscale="YlGn",
        add_overlays=True,
        add_axes=True,
    )
    return (fig_3d,)


@app.cell
def _(fig_3d):
    fig_3d
    return


if __name__ == "__main__":
    app.run()
