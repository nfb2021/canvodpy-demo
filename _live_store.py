"""Build live Icechunk stores from real Rosalia RINEX v3.04 raw data.

demo/08_icechunk_store.py and demo/18_workflow_store_operations.py both
need a populated MyIcechunkStore to render their read-only demo cells
(branches, groups, commit history, metadata ledger, root attrs). No
pre-built store fixture is published: canvodpy-test-data commit 7da92ea
accidentally gitignored the store fixture's chunk/manifest/snapshot data,
so both the tracked repo and its Zenodo archive contain only an empty
first-commit snapshot (unrecoverable).

This module runs the real `canvodpy` CLI once, at notebook-run time,
against the real raw RINEX under `_paths.ROSALIA` -- never against
`_paths.STORES_DIR`, which is read-only test data -- writing into a fresh
scratch Icechunk repository. Uses the CLI (not the Python Site/Pipeline API
directly) per this project's own documented "Running-the-pipeline rule",
via `sys.executable -m canvodpy.cli.app run --config <overlay>` so it runs
in the same interpreter/venv this notebook's own PEP 723 deps already
resolved -- no dependency on `canvodpy`'s console-script entry point being
on PATH.

`--no-vod` defaults to False and the recipe defines `vod_analyses`, so a
single CLI run produces *both* a GNSS observation store and a VOD store
(sibling directories under the same scratch `stores_root_dir`) -- no
separate VOD computation step needed. `_run_pipeline()` runs the CLI once
and is shared/cached by both accessors below, so calling both
`build_rosalia_store()` and `build_rosalia_vod_store()` in the same kernel
session only invokes the pipeline once.

Usage in a notebook cell::

    from _live_store import (
        build_rosalia_store, build_rosalia_vod_store,
        get_pipeline_command, get_pipeline_output,
    )
    store, store_path = build_rosalia_store()
    vod_store, vod_store_path = build_rosalia_vod_store()
    mo.md(f"```bash\\n{get_pipeline_command()}\\n```")
    mo.md(f"```text\\n{get_pipeline_output()}\\n```")
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

import _paths

if TYPE_CHECKING:
    from canvod.store import MyIcechunkStore

_RECIPE_PATH = Path(__file__).resolve().parent / "_rosalia_v3_04_recipe.yaml"
_SITE_NAME = "rosalia_v3_04"
_DATE = "2025001"  # the only DOY the test-data fixture ships

_cached: tuple["MyIcechunkStore", Path, "MyIcechunkStore", Path] | None = None
_last_cmd: list[str] | None = None
_last_stdout: str | None = None
_last_stderr: str | None = None


def _seed_aux_cache(scratch_aux_dir: Path) -> None:
    """Copy real SP3/CLK products into a writable scratch dir.

    The pipeline reads raw products from `aux_data_dir/01_SP3` and
    `.../02_CLK` but also *writes* its Hermite-interpolated cache back into
    the same `aux_data_dir` tree (`00_aux_zarr/`) -- confirmed via direct
    read of canvodpy/orchestrator/processor.py's
    `_ensure_aux_data_preprocessed`. So `aux_data_dir` can never be
    `_paths.AUX_DATA_DIR` directly (that's the read-only submodule); copy
    the real products into a scratch dir instead. A local-file hit means
    `download_aux_file()` is never called (it only fetches
    `if not file_path.exists()`), so this seed step means zero network
    calls.
    """
    shutil.copytree(_paths.SP3_DIR, scratch_aux_dir / "01_SP3")
    shutil.copytree(_paths.CLK_DIR, scratch_aux_dir / "02_CLK")


def _build_overlay(scratch_dir: Path) -> Path:
    """Merge the tracked recipe with this run's environment-specific paths.

    The tracked recipe (_rosalia_v3_04_recipe.yaml) deliberately omits
    `gnss_site_data_root` and the storage paths -- those are real absolute
    paths that vary by machine/CI runner, injected here instead.
    """
    recipe = yaml.safe_load(_RECIPE_PATH.read_text())
    recipe["sites"][_SITE_NAME]["gnss_site_data_root"] = str(_paths.ROSALIA)
    recipe.setdefault("processing", {}).setdefault("storage", {}).update(
        {
            "stores_root_dir": str(scratch_dir / "stores"),
            "aux_data_dir": str(scratch_dir / "aux"),
            "shared_aux_cache_dir": None,
        }
    )
    overlay_path = scratch_dir / "overlay.yaml"
    overlay_path.write_text(yaml.safe_dump(recipe, sort_keys=False))
    return overlay_path


def _run_pipeline(n_workers: int | None = 2) -> tuple["MyIcechunkStore", Path, "MyIcechunkStore", Path]:
    """Run the real ingest+VOD pipeline once and return both populated stores.

    A single `canvodpy run` produces a GNSS observation store *and* a VOD
    store (`--no-vod` defaults to False, and the recipe defines
    `vod_analyses`) -- both are scratch Icechunk repositories under a
    freshly created `tempfile.mkdtemp()` directory, never inside the
    read-only `_paths.STORES_DIR` tree. Not cleaned up automatically (same
    trade-off `00_convenience_speedrun.py` and `16_workflow_single_day.py`
    already make re-decoding RINEX from scratch on every run: consistency
    over caching across kernel restarts). Cached for the remainder of this
    kernel session so re-importing/re-calling within one run doesn't
    rebuild, and so `build_rosalia_store()` + `build_rosalia_vod_store()`
    together only invoke the CLI once.
    """
    global _cached, _last_cmd, _last_stdout, _last_stderr
    if _cached is not None:
        return _cached

    if _paths.MONOREPO_ROOT is None:
        raise RuntimeError(
            "build_rosalia_store()/build_rosalia_vod_store() require a local "
            "canvodpy monorepo checkout with a configured "
            "config/canvod-settings.yaml (run `canvodpy config init` there "
            "once if you haven't) -- `canvodpy run` always merges its "
            "--config overlay on top of that file, it never stands alone. "
            "Not available from a standalone demo/ clone, pooch cache, or "
            "Zenodo download."
        )

    _paths.ensure_data()  # no-op if an earlier cell already resolved it

    scratch_dir = Path(tempfile.mkdtemp(prefix="canvodpy_demo_rosalia_store_"))
    _seed_aux_cache(scratch_dir / "aux")
    overlay_path = _build_overlay(scratch_dir)

    cmd = [
        sys.executable,
        "-m",
        "canvodpy.cli.app",
        "run",
        "--site",
        _SITE_NAME,
        "--start",
        _DATE,
        "--end",
        _DATE,
        "--config",
        str(overlay_path),
    ]
    if n_workers is not None:
        cmd += ["--workers", str(n_workers)]
    _last_cmd = cmd

    # cwd=MONOREPO_ROOT: canvod-config's find_monorepo_root() walks up from
    # the subprocess's cwd looking for the nearest `.git` to locate the
    # (never-committed, machine-local) base config/canvod-settings.yaml the
    # --config overlay above merges onto. Without this, the subprocess
    # inherits marimo's own cwd (wherever `marimo edit/run/export` was
    # invoked from, typically demo/) -- and demo/ is itself a separate git
    # submodule with its own `.git`, so find_monorepo_root() stops there,
    # finds no config/ subdirectory, falls back to the XDG default
    # (~/.config/canvodpy/), and fails with a confusing "Settings file not
    # found" error that has nothing to do with the actual overlay recipe.
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=_paths.MONOREPO_ROOT
    )
    _last_stdout = result.stdout
    _last_stderr = result.stderr
    if result.returncode != 0:
        raise RuntimeError(
            "canvodpy run failed while building the demo stores "
            f"(exit {result.returncode}):\n"
            f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
        )

    from canvod.config import load_config
    from canvod.store import MyIcechunkStore

    # Resolve the real store paths from the merged config rather than
    # guessing directory names: gnss_store_name/vod_store_name default to
    # "rinex"/"vod", but a local base config/canvod-settings.yaml can (and
    # in practice does, at least on one dev machine -- discovered the hard
    # way) override them to something else entirely. The overlay above
    # only sets stores_root_dir/aux_data_dir, so any such override in the
    # base file survives the merge untouched.
    #
    # config_dir=MONOREPO_ROOT/"config" explicitly, same reason as cwd=
    # above: this call runs in-process (marimo's own cwd, typically demo/),
    # not the subprocess, so find_monorepo_root()'s default lookup would
    # hit the exact same demo/.git-stops-the-walk issue here too.
    merged_config = load_config(
        config_dir=_paths.MONOREPO_ROOT / "config", config_file=overlay_path
    )
    store_path = merged_config.processing.storage.get_gnss_store_path(_SITE_NAME)
    vod_store_path = merged_config.processing.storage.get_vod_store_path(_SITE_NAME)
    store = MyIcechunkStore(store_path=store_path)
    vod_store = MyIcechunkStore(store_path=vod_store_path)
    _cached = (store, store_path, vod_store, vod_store_path)
    return _cached


def build_rosalia_store(n_workers: int | None = 2) -> tuple["MyIcechunkStore", Path]:
    """Return (store, store_path) for the GNSS observation store."""
    store, store_path, _vod_store, _vod_store_path = _run_pipeline(n_workers)
    return store, store_path


def build_rosalia_vod_store(n_workers: int | None = 2) -> tuple["MyIcechunkStore", Path]:
    """Return (vod_store, vod_store_path) for the VOD store."""
    _store, _store_path, vod_store, vod_store_path = _run_pipeline(n_workers)
    return vod_store, vod_store_path


def get_pipeline_command() -> str:
    """Return the exact `canvodpy run` command last executed, shell-quoted.

    marimo notebooks can't run shell commands directly (there's no cell
    type for it), but the CLI invocation is real and worth showing --
    render this string in a markdown code fence rather than leaving the
    subprocess call as an invisible implementation detail. Call after
    build_rosalia_store()/build_rosalia_vod_store() in the same cell (or a
    later one -- _run_pipeline() is cached, so the command persists for the
    rest of the kernel session).
    """
    if _last_cmd is None:
        return "# not yet run -- call build_rosalia_store() or build_rosalia_vod_store() first"
    import shlex

    return " ".join(shlex.quote(part) for part in _last_cmd)


def get_pipeline_output() -> str:
    """Return the captured stdout+stderr of the last `canvodpy run` invocation.

    subprocess.run(..., capture_output=True) buffers everything and only
    returns once the process exits -- there's no way to stream a live,
    in-place-updating progress bar into a marimo cell this way, so this is
    the full transcript *after* the run finished, not a live view. Still
    real and worth showing: the CLI prints a run banner, ephemeris/aux
    status, and per-date progress that would otherwise be silently
    discarded (subprocess.run's captured output was previously only
    surfaced on failure).
    """
    if _last_stdout is None:
        return "# not yet run -- call build_rosalia_store() or build_rosalia_vod_store() first"
    combined = _last_stdout
    if _last_stderr:
        combined += f"\n--- stderr ---\n{_last_stderr}"
    return combined
