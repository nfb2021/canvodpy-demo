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
#   "pooch>=1.6",
#   "marimo>=0.21.1",
# ]
#
# [tool.uv.sources]
# canvod-auxiliary = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-auxiliary", rev = "f30959f710ca71e28433135f25140097d0c0e08f" }
# canvod-config = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-config", rev = "f30959f710ca71e28433135f25140097d0c0e08f" }
# canvod-grids = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-grids", rev = "f30959f710ca71e28433135f25140097d0c0e08f" }
# canvod-ops = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-ops", rev = "f30959f710ca71e28433135f25140097d0c0e08f" }
# canvod-preflight = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-preflight", rev = "f30959f710ca71e28433135f25140097d0c0e08f" }
# canvod-readers = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-readers", rev = "f30959f710ca71e28433135f25140097d0c0e08f" }
# canvod-store = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-store", rev = "f30959f710ca71e28433135f25140097d0c0e08f" }
# canvod-store-metadata = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-store-metadata", rev = "f30959f710ca71e28433135f25140097d0c0e08f" }
# canvod-utils = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-utils", rev = "f30959f710ca71e28433135f25140097d0c0e08f" }
# canvod-viz = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-viz", rev = "f30959f710ca71e28433135f25140097d0c0e08f" }
# canvod-vod = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "packages/canvod-vod", rev = "f30959f710ca71e28433135f25140097d0c0e08f" }
# canvodpy = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "canvodpy", rev = "f30959f710ca71e28433135f25140097d0c0e08f" }
#
# [tool.marimo.opengraph]
# title = "21 · Your Own VOD Calculator"
# description = "Write a VOD calculator of your own, register it, compare it with the built-in tau-omega calculator, and turn it into a plugin that canvodpy run can use."
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium", app_title="Your Own VOD Calculator", css_file="canvod_nordic.css",
    html_head_file="canvod_head.html"
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

    # Your Own VOD Calculator

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/21_plugins.py?mode=edit)

    canVODpy computes VOD with the calculators it knows by name. You can
    add your own without changing canVODpy:

    1. write a class that inherits the abstract base class
       `VODCalculator`;
    2. register it with `VODFactory` to use it in your own Python code;
    3. put it in a small package of your own, a **plugin**, to use it with
       `canvodpy run`.

    This notebook goes through the three steps with one file per receiver
    of the demo data. Readers work the same way, with `GNSSDataReader`
    and `ReaderFactory`; the
    [plugins guide](https://canvodpy.eu/guides/plugins/)
    shows both.

    ---
    """
    )

    return (mo,)


@app.cell
def _():
    import _paths
    from _download import marimo_downloader

    _paths.ensure_data(downloader=marimo_downloader)


# ---------------------------------------------------------------------------
# Section: what is registered
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvodpy import GridFactory, ReaderFactory, VODFactory

    mo.md(
        f"""
    ## What canVODpy knows by name

    Each kind of component has an abstract base class and a factory, which
    maps names to classes. canVODpy registers its own classes when it is
    imported, and the installed plugins after them.

    | Factory | Base class | Registered now |
    |---------|------------|----------------|
    | `ReaderFactory` | `GNSSDataReader` | {", ".join(f"`{n}`" for n in ReaderFactory.list_available())} |
    | `VODFactory` | `VODCalculator` | {", ".join(f"`{n}`" for n in VODFactory.list_available())} |
    | `GridFactory` | `BaseGridBuilder` | {", ".join(f"`{n}`" for n in GridFactory.list_available())} |

    `canvodpy run --vod-calculator` offers exactly the names that
    `VODFactory` holds when canVODpy is imported.
    """
    )

    return (VODFactory,)


# ---------------------------------------------------------------------------
# Section: paired datasets
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## The data

    A calculator gets two datasets: the canopy receiver's and the
    reference receiver's, each with `SNR`, `theta` and `phi` on the
    dimensions `(epoch, sid)`. As in
    [10 · VOD Retrieval](./10_vod_retrieval.py), we read one file per
    receiver and add the angles of each satellite from the orbits.
    """
    )

    return


