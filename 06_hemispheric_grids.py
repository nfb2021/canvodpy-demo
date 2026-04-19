# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvodpy>=0.2.2",
#   "marimo>=0.21.1",
# ]
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium", app_title="Hemispheric Grids", css_file="canvod_nordic.css"
)


# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    # Hemispheric Grids

    The **canvod-grids** package discretises the upper hemisphere into grid
    cells for spatially resolved VOD retrieval.  Each GNSS observation is
    assigned to the cell that contains its satellite direction ($\phi$,
    $\theta$), producing a spatial map of canopy transmittance.

    The hemisphere is parameterised in spherical coordinates:

    - **$\phi$ (azimuth)**: 0 to $2\pi$ radians (0 = North, clockwise)
    - **$\theta$ (polar angle)**: 0 to $\pi/2$ radians (0 = overhead,
      $\pi/2$ = horizon)

    Seven grid types are available, each with different trade-offs between
    cell uniformity, computational cost, and compatibility with external
    tools.

    ---

    """
    )

    return (mo,)


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------


@app.cell
def _():
    import numpy as np

    return (np,)


# ---------------------------------------------------------------------------
# Section: grid types
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Available grid types

    | Type | Key property | Use case |
    |------|-------------|----------|
    | **`equal_area`** | Constant solid angle per cell | Default for GNSS-T (fair spatial averaging) |
    | **`equal_angle`** | Constant angular spacing | Compatible with gnssvod (Humphrey et al.) |
    | **`equirectangular`** | Simple lat/lon grid | Quick visualisation |
    | **`fibonacci`** | Golden-spiral + Voronoi | Nearly uniform sampling |
    | **`healpix`** | Hierarchical equal area | CMB / astronomy heritage |
    | **`geodesic`** | Icosahedral subdivision | Triangular cells |
    | **`HTM`** | Hierarchical triangular mesh | Database indexing |

    The **equal-area** grid is the default for canvodpy.  It divides the
    hemisphere into concentric polar-angle bands, then subdivides each
    band into azimuthal sectors such that every cell subtends the same
    solid angle.  This ensures that observations at different elevations
    contribute equally to spatial averages.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: creating a grid
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Creating a grid

    The `create_hemigrid()` factory function is the main entry point.
    It accepts a grid type string and an angular resolution in degrees.
    """
    )

    return


@app.cell
def _(mo):
    from canvod.grids import create_hemigrid

    grid_2deg = create_hemigrid("equal_area", angular_resolution=2.0)

    mo.md(
        f"""
    ```python
    from canvod.grids import create_hemigrid

    grid = create_hemigrid("equal_area", angular_resolution=2.0)
    ```

    | Property | Value |
    |----------|-------|
    | **Grid type** | `{grid_2deg.grid_type}` |
    | **Cells** | {grid_2deg.ncells:,} |
    | **Angular resolution** | 2.0 degrees |
    | **Polar angle bands** | {len(grid_2deg.theta_lims) - 1} |
    """
    )

    return create_hemigrid, grid_2deg


# ---------------------------------------------------------------------------
# Section: grid data structure
# ---------------------------------------------------------------------------


