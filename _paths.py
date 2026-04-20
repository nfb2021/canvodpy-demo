"""Resolve test data directory for demo notebooks.

Works in three scenarios (checked in order):
  1. Monorepo (development): finds ../packages/canvod-readers/tests/test_data/valid/
  2. Standalone clone: finds ./test_data/valid/ (user cloned canvodpy-test-data)
  3. Pooch cache: downloads from Zenodo on first access, cached at
     ~/.cache/canvodpy/test_data/valid/  [NOT YET IMPLEMENTED — see TODO below]

TODO (post-Zenodo publish):
  After the test data DOI is assigned at https://zenodo.org/doi/<DOI>,
  add a third resolution path here using Pooch:

    import pooch

    _ZENODO_DOI = "<DOI>"           # e.g. "10.5281/zenodo.XXXXXXX"
    _CACHE_DIR = Path.home() / ".cache" / "canvodpy" / "test_data" / "valid"

    # Archive registry — sha256 hashes filled in after Zenodo upload
    _REGISTRY = {
        "rinex_v3_04.tar.gz":          "sha256:<hash>",
        "sbf.tar.gz":                  "sha256:<hash>",
        "nmea.tar.gz":                 "sha256:<hash>",
        "aux_data.tar.gz":             "sha256:<hash>",
        "rinex_v2_11.tar.gz":          "sha256:<hash>",
        "rinex_v3_05_stripped.tar.gz": "sha256:<hash>",
        "nav_data.tar.gz":             "sha256:<hash>",
        "stores.tar.gz":               "sha256:<hash>",
        "invalid.tar.gz":              "sha256:<hash>",
    }

    Each path constant below should trigger download of only the required
    archive (lazy per-archive fetch), not the full ~3 GB dataset. Example:

        ROSALIA_CANOPY_DIR = _fetch_and_extract("rinex_v3_04.tar.gz") / ...

    See https://www.fatiando.org/pooch for the Pooch API.
    Resolution order once implemented:
      1. Monorepo  → packages/canvod-readers/tests/test_data/valid/   (dev)
      2. Standalone clone → ./test_data/valid/                         (git clone)
      3. Pooch cache → ~/.cache/canvodpy/test_data/valid/              (auto-download)
"""

from pathlib import Path

_here = Path(__file__).resolve().parent

# Monorepo: demo/ is inside canvodpy/
_monorepo = (
    _here.parent / "packages" / "canvod-readers" / "tests" / "test_data" / "valid"
)

# Standalone: user cloned canvodpy-test-data into demo/test_data/
_standalone = _here / "test_data" / "valid"

if _monorepo.is_dir():
    TEST_DATA = _monorepo
elif _standalone.is_dir():
    TEST_DATA = _standalone
else:
    raise FileNotFoundError(
        "Test data not found. Either:\n"
        "  - Run from the canvodpy monorepo, or\n"
        "  - Clone test data: git clone https://github.com/nfb2021/canvodpy-test-data.git test_data\n"
        "  - (future) Install pooch and run with Zenodo auto-download once DOI is assigned."
    )

# ── Rosalia site paths ──────────────────────────────────────────────
ROSALIA = TEST_DATA / "rinex_v3_04" / "01_Rosalia"
ROSALIA_CANOPY_DIR = ROSALIA / "02_canopy" / "01_GNSS" / "01_raw"
ROSALIA_REFERENCE_DIR = ROSALIA / "01_reference" / "01_GNSS" / "01_raw"
AUX_DATA_DIR = TEST_DATA / "aux_data"
SP3_DIR = AUX_DATA_DIR / "01_SP3"
CLK_DIR = AUX_DATA_DIR / "02_CLK"

# ── SBF paths ─────────────────────────────────────────────────────
SBF_DIR = TEST_DATA / "sbf" / "01_Rosalia"
SBF_CANOPY_DIR = SBF_DIR / "02_canopy"
SBF_REFERENCE_DIR = SBF_DIR / "01_reference"

# ── Icechunk test stores ────────────────────────────────────────────
STORES_DIR = TEST_DATA / "stores"