@app.cell
def _():
    import numpy as np
    import xarray as xr
    from canvod.auxiliary import (
        ECEFPosition,
        add_spherical_coords_to_dataset,
        compute_spherical_coordinates,
    )
    from canvod.readers import Rnxv3Obs

    from _paths import AUX_DATA_DIR, ROSALIA_CANOPY_DIR, ROSALIA_REFERENCE_DIR

    _aux = xr.open_zarr(str(AUX_DATA_DIR / "aux_2025001.zarr"), decode_timedelta=False)

    def _with_angles(fpath):
        ds = Rnxv3Obs(fpath=fpath).to_ds(
            keep_data_vars=["SNR"], write_global_attrs=True
        )
        sids = np.intersect1d(ds.sid.values, _aux.sid.values)
        epochs = np.intersect1d(ds.epoch.values, _aux.epoch.values)
        aux = _aux.sel(sid=sids, epoch=epochs)
        r, theta, phi = compute_spherical_coordinates(
            aux["X"].values,
            aux["Y"].values,
            aux["Z"].values,
            ECEFPosition.from_ds_metadata(ds),
        )
        return add_spherical_coords_to_dataset(
            ds.sel(sid=sids, epoch=epochs), r, theta, phi
        )

    ds_canopy = _with_angles(min(ROSALIA_CANOPY_DIR.glob("25001/*.rnx")))
    ds_reference = _with_angles(min(ROSALIA_REFERENCE_DIR.glob("25001/*.rnx")))

    return ds_canopy, ds_reference, np, xr


