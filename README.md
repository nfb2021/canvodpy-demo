[![canVODpy](https://img.shields.io/badge/canVODpy-demo-2d6a4f)](https://github.com/nfb2021/canvodpy)
[![marimo](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# canvodpy-demo

Interactive [marimo](https://marimo.io) notebooks for the [canVODpy](https://github.com/nfb2021/canvodpy) GNSS-Transmissometry (GNSS-T) VOD retrieval ecosystem. The notebooks cover the full pipeline — from raw GNSS file reading to vegetation optical depth retrieval, versioned storage, and visualisation.

> **Pre-release note:** canvodpy is not yet published to PyPI. Until the first release, the standalone setup below requires cloning both repositories. Once canvodpy is on PyPI, only `uv sync` is needed. See `pyproject.toml` for the transition instructions.

---

## Run in the browser (no installation)

Open any notebook directly in [marimo molab](https://molab.marimo.io/github/nfb2021/canvodpy-demo) — no local installation required.

> molab does not have access to local files. Notebooks that read GNSS data from disk will prompt you to upload the files manually.

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

### 1. Clone both repositories side by side

```bash
git clone https://github.com/nfb2021/canvodpy.git
git clone https://github.com/nfb2021/canvodpy-demo.git
```

The directory layout should be:

```text
your-workspace/
├── canvodpy/          ← canvodpy monorepo
└── canvodpy-demo/     ← this repo
```

### 2. Enable the canvodpy dependency

Open `pyproject.toml` and uncomment the local path line:

```toml
"canvodpy @ ../canvodpy",
```

### 3. Install

```bash
cd canvodpy-demo
uv sync
```

### 4. Get the test data

The notebooks use real GNSS data from Rosalia, Austria (2025-01-01). Clone it into `test_data/`:

```bash
git clone https://github.com/nfb2021/canvodpy-test-data.git test_data
```

`_paths.py` detects the `test_data/` directory automatically.

### 5. Run a notebook

```bash
# Interactive editing
uv run marimo edit 07_vod_retrieval.py

# Read-only app
uv run marimo run 07_vod_retrieval.py
```

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

| # | Notebook | Topic |
|---|---|---|
| 01 | `01_naming_convention.py` | GNSS filename convention parsing and validation |
| 02 | `02_rinex_reading.py` | RINEX v3.04 file reading → `xarray.Dataset` |
| 03 | `03_satellite_catalog.py` | IGS SatelliteCatalog — PRN metadata and lookup |
| 04 | `04_sbf_reading.py` | SBF binary file reading |
| 05 | `05_ephemeris_coordinates.py` | SP3/CLK augmentation and ECEF → spherical transforms |
| 06 | `06_hemispheric_grids.py` | Equal-area, HEALPix, geodesic, Fibonacci grids |
| 07 | `07_vod_retrieval.py` | Tau-Omega VOD retrieval algorithm |
| 08 | `08_icechunk_store.py` | Versioned Icechunk/Zarr storage |
| 09 | `09_store_metadata.py` | DataCite/ACDD/STAC provenance metadata |
| 10 | `10_visualization.py` | 2D/3D hemispheric visualisation |
| 11 | `11_configuration.py` | Pydantic configuration models |
| 12 | `12_api_overview.py` | Four API levels overview |
| 13 | `13_api_level1_convenience.py` | L1: one-liner `process_date()` |
| 14 | `14_api_level2_fluent.py` | L2: `FluentWorkflow().read().augment().grid().vod()` |
| 15 | `15_api_level3_site_pipeline.py` | L3: `Site().pipeline().process_range()` |
| 16 | `16_api_level4_functional.py` | L4: pure functions for custom pipelines |
| 17 | `17_workflow_single_day.py` | End-to-end single-day processing |
| 18 | `18_workflow_batch_processing.py` | Batch processing with Dask |
| 19 | `19_workflow_store_operations.py` | Store read/write/branch operations |
| 20 | `20_grid_exploration.py` | Interactive hemispheric grid explorer |

---

## Test data

The notebooks use [canvodpy-test-data](https://github.com/nfb2021/canvodpy-test-data): real GNSS observations from Rosalia, Austria (DOY 2025-001), including RINEX v3.04, SBF binary files, precise SP3/CLK ephemerides, and a pre-built Icechunk store snapshot.

Path resolution is handled automatically by `_paths.py`:

| Scenario | Expected location |
|---|---|
| Standalone | `./test_data/` — clone canvodpy-test-data here |
| Monorepo | `../packages/canvod-readers/tests/test_data/` — resolved automatically |

---

## License

[Apache License 2.0](LICENSE)
