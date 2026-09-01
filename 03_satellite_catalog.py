# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvod-readers",
#   "marimo>=0.21.1",
# ]
#
# [tool.uv.sources]
# canvod-readers = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-readers", rev = "6aa534fb8d78251c5640857361505d98a9b7dfb9" }
#
# [tool.marimo.opengraph]
# title = "03 · Satellite Catalog"
# description = "Query the IGS SatelliteCatalog for PRN metadata: SVN, block type, transmit power, mass, orbital plane, and GLONASS frequency channel."
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium", app_title="Satellite Catalog", css_file="canvod_nordic.css"
)


# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Satellite Catalog — IGS SINEX Metadata

    The **SatelliteCatalog** provides comprehensive satellite metadata from
    the IGS `igs_satellite_metadata.snx` SINEX file, maintained by DLR on
    behalf of the International GNSS Service (IGS).

    This catalog is the authoritative source for mapping between PRN
    (Pseudo-Random Noise number, a slot identifier) and SVN (Space Vehicle
    Number, a permanent hardware identifier).  PRNs are reassigned when
    satellites are decommissioned or replaced; SVNs are unique to each
    physical spacecraft.

    The catalog also provides transmit power, satellite mass, orbital plane
    and slot assignments, and GLONASS FDMA frequency channel numbers — all
    of which are relevant for precise GNSS-T analysis.

    ---

    **Data source**: IGS `igs_satellite_metadata.snx`, updated every 2--4
    weeks.  The catalog ships a bundled fallback copy and will never fail,
    even offline.

    """
    )

    return (mo,)


# ---------------------------------------------------------------------------
# Load catalog
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvod.readers.gnss_specs.satellite_catalog import SatelliteCatalog

    catalog = SatelliteCatalog.load()
    mo.md(
        f"Loaded catalog with **{len(catalog.identities):,}** satellite entries "
        f"(all constellations, all time)."
    )

    return SatelliteCatalog, catalog


# ---------------------------------------------------------------------------
# Active PRNs
# ---------------------------------------------------------------------------


@app.cell
def _(catalog, mo):
    from datetime import date

    _ref_date = date(2025, 1, 1)
    _prefixes = {
        "G": "GPS",
        "R": "GLONASS",
        "E": "Galileo",
        "C": "BeiDou",
        "J": "QZSS",
        "I": "IRNSS/NavIC",
        "S": "SBAS",
    }

    _rows = []
    for _p, _name in _prefixes.items():
        _prns = catalog.active_prns(_p, on_date=_ref_date)
        _rows.append(
            f"| {_name} (`{_p}`) | {len(_prns)} | `{', '.join(sorted(_prns)[:6])}`, ... |"
        )

    mo.md(
        f"""
    ## Active satellites on {_ref_date}

    `active_prns(system_prefix, on_date)` returns the set of PRNs that
    were operational on a given date.  This is determined from the PRN
    assignment start and end dates in the SINEX file.

    | Constellation | Active | Sample PRNs |
    |---------------|--------|-------------|
    {chr(10).join(_rows)}

    These counts reflect the *operational* constellation, not the total
    number of satellites ever launched.  Decommissioned satellites have
    end dates in the past.
    """
    )

    return (date,)


# ---------------------------------------------------------------------------
# PRN <-> SVN mapping
# ---------------------------------------------------------------------------


@app.cell
def _(catalog, date, mo):
    _ref = date(2025, 1, 1)
    _examples = ["G01", "G02", "G32", "E01", "E02", "R01", "R24", "C01", "C06"]
    _rows = []
    for _prn in _examples:
        _svn = catalog.prn_to_svn(_prn, on_date=_ref)
        _rows.append(f"| `{_prn}` | `{_svn or '---'}` |")

    mo.md(
        f"""
    ## PRN to SVN mapping

    A PRN is a **slot** in a constellation's signal plan.  When a new
    satellite replaces an old one in the same orbital slot, it inherits
    the PRN but receives a new SVN.

    | PRN | SVN (on {_ref}) |
    |-----|-----------------|
    {chr(10).join(_rows)}

    The reverse lookup is also available:

    ```python
    catalog.svn_to_prn("G076", on_date=date(2025, 1, 1))  # -> "G01"
    ```
    """
    )

    return


# ---------------------------------------------------------------------------
# Reassignment history
# ---------------------------------------------------------------------------


@app.cell
def _(catalog, date, mo):
    _start = date(2020, 1, 1)
    _end = date(2025, 1, 1)
    _reassignments = catalog.reassignments_in_range("G", _start, _end)

    if _reassignments:
        _rows = []
        for _r in _reassignments[:10]:
            _rows.append(
                f"| `{_r['prn']}` | `{_r['old_svn']}` -> `{_r['new_svn']}` | {_r['date']} |"
            )
        _table = f"""
    | PRN | SVN change | Date |
    |-----|------------|------|
    {chr(10).join(_rows)}
    """
    else:
        _table = "No GPS PRN reassignments found in this period."

    mo.md(
        f"""
    ## PRN reassignment history

    `reassignments_in_range(prefix, start, end)` identifies PRN slot changes.
    These events matter for long time series: the same PRN may refer to
    different physical hardware (with different transmit power and antenna
    characteristics) before and after a reassignment.

    **GPS reassignments ({_start} to {_end})**:

    {_table}
    """
    )

    return


# ---------------------------------------------------------------------------
# Satellite metadata
# ---------------------------------------------------------------------------


@app.cell
def _(catalog, date, mo):
    _ref = date(2025, 1, 1)
    _meta = catalog.get_prn_metadata("G01", on_date=_ref)

    _rows = "\n".join(f"| `{k}` | {v} |" for k, v in _meta.items())

    mo.md(
        f"""
    ## Full satellite metadata

    `get_prn_metadata(prn, on_date)` aggregates all available information
    for a satellite into a single dictionary.

    ### G01 on {_ref}

    | Field | Value |
    |-------|-------|
    {_rows}
    """
    )

    return


# ---------------------------------------------------------------------------
# TX power and mass
# ---------------------------------------------------------------------------


@app.cell
def _(catalog, date, mo):
    _ref = date(2025, 1, 1)
    _sats = ["G01", "G02", "G11", "E01", "E02", "R01", "C06"]
    _rows = []
    for _prn in _sats:
        _svn = catalog.prn_to_svn(_prn, on_date=_ref)
        _power = catalog.tx_power(_svn, on_date=_ref) if _svn else None
        _mass = catalog.mass(_svn, on_date=_ref) if _svn else None
        _rows.append(
            f"| `{_prn}` | `{_svn or '?'}` | "
            f"{f'{_power:.1f} W' if _power else '---'} | "
            f"{f'{_mass:.0f} kg' if _mass else '---'} |"
        )

    mo.md(
        f"""
    ## Transmit power and mass

    | PRN | SVN | TX Power | Mass |
    |-----|-----|----------|------|
    {chr(10).join(_rows)}

    Transmit power affects the received SNR: higher-power satellites produce
    stronger signals at the receiver.  In GNSS-T, this is cancelled out when
    computing the canopy-to-reference SNR ratio (both receivers see the same
    transmit power), but it affects the absolute SNR level and therefore the
    signal-to-noise budget.

    Satellite mass is relevant for orbit perturbation models (solar radiation
    pressure scales with area-to-mass ratio).
    """
    )

    return


# ---------------------------------------------------------------------------
# GLONASS frequency channels
# ---------------------------------------------------------------------------


@app.cell
def _(catalog, date, mo):
    _ref = date(2025, 1, 1)
    _glonass = sorted(catalog.active_prns("R", on_date=_ref))
    _rows = []
    for _prn in _glonass[:12]:
        _svn = catalog.prn_to_svn(_prn, on_date=_ref)
        _ch = catalog.glonass_channel(_svn, on_date=_ref) if _svn else None
        _rows.append(
            f"| `{_prn}` | `{_svn or '?'}` | {_ch if _ch is not None else '---'} |"
        )

    mo.md(
        f"""
    ## GLONASS frequency channels

    Unlike GPS, Galileo, and BeiDou (which use Code Division Multiple Access),
    GLONASS uses **Frequency Division Multiple Access (FDMA)** for its L1 and
    L2 signals.  Each satellite broadcasts on a unique frequency channel
    number (ranging from -7 to +6), and antipodal satellites (180 degrees
    apart in the orbital plane) share the same channel.

    | PRN | SVN | Channel |
    |-----|-----|---------|
    {chr(10).join(_rows)}

    The frequency channel determines the exact carrier frequency:

    $$f_{{L1}} = 1602.0 + k \\times 0.5625 \\text{{ MHz}}$$
    $$f_{{L2}} = 1246.0 + k \\times 0.4375 \\text{{ MHz}}$$

    where $k$ is the channel number.  The SBF reader resolves these
    frequencies from a live `ChannelStatus` cache; the catalog provides
    the ground-truth assignment for validation.
    """
    )

    return


# ---------------------------------------------------------------------------
# Catalog as DataFrame
# ---------------------------------------------------------------------------


@app.cell
def _(catalog, date, mo):
    _ref = date(2025, 1, 1)
    df_catalog = catalog.to_dataframe(on_date=_ref)

    mo.md(
        f"""
    ## Catalog as Polars DataFrame

    `to_dataframe(on_date)` returns a snapshot of all active satellites
    on a given date as a Polars DataFrame — one row per satellite.

    **Shape**: {df_catalog.shape[0]} rows x {df_catalog.shape[1]} columns

    **Columns**: {", ".join(f"`{c}`" for c in df_catalog.columns)}
    """
    )

    return (df_catalog,)


@app.cell
def _(df_catalog, mo):
    mo.ui.dataframe(df_catalog.head(20))

    return


# ---------------------------------------------------------------------------
# Load chain
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Data source and load chain

    `SatelliteCatalog.load()` searches for the SINEX file in this order:

    1. **User-specified directories** (if provided)
    2. **Local cache** (`~/.cache/canvod/`)
    3. **Download from IGS** (CDDIS FTP, automatic)
    4. **Bundled fallback** (ships with canvod-readers)

    The fallback guarantees that the catalog **never fails**, even without
    network access.  The bundled copy is updated with each canvodpy release.

    The SINEX file contains seven parsed blocks:

    | Block | Contents |
    |-------|----------|
    | `SATELLITE/IDENTIFIER` | SVN, COSPAR ID, satellite name, launch date |
    | `SATELLITE/PRN` | PRN-to-SVN mapping with date ranges |
    | `SATELLITE/TX_POWER` | Transmit power per SVN (Watts) |
    | `SATELLITE/MASS` | Satellite mass per SVN (kg) |
    | `SATELLITE/FREQUENCY_CHANNEL` | GLONASS FDMA channel assignments |
    | `SATELLITE/PLANE` | Orbital plane and slot per SVN |
    | `SATELLITE/COM/ECCENTRICITY` | Center-of-mass offset from antenna |
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

    **Previous**: [02 — RINEX Reading](./02_rinex_reading.py)
    | **Next**: [04 — SBF Reading](./04_sbf_reading.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
