"""Resolve test data directory for demo notebooks.

Works in two scenarios:
  1. Monorepo (development): finds ../packages/canvod-readers/tests/test_data/valid/
  2. Standalone: finds ./test_data/valid/ (user clones canvodpy-test-data)
"""

from pathlib import Path

_here = Path(__file__).resolve().parent

# Monorepo: demo/ is inside canvodpy/
_monorepo = _here.parent / "packages" / "canvod-readers" / "tests" / "test_data" / "valid"

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
        "  - Clone test data: git clone https://github.com/nfb2021/canvodpy-test-data.git test_data"
    )

# ── Rosalia site paths ──────────────────────────────────────────────
ROSALIA = TEST_DATA / "rinex_v3_04" / "01_Rosalia"
ROSALIA_CANOPY_DIR = ROSALIA / "02_canopy" / "01_GNSS" / "01_raw"
ROSALIA_REFERENCE_DIR = ROSALIA / "01_reference" / "01_GNSS" / "01_raw"
AUX_DATA_DIR = TEST_DATA / "aux_data"
SP3_DIR = ROSALIA / "01_SP3"
CLK_DIR = ROSALIA / "02_CLK"

# ── Icechunk test stores ────────────────────────────────────────────
STORES_DIR = TEST_DATA / "stores"
