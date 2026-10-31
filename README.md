<!-- Python & Package Manager -->
[![Python](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![marimo](https://marimo.io/shield.svg)](https://canvodpy.eu/notebooks/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)

<!-- Identity -->
[![canVODpy](https://img.shields.io/badge/canVODpy-submodule-2d6a4f)](https://github.com/TUW-GEO/canvodpy)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CLIMERS @ TU Wien](https://img.shields.io/badge/CLIMERS-TU_Wien-006699)](https://www.tuwien.at/en/mg/geo/climers)
[![VODnet](https://img.shields.io/badge/-VODnet-2d6a4f?labelColor=555555&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAAAXNSR0IArs4c6QAAAHhlWElmTU0AKgAAAAgABAEaAAUAAAABAAAAPgEbAAUAAAABAAAARgEoAAMAAAABAAIAAIdpAAQAAAABAAAATgAAAAAAAABIAAAAAQAAAEgAAAABAAOgAQADAAAAAQABAACgAgAEAAAAAQAAAA6gAwAEAAAAAQAAAA4AAAAAjn8NzQAAAAlwSFlzAAALEwAACxMBAJqcGAAAAflJREFUKBWtUEtoE1EUPe+9SczHiam/aixtqi1E7aai4kK0CAVBDFZwrQs3xp2KIriYtiKuav3QRVxYKIjFVihWrCBIaaWioKidQBsxi3SwYmMmkxidYWaemYEEKUgRPHDhXu4575x3gf+NKfVD3UQ2u/Zv7wrLF8mPfV2ZH1ZCNIM7xUCAHHjyfN6wQ8mZo3vvE4Av57tzOjfd/WZpivfJSW5wkzvomnzFe2SFTyyU+iFJtCpk1eaRfOIw84TuRsN7kEkVMDzyEjPvUtga2YiDTRFM5+m+F8XYHMZuzDqaWlQf8yVMpmJ0/DUu9g6hVNQAy8au3W04NHAV85oFRulZS+LDkIjtWmcyHT6vQHYoXwrouTWKkv4LLOAHE4N4K6dxZ2AISl4DpawVDVrYcXSFZtTPGSV8IatjUVErJ+Cwbdstx3Vw8CG+pmQIHg+HUVlWo7aSp/qz9Kn3W5p5S/x4DJ8/lfGt4kAow7bmBpQ9fuQ3RUFtM4Uz61Qk/vijbpLbgtc61n05zjQ1hCvXHmB9fT3OnT8NOWfi+uxP0IJxE4S4jrXzxrffm1xlb75Aud/cEFmD9vYW6KaNUoUmCpS3BblUPNk45sR0UBM6Qzx2qd9LVnfqujGS+64puaX8olEuj4uMHHnc2dTrcFZGtCOMxv11KxP/kfEbTTzNcyb5ar0AAAAASUVORK5CYII=&logoColor=white)](https://www.gfz.de/en/section/remote-sensing-and-geoinformatics/projects/vodnet)

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/TUW-GEO/canvodpy/main/docs/assets/logo/canvodpy_logo_dark_mode.svg">
    <img alt="canVODpy logo" src="https://raw.githubusercontent.com/TUW-GEO/canvodpy/main/docs/assets/logo/canvodpy_logo_bright_mode.svg" width="312">
  </picture>
</p>

# canVODpy Demo Notebooks

[marimo](https://marimo.io) notebooks for
[canVODpy](https://github.com/TUW-GEO/canvodpy), the software for canopy
Vegetation Optical Depth (VOD) from GNSS transmissometry. They go through
the whole pipeline on real data: reading receiver files, adding satellite
positions, hemispheric grids, VOD, versioned storage and plots.

## In your browser

Each notebook in the [table below](#notebooks) opens in
[molab](https://molab.marimo.io/), with no installation. The copies on
[canvodpy.eu/notebooks](https://canvodpy.eu/notebooks/) also show their
results, run on the test data when the site was built.

## On your machine

Install [uv](https://docs.astral.sh/uv/getting-started/installation/),
clone this repository and run a notebook:

```bash
git clone https://github.com/TUW-GEO/canvodpy-demo.git
cd canvodpy-demo
uvx marimo edit --sandbox 10_vod_retrieval.py   # edit and run
uvx marimo run --sandbox 10_vod_retrieval.py    # read-only app
```

Each notebook lists its own dependencies in a PEP 723 header; with
`--sandbox`, uv installs them into a temporary environment of the notebook,
so no project environment is needed.

### As a single file

You don't need the repository: give marimo the raw URL of one notebook, and
`--sandbox` builds a temporary environment from its PEP 723 header:

```bash
uvx marimo edit --sandbox https://raw.githubusercontent.com/TUW-GEO/canvodpy-demo/main/10_vod_retrieval.py
```

Every notebook declares its `canvod*` dependencies and fetches its data
with `canvodpy.demo_data()`. Outside a clone the page has no canVODpy
theme (`canvod_nordic.css` and `canvod_head.html` are files of the
repository); everything else works.

marimo notebooks also run in the
[VS Code marimo extension](https://marketplace.visualstudio.com/items?itemName=marimo-team.vscode-marimo).

### Inside the canvodpy repository

The notebooks are the `demo/` submodule of canvodpy and use its
environment:

```bash
git clone --recurse-submodules https://github.com/TUW-GEO/canvodpy.git
cd canvodpy
uv sync
uv run marimo edit demo/10_vod_retrieval.py
```

## Notebooks

| # | Notebook | Topic | Open |
|---|---|---|---|
| 01 | `01_cli_pipeline.py` | `canvodpy run`: the production CLI | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/01_cli_pipeline.py) |
| 02 | `02_configuration.py` | Pydantic configuration models | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/02_configuration.py) |
| 03 | `03_convenience_speedrun.py` | Full pipeline in five cells | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/03_convenience_speedrun.py) |
| 04 | `04_naming_convention.py` | GNSS filename convention parsing and validation | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/04_naming_convention.py) |
| 05 | `05_rinex_reading.py` | RINEX v3.04 file reading → `xarray.Dataset` | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/05_rinex_reading.py) |
| 06 | `06_sbf_reading.py` | SBF binary file reading | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/06_sbf_reading.py) |
| 07 | `07_satellite_catalog.py` | IGS SatelliteCatalog: PRN metadata and lookup | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/07_satellite_catalog.py) |
| 08 | `08_ephemeris_coordinates.py` | SP3/CLK augmentation and ECEF → spherical transforms | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/08_ephemeris_coordinates.py) |
| 09 | `09_hemispheric_grids.py` | Equal-area, equal-angle, geodesic, Fibonacci grids | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/09_hemispheric_grids.py) |
| 10 | `10_vod_retrieval.py` | Tau-Omega VOD retrieval algorithm | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/10_vod_retrieval.py) |
| 11 | `11_icechunk_store.py` | Versioned Icechunk/Zarr storage | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/11_icechunk_store.py) |
| 12 | `12_store_metadata.py` | DataCite/ACDD/STAC provenance metadata | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/12_store_metadata.py) |
| 13 | `13_workflow_store_operations.py` | Store read/write/branch operations | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/13_workflow_store_operations.py) |
| 14 | `14_visualization.py` | 2D/3D hemispheric visualization | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/14_visualization.py) |
| 15 | `15_grid_exploration.py` | Interactive hemispheric grid explorer | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/15_grid_exploration.py) |
| 16 | `16_grid_3d_gallery.py` | 3D gallery comparing all hemispheric grid types | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/16_grid_3d_gallery.py) |
| 17 | `17_api_overview.py` | API overview: CLI and Site pipeline | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/17_api_overview.py) |
| 18 | `18_site_pipeline.py` | `Site().pipeline().process_range()` | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/18_site_pipeline.py) |
| 19 | `19_workflow_single_day.py` | End-to-end single-day processing | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/19_workflow_single_day.py) |
| 20 | `20_workflow_batch_processing.py` | Batch processing with Dask | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/20_workflow_batch_processing.py) |
| 21 | `21_plugins.py` | Your own VOD calculator: register it, compare it, make it a plugin | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/21_plugins.py) |
| 22 | `22_s3_stores.py` | Stores on S3: credentials, two runs on one store, settings from a store (needs an S3 endpoint, RustFS works) | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/22_s3_stores.py) |
| 23 | `23_run_dashboard.py` | The run dashboard on an example run history: progress, stage times, resources, problems, comparison by label | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/23_run_dashboard.py) |

