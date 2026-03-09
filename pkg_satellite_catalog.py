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
    # SatelliteCatalog — IGS SINEX Satellite Metadata

    The **SatelliteCatalog** provides comprehensive satellite metadata from
    the IGS `igs_satellite_metadata.snx` SINEX file, maintained by DLR/IGS.

    It replaces the previous Wikipedia-based scraper with a reliable,
    offline-capable source covering all GNSS constellations: GPS, GLONASS,
    Galileo, BeiDou, QZSS, IRNSS/NavIC, and SBAS.

    ---

    *Nicolas F. Bader, CLIMERS — TU Wien*
    *Licensed under Apache 2.0.  Provided "as is" without warranty of any kind.*
    """
    )


@app.cell
def _():
    from datetime import date

    return (date,)


# ---------------------------------------------------------------------------
# Load catalog
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvod.readers.gnss_specs.satellite_catalog import SatelliteCatalog

    catalog = SatelliteCatalog.load()
    mo.md(f"Loaded SatelliteCatalog with **{len(catalog.identities):,}** satellite entries.")

    return SatelliteCatalog, catalog


# ---------------------------------------------------------------------------
# Active PRNs by constellation
# ---------------------------------------------------------------------------


@app.cell
def _(catalog, date, mo):
    _today = date(2025, 1, 1)
    _prefixes = {"G": "GPS", "R": "GLONASS", "E": "Galileo", "C": "BeiDou",
                 "J": "QZSS", "I": "IRNSS/NavIC", "S": "SBAS"}

    _rows = []
    for _prefix, _name in _prefixes.items():
        _prns = catalog.active_prns(_prefix, on_date=_today)
        _rows.append(f"| {_name} (`{_prefix}`) | {len(_prns)} |")

    mo.md(f"""
## Active PRNs on 2025-01-01

| Constellation | Active satellites |
|---|---|
{chr(10).join(_rows)}
""")


# ---------------------------------------------------------------------------
# PRN ↔ SVN mapping
# ---------------------------------------------------------------------------


@app.cell
def _(catalog, date, mo):
    _today = date(2025, 1, 1)
    _examples = ["G01", "G02", "E01", "E02", "R01", "C01"]
    _rows = []
    for _prn in _examples:
        _svn = catalog.prn_to_svn(_prn, on_date=_today)
        _rows.append(f"| `{_prn}` | `{_svn}` |")

    mo.md(f"""
## PRN → SVN Mapping

PRN (Pseudo-Random Noise) numbers are slot identifiers that can be reassigned
when satellites are decommissioned or replaced.  SVN (Space Vehicle Number) is
the permanent hardware identifier.

| PRN | SVN (on 2025-01-01) |
|---|---|
{chr(10).join(_rows)}

Use `prn_to_svn(prn, on_date)` to resolve the correct SVN for any date.
""")


# ---------------------------------------------------------------------------
# Satellite metadata
# ---------------------------------------------------------------------------


@app.cell
def _(catalog, date, mo):
    _today = date(2025, 1, 1)
    _meta = catalog.get_prn_metadata("G01", on_date=_today)
    _rows = "\n".join(f"| `{k}` | {v} |" for k, v in _meta.items())

    mo.md(f"""
## Satellite Metadata (G01)

`get_prn_metadata(prn, on_date)` returns all available information for a
satellite on a given date.

| Field | Value |
|---|---|
{_rows}
""")


# ---------------------------------------------------------------------------
# TX power and mass
# ---------------------------------------------------------------------------


@app.cell
def _(catalog, date, mo):
    _today = date(2025, 1, 1)
    _sats = ["G01", "G02", "E01", "E02", "R01", "C06"]
    _rows = []
    for _prn in _sats:
        _svn = catalog.prn_to_svn(_prn, on_date=_today)
        _power = catalog.tx_power(_svn, on_date=_today) if _svn else None
        _mass = catalog.mass(_svn, on_date=_today) if _svn else None
        _rows.append(
            f"| `{_prn}` | `{_svn or '?'}` | "
            f"{f'{_power:.1f} W' if _power else '—'} | "
            f"{f'{_mass:.0f} kg' if _mass else '—'} |"
        )

    mo.md(f"""
## Transmit Power & Mass

| PRN | SVN | TX Power | Mass |
|---|---|---|---|
{chr(10).join(_rows)}

TX power affects SNR measurements — higher-power satellites produce
stronger signals, which must be accounted for in VOD analysis.
""")


# ---------------------------------------------------------------------------
# GLONASS frequency channels
# ---------------------------------------------------------------------------


@app.cell
def _(catalog, date, mo):
    _today = date(2025, 1, 1)
    _glonass = catalog.active_prns("R", on_date=_today)
    _rows = []
    for _prn in sorted(_glonass)[:12]:
        _svn = catalog.prn_to_svn(_prn, on_date=_today)
        _ch = catalog.glonass_channel(_svn, on_date=_today) if _svn else None
        _rows.append(f"| `{_prn}` | `{_svn or '?'}` | {_ch if _ch is not None else '—'} |")

    mo.md(f"""
## GLONASS Frequency Channels

GLONASS uses Frequency Division Multiple Access (FDMA) — each satellite
broadcasts on a unique frequency channel (−7 to +6).  This is needed for
correct frequency assignment.

| PRN | SVN | Channel |
|---|---|---|
{chr(10).join(_rows)}
""")


# ---------------------------------------------------------------------------
# Catalog as DataFrame
# ---------------------------------------------------------------------------


@app.cell
def _(catalog, date, mo):
    _today = date(2025, 1, 1)
    df = catalog.to_dataframe(on_date=_today)

    mo.md(f"""
## Full Catalog as DataFrame

`to_dataframe(on_date)` returns a Polars DataFrame snapshot — one row per
active satellite on the given date.

Shape: **{df.shape[0]}** rows × **{df.shape[1]}** columns

Columns: {', '.join(f'`{c}`' for c in df.columns)}
""")

    return (df,)


@app.cell
def _(df, mo):
    mo.ui.dataframe(df.head(20))


# ---------------------------------------------------------------------------
# Data source
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Data Source & Update Chain

    1. **IGS** maintains `igs_satellite_metadata.snx` (updated every 2–4 weeks by DLR)
    2. **`SatelliteCatalog.load()`** searches:
       - User-specified directories
       - `~/.cache/canvod/` local cache
       - CDDIS/IGS FTP download (automatic)
       - Bundled fallback (ships with package, always works offline)
    3. The SINEX file contains 7 blocks: IDENTIFIER, PRN, TX_POWER, MASS,
       FREQUENCY_CHANNEL, PLANE, COM/ECCENTRICITY

    The catalog **never fails** — the bundled fallback guarantees offline
    operation, even if the IGS server is unreachable.
    """
    )


@app.cell
def _(mo):
    mo.md(
        r"""
    ---

    *canVODpy — CLIMERS, TU Wien | Apache 2.0 | No warranty*
    """
    )


if __name__ == "__main__":
    app.run()
