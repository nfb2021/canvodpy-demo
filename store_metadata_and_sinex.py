import marimo

__generated_with = "0.20.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # Store Metadata & IGS Satellite Catalog

    This notebook demonstrates two canVODpy subsystems:

    **Part A — Store Metadata** (`canvod-store-metadata`):
    Rich provenance metadata attached to Icechunk stores, aligned with
    DataCite 4.5, ACDD 1.3, and STAC 1.1.

    **Part B — Satellite Catalog** (`SatelliteCatalog`):
    Time-aware GNSS satellite metadata parsed from the IGS
    `igs_satellite_metadata.snx` SINEX file — PRN↔SVN mapping, transmit
    power, mass, orbital plane, and GLONASS frequency channels.

    ## Contents

    1. Inspect store metadata (schema, collection, validation)
    2. Load the IGS satellite catalog
    3. Query PRN assignments and reassignments
    4. Export to Polars DataFrame
    5. Visualise TX power by constellation
    6. Enrich an xarray Dataset with satellite metadata
    """)
    return


# ── Part A: Store Metadata ──────────────────────────────────────────────


@app.cell
def _(mo):
    mo.md(r"""
    ---

    # Part A — Store Metadata

    `canvod-store-metadata` captures 11 metadata sections (~90 fields) that
    describe an Icechunk store: identity, creator, temporal/spatial extent,
    instruments, software provenance, environment, configuration snapshot,
    references, and aggregate summaries.
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
    mo,
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

    mo.md(f"""
    ### Constructed `StoreMetadata` object

    The metadata has **{len(demo_meta.model_fields)}** top-level sections. Below is
    the full JSON-serializable representation that gets written to the Zarr
    store's root attributes.
    """)
    return (demo_meta,)


@app.cell
def _(demo_meta, mo):
    import json

    mo.md(f"""
    ### Serialised metadata (what goes into the store)

    ```json
    {json.dumps(demo_meta.model_dump(), indent=2, default=str)[:3000]}
    ...
    ```
    """)
    return (json,)


@app.cell
def _(demo_meta, mo):
    from canvod.store_metadata import validate_all

    results = validate_all(demo_meta)

    total_issues = sum(len(v) for v in results.values())

    summary_rows = []
    for standard, issues in results.items():
        status = "pass" if not issues else f"{len(issues)} issue(s)"
        summary_rows.append({"Standard": standard, "Status": status, "Issues": "; ".join(issues) if issues else "All checks passed"})

    mo.md(f"""
    ### Validation against standards

    `validate_all()` checks DataCite 4.5, ACDD 1.3, STAC 1.1, and FAIR
    compliance. Total issues: **{total_issues}**
    """)
    return results, summary_rows, total_issues, validate_all


@app.cell
def _(mo, summary_rows):
    import polars as pl

    mo.ui.table(pl.DataFrame(summary_rows))
    return (pl,)


# ── Part B: Satellite Catalog ───────────────────────────────────────────


@app.cell
def _(mo):
    mo.md(r"""
    ---

    # Part B — IGS Satellite Catalog

    The `SatelliteCatalog` parses the IGS `igs_satellite_metadata.snx` SINEX
    file — an authoritative, time-aware catalog of all GNSS satellite vehicles.
    It contains PRN↔SVN assignments, satellite block types, transmit power,
    mass, GLONASS frequency channels, and orbital plane/slot assignments.
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
    ### Catalog summary

    | Metric | Value |
    |--------|-------|
    | Total SVNs | **{s['total_svns']}** |
    | PRN assignments | **{s['prn_assignments']}** |
    | TX power records | **{s['tx_power_records']}** |
    | Mass records | **{s['mass_records']}** |
    | Frequency channels | **{s['frequency_channels']}** |
    | Plane/slot records | **{s['plane_slots']}** |

    **Constellations:** {', '.join(f'{k} ({v})' for k, v in s['constellations'].items())}
    """)
    return (s,)


@app.cell
def _(mo):
    mo.md(r"""
    ### PRN ↔ SVN queries

    PRN codes (like `G01`) are **not permanent**. They can be reassigned to
    different satellite vehicles. The catalog tracks every assignment with
    validity periods.
    """)
    return


