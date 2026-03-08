# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "matplotlib",
#     "numpy",
#     "zarr",
#     "canvod-ops",
#     "canvod-streamstats",
# ]
# ///
"""Live Statistics Dashboard — Phase 11 display pipeline.

Interactive dashboard for querying streaming statistics snapshots,
viewing climatology heatmaps, anomaly timelines, changepoint status,
and spectral diagnostics with EWMA/median smoothing controls.
"""

import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np

    return mo, np, plt


@app.cell
def _(mo):
    is_script_mode = mo.app_meta().mode == "script"
    return (is_script_mode,)


@app.cell
def _(mo):
    mo.md("""
    # Live Statistics Dashboard
    **Streaming statistics snapshot viewer with spectral diagnostics**

    Configure the store path and receiver type below to load statistics.
    """)
    return


@app.cell
def _(is_script_mode, mo):
    _default = "/tmp/canvodpy_demo/stores/Rosalia/statistics" if is_script_mode else ""
    store_path_input = mo.ui.text(
        value=_default,
        label="Statistics store path (Zarr directory)",
        full_width=True,
    )
    store_path_input
    return (store_path_input,)


@app.cell
def _(mo, store_path_input):
    import zarr

    from canvod.ops.statistics.query import StatisticsQuery
    from canvod.ops.statistics.store import StatisticsStore

    mo.stop(
        not store_path_input.value,
        mo.md("**Enter a store path above to begin.**"),
    )

    root = zarr.open_group(store_path_input.value, mode="r")
    store = StatisticsStore(root)
    query = StatisticsQuery(store)
    rx_types = query.list_receiver_types()

    mo.stop(
        not rx_types,
        mo.md("**No receiver types found in store.**"),
    )

    rx_dropdown = mo.ui.dropdown(
        options=rx_types,
        value=rx_types[0],
        label="Receiver type",
    )
    rx_dropdown
    return StatisticsQuery, query, rx_dropdown


@app.cell
def _(mo, query, rx_dropdown):
    snap = query.snapshot(rx_dropdown.value)

    _summary = snap.registry_summary
    _summary_rows = [{"Metric": k, "Value": str(v)} for k, v in _summary.items()]
    mo.vstack(
        [
            mo.md(f"## Statistics Overview — `{rx_dropdown.value}`"),
            mo.ui.table(_summary_rows),
        ]
    )
    return (snap,)


@app.cell
def _(mo, snap):
    # Use all available variables: from stats, heatmaps, or summary
    _all_vars = set(snap.variable_stats.keys()) | set(snap.climatology_heatmaps.keys())
    if not _all_vars:
        _all_vars = set(snap.registry_summary.get("variables", []))
    var_names = sorted(_all_vars)
    var_dropdown = mo.ui.dropdown(
        options=var_names,
        value=var_names[0] if var_names else None,
        label="Variable",
    )
    var_dropdown
    return (var_dropdown,)


@app.cell
def _(mo, snap, var_dropdown):
    mo.stop(var_dropdown.value is None)

    _vs = snap.variable_stats.get(var_dropdown.value)
    _ce = snap.confidence_envelopes.get(var_dropdown.value)

    _parts = []
    if _vs is not None and _vs.total_count > 0:
        _parts.append(f"""### Variable: `{_vs.variable}`
| Metric | Value |
|--------|-------|
| Keys | {_vs.n_keys} |
| Total count | {_vs.total_count:,} |
| Mean | {_vs.global_mean:.4f} |
| Std | {_vs.global_std:.4f} |
| Min | {_vs.min_val:.4f} |
| Max | {_vs.max_val:.4f} |
""")
    if _ce is not None and _ce.n_eff > 0:
        _parts.append(f"""### Confidence Envelope (z={_ce.z_multiplier})
| Metric | Value |
|--------|-------|
| n_eff | {_ce.n_eff:.1f} |
| Lower | {_ce.lower:.4f} |
| Upper | {_ce.upper:.4f} |
""")
    if not _parts:
        _parts.append(
            f"*No moment statistics for `{var_dropdown.value}` "
            "(data lacks cell_id coordinates). "
            "Climatology, anomaly, and changepoint data shown below.*"
        )

    mo.md("\n".join(_parts))
    return


