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
    # canvod-auxiliary — Ephemeris & Coordinate Augmentation

    The **canvod-auxiliary** package downloads precise satellite orbits (SP3)
    and clock corrections (CLK) from IGS analysis centres, interpolates them
    to observation epochs, and computes satellite positions in a local
    spherical coordinate system (theta, phi) relative to the receiver.

    This notebook walks through the full augmentation pipeline on one day
    of RINEX data from Rosalia.

    ---

    *Nicolas F. Bader, CLIMERS — TU Wien*
    *Licensed under Apache 2.0.  Provided "as is" without warranty of any kind.*
    """
    )


@app.cell
def _():
    from pathlib import Path

    import numpy as np

    return Path, np


@app.cell
def _():
    from _paths import AUX_DATA_DIR, ROSALIA_CANOPY_DIR

    RINEX_DIR = ROSALIA_CANOPY_DIR / "25001"
    SAMPLE_FILE = sorted(RINEX_DIR.glob("*.rnx"))[0]

    return AUX_DATA_DIR, RINEX_DIR, SAMPLE_FILE


# ---------------------------------------------------------------------------
# Parse RINEX
# ---------------------------------------------------------------------------


@app.cell
def _(SAMPLE_FILE):
    from canvod.readers import Rnxv3Obs

    reader = Rnxv3Obs(fpath=SAMPLE_FILE)
    ds_raw = reader.to_ds()

    return Rnxv3Obs, ds_raw, reader


@app.cell
def _(SAMPLE_FILE, ds_raw, mo):
    mo.md(f"""
## Raw RINEX Dataset

Parsed `{SAMPLE_FILE.name}` — **{ds_raw.sizes['epoch']:,}** epochs × **{ds_raw.sizes['sid']:,}** SIDs.

The dataset has `SNR` but no spatial coordinates yet.  The augmentation step
adds `theta` (polar angle from zenith) and `phi` (azimuth from North).
""")


# ---------------------------------------------------------------------------
# Receiver Position
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Receiver Position (ECEF)

    The augmentation requires the receiver's position in Earth-Centered
    Earth-Fixed (ECEF) coordinates.  This is extracted from the RINEX header
    `APPROX POSITION XYZ` field.
    """
    )


@app.cell
def _(mo, reader):
    from canvod.auxiliary import ECEFPosition

    _pos = reader.header.approx_position
    receiver_pos = ECEFPosition(
        x=_pos[0].magnitude, y=_pos[1].magnitude, z=_pos[2].magnitude
    )
    _geo = receiver_pos.to_geodetic()

    mo.md(f"""
| Frame | X / Lat | Y / Lon | Z / Alt |
|---|---|---|---|
| ECEF (m) | {receiver_pos.x:,.2f} | {receiver_pos.y:,.2f} | {receiver_pos.z:,.2f} |
| Geodetic | {_geo[0]:.6f}° | {_geo[1]:.6f}° | {_geo[2]:.1f} m |
""")

    return ECEFPosition, receiver_pos


# ---------------------------------------------------------------------------
# Augmentation
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Ephemeris Augmentation

    `augment_with_ephemeris()` performs these steps:

    1. **Download** SP3 (orbit) and CLK (clock) files from the selected agency
    2. **Interpolate** satellite positions to observation epochs (Hermite cubic for orbits, linear for clocks)
    3. **Transform** ECEF satellite coordinates to local spherical coordinates (theta, phi) relative to the receiver
    4. **Attach** theta and phi as data variables on the dataset
    """
    )


@app.cell
def _(AUX_DATA_DIR, ds_raw, receiver_pos):
    from canvodpy.functional import augment_with_ephemeris

    ds_aug = augment_with_ephemeris(
        ds_raw,
        receiver_position=receiver_pos,
        source="final",
        agency="COD",
        date="2025001",
        aux_data_dir=AUX_DATA_DIR,
    )

    return augment_with_ephemeris, ds_aug


@app.cell
def _(ds_aug, mo, np):
    _theta = ds_aug["theta"].values
    _phi = ds_aug["phi"].values
    _valid = np.isfinite(_theta)

    mo.md(f"""
## Augmented Dataset

| Metric | Value |
|---|---|
| Variables | {', '.join(f'`{v}`' for v in ds_aug.data_vars)} |
| Valid theta/phi | {_valid.sum():,} / {_valid.size:,} ({100 * _valid.sum() / _valid.size:.1f}%) |
| Theta range | {np.nanmin(_theta):.4f} — {np.nanmax(_theta):.4f} rad |
| Phi range | {np.nanmin(_phi):.4f} — {np.nanmax(_phi):.4f} rad |

Theta = 0 is zenith, π/2 is horizon.  Phi = 0 is North, increasing clockwise.
NaN values indicate epochs where a satellite was below the horizon or ephemeris
data was unavailable.
""")


# ---------------------------------------------------------------------------
# Coordinate system diagram
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Coordinate Convention

    ```
              Zenith (θ=0)
                 │
                 │  ╲ satellite
                 │ θ ╲
                 │    ╲
    ─────────────┼─────────── Horizon (θ=π/2)
                 │
               Receiver

    φ = 0°  → North
    φ = 90° → East
    φ = 180°→ South
    φ = 270°→ West
    ```

    - **θ (theta):** Polar angle from zenith [0, π/2] — 0 = directly overhead
    - **φ (phi):** Azimuth from North, clockwise [0, 2π)
    - **r:** Radial distance receiver → satellite (optional, not stored by default)
    """
    )


# ---------------------------------------------------------------------------
# Available agencies
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvod.auxiliary import ProductRegistry

    _reg = ProductRegistry()
    _rows = []
    for _agency in sorted(_reg.list_agencies()):
        _products = _reg.get_products_for_agency(_agency)
        _rows.append(f"| `{_agency}` | {', '.join(f'`{p}`' for p in _products)} |")

    mo.md(f"""
## Available Analysis Centres

The product registry defines which agencies and product types can be used
for ephemeris downloads.

| Agency | Product types |
|---|---|
{chr(10).join(_rows)}

**Recommendation:** CODE (`COD`) final products provide the highest accuracy
(~2 cm orbit, ~0.1 ns clock) with a ~2 week latency.  For near-real-time
processing, use `rapid` (~1 day) or `ultra` (predicted).
""")

    return (ProductRegistry,)


# ---------------------------------------------------------------------------
# Position utilities
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Position Utilities

    The package provides `ECEFPosition` and `GeodeticPosition` dataclasses
    with bidirectional conversion.

    ```python
    from canvod.auxiliary import ECEFPosition, GeodeticPosition

    # ECEF → Geodetic
    ecef = ECEFPosition(x=4194000, y=1162000, z=4647000)
    lat, lon, alt = ecef.to_geodetic()

    # Geodetic → ECEF
    geo = GeodeticPosition(lat=47.1, lon=15.5, alt=400)
    ecef = geo.to_ecef()
    ```
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
