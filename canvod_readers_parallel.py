"""Helper for parallel RINEX reading.

This module provides functions for parallel processing of RINEX files.
Used by demo notebooks to enable ProcessPoolExecutor.

Note: Functions must be at module level (not nested) for pickling.
"""

from pathlib import Path

import xarray as xr
from canvod.readers import Rnxv3Obs


def read_rinex_file(fpath: Path) -> xr.Dataset:
    """Read a RINEX file and convert to xarray Dataset.

    Parameters
    ----------
    fpath : Path
        Path to RINEX file

    Returns
    -------
    xr.Dataset
        RINEX data as xarray Dataset with SNR data

    """
    obs = Rnxv3Obs(fpath=fpath)
    return obs.to_ds(keep_rnx_data_vars=["SNR"], write_global_attrs=True)
