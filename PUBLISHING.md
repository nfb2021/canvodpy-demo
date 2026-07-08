# Publishing canvodpy-demo to molab

Working checklist for preparing all notebooks for molab, gallery, and thumbnails.

## Context

- **WASM / playground**: not viable — canvodpy depends on native C extensions
  (icechunk, xarray, numpy) that cannot compile to WebAssembly.
- **molab**: the right path. Runs on real cloud servers, installs from `pyproject.toml`,
  reads repo files, triggers Pooch/Zenodo download for test data.
- **Gallery**: rendered by `marimo run ./` (locally) and on molab. Driven by OpenGraph
  metadata in each notebook's PEP 723 header + thumbnail images.
- **Thumbnails**: generated via `marimo export thumbnail ./` using Playwright/Chromium.
  Stored at `__marimo__/assets/<stem>/opengraph.png`. Not committed to git.

---

## Step 1 — Add OpenGraph metadata to every notebook

Add a `[tool.marimo.opengraph]` section inside the PEP 723 `/// script` block of
each notebook. Fields: `title`, `description`.

Format:
```toml
# /// script
# requires-python = ">=3.14"
# dependencies = [...]
#
# [tool.marimo.opengraph]
# title = "..."
# description = "..."
# ///
```

### Notebook list

- [x] `00_convenience_speedrun.py` — Speedrun — Full Pipeline
- [x] `01_naming_convention.py` — Naming Convention & Validation
- [x] `02_rinex_reading.py` — RINEX v3 Observation Reading
- [x] `03_satellite_catalog.py` — Satellite Catalog
- [x] `04_sbf_reading.py` — SBF Binary Reading
- [x] `05_ephemeris_coordinates.py` — Ephemeris & Coordinate Augmentation
- [x] `06_hemispheric_grids.py` — Hemispheric Grids
- [x] `07_vod_retrieval.py` — VOD Retrieval
- [x] `08_icechunk_store.py` — Icechunk Store
- [x] `09_store_metadata.py` — Store Metadata & FAIR Compliance
- [x] `10_visualization.py` — Visualization
- [x] `11_configuration.py` — Configuration & Utilities
- [x] `12_api_overview.py` — API Overview
- [x] `13_cli_pipeline.py` — Running the Pipeline (CLI)
- [x] `14_site_pipeline.py` — Site Pipeline
- [x] `15_functional_api.py` — Functional API
- [x] `16_workflow_single_day.py` — Single-Day Workflow
- [x] `17_workflow_batch_processing.py` — Batch Processing Workflows
- [x] `18_workflow_store_operations.py` — Store Operations
- [x] `19_grid_exploration.py` — Grid Exploration

---

## Step 2 — Add `ensure_data()` setup cell to data-reading notebooks

Notebooks that load GNSS data must call `_paths.ensure_data()` before using any
path constants. Use the marimo downloader for a progress bar in the browser.

```python
@app.cell
def _():
    import _paths
    from _download import marimo_downloader
    _paths.ensure_data(downloader=marimo_downloader)
```

Notebooks that need this (read files from `TEST_DATA`):
- [x] `00_convenience_speedrun.py`
- [x] `02_rinex_reading.py`
- [x] `04_sbf_reading.py`
- [x] `05_ephemeris_coordinates.py`
- [x] `07_vod_retrieval.py`
- [x] `08_icechunk_store.py`
- [ ] `13_cli_pipeline.py` — shell/documentation only, no real data
- [ ] `14_site_pipeline.py` — uses `"my_site"` placeholder, no real data
- [ ] `15_functional_api.py` — uses `"my_site"` placeholder, no real data
- [x] `16_workflow_single_day.py`
- [ ] `17_workflow_batch_processing.py` — uses `"my_site"` placeholder, no real data
- [x] `18_workflow_store_operations.py`

---

## Step 3 — Ensure `__marimo__/` is NOT in `.gitignore` ✓

Thumbnails must be committed so molab can read them from the repo for
gallery display. Removed `__marimo__/` from `.gitignore`.

---

## Step 4 — Generate thumbnails

Requires Playwright + Chromium. Run once locally after notebooks are stable:

```bash
uv run playwright install chromium
uv run marimo export thumbnail ./
```

Thumbnails land at `__marimo__/assets/<stem>/opengraph.png` (1200×630 px).
Regenerate whenever a notebook's output changes significantly.

Options:
- `--execute` — run notebook before screenshotting (slower but live output)
- `--scale 3` — higher resolution
- `--overwrite` — replace existing thumbnails

---

## Step 5 — Add open-in-molab badge to README ✓

Badge already present in README header. Per-notebook molab links added to
the notebooks table (Open column with individual `blob/main/<notebook>` links).
Also updated the "Run in the browser" section to mention Zenodo auto-download.

---

## Step 6 — Submit to molab public gallery (optional)

Visit https://molab.marimo.io/gallery and submit the repo.
Requires OpenGraph metadata (Step 1) and thumbnails (Step 4) to look good.

---

## Notes

- `css_file="canvod_nordic.css"` is already set on all notebooks — the Nordic
  Green theme will render on molab as long as the CSS file is in the repo root.
- molab reads `pyproject.toml` for dependencies — `pooch` and `tqdm` are already
  declared, so the Zenodo download will work out of the box.
- The `_paths.py` and `_download.py` helper files must be in the same directory
  as the notebooks (repo root of canvodpy-demo).
