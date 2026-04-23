"""Resolve test data directory for demo notebooks.

Resolution order:
  1. Monorepo  — ../packages/canvod-readers/tests/test_data/valid/   (dev)
  2. Standalone — ./test_data/valid/                                  (git clone)
  3. Pooch cache — ~/.cache/canvodpy/canvodpy-test-data-v0.1.0/      (auto-download)

The Pooch path downloads canvodpy-test-data v0.1.0 from Zenodo on first use
(1.69 GB zip, DOI: 10.5281/zenodo.19708759) and caches it locally.
Subsequent imports are instant.
"""

from pathlib import Path

_here = Path(__file__).resolve().parent

# ── 1. Monorepo ─────────────────────────────────────────────────────
_monorepo = (
    _here.parent / "packages" / "canvod-readers" / "tests" / "test_data" / "valid"
)

# ── 2. Standalone clone ─────────────────────────────────────────────
_standalone = _here / "test_data" / "valid"


# ── 3. Pooch / Zenodo ───────────────────────────────────────────────
_ZENODO_URL = (
    "https://zenodo.org/records/19708760"
    "/files/nfb2021/canvodpy-test-data-v0.1.0.zip?download=1"
)
_ZENODO_HASH = "md5:08be83eb1fb3961f23ce1d4b66296cb9"
_ZENODO_VERSION = "canvodpy-test-data-v0.1.0"


def _zenodo_valid_dir() -> Path:
    """Download test data from Zenodo and return path to valid/."""
    try:
        import pooch
    except ImportError as exc:
        raise ImportError(
            "Install pooch to enable automatic data download:\n"
            "  pip install pooch\n"
            "Or clone the test data manually:\n"
            "  git clone https://github.com/nfb2021/canvodpy-test-data.git test_data"
        ) from exc

    cache_root = Path(pooch.os_cache("canvodpy"))
    extract_dir = cache_root / _ZENODO_VERSION

    # Return immediately if already extracted
    existing = list(extract_dir.glob("*/valid"))
    if existing:
        return existing[0]

    pooch.retrieve(
        url=_ZENODO_URL,
        known_hash=_ZENODO_HASH,
        fname=f"{_ZENODO_VERSION}.zip",
        path=cache_root,
        downloader=pooch.HTTPDownloader(progressbar=True),
        processor=pooch.Unzip(extract_dir=str(extract_dir)),
    )

    found = list(extract_dir.glob("*/valid"))
    if not found:
        raise FileNotFoundError(
            f"Could not find valid/ in extracted archive at {extract_dir}. "
            "The archive structure may have changed — please file an issue."
        )
    return found[0]


# ── Resolve TEST_DATA ────────────────────────────────────────────────
if _monorepo.is_dir():
    TEST_DATA = _monorepo
elif _standalone.is_dir():
    TEST_DATA = _standalone
else:
    TEST_DATA = _zenodo_valid_dir()

# ── Rosalia site paths ──────────────────────────────────────────────
ROSALIA = TEST_DATA / "rinex_v3_04" / "01_Rosalia"
ROSALIA_CANOPY_DIR = ROSALIA / "02_canopy" / "01_GNSS" / "01_raw"
ROSALIA_REFERENCE_DIR = ROSALIA / "01_reference" / "01_GNSS" / "01_raw"
AUX_DATA_DIR = TEST_DATA / "aux_data"
SP3_DIR = AUX_DATA_DIR / "01_SP3"
CLK_DIR = AUX_DATA_DIR / "02_CLK"

# ── SBF paths ───────────────────────────────────────────────────────
SBF_DIR = TEST_DATA / "sbf" / "01_Rosalia"
SBF_CANOPY_DIR = SBF_DIR / "02_canopy"
SBF_REFERENCE_DIR = SBF_DIR / "01_reference"

# ── Icechunk test stores ─────────────────────────────────────────────
STORES_DIR = TEST_DATA / "stores"
