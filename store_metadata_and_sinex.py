import marimo

__generated_with = "0.20.1"
app = marimo.App(width="medium", css_file="canvod_nordic.css")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # Store Metadata & IGS Satellite Catalog

    An interactive explorer for two canVODpy subsystems that power data
    provenance and satellite awareness across the GNSS-T pipeline.

    | System | Package | Purpose |
    |--------|---------|---------|
    | **Store Metadata** | `canvod-store-metadata` | Rich provenance metadata for Icechunk stores — DataCite 4.5, ACDD 1.3, STAC 1.1 |
    | **Satellite Catalog** | `canvod-readers` | Time-aware GNSS satellite metadata from the IGS SINEX file |

    Use the tabs and controls below to explore each system interactively.
    """)
    return


# ── Part A: Store Metadata ──────────────────────────────────────────────


@app.cell
def _(mo):
    mo.md(r"""
    ---

    # Part A — Store Metadata

    Every Icechunk store in canVODpy carries **11 metadata sections** (~90 fields)
    written to the Zarr root attributes. This metadata enables:

    - **Reproducibility** — full software versions, config snapshots, and environment capture
    - **Discovery** — DataCite-compatible identifiers, keywords, and spatial/temporal extent
    - **Compliance** — automated validation against DataCite 4.5, ACDD 1.3, STAC 1.1, and FAIR principles
    - **Cataloging** — `scan_stores()` builds a Polars inventory across all stores on disk

    The metadata is collected automatically by the orchestrator on first ingest
    and updated on subsequent writes.
    """)
    return


@app.cell
def _():
    from canvod.store_metadata.schema import (
        Creator,
        Environment,
        ProcessingProvenance,
        Publisher,
        SiteInfo,
        SpatialExtent,
        StoreIdentity,
        StoreMetadata,
        Summaries,
        TemporalExtent,
    )

    return (
        Creator,
        Environment,
        ProcessingProvenance,
        Publisher,
        SiteInfo,
        SpatialExtent,
        StoreIdentity,
        StoreMetadata,
        Summaries,
        TemporalExtent,
    )


@app.cell
def _(
    Creator,
    Environment,
    ProcessingProvenance,
    Publisher,
    SiteInfo,
    SpatialExtent,
    StoreIdentity,
    StoreMetadata,
    Summaries,
    TemporalExtent,
):
    # Build a representative metadata object
    demo_meta = StoreMetadata(
        identity=StoreIdentity(
            id="Rosalia/rinex_store",
            title="Rosalia GNSS-T RINEX Observation Store",
            description="Multi-receiver RINEX v3 observations for GNSS transmissometry VOD retrieval",
            store_type="rinex_store",
            source_format="rinex3",
            keywords=["GNSS", "VOD", "RINEX", "transmissometry", "vegetation"],
            conventions="ACDD-1.3",
            naming_authority="at.ac.tuwien.geo",
        ),
        creator=Creator(
            name="Nicolas Bader",
            email="nicolas.bader@geo.tuwien.ac.at",
            orcid="0000-0002-1234-5678",
            institution="TU Wien",
            institution_ror="https://ror.org/04d836q62",
            department="Geodesy and Geoinformation",
            research_group="CLIMERS",
        ),
        publisher=Publisher(
            name="TU Wien",
            license="Apache-2.0",
        ),
        temporal=TemporalExtent(
            created="2026-03-01T10:00:00Z",
            updated="2026-03-09T14:00:00Z",
            collected_start="2025-01-01T00:00:00Z",
            collected_end="2025-01-07T23:59:55Z",
            time_coverage_duration="P7D",
            time_coverage_resolution="PT5S",
        ),
        spatial=SpatialExtent(
            site=SiteInfo(
                name="Rosalia",
                description="Rosalia GNSS-T research site, mixed forest",
                country="Austria",
            ),
            geospatial_lat=47.702,
            geospatial_lon=16.299,
            geospatial_alt_m=575.0,
        ),
        processing=ProcessingProvenance(
            software={"canvodpy": "0.1.0", "icechunk": "0.1.0", "xarray": "2025.1.0"},
            python="3.13.2 (CPython)",
            level="L1 (calibrated observations)",
            lineage="RINEX v3 → canvod-readers → Icechunk store",
            facility="TU Wien CLIMERS",
            datetime="2026-03-09T14:00:00Z",
        ),
        environment=Environment(
            hostname="climers-workstation",
            os="Darwin 25.3.0",
            arch="arm64",
            cpu_count=10,
            memory_gb=32.0,
        ),
        summaries=Summaries(
            total_epochs=120960,
            total_sids=3658,
            constellations=["GPS", "GLONASS", "Galileo", "BeiDou"],
            variables=["SNR"],
        ),
    )
    return (demo_meta,)


@app.cell
def _(demo_meta, mo):
    _sections = list(demo_meta.model_fields.keys())
    section_select = mo.ui.dropdown(
        options=_sections,
        value="identity",
        label="Inspect metadata section",
    )
    section_select
    return (section_select,)


@app.cell
def _(demo_meta, mo, section_select):
    import json

    _section = getattr(demo_meta, section_select.value)
    _data = _section.model_dump() if hasattr(_section, "model_dump") else _section

    mo.md(f"""
    ### Section: `{section_select.value}`

    {_section.__class__.__doc__ or ""}

    ```json
    {json.dumps(_data, indent=2, default=str)}
    ```
    """)
    return (json,)


@app.cell
def _(mo):
    mo.md(r"""
    ### Standards compliance validation

    `validate_all()` checks the metadata against four standards. Each standard
    defines mandatory and recommended fields. Issues indicate missing or
    incomplete metadata that would prevent compliance.
    """)
    return


@app.cell
def _(demo_meta, mo):
    from canvod.store_metadata import validate_all

    results = validate_all(demo_meta)

    total_issues = sum(len(v) for v in results.values())

    summary_rows = []
    for standard, issues in results.items():
        status = "PASS" if not issues else f"{len(issues)} issue(s)"
        summary_rows.append({
            "Standard": standard,
            "Status": status,
            "Issues": "; ".join(issues) if issues else "All checks passed",
        })

    mo.md(f"""
    **Validation result:** {"All standards passed" if total_issues == 0 else f"{total_issues} issue(s) found"}
    """)
    return results, summary_rows, total_issues, validate_all


@app.cell
def _(mo, summary_rows):
    import polars as pl

    mo.ui.table(pl.DataFrame(summary_rows))
    return (pl,)


@app.cell
def _(mo):
    mo.md(r"""
    ### How metadata flows through the pipeline

    ```
    First ingest                          Subsequent writes
    ───────────                           ─────────────────
    orchestrator                          orchestrator
      │                                     │
      ├─ collect_metadata()                 ├─ update_metadata()
      │    ├─ config → identity,            │    ├─ temporal.updated = now
      │    │   creator, spatial             │    ├─ temporal.collected_end = max
      │    ├─ runtime → environment,        │    └─ summaries = recompute
      │    │   processing                   │
      │    └─ store → summaries             └─ commit snapshot
      │
      ├─ write_metadata(store, meta)
      │    └─ zarr root attrs["canvod_metadata"] = {...}
      │
      └─ commit snapshot
    ```
    """)
    return


# ── Part B: Satellite Catalog ───────────────────────────────────────────


@app.cell
def _(mo):
    mo.md(r"""
    ---

    # Part B — IGS Satellite Catalog

    The `SatelliteCatalog` parses the IGS `igs_satellite_metadata.snx` SINEX
    file — a single authoritative source maintained by the International GNSS
    Service (updated every 2–4 weeks by DLR).

    **Why it matters for GNSS-T:**

    - **PRN reassignments** break time-series continuity (different satellite = different TX power, antenna pattern, orbit)
    - **Transmit power** directly affects SNR — higher-power satellites produce stronger signals
    - **Satellite generation** (block type) determines signal characteristics relevant to VOD retrieval

    The catalog ships with a bundled fallback copy and **never fails offline**.
    """)
    return


@app.cell
def _():
    from canvod.readers.gnss_specs import SatelliteCatalog

    catalog = SatelliteCatalog.load(allow_download=False)
    return SatelliteCatalog, catalog


@app.cell
def _(catalog, mo):
    s = catalog.summary()
    mo.md(f"""
    ### Catalog contents

    | Metric | Count |
    |--------|------:|
    | Satellite vehicles (SVNs) | **{s['total_svns']}** |
    | PRN assignments | **{s['prn_assignments']}** |
    | TX power records | **{s['tx_power_records']}** |
    | Mass records | **{s['mass_records']}** |
    | GLONASS frequency channels | **{s['frequency_channels']}** |
    | Orbital plane/slot records | **{s['plane_slots']}** |

    **Constellations:** {', '.join(f'{k} ({v} SVNs)' for k, v in s['constellations'].items())}
    """)
    return (s,)


@app.cell
def _(mo):
    mo.md(r"""
    ### Interactive PRN query

    Select a PRN code and date to look up the satellite behind it. PRN codes
    are **not permanent** — they can be reassigned when a satellite is
    decommissioned and its slot is taken by a replacement.
    """)
    return


@app.cell
def _(catalog, mo):
    from datetime import date

    # Build PRN options from all known PRNs
    _all_prns = sorted({a.prn for a in catalog.prn_assignments})

    prn_input = mo.ui.dropdown(
        options=_all_prns,
        value="G01",
        label="PRN code",
    )
    date_input = mo.ui.date(
        value=date(2025, 1, 1),
        label="Query date",
    )

    mo.hstack([prn_input, date_input], justify="start")
    return date, date_input, prn_input


@app.cell
def _(catalog, date_input, mo, prn_input):
    _prn = prn_input.value
    _qdate = date_input.value

    _svn = catalog.prn_to_svn(_prn, _qdate)

    if _svn:
        _block = catalog.satellite_block(_svn)
        _power = catalog.tx_power(_svn, _qdate)
        _mass = catalog.mass(_svn, _qdate)
        _plane_slot = catalog.plane_and_slot(_svn, _qdate)

        mo.md(f"""
    **{_prn} on {_qdate}:**

    | Property | Value |
    |----------|------:|
    | SVN | {_svn} |
    | Block type | {_block or "—"} |
    | TX power | {f"{_power} W" if _power else "—"} |
    | Mass | {f"{_mass} kg" if _mass else "—"} |
    | Orbital plane / slot | {f"{_plane_slot[0]}/{_plane_slot[1]}" if _plane_slot and _plane_slot[0] else "—"} |
    """)
    else:
        mo.md(f"**{_prn}** was not active on {_qdate}.")
    return


@app.cell
def _(catalog, date_input, mo, prn_input):
    _prn = prn_input.value
    _history = catalog.prn_history(_prn)

    if _history:
        _rows = "\n".join(
            f"    | {a.svn} | {a.start} | {a.end or '**active**'} |"
            for a in _history
        )
        mo.md(f"""
    ### Assignment history for {_prn}

    Each row represents a period when this PRN code was assigned to a
    specific satellite vehicle. Gaps between assignments mean the PRN
    was temporarily unused.

    | SVN | Start | End |
    |-----|-------|-----|
    {_rows}
    """)
    else:
        mo.md(f"No assignment history found for {_prn}.")
    return


@app.cell
def _(catalog, date, mo, prn_input):
    _prn = prn_input.value
    _reassignments = catalog.reassignments_in_range(
        _prn, date(1990, 1, 1), date(2030, 12, 31)
    )

    if _reassignments:
        _rows = "\n".join(
            f"    | {r.old_svn} → {r.new_svn} | {r.new_start} |"
            for r in _reassignments
        )
        mo.md(f"""
    ### Reassignment events for {_prn}

    A reassignment means the physical satellite behind this PRN changed.
    This affects transmit power, antenna gain pattern, and signal
    characteristics — important for long-term VOD time series.

    | Transition | Date |
    |-----------|------|
    {_rows}
    """)
    else:
        mo.md(f"""
    ### No reassignments for {_prn}

    This PRN has been assigned to the same satellite vehicle throughout
    its operational history — no continuity concerns for time-series analysis.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### Constellation snapshot

    The table below shows all active PRNs on the selected date with their
    resolved metadata. Use the search and sort controls to explore.
    """)
    return


@app.cell
def _(catalog, date_input, mo):
    df_snapshot = catalog.to_dataframe(on_date=date_input.value)

    mo.md(f"**{len(df_snapshot)} active PRNs on {date_input.value}**")
    return (df_snapshot,)


@app.cell
def _(df_snapshot, mo):
    mo.ui.table(df_snapshot, page_size=20, selection=None)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Transmit power by constellation

    Transmit power varies significantly across constellations and satellite
    generations. Higher TX power improves signal-to-noise ratio at the
    receiver, which directly affects VOD retrieval quality.

    GPS Block III satellites (launched from 2018) transmit at ~280 W,
    while earlier Block IIA (1990s) satellites transmitted at ~50 W —
    a factor of 5× difference in received signal strength.
    """)
    return


