# /// script
# dependencies = [
#   "tqdm"
# ]
# ///

import shutil
from pathlib import Path

from tqdm import trange

dirs = ["25001", "25002"]

for d in dirs:
    src = (
        Path(
            "/Users/work/GNSS_Vegetation_Study/05_data/01_Rosalia/02_canopy/01_GNSS/01_raw"
        )
        / d
    )

    dst = (
        Path(
            "/Users/work/Developer/GNSS/canvodpy-demo/data/01_Rosalia/02_canopy/01_GNSS/01_raw"
        )
        / d
    )

    if not dst.exists():
        dst.mkdir()

    print(dst)
    rnx_pat = "*.25o"

    rnx_files = sorted([x for x in src.glob(rnx_pat)])

    print(len(rnx_files))
    print(rnx_files[0:5])

    for r in trange(len(rnx_files), desc=f"copying files in {d}"):
        rnx_file = rnx_files[r]
        if (dst / rnx_file.name).exists():
            print(f"File {(dst / rnx_file.name)} exist. Continue")
        else:
            shutil.copy(rnx_file, dst / rnx_file.name)