@app.cell
def _(catalog, mo):
    from datetime import date

    query_date = date(2025, 1, 1)

    # What satellite is behind G01?
    svn_g01 = catalog.prn_to_svn("G01", query_date)
    block_g01 = catalog.satellite_block(svn_g01) if svn_g01 else None
    power_g01 = catalog.tx_power(svn_g01, query_date) if svn_g01 else None
    mass_g01 = catalog.mass(svn_g01, query_date) if svn_g01 else None

    # G01 reassignment history
    history = catalog.prn_history("G01")

    history_text = "\n".join(
        f"    | {a.svn} | {a.start} | {a.end or 'active'} |"
        for a in history
    )

    mo.md(f"""
    **G01 on {query_date}:**

    | Property | Value |
    |----------|-------|
    | SVN | {svn_g01} |
    | Block | {block_g01} |
    | TX power | {power_g01} W |
    | Mass | {mass_g01} kg |

    **Full PRN history for G01:**

    | SVN | Start | End |
    |-----|-------|-----|
    {history_text}
    """)
    return date, history, query_date


@app.cell
def _(catalog, date, mo):
    # Detect reassignments in a time range
    reassignments = catalog.reassignments_in_range("G01", date(2000, 1, 1), date(2025, 12, 31))

    if reassignments:
        r_text = "\n".join(
            f"    | {r.old_svn} → {r.new_svn} | {r.new_start} |"
            for r in reassignments
        )
        mo.md(f"""
    ### Reassignment events for G01

    | Transition | Date |
    |-----------|------|
    {r_text}
    """)
    else:
        mo.md("### No reassignments detected for G01 in 2000–2025")
    return (reassignments,)


@app.cell
def _(mo):
    mo.md(r"""
    ### Polars DataFrame export

    `to_dataframe(on_date)` produces a snapshot of all active PRNs with
    resolved metadata. Without a date, it returns the full assignment history.
    """)
    return


@app.cell
def _(catalog, mo, query_date):
    df_snapshot = catalog.to_dataframe(on_date=query_date)

    mo.md(f"""
    **Snapshot on {query_date}:** {len(df_snapshot)} active PRNs
    """)
    return (df_snapshot,)


@app.cell
def _(df_snapshot, mo):
    mo.ui.table(df_snapshot.head(30))
    return


@app.cell
def _(df_snapshot, mo, pl):
    # TX power statistics by constellation
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

    mo.md(r"""
    ### Transmit power by constellation

    Transmit power varies significantly across constellations and satellite
    generations. Higher TX power generally improves signal-to-noise ratio
    at the receiver.
    """)
    return (power_stats,)


@app.cell
def _(mo, power_stats):
    mo.ui.table(power_stats)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Dataset enrichment

    `enrich_dataset()` adds satellite metadata as `sid`-level coordinates
    on an existing `xarray.Dataset`. This enables filtering by satellite
    generation, TX power class, or orbital plane.
    """)
    return


@app.cell
def _(catalog, mo, query_date):
    import numpy as np
    import xarray as xr

    # Create a small synthetic dataset to demonstrate enrichment
    sids = ["G01|L1|C", "G07|L1|C", "E01|E1|C", "R01|G1|C", "C01|B1I|C"]
    epochs = np.array(
        [np.datetime64(f"2025-01-01T{h:02d}:00:00") for h in range(24)],
        dtype="datetime64[ns]",
    )
    rng = np.random.default_rng(42)
    snr = rng.uniform(30, 50, size=(len(epochs), len(sids))).astype(np.float32)

    demo_ds = xr.Dataset(
        {"SNR": (["epoch", "sid"], snr)},
        coords={"epoch": epochs, "sid": sids},
    )

    # Enrich with catalog metadata
    enriched = catalog.enrich_dataset(demo_ds, on_date=query_date)

    # Show the new coordinates
    coord_info = []
    for coord_name in ["svn", "block", "tx_power_watts", "mass_kg", "plane", "slot"]:
        if coord_name in enriched.coords:
            vals = enriched.coords[coord_name].values
            coord_info.append(f"    | `{coord_name}` | {list(vals)} |")

    coord_text = "\n".join(coord_info)

    mo.md(f"""
    **Enriched dataset coordinates (per SID):**

    | Coordinate | Values |
    |-----------|--------|
    {coord_text}

    These coordinates enable selections like:

    ```python
    # Only GPS-IIF satellites
    iif = enriched.sel(sid=enriched.coords["block"] == "GPS-IIF")

    # Satellites with TX power > 200W
    high_power = enriched.sel(sid=enriched.coords["tx_power_watts"] > 200)
    ```
    """)
    return demo_ds, enriched, epochs, np, rng, sids, snr, xr


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## Summary

    - **Store metadata** provides reproducible provenance for every Icechunk
      store, validated against DataCite/ACDD/STAC standards
    - **SatelliteCatalog** gives time-aware access to IGS satellite metadata
      with offline-first design (bundled fallback, never fails without internet)
    - Both integrate seamlessly with the canVODpy pipeline and marimo notebooks
    """)
    return


if __name__ == "__main__":
    app.run()
