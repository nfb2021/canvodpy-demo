# canvodpy Demo Notebooks

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

Interactive [marimo](https://marimo.io/) notebooks demonstrating the
[canVODpy](https://github.com/nfb2021/canvodpy) framework.
All notebooks use the **Rosalia, Austria** test site (DOY 2025-001).

> **Note:** This repository is a Git submodule of the canVODpy monorepo (`demo/`).
> It requires the monorepo's virtual environment for all `canvod.*` imports.

## Notebooks

| Notebook | Description |
|---|---|
| `hackathon_demo.py` | End-to-end pipeline: Site → process → store → VOD → hemisphere visualisation |
| `canvodpy_complete_demo.py` | Complete canVODpy walkthrough covering all packages |
| `gnss_vod_complete_demo.py` | Full GNSS-VOD analysis from raw data to results |
| `pipeline_demo.py` | Production pipeline walkthrough with timing and store inspection |
| `timing_diagnostics.py` | Processing performance profiling and throughput benchmarking |
| `read_icechunk_store.py` | Reading and exploring the Icechunk store |
| `store_metadata_and_sinex.py` | Store metadata inspection and IGS SINEX satellite catalog |
| `live_statistics_dashboard.py` | Real-time processing statistics dashboard |
| `01_reader.py` | RINEX reader deep-dive: parsing, signal IDs, dataset structure |
| `01_factory_basics.py` | Factory API basics |
| `02_workflow_usage.py` | Workflow API usage patterns |
| `03_augment_data.py` | Hermite interpolation and spherical coordinate augmentation |
| `03_functional_api.py` | Level 4 functional API examples |
| `04_custom_components.py` | Building custom marimo components |
| `grids_overview.py` | Hemispheric grid types, cell assignment, visualisation |
| `level1_convenience.py` | Level 1 convenience API |
| `level2_fluent.py` | Level 2 fluent workflow API |
| `level3_workflow.py` | Level 3 site + pipeline API |
| `level4_functional.py` | Level 4 functional API for Airflow |

## Running

From the **monorepo root**:

```bash
# Interactive editing (browser)
just open-notebook hackathon_demo

# Read-only app mode (browser)
just app-notebook hackathon_demo

# Or directly
uv run marimo edit demo/hackathon_demo.py
uv run marimo run demo/hackathon_demo.py
```

## Configuration

Notebooks are driven by the monorepo config files:

- `config/sites.yaml` — site and receiver definitions
- `config/processing.yaml` — store paths, aux data directory, processing parameters

Stores and aux caches are written to `/tmp/canvodpy_demo/` by default.

## Requirements

```bash
# From monorepo root
uv sync
```

Auxiliary data (SP3/CLK) for the test date is included in the
`canvod-readers` test data submodule and pre-configured in `processing.yaml`.

## License

Licensed under the Apache License 2.0 — see [LICENSE](LICENSE).
