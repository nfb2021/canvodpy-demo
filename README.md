[![canVODpy](https://img.shields.io/badge/canVODpy-submodule-2d6a4f)](https://github.com/nfb2021/canvodpy)
[![marimo](https://marimo.io/shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# canvodpy-demo

Interactive marimo notebooks for the [canVODpy](https://github.com/nfb2021/canvodpy) GNSS-T VOD retrieval ecosystem.
This repository is used as the `demo/` submodule in canvodpy.

## Notebooks

| Notebook | Topic |
|---|---|
| `01_naming_convention.py` | GNSS filename convention parsing and validation |
| `02_rinex_reading.py` | RINEX v3.04 file reading → `xarray.Dataset` |
| `03_satellite_catalog.py` | IGS SatelliteCatalog — PRN metadata and lookup |
| `04_sbf_reading.py` | SBF binary file reading |
| `05_ephemeris_coordinates.py` | SP3/CLK augmentation and ECEF → spherical transforms |
| `06_hemispheric_grids.py` | Equal-area, HEALPix, geodesic, Fibonacci grids |
| `07_vod_retrieval.py` | Tau-Omega VOD retrieval algorithm |
| `08_icechunk_store.py` | Versioned Icechunk/Zarr storage |
| `09_store_metadata.py` | DataCite/ACDD/STAC provenance metadata |
| `10_visualization.py` | 2D/3D hemispheric visualisation |
| `11_configuration.py` | Pydantic configuration models |
| `12_api_overview.py` | Four API levels overview |
| `13_api_level1_convenience.py` | L1: one-liner `process_date()` |
| `14_api_level2_fluent.py` | L2: `FluentWorkflow().read().augment().grid().vod()` |
| `15_api_level3_site_pipeline.py` | L3: `Site().pipeline().process_range()` |
| `16_api_level4_functional.py` | L4: pure functions for custom pipelines |
| `17_workflow_single_day.py` | End-to-end single-day processing |
| `18_workflow_batch_processing.py` | Batch processing with Dask |
| `19_workflow_store_operations.py` | Store read/write/branch operations |
| `20_grid_exploration.py` | Interactive hemispheric grid explorer |

## Usage

Notebooks run inside the parent [canvodpy](https://github.com/nfb2021/canvodpy) repo:

```bash
# Clone canvodpy with submodules
git clone --recurse-submodules https://github.com/nfb2021/canvodpy.git
cd canvodpy

# List available notebooks
just notebooks

# Edit a notebook interactively
just open-notebook 07_vod_retrieval.py

# Run as read-only app
just app-notebook 07_vod_retrieval.py
```

Or open in the browser via [marimo molab](https://molab.marimo.io/github/nfb2021/canvodpy) — no installation required.

## License

[Apache License 2.0](LICENSE)
