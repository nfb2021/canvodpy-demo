"""Marimo-aware Pooch downloader for canvodpy-demo notebooks.

Usage in a notebook setup cell::

    import marimo as mo
    import _paths
    from _download import marimo_downloader

    _paths.ensure_data(downloader=marimo_downloader)

If data is already cached the downloader is never called — the call
returns instantly with no UI rendered.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def marimo_downloader(url: str, output_file: Path | str, _pooch) -> None:  # noqa: ANN001
    """Pooch-compatible downloader that renders a marimo progress bar.

    Falls back to a plain requests stream (no bar) if marimo is not
    available (e.g. when running from a plain Python script).
    """
    try:
        import marimo as mo
        _has_marimo = True
    except ImportError:
        _has_marimo = False

    import requests

    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    total = int(response.headers.get("content-length", 0))
    chunk_size = 64 * 1024  # 64 KB

    if _has_marimo and total > 0:
        with mo.status.progress_bar(
            total=total,
            title="Downloading canvodpy-test-data from Zenodo",
            subtitle=f"{total / 1_073_741_824:.1f} GB · cached after first run",
        ) as bar:
            with open(output_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    bar.update(len(chunk))
    else:
        # Plain stream — tqdm fallback or no bar
        with open(output_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                f.write(chunk)