@app.cell
def _(mo, plt, snap, var_dropdown):
    mo.stop(var_dropdown.value is None)

    _hm = snap.climatology_heatmaps.get(var_dropdown.value)
    mo.stop(_hm is None, mo.md("*No climatology data for this variable.*"))

    _fig_clim, _ax_clim = plt.subplots(figsize=(12, 5))
    _mesh = _ax_clim.pcolormesh(
        _hm.tod_bins,
        _hm.doy_bins,
        _hm.mean_grid,
        shading="flat",
        cmap="viridis",
    )
    _fig_clim.colorbar(_mesh, ax=_ax_clim, label="Mean")
    _ax_clim.set_xlabel("Time of Day (h)")
    _ax_clim.set_ylabel("Day of Year")
    _ax_clim.set_title(f"Climatology — {var_dropdown.value}")
    plt.tight_layout()
    mo.as_html(_fig_clim)
    return


@app.cell
def _(mo, np, plt, snap):
    _at = snap.anomaly_timeline
    mo.stop(_at is None, mo.md("*No anomaly data available.*"))

    _fig_anom, (_ax_bar, _ax_line) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    _x = np.arange(len(_at.dates))

    for _vi, _var in enumerate(_at.variables):
        _n_mild = _at.data[:, _vi, 1]
        _n_moderate = _at.data[:, _vi, 2]
        _n_severe = _at.data[:, _vi, 3]
        _bottom = np.zeros(len(_x))
        _ax_bar.bar(_x, _n_mild, bottom=_bottom, label=f"{_var} mild", alpha=0.7)
        _bottom += _n_mild
        _ax_bar.bar(
            _x,
            _n_moderate,
            bottom=_bottom,
            label=f"{_var} moderate",
            alpha=0.7,
        )
        _bottom += _n_moderate
        _ax_bar.bar(
            _x,
            _n_severe,
            bottom=_bottom,
            label=f"{_var} severe",
            alpha=0.7,
        )

    _ax_bar.set_ylabel("Count")
    _ax_bar.set_title("Anomaly Timeline")
    _ax_bar.legend(fontsize=7, ncol=3)

    for _vi, _var in enumerate(_at.variables):
        _ax_line.plot(_x, _at.data[:, _vi, 5], marker="o", markersize=3, label=_var)
    _ax_line.set_ylabel("Max |z|")
    _ax_line.set_xticks(_x)
    _ax_line.set_xticklabels(_at.dates, rotation=45, ha="right", fontsize=7)
    _ax_line.legend(fontsize=7)
    plt.tight_layout()
    mo.as_html(_fig_anom)
    return


@app.cell
def _(mo, snap):
    _cp = snap.changepoint_status
    mo.stop(_cp is None, mo.md("*No changepoint data available.*"))

    _cp_rows = []
    for _i, _var in enumerate(_cp.variables):
        _cp_rows.append(
            {
                "Variable": _var,
                "P(changepoint)": f"{_cp.changepoint_probs[_i]:.4f}",
                "MAP run length": _cp.map_run_lengths[_i],
                "Predictive mean": f"{_cp.predictive_means[_i]:.4f}",
                "Predictive std": f"{_cp.predictive_stds[_i]:.4f}",
                "N observations": _cp.n_observations[_i],
            }
        )

    mo.vstack(
        [
            mo.md("## Changepoint Monitor"),
            mo.ui.table(_cp_rows),
        ]
    )
    return


