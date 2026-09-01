<!-- Python & Package Manager -->
[![Python](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![marimo](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)

<!-- Identity -->
[![canVODpy](https://img.shields.io/badge/canVODpy-submodule-2d6a4f)](https://github.com/nfb2021/canvodpy)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CLIMERS @ TU Wien](https://img.shields.io/badge/CLIMERS-TU_Wien-006699)](https://www.tuwien.at/en/mg/geo/climers)
[![VODnet](https://img.shields.io/badge/-VODnet-2d6a4f?labelColor=555555&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAAAXNSR0IArs4c6QAAAHhlWElmTU0AKgAAAAgABAEaAAUAAAABAAAAPgEbAAUAAAABAAAARgEoAAMAAAABAAIAAIdpAAQAAAABAAAATgAAAAAAAABIAAAAAQAAAEgAAAABAAOgAQADAAAAAQABAACgAgAEAAAAAQAAAA6gAwAEAAAAAQAAAA4AAAAAjn8NzQAAAAlwSFlzAAALEwAACxMBAJqcGAAAAflJREFUKBWtUEtoE1EUPe+9SczHiam/aixtqi1E7aai4kK0CAVBDFZwrQs3xp2KIriYtiKuav3QRVxYKIjFVihWrCBIaaWioKidQBsxi3SwYmMmkxidYWaemYEEKUgRPHDhXu4575x3gf+NKfVD3UQ2u/Zv7wrLF8mPfV2ZH1ZCNIM7xUCAHHjyfN6wQ8mZo3vvE4Av57tzOjfd/WZpivfJSW5wkzvomnzFe2SFTyyU+iFJtCpk1eaRfOIw84TuRsN7kEkVMDzyEjPvUtga2YiDTRFM5+m+F8XYHMZuzDqaWlQf8yVMpmJ0/DUu9g6hVNQAy8au3W04NHAV85oFRulZS+LDkIjtWmcyHT6vQHYoXwrouTWKkv4LLOAHE4N4K6dxZ2AISl4DpawVDVrYcXSFZtTPGSV8IatjUVErJ+Cwbdstx3Vw8CG+pmQIHg+HUVlWo7aSp/qz9Kn3W5p5S/x4DJ8/lfGt4kAow7bmBpQ9fuQ3RUFtM4Uz61Qk/vijbpLbgtc61n05zjQ1hCvXHmB9fT3OnT8NOWfi+uxP0IJxE4S4jrXzxrffm1xlb75Aud/cEFmD9vYW6KaNUoUmCpS3BblUPNk45sR0UBM6Qzx2qd9LVnfqujGS+64puaX8olEuj4uMHHnc2dTrcFZGtCOMxv11KxP/kfEbTTzNcyb5ar0AAAAASUVORK5CYII=&logoColor=white)](https://vodnet.netlify.app)

# canVODpy — Demo Notebooks

Interactive [marimo](https://marimo.io) notebooks for the [canVODpy](https://github.com/nfb2021/canvodpy) GNSS-Transmissometry (GNSS-T) VOD retrieval ecosystem. The notebooks cover the full pipeline — from raw GNSS file reading to vegetation optical depth retrieval, versioned storage, and visualisation.

---

## Run in the browser (no installation)

Open any notebook directly in [marimo molab](https://molab.marimo.io/github/nfb2021/canvodpy-demo) — no local installation required.

Notebooks that read real GNSS data automatically download the test dataset (~1.7 GB) from Zenodo on first run and cache it — no manual file upload required.

---

## Run locally — standalone

### Prerequisites

Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 1. Clone

```bash
git clone https://github.com/nfb2021/canvodpy-demo.git
cd canvodpy-demo
```

### 2. Run a notebook

Each notebook declares its own dependencies via a PEP 723 header. `uv` installs them automatically on first run — no `uv sync` or manual dependency management required.

```bash
# Interactive editing
uvx marimo edit --sandbox 07_vod_retrieval.py

# Read-only app
uvx marimo run --sandbox 07_vod_retrieval.py
```

`uvx` and `--sandbox` together mean this never touches (or requires) any
project-level virtual environment -- the notebook's own PEP 723 header
declares everything it needs, installed into a throwaway venv.

### 3. Test data

Notebooks that read GNSS data download the test dataset (~1.7 GB) automatically from Zenodo on first run and cache it at `~/.cache/canvodpy/`. Subsequent runs are instant.

To skip the download and use a local copy instead, clone the test data into `test_data/`:

```bash
git clone https://github.com/nfb2021/canvodpy-test-data.git test_data
```

`_paths.py` detects this directory automatically and skips the Zenodo download.

---

## Run locally — inside the canvodpy monorepo

If you are working inside the canvodpy monorepo, the notebooks are available as the `demo/` submodule and share the monorepo's virtual environment and test data automatically.

```bash
git clone --recurse-submodules https://github.com/nfb2021/canvodpy.git
cd canvodpy
uv sync

# Interactive editing
uv run marimo edit demo/07_vod_retrieval.py

# Read-only app
uv run marimo run demo/07_vod_retrieval.py
```

---

## Notebooks

| # | Notebook | Topic | Open |
|---|---|---|---|
| 00 | `00_convenience_speedrun.py` | Full pipeline in five cells | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/00_convenience_speedrun.py?mode=edit) |
| 01 | `01_naming_convention.py` | GNSS filename convention parsing and validation | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/01_naming_convention.py?mode=edit) |
| 02 | `02_rinex_reading.py` | RINEX v3.04 file reading → `xarray.Dataset` | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/02_rinex_reading.py?mode=edit) |
| 03 | `03_satellite_catalog.py` | IGS SatelliteCatalog — PRN metadata and lookup | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/03_satellite_catalog.py?mode=edit) |
| 04 | `04_sbf_reading.py` | SBF binary file reading | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/04_sbf_reading.py?mode=edit) |
| 05 | `05_ephemeris_coordinates.py` | SP3/CLK augmentation and ECEF → spherical transforms | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/05_ephemeris_coordinates.py?mode=edit) |
| 06 | `06_hemispheric_grids.py` | Equal-area, equal-angle, geodesic, Fibonacci grids | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/06_hemispheric_grids.py?mode=edit) |
| 07 | `07_vod_retrieval.py` | Tau-Omega VOD retrieval algorithm | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/07_vod_retrieval.py?mode=edit) |
| 08 | `08_icechunk_store.py` | Versioned Icechunk/Zarr storage | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/08_icechunk_store.py?mode=edit) |
| 09 | `09_store_metadata.py` | DataCite/ACDD/STAC provenance metadata | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/09_store_metadata.py?mode=edit) |
| 10 | `10_visualization.py` | 2D/3D hemispheric visualisation | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/10_visualization.py?mode=edit) |
| 11 | `11_configuration.py` | Pydantic configuration models | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/11_configuration.py?mode=edit) |
| 12 | `12_api_overview.py` | API overview: CLI, Site pipeline, functional | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/12_api_overview.py?mode=edit) |
| 13 | `13_cli_pipeline.py` | `canvodpy run` — the production CLI | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/13_cli_pipeline.py?mode=edit) |
| 14 | `14_site_pipeline.py` | `Site().pipeline().process_range()` | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/14_site_pipeline.py?mode=edit) |
| 15 | `15_functional_api.py` | Pure functions for custom pipelines | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/15_functional_api.py?mode=edit) |
| 16 | `16_workflow_single_day.py` | End-to-end single-day processing | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/16_workflow_single_day.py?mode=edit) |
| 17 | `17_workflow_batch_processing.py` | Batch processing with Dask | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/17_workflow_batch_processing.py?mode=edit) |
| 18 | `18_workflow_store_operations.py` | Store read/write/branch operations | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/18_workflow_store_operations.py?mode=edit) |
| 19 | `19_grid_exploration.py` | Interactive hemispheric grid explorer | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/19_grid_exploration.py?mode=edit) |
| 20 | `20_grid_3d_gallery.py` | 3D gallery comparing all hemispheric grid types | [![molab](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/20_grid_3d_gallery.py?mode=edit) |

---

## Test data

The notebooks use [canvodpy-test-data](https://github.com/nfb2021/canvodpy-test-data): real GNSS observations from Rosalia, Austria (DOY 2025-001), including RINEX v3.04, SBF binary files, precise SP3/CLK ephemerides, and a pre-built Icechunk store snapshot.

Path resolution is handled automatically by `_paths.py`:

| Scenario | Expected location |
|---|---|
| molab / cloud | Zenodo auto-download (~1.7 GB, cached after first run) |
| Standalone | `./test_data/` — clone canvodpy-test-data here |
| Monorepo | `../packages/canvod-readers/tests/test_data/` — resolved automatically |

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](https://github.com/nfb2021/canvodpy/blob/main/CONTRIBUTING.md) in the canvodpy repository for guidelines.

---

## License

[Apache License 2.0](LICENSE)

---

## Affiliation

Founded by **Nicolas François Bader**

[Climate and Environmental Remote Sensing Research Unit (CLIMERS)](https://www.tuwien.at/en/mg/geo/climers)
Department of Geodesy and Geoinformation, TU Wien

Email: support@canvodpy.eu
