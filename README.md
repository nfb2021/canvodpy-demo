# canvodpy Demo Notebooks

Interactive marimo notebooks demonstrating the canvodpy framework.
All notebooks use the **Rosalia, Austria** test site (DOY 2025-001).

## Notebooks

| Notebook | Description |
|---|---|
| `hackathon_demo.py` | End-to-end pipeline: Site → process → store → VOD → hemisphere visualisation |
| `pipeline_demo.py` | Production pipeline walkthrough with timing and store inspection |
| `timing_diagnostics.py` | Processing performance profiling and throughput benchmarking |
| `read_icechunk_store.py` | Reading and exploring the Icechunk store |
| `01_reader.py` | RINEX reader deep-dive: parsing, signal IDs, dataset structure |
| `01_factory_basics.py` | Factory API basics |
| `03_augment_data.py` | Hermite interpolation and spherical coordinate augmentation |
| `grids_overview.py` | Hemispheric grid types, cell assignment, visualisation |

## Running

```bash
# Interactive (browser)
uv run marimo edit hackathon_demo.py

# Headless script mode
uv run hackathon_demo.py
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