## Release notebooks

Every minor and major release of canVODpy has a notebook in `releases/`
that shows what is new and how to use it, next to the
[changelog](https://github.com/TUW-GEO/canvodpy/blob/main/CHANGELOG.md).
Each pins the release it describes. CI checks their format but doesn't run
them: some cells only show code that needs your own data.

| Release | Open |
|---|---|
| [v1.1.0](releases/v1.1.0.py): broadcast ephemeris from RINEX navigation files | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-demo/blob/main/releases/v1.1.0.py) |

To write one, copy `releases/_template.py` to `releases/vX.Y.Z.py` before
the release; [Release process](https://canvodpy.eu/RELEASING/) in the
canvodpy docs says when.

## Test data

Notebooks that read real GNSS data get it from `canvodpy.demo_data()`,
which downloads it on first use into your platform's cache folder: Linux
`~/.cache/canvodpy/demo/2`, macOS `~/Library/Caches/canvodpy/demo/2`,
Windows `%LOCALAPPDATA%\canvodpy\canvodpy\Cache\demo\2`. The reference
stores of `demo_data("stores")` go next to it, into
`demo/stores/<revision>`. Later runs
reuse the cached copy; no manual download and no cloned test-data
repository are needed.

The download is about 350 MB and holds the Rosalia, Austria site on DOY
2025-001 (part of
[canvodpy-test-data](https://github.com/TUW-GEO/canvodpy-test-data),
[doi:10.5281/zenodo.19708759](https://doi.org/10.5281/zenodo.19708759)):

- **RINEX v3.04** observations: a full day for the reference and the
  canopy receiver (about 350 MB once unpacked).
- **SBF** observations: the first two hours of the day (about 190 MB once
  unpacked).
- **Auxiliary data**: CODE final SP3 orbit and CLK clock files for the day
  and its neighboring days, plus the pre-computed auxiliary Zarr store
  (about 350 MB once unpacked).

A notebook session writes its settings, stores, logs and auxiliary data
into a fresh temporary folder, so the cache holds only the downloaded test
data and is never written to.

Notebook 23 reads an anonymized run history with
`canvodpy.demo_data("run_history")`: under 1 MB, downloaded once into the
user cache folder.

## Contributing

See [CONTRIBUTING.md](https://github.com/TUW-GEO/canvodpy/blob/main/CONTRIBUTING.md)
in the canvodpy repository.

CI runs every notebook on each pull request and once a week. To run the same
checks locally:

```bash
uv run --locked marimo check --strict [0-9][0-9]_*.py releases/*.py   # format; --fix fixes most warnings
scripts/run_notebooks.sh                                # all notebooks
scripts/run_notebooks.sh 05 13                          # only these
```

Notebook 22 needs an S3 endpoint and credentials in the environment; the
notebook shows how to start a local S3 emulator for it. Every notebook must
pin the same canVODpy release from PyPI (`"canvodpy==1.0.0"`).

## Citation

The notebooks have no DOI of their own. If you use canVODpy, please cite it:
[doi:10.5281/zenodo.18496233](https://doi.org/10.5281/zenodo.18496233).
If you use the test data, please cite it as well:
[doi:10.5281/zenodo.19708759](https://doi.org/10.5281/zenodo.19708759).
[CITATION.cff](CITATION.cff) holds both; GitHub shows it under
"Cite this repository".

## License

[Apache License 2.0](LICENSE)

## Affiliation

[Climate and Environmental Remote Sensing Research Unit (CLIMERS)](https://www.tuwien.at/en/mg/geo/climers)
Department of Geodesy and Geoinformation, TU Wien

Email: support@canvodpy.eu