@app.cell
def _(mo):
    halflife_slider = mo.ui.slider(
        start=1,
        stop=100,
        value=10,
        step=1,
        label="EWMA half-life",
    )
    window_slider = mo.ui.slider(
        start=3,
        stop=51,
        value=5,
        step=2,
        label="Median window",
    )
    mo.hstack([halflife_slider, window_slider])
    return halflife_slider, window_slider


@app.cell
def _(
    StatisticsQuery,
    halflife_slider,
    mo,
    np,
    plt,
    snap,
    var_dropdown,
    window_slider,
):
    from canvod.streamstats import lomb_scargle, multitaper_psd

    mo.stop(var_dropdown.value is None)

    _vs = snap.variable_stats.get(var_dropdown.value)
    mo.stop(
        _vs is None or _vs.total_count < 10,
        mo.md(
            "*Spectral diagnostics require moment statistics (cell_id coordinates).*"
        ),
    )

    # Synthetic time series from variable stats for spectral demo
    # (in production this would come from actual stored time series)
    _rng = np.random.default_rng(0)
    _n = min(_vs.total_count, 1000)
    _raw = _rng.normal(_vs.global_mean, _vs.global_std, size=_n)

    _ewma_out = StatisticsQuery.filtered_series(
        _raw, method="ewma", half_life=halflife_slider.value
    )
    _median_out = StatisticsQuery.filtered_series(
        _raw, method="median", window=window_slider.value
    )

    _fig_spec, _axes = plt.subplots(2, 2, figsize=(14, 8))

    # Top-left: Lomb-Scargle PSD
    _times = np.arange(_n, dtype=np.float64)
    _ls = lomb_scargle(_times, _raw - np.mean(_raw))
    _axes[0, 0].semilogy(_ls.frequencies, _ls.power)
    _axes[0, 0].set_title("Lomb-Scargle PSD")
    _axes[0, 0].set_xlabel("Frequency")
    _axes[0, 0].set_ylabel("Power")

    # Top-right: Multitaper PSD
    _mt = multitaper_psd(_raw - np.mean(_raw))
    _axes[0, 1].semilogy(_mt.frequencies, _mt.psd)
    _axes[0, 1].set_title(f"Multitaper PSD (noise: {_mt.noise_type})")
    _axes[0, 1].set_xlabel("Frequency (Hz)")
    _axes[0, 1].set_ylabel("PSD")

    # Bottom-left: Raw vs smoothed
    _t = np.arange(min(200, _n))
    _axes[1, 0].plot(_t, _raw[: len(_t)], alpha=0.4, label="Raw")
    _axes[1, 0].plot(
        _t, _ewma_out[: len(_t)], label=f"EWMA (hl={halflife_slider.value})"
    )
    _axes[1, 0].plot(
        _t, _median_out[: len(_t)], label=f"Median (w={window_slider.value})"
    )
    _axes[1, 0].set_title("Smoothing Comparison")
    _axes[1, 0].legend(fontsize=7)

    # Bottom-right: ACF of raw vs smoothed
    def _acf(x, max_lag=50):
        x = x - np.mean(x)
        c0 = np.var(x)
        if c0 == 0:
            return np.zeros(max_lag)
        return np.array([np.mean(x[: len(x) - k] * x[k:]) / c0 for k in range(max_lag)])

    _lags = np.arange(50)
    _axes[1, 1].plot(_lags, _acf(_raw, 50), alpha=0.5, label="Raw")
    _axes[1, 1].plot(_lags, _acf(_ewma_out, 50), label="EWMA")
    _axes[1, 1].plot(_lags, _acf(_median_out, 50), label="Median")
    _axes[1, 1].axhline(0, color="k", lw=0.5)
    _axes[1, 1].set_title("Autocorrelation")
    _axes[1, 1].set_xlabel("Lag")
    _axes[1, 1].legend(fontsize=7)

    plt.tight_layout()
    mo.as_html(_fig_spec)
    return


if __name__ == "__main__":
    app.run()