# ---------------------------------------------------------------------------
# Section: the calculator
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Step 1: the calculator

    A calculator inherits `VODCalculator` and implements one method,
    `calculate_vod()`. When the calculator is created, the base class has
    already restricted `canopy_ds` and `sky_ds` to the epochs and signals
    both receivers have.

    The built-in `tau_omega` calculator computes the transmissivity $T$
    from the difference of the two SNR values in decibels and returns
    $-\ln(T)\cos\theta$. The example below leaves out the factor
    $\cos\theta$ and returns $-\ln(T)$. It is only an example of how a
    calculator is built, not a model to use; replace `calculate_vod()`
    with your own.
    """
    )

    return


@app.cell
def _(np, xr):
    from canvod.vod.calculator import VODCalculator

    class SlantOpticalDepth(VODCalculator):
        """Example calculator: -ln(T), without the factor cos(theta)."""

        def calculate_vod(self) -> xr.Dataset:
            delta_snr = self.canopy_ds["SNR"] - self.sky_ds["SNR"]
            transmissivity = 10 ** (delta_snr / 10)
            vod = -np.log(transmissivity)
            # Keep the grid cells of a grid assignment (processing.preprocessing)
            cell_ids = {
                name: self.canopy_ds[name]
                for name in self.canopy_ds.data_vars
                if str(name).startswith("cell_id_")
            }
            return xr.Dataset(
                {
                    "VOD": vod,
                    "phi": self.canopy_ds["phi"],
                    "theta": self.canopy_ds["theta"],
                    **cell_ids,
                },
                coords=self.canopy_ds.coords,
            )

    return SlantOpticalDepth, VODCalculator


@app.cell
def _(VODCalculator, ds_canopy, ds_reference, mo):
    class Incomplete(VODCalculator):
        """Lacks calculate_vod()."""

    try:
        Incomplete(canopy_ds=ds_canopy, sky_ds=ds_reference)
        _abc_error = "no error"
    except TypeError as _exc:
        _abc_error = str(_exc)

    mo.md(
        f"""
    Because `VODCalculator` is an abstract base class, Python refuses to
    create a calculator that lacks `calculate_vod()`. The error comes when
    the object is created, not halfway through a run:

    ```python
    class Incomplete(VODCalculator):
        \"\"\"Lacks calculate_vod().\"\"\"

    Incomplete(canopy_ds=ds_canopy, sky_ds=ds_reference)
    ```

    ```text
    TypeError: {_abc_error}
    ```
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: register and compare
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Step 2: register it in your code

    `VODFactory.register()` adds the class under a name of your choice.
    It checks that the class inherits `VODCalculator` and refuses a name
    that is already taken. This notebook passes `replace=True`, so that
    running the cell again replaces the class registered the first time.
    """
    )

    return


@app.cell
def _(SlantOpticalDepth, VODFactory):
    VODFactory.register("slant_optical_depth", SlantOpticalDepth, replace=True)
    VODFactory.list_available()
    return


@app.cell
def _(VODFactory, mo):
    from canvod.vod.calculator import TauOmegaZerothOrder

    class AnotherTauOmega(TauOmegaZerothOrder):
        """Would replace the built-in calculator."""

    try:
        VODFactory.register("tau_omega", AnotherTauOmega)
        _taken_error = "no error"
    except ValueError as _exc:
        _taken_error = str(_exc)

    mo.md(
        f"""
    Without `replace=True`, a name that is taken is an error, so a script
    can't replace the built-in calculator by accident:

    ```text
    ValueError: {_taken_error}
    ```
    """
    )

    return


@app.cell
def _(mo):
    mo.md(
        r"""
    Now both calculators are created by name, in the same way
    `Site(...).vod` creates the calculator it is given:
    """
    )

    return


@app.cell
def _(VODFactory, ds_canopy, ds_reference):
    vod_tau_omega = VODFactory.create(
        "tau_omega", canopy_ds=ds_canopy, sky_ds=ds_reference
    ).calculate_vod()
    vod_slant = VODFactory.create(
        "slant_optical_depth", canopy_ds=ds_canopy, sky_ds=ds_reference
    ).calculate_vod()
    return vod_slant, vod_tau_omega


@app.cell
def _(mo, np, vod_slant, vod_tau_omega):
    _both = np.isfinite(vod_tau_omega["VOD"].values) & np.isfinite(
        vod_slant["VOD"].values
    )
    _expected = vod_slant["VOD"].values * np.cos(vod_slant["theta"].values)
    _max_diff = np.max(np.abs(vod_tau_omega["VOD"].values[_both] - _expected[_both]))

    mo.md(
        f"""
    ### Comparison

    | | `tau_omega` | `slant_optical_depth` |
    |-|-------------|-----------------------|
    | **Dimensions** | `{dict(vod_tau_omega.sizes)}` | `{dict(vod_slant.sizes)}` |
    | **Variables** | {list(vod_tau_omega.data_vars)} | {list(vod_slant.data_vars)} |
    | **Median VOD** | {np.nanmedian(vod_tau_omega["VOD"].values):.4f} | {np.nanmedian(vod_slant["VOD"].values):.4f} |

    The two differ only by the factor $\\cos\\theta$. Over the
    {_both.sum():,} values both calculators give, `tau_omega` and
    `slant_optical_depth` $\\times \\cos\\theta$ differ by at most
    {_max_diff:.1e}.
    """
    )

    return


# ---------------------------------------------------------------------------
# Section: plugin package
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    from canvod.utils.plugins import VOD_CALCULATOR_GROUP, plugin_names

    _installed = plugin_names(VOD_CALCULATOR_GROUP)

    mo.md(
        f"""
    ## Step 3: a plugin for `canvodpy run`

    A registration in your code lasts as long as your Python session.
    `canvodpy run` starts its own Python process and doesn't see it.
    To use the calculator there, put it in a package of your own and
    declare it as an **entry point**, Python's standard way for a package
    to offer plugins:

    ```text
    my-canvod-plugin/
    ├── pyproject.toml
    └── src/
        └── my_canvod_plugin/
            ├── __init__.py
            └── calculator.py      # the class SlantOpticalDepth from above
    ```

    ```toml
    # pyproject.toml
    [project]
    name = "my-canvod-plugin"
    version = "0.1.0"
    requires-python = ">=3.14"
    dependencies = ["canvodpy"]

    [project.entry-points."canvodpy.vod_calculators"]
    slant_optical_depth = "my_canvod_plugin.calculator:SlantOpticalDepth"

    [build-system]
    requires = ["uv_build"]
    build-backend = "uv_build"
    ```

    Install it into the environment canVODpy runs in, and run with it:

    ```bash
    uv add --editable ./my-canvod-plugin
    canvodpy run --site ExampleSite --start 2025001 --end 2025007 \\
        --vod-calculator slant_optical_depth
    ```

    When canVODpy is imported, it imports every installed plugin and
    checks it: the class must inherit `VODCalculator`, and its name must
    not be the name of a built-in calculator or of another installed
    plugin. A plugin that fails a check stops canVODpy with an error that
    names the plugin's package. The VOD store keeps the results under the
    calculator's name, `slant_optical_depth/<analysis>`, apart from those
    of `tau_omega`.

    Installed calculator plugins in this environment:
    {", ".join(f"`{n}`" for n in _installed) if _installed else "none"}.
    This notebook can't install a package of its own, so it only shows
    the files.

    Reader plugins use the entry point group `canvodpy.readers` and
    inherit `GNSSDataReader`; the
    [plugins guide](https://canvodpy.eu/guides/plugins/)
    shows a complete package with a reader and a calculator.
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

    **Previous**: [20 · Batch Processing](./20_workflow_batch_processing.py)

    *canVODpy · Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
