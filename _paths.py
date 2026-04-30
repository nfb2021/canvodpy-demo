"""Resolve test data directory for demo notebooks.

Resolution order (checked in order):
  1. Monorepo    — ../packages/canvod-readers/tests/test_data/valid/  (dev)
  2. Pooch cache — ~/.cache/canvodpy/canvodpy-test-data-v0.1.0/       (default)
  3. Standalone  — ./test_data/valid/                                  (manual clone)
  4. Download    — Zenodo DOI 10.5281/zenodo.19708759 via ensure_data()

Paths 1–3 resolve immediately at import. Path 4 is deferred: TEST_DATA is
set to None and resolved lazily via ensure_data() so notebooks can inject
a marimo-aware progress bar before the download starts.

The Pooch/Zenodo path is the default for all non-developer users: the first
call to ensure_data() downloads canvodpy-test-data v0.1.0 (1.69 GB zip)
and caches it locally. Subsequent imports are instant (cache hit, path 2).

Usage
-----
In a notebook setup cell::

    import _paths
    _paths.ensure_data()          # terminal progress bar (tqdm)

Or with a marimo progress bar::

    from _download import marimo_downloader
    _paths.ensure_data(downloader=marimo_downloader)
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


def _zenodo_valid_dir(downloader=None) -> Path:
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
        downloader=downloader or pooch.HTTPDownloader(progressbar=True),
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
# Paths 1–3 resolve immediately at import. Path 4 is deferred: TEST_DATA
# is set to None and resolved lazily via ensure_data() so notebooks can
# inject a marimo-aware progress bar before the download starts.

def _pooch_cache_dir() -> Path | None:
    """Return the pooch cache valid/ path if data was already downloaded."""
    try:
        import pooch
        existing = list(
            (Path(pooch.os_cache("canvodpy")) / _ZENODO_VERSION).glob("*/valid")
        )
        return existing[0] if existing else None
    except ImportError:
        return None


if _monorepo.is_dir():
    TEST_DATA = _monorepo
elif (_cached := _pooch_cache_dir()) is not None:
    TEST_DATA = _cached
elif _standalone.is_dir():
    TEST_DATA = _standalone
else:
    TEST_DATA = None  # resolved by ensure_data() → Zenodo download


def ensure_data(downloader=None) -> Path:
    """Ensure test data is available and return the valid/ path.

    Call this in a notebook setup cell before using any path constants.
    If data is already present (monorepo or standalone clone), returns
    immediately. Otherwise triggers Zenodo download.

    Parameters
    ----------
    downloader:
        Optional Pooch-compatible downloader. Defaults to tqdm terminal
        progress bar. Pass ``_download.marimo_downloader`` for a marimo
        progress bar inside notebooks.
    """
    global TEST_DATA
    if TEST_DATA is not None:
        return TEST_DATA
    TEST_DATA = _zenodo_valid_dir(downloader=downloader)
    _refresh_path_constants()
    return TEST_DATA


def _refresh_path_constants() -> None:
    """Recompute all path constants after TEST_DATA is resolved."""
    import sys
    mod = sys.modules[__name__]

    rosalia = TEST_DATA / "rinex_v3_04" / "01_Rosalia"
    mod.ROSALIA = rosalia
    mod.ROSALIA_CANOPY_DIR = rosalia / "02_canopy" / "01_GNSS" / "01_raw"
    mod.ROSALIA_REFERENCE_DIR = rosalia / "01_reference" / "01_GNSS" / "01_raw"
    mod.AUX_DATA_DIR = TEST_DATA / "aux_data"
    mod.SP3_DIR = mod.AUX_DATA_DIR / "01_SP3"
    mod.CLK_DIR = mod.AUX_DATA_DIR / "02_CLK"
    sbf = TEST_DATA / "sbf" / "01_Rosalia"
    mod.SBF_DIR = sbf
    mod.SBF_CANOPY_DIR = sbf / "02_canopy"
    mod.SBF_REFERENCE_DIR = sbf / "01_reference"
    mod.STORES_DIR = TEST_DATA / "stores"


# Initialise path constants (None-safe: point to unresolved base if
# TEST_DATA is None, resolved values set by ensure_data() later)
if TEST_DATA is not None:
    _refresh_path_constants()
else:
    ROSALIA = None
    ROSALIA_CANOPY_DIR = None
    ROSALIA_REFERENCE_DIR = None
    AUX_DATA_DIR = None
    SP3_DIR = None
    CLK_DIR = None
    SBF_DIR = None
    SBF_CANOPY_DIR = None
    SBF_REFERENCE_DIR = None
    STORES_DIR = None
