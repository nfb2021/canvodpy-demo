import marimo

__generated_with = "0.19.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
 
    """)


@app.cell
def _(mo):
    from pathlib import Path

    # Demo data directory (from submodule)
    DEMO_ROOT = Path(__file__).parent
    DEMO_DATA = DEMO_ROOT / "data"

    # Rosalia site paths
    ROSALIA_DIR = DEMO_DATA / "01_Rosalia"
    ROSALIA_REFERENCE = ROSALIA_DIR / "01_reference/01_GNSS/01_raw"
    ROSALIA_CANOPY = ROSALIA_DIR / "02_canopy/01_GNSS/01_raw"
    AUX_DIR = DEMO_DATA / "00_aux_files"

    # Output directory
    OUTPUT_DIR = DEMO_ROOT / "outputs"
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Check directories exist
    if not DEMO_DATA.exists():
        mo.md("""
        ⚠️ **Demo data not found!**

        Make sure the demo submodule is initialized:
        ```bash
        git submodule update --init demo
        ```
        """)
    else:
        mo.md(f"""
        ✅ **Demo Data Located**

        - **Reference RINEX**: `{ROSALIA_REFERENCE}`
        - **Canopy RINEX**: `{ROSALIA_CANOPY}`
        - **Auxiliary Files**: `{AUX_DIR}`
        - **Output**: `{OUTPUT_DIR}`
        """)
    return (ROSALIA_REFERENCE,)


@app.cell
def _(mo):
    mo.md(r"""
    # Let's define the test file
    """)


@app.cell
def _(ROSALIA_REFERENCE, mo):
    TEST_FILE = list((ROSALIA_REFERENCE / "25001").glob("*.25o"))[0]

    mo.md(f"""
        📄 **Test File Located**

        - `{TEST_FILE}`
        """)
    return (TEST_FILE,)


@app.cell
def _(mo):
    mo.md(r"""
    # We already know that the file is a RINEX v3.04 file so we will use the `Rnxv3Obs` class to load it
    """)


@app.cell
def _(TEST_FILE):
    import xarray as xr
    from canvod.readers import Rnxv3Obs

    obs = Rnxv3Obs(fpath=TEST_FILE)
    obs
    return obs, xr


@app.cell
def _(mo):
    mo.md(r"""
    The observation object contains all information stored within the RINEX file, like the header.
    """)


@app.cell
def _(obs):
    obs.header


@app.cell
def _(obs):
    # Let's define a helper dataframe to visually assess the information contained within

    import pandas as pd

    df_header = pd.DataFrame.from_dict(
        obs.header.__dict__, orient="index", columns=["Value"]
    )
    df_header


@app.cell
def _(mo):
    mo.md(r"""
    Indeed, the RINEX is version 3.04. Some information is serialized, like the antenna appproximate position.
    """)


@app.cell
def _(obs):
    obs.header.approx_position


@app.cell
def _(mo):
    mo.md(r"""
    Now, lets have a look at how the observation data is stored within the object.
    """)


@app.cell
def _(obs):
    obs.infer_sampling_interval(), obs.infer_dump_interval()


@app.cell
def _(mo):
    mo.md(r"""
    Each recorded epoch is stored within the `Rnxv3Ob.epochs` list, as a `Rnxv3ObsEpochRecord` object. Each epoch object contains the epoch header information as well as the list of observed satellites at that epoch, again each as its own object wit the recorded observations.
    """)


@app.cell
def _(obs):
    obs.epochs[0]


@app.cell
def _(mo, obs):
    mo.vstack(
        [
            mo.md("### Epoch Record Line of First Epoch"),
            obs.epochs[0].info,
            mo.md("### Data of First Satellite withtin First Epoch"),
            obs.epochs[0].data[0],
        ]
    )


@app.cell
def _(mo):
    mo.md(r"""
    Usually though, we want to work with the observation data in a more convenient format, like an `xarray.Dataset`. The `to_ds()` method allows us to convert the observation data into such format. All header information is preserved as dataset attributes, each dataset dimension, coordinate and data variable contains metadata metadata as well. Per default, only the Signal-to-Noise data is included in the dataset. We can include additional observation types by specifying them via the `keep_rnx_data_vars` argument.

    🚨 Warning: While LLI and SSI may be written to the dataset, this feature is still under development and no guarantee of correctness is given.

    We want to conserve all information, that means per value of SNR we need to track:
    1. Epoch
    2. Satellite PRN
    3. Carrier Band
    4. Ranging Code Type

    The GNSS system may be deduced from the satellite PNR. This means that technically SNR possesses four degrees of freedom, or is four dimensional

    \begin{equation}
    SNR = f(\text{Epoch}, \text{Satellite PRN}, \text{Carrier Band}, \text{Ranging Code Type})
    \end{equation}


    If all four dimensions were to be taken as dataset dimensions, this would create plenty of NaNs, potentially an issue with lots of data and unnecesarily complex to work with later.

    Here, we use the **Signal ID**, **SID** for short. It reduces the dimensionality to only two, as it is defiend as a linearcombination:

    \begin{equation}
    SNR = f(\text{Epoch}, \underbrace{\text{SID}}_{= \text{SV|Band|Code}})
    \end{equation}

    Examples: `C02|B1C|P` is the information trasnmitted by BDS satellite C02 on the B1C band using the P code.
    Nomenclature strictly follows RINEX v3.04 conventions.
    """)


@app.cell
def _(obs):
    obs.to_ds(
        keep_rnx_data_vars=["SNR", "Doppler", "Pseudorange", "Phase", "LLI", "SSI"],
        write_global_attrs=True,
    )


@app.cell
def _(mo):
    mo.md(r"""
    # Let's read in the day's worth of data

    We will do this parallelized using a `ProcessPoolExecutor`. To do so, we need a helper function and import that:

    python
    ```
    # canvod_readers_parallel.py
    from pathlib import Path
    import xarray as xr

    def read_rinex_file(fpath: Path) -> xr.Dataset:
        obs = Rnxv3Obs(fpath=fpath)
        return obs.to_ds(keep_rnx_data_vars=["SNR"])
    ```
    """)


@app.cell
def _(ROSALIA_REFERENCE, xr):
    from concurrent.futures import ProcessPoolExecutor, as_completed

    from canvod_readers_parallel import read_rinex_file
    from natsort import natsorted

    rinex_files = natsorted((ROSALIA_REFERENCE / "25001").glob("*.25o"))

    with ProcessPoolExecutor(max_workers=12) as executor:
        _ds = None
        datasets = []

        futures = {
            executor.submit(read_rinex_file, fpath): fpath for fpath in rinex_files
        }

        for future in as_completed(futures):
            fpath = futures[future]
            try:
                ds = future.result()
                datasets.append(ds)

            except Exception as e:
                print(f"❌ Failed: {fpath.name} — {e}")

    final_ds = xr.concat(
        datasets,
        dim="epoch",
        join="outer",
        coords="different",
        compat="equals",
    )

    final_ds
    return (final_ds,)


@app.cell
def _():
    return


@app.cell
def _(mo):
    mo.md(r"""
    Filtering is straightforward using Regex, e.g.:
    - All information transmitted by satellite E03: `E03|.*|.*`
    - All information transmitted on the L1C band: `.*|L1C|.*`
    - Only Q codes: `.*|.*|Q`
    - Only GLONASS: `R..|.*|.*`
    - ...
    """)


@app.cell
def _(final_ds):
    ds_e03 = final_ds.where(
        final_ds.sid.str.startswith("E03"),
        drop=True,
    )
    ds_e03.sid.values


@app.cell
def _(final_ds):
    ds_l1c = final_ds.where(
        final_ds.sid.str.contains("L2"),
        drop=True,
    )
    ds_l1c.sid.values


@app.cell
def _(final_ds):
    ds_q = final_ds.sel(sid=[x for x in final_ds.sid.values if x.endswith("Q")])
    ds_q.sid.values


@app.cell
def _(final_ds):
    ds_glonass = final_ds.sel(sid=[x for x in final_ds.sid.values if x.startswith("R")])
    ds_glonass.sid.values


@app.cell
def _(final_ds):
    ds_gps_l1_c = final_ds.where(
        final_ds.sid.str.startswith("G")
        & final_ds.sid.str.contains("|L1|")
        & final_ds.sid.str.endswith("C"),
        drop=True,
    )
    ds_gps_l1_c.sid.values
    return (ds_gps_l1_c,)


@app.cell
def _(ds_gps_l1_c):
    ds_gps_l1_c_aggr = ds_gps_l1_c.mean(dim="sid")

    ds_gps_l1_c_aggr.hvplot.line(
        x="epoch",
        y="SNR",
        title="Mean SNR of GPS L1C signals over time",
    )


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