@app.cell
def _(grid_2deg, mo, np):
    _df = grid_2deg.grid
    _sa = grid_2deg.get_solid_angles()
    _cv = np.std(_sa) / np.mean(_sa) * 100 if len(_sa) > 0 else 0

    mo.md(
        f"""
    ### GridData structure

    The `GridData` object is a frozen dataclass containing:

    - **`grid`**: a Polars DataFrame with one row per cell
      (columns include `cell_id`, `phi`, `theta`, cell boundaries)
    - **`theta_lims`**: polar-angle band boundaries
    - **`phi_lims`**: azimuthal boundaries per band
    - **`solid_angles`**: solid angle per cell (steradians)

    **Cell DataFrame** ({_df.shape[0]} rows x {_df.shape[1]} columns):

    Columns: {", ".join(f"`{c}`" for c in _df.columns)}

    **Solid angle uniformity**:

    | Statistic | Value |
    |-----------|-------|
    | **Mean** | {np.mean(_sa):.6f} sr |
    | **Std** | {np.std(_sa):.6f} sr |
    | **CV** | {_cv:.2f}% |
    | **Min / Max** | {np.min(_sa):.6f} / {np.max(_sa):.6f} sr |

    A coefficient of variation (CV) near zero indicates that all cells
    have nearly identical solid angles — the defining property of an
    equal-area grid.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: comparing grid types
# ---------------------------------------------------------------------------


@app.cell
def _(create_hemigrid, mo, np):
    _types = ["equal_area", "equal_angle", "fibonacci", "healpix"]
    _res = 5.0

    _rows = []
    for _t in _types:
        try:
            _g = create_hemigrid(_t, angular_resolution=_res)
            _sa = _g.get_solid_angles()
            _cv = np.std(_sa) / np.mean(_sa) * 100 if len(_sa) > 1 else 0
            _rows.append(
                f"| `{_t}` | {_g.ncells:,} | {np.mean(_sa):.5f} | {_cv:.1f}% |"
            )
        except Exception as _e:
            _rows.append(f"| `{_t}` | — | — | {_e} |")

    mo.md(
        f"""
    ### Comparison at {_res}-degree resolution

    | Grid type | Cells | Mean solid angle (sr) | CV |
    |-----------|-------|-----------------------|----|
    {chr(10).join(_rows)}

    The **CV (coefficient of variation)** of solid angles measures how
    uniform the cells are.  Equal-area and HEALPix grids achieve near-zero
    CV by construction.  Equal-angle grids have cells that shrink toward
    the pole (small $\\theta$), producing higher CV.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: cell assignment
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Assigning observations to grid cells

    Once a dataset has been augmented with $\phi$ and $\theta$ coordinates,
    each observation is assigned to the nearest grid cell.  The assignment
    uses a **KDTree** projected onto Cartesian coordinates for $O(n \log m)$
    lookups, where $n$ is the number of observations and $m$ is the number
    of grid cells.

    ```python
    from canvod.grids import add_cell_ids_to_vod_fast

    ds = add_cell_ids_to_vod_fast(ds, grid, grid_name="equal_area_2deg")
    # Adds: ds["cell_id_equal_area_2deg"] with shape (epoch, sid)
    ```

    Observations with non-finite $\phi$ or $\theta$ (below horizon,
    missing ephemeris) receive `NaN` cell IDs.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: converting to xarray
# ---------------------------------------------------------------------------


@app.cell
def _(grid_2deg, mo):
    from canvod.grids import grid_to_dataset

    ds_grid = grid_to_dataset(grid_2deg)

    _vars = list(ds_grid.data_vars)
    _rows = []
    for _v in _vars:
        _da = ds_grid[_v]
        _rows.append(f"| `{_v}` | `{', '.join(_da.dims)}` | `{_da.dtype}` |")  # type: ignore[no-matching-overload]

    mo.md(
        f"""
    ## Grid as xarray.Dataset

    `grid_to_dataset()` converts a `GridData` into an `xarray.Dataset`
    suitable for storage in Zarr/Icechunk or for merging with observation
    data.

    **Dimensions**: `{dict(ds_grid.sizes)}`

    | Variable | Dimensions | Dtype |
    |----------|-----------|-------|
    {chr(10).join(_rows)}

    **Attributes**: {", ".join(f"`{k}`" for k in ds_grid.attrs)}
    """
    )

    return ds_grid, grid_to_dataset


@app.cell
def _(ds_grid):
    ds_grid

    return


# ---------------------------------------------------------------------------
# Section: resolution choice
# ---------------------------------------------------------------------------


@app.cell
def _(create_hemigrid, mo):
    _resolutions = [1.0, 2.0, 5.0, 10.0, 15.0]
    _rows = []
    for _r in _resolutions:
        _g = create_hemigrid("equal_area", angular_resolution=_r)
        _rows.append(f"| {_r} deg | {_g.ncells:,} |")

    mo.md(
        f"""
    ## Choosing angular resolution

    The angular resolution controls the trade-off between spatial detail
    and the number of observations per cell.  Finer grids reveal spatial
    structure but require more data to fill each cell.

    | Resolution | Cells |
    |-----------|-------|
    {chr(10).join(_rows)}

    For a single day of observations from one receiver (typical for
    GNSS-T), **2 degrees** provides a good balance: enough cells to
    resolve azimuthal canopy structure, but not so many that cells are
    sparsely populated.

    The choice depends on the scientific question:

    - **2 deg**: standard for canopy structure analysis
    - **5 deg**: robust averages with fewer observations
    - **10--15 deg**: coarse monitoring or sites with few visible satellites
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

    **Previous**: [05 — Ephemeris & Coordinates](./05_ephemeris_coordinates.py)
    | **Next**: [07 — VOD Retrieval](./07_vod_retrieval.py)

    *canVODpy — Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