@app.cell
def _(df_snapshot, mo, pl):
    power_stats = (
        df_snapshot
        .filter(pl.col("tx_power_watts").is_not_null())
        .group_by("constellation")
        .agg(
            pl.col("tx_power_watts").mean().round(1).alias("mean_W"),
            pl.col("tx_power_watts").min().alias("min_W"),
            pl.col("tx_power_watts").max().alias("max_W"),
            pl.len().alias("count"),
        )
        .sort("constellation")
    )

    mo.ui.table(power_stats, selection=None)
    return (power_stats,)


@app.cell
def _(df_snapshot, mo, pl):
    import altair as alt

    _chart_data = (
        df_snapshot
        .filter(pl.col("tx_power_watts").is_not_null())
        .select(["prn", "constellation", "tx_power_watts", "block"])
        .sort("constellation", "tx_power_watts")
        .to_pandas()
    )

    _chart = (
        alt.Chart(_chart_data)
        .mark_bar()
        .encode(
            x=alt.X("prn:N", sort="-y", title="PRN"),
            y=alt.Y("tx_power_watts:Q", title="TX Power (W)"),
            color=alt.Color("constellation:N", title="Constellation"),
            tooltip=["prn", "block", "tx_power_watts", "constellation"],
        )
        .properties(width=700, height=300, title="Transmit Power by Satellite")
    )

    mo.ui.altair_chart(_chart)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### Dataset enrichment

    `enrich_dataset()` adds satellite metadata as `sid`-level coordinates
    on any `(epoch, sid)` xarray Dataset. This enables powerful filtering
    by satellite generation, TX power class, or orbital plane — without
    any manual lookups.
    """)
    return


@app.cell
def _(catalog, date_input, mo):
    import numpy as np
    import xarray as xr

    # Create a small synthetic dataset to demonstrate enrichment
    _sids = ["G01|L1|C", "G07|L1|C", "E01|E1|C", "R01|G1|C", "C01|B1I|C"]
    _epochs = np.array(
        [np.datetime64(f"2025-01-01T{h:02d}:00:00") for h in range(24)],
        dtype="datetime64[ns]",
    )
    _rng = np.random.default_rng(42)
    _snr = _rng.uniform(30, 50, size=(len(_epochs), len(_sids))).astype(np.float32)

    _demo_ds = xr.Dataset(
        {"SNR": (["epoch", "sid"], _snr)},
        coords={"epoch": _epochs, "sid": _sids},
    )

    enriched = catalog.enrich_dataset(_demo_ds, on_date=date_input.value)

    # Build coordinate table
    _coord_rows = []
    for _coord_name in ["svn", "block", "tx_power_watts", "mass_kg", "plane", "slot"]:
        if _coord_name in enriched.coords:
            _vals = enriched.coords[_coord_name].values
            _coord_rows.append(f"    | `{_coord_name}` | {list(_vals)} |")

    _coord_text = "\n".join(_coord_rows)

    mo.md(f"""
    **Enriched coordinates added to each SID:**

    | Coordinate | Values |
    |-----------|--------|
    {_coord_text}

    After enrichment, you can filter by satellite properties:

    ```python
    # Only GPS Block III satellites (highest TX power)
    gps3 = enriched.sel(sid=enriched.coords["block"].str.startswith("GPS-III"))

    # Satellites with TX power > 200 W
    high_power = enriched.sel(sid=enriched.coords["tx_power_watts"] > 200)
    ```
    """)
    return enriched, np, xr


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## Key takeaways

    - **Store metadata** is collected automatically on first ingest and kept
      up to date — no manual annotation needed
    - **Validation** checks compliance against 4 standards in one call
    - **SatelliteCatalog** resolves PRN→SVN mappings with full time awareness,
      critical for multi-year GNSS-T time series
    - **Enrichment** adds satellite properties directly to xarray Datasets,
      enabling physics-informed filtering and analysis

    Both systems are designed offline-first: bundled fallbacks ensure they
    work without internet access.
    """)
    return


if __name__ == "__main__":
    app.run()
