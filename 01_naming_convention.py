import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium",
    app_title="Naming Convention & Validation",
    css_file="canvod_nordic.css",
)


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # Naming Convention and File Validation

    GNSS-Transmissometry campaigns generate thousands of files across
    multiple receivers, days, and sampling intervals.  Without a strict
    naming convention, duplicate or misattributed files can silently
    corrupt a dataset.

    The **canvod-virtualiconvname** package is the single source of truth for
    GNSS filename conventions in canvodpy.  It provides:

    1. **`CanVODFilename`** — a structured parser for the IGS-derived
       long-name convention
    2. **`BUILTIN_PATTERNS`** — regex patterns for recognising RINEX v2,
       RINEX v3, Septentrio SBF, and canVOD filenames
    3. **`FilenameMapper`** — maps physical files on disk to canonical names
    4. **`DataDirectoryValidator`** — pre-pipeline hard gate that rejects
       unmapped files and temporal overlaps before any data is read

    The naming convention encodes station identity, receiver role, time window,
    sampling rate, and file type into a single, self-describing filename.
    This eliminates ambiguity when ingesting data from multiple receivers
    and time periods.

    ---
    """)
    return


@app.cell
def _():
    from _paths import ROSALIA_CANOPY_DIR

    return (ROSALIA_CANOPY_DIR,)


@app.cell
def _(mo):
    mo.md(r"""
    ## The canVOD filename convention

    ```
    ROSA01TUW_R_20250010000_15M_05S_AA.rnx
    ^^^|^|^^^   ^^^^|^^^|^^^^ ^^^ ^^^ ^^
    SIT T NN AGC  YYYY DOY HHMM PER SMP PH  TYPE
    ```

    | Field | Chars | Description | Example |
    |-------|-------|-------------|---------|
    | **SIT** | 3 | Site identifier (uppercase) | `ROS` |
    | **T** | 1 | Receiver type: `R`=reference, `A`=active (canopy) | `A` |
    | **NN** | 2 | Receiver number (01--99) | `01` |
    | **AGC** | 3 | Operating agency (uppercase) | `TUW` |
    | `_R_` | 3 | Separator (RINEX convention) | |
    | **YYYY** | 4 | Year | `2025` |
    | **DOY** | 3 | Day of year (001--366) | `001` |
    | **HHMM** | 4 | Start hour and minute (UTC) | `0000` |
    | **PER** | 3 | File duration (`15M`, `01H`, `01D`) | `15M` |
    | **SMP** | 3 | Sampling interval (`05S`, `01S`) | `05S` |
    | **PH** | 2 | Reserved; ignored during parsing | `AA` |
    | **TYPE** | 3+ | File extension (`rnx`, `sbf`, `nmea`) | `rnx` |

    This convention extends the
    [IGS long-name standard](http://acc.igs.org/misc/rinex304.pdf)
    (page 14f) with a receiver-type field (`T`) that distinguishes
    reference and canopy receivers at the same site.
    """)
    return


@app.cell
def _(mo):
    mo.mermaid("""
    packet-beta
        0-2: "SIT"
        3: "T"
        4-5: "NN"
        6-8: "AGC"
        9-11: "_R_"
        12-15: "YYYY"
        16-18: "DOY"
        19-22: "HHMM"
        23: "_"
        24-26: "PPP"
        27: "_"
        28-30: "SSS"
        31: "_"
        32-33: "CC"
        34: "."
        35-37: "TTT"
    """)
    return


@app.cell
def _():
    from canvod.virtualiconvname import CanVODFilename

    return (CanVODFilename,)


@app.cell
def _(CanVODFilename, ROSALIA_CANOPY_DIR, mo):
    _file = sorted(ROSALIA_CANOPY_DIR.glob("25001/*.rnx"))[0]
    parsed = CanVODFilename.from_filename(_file.name)

    mo.md(f"""
    ## Parsing a filename

    ```python
    from canvod.virtualiconvname import CanVODFilename

    parsed = CanVODFilename.from_filename("{_file.name}")
    ```

    | Field | Value |
    |-------|-------|
    | **Site** | `{parsed.site}` |
    | **Receiver type** | `{parsed.receiver_type}` |
    | **Receiver number** | `{parsed.receiver_number}` |
    | **Agency** | `{parsed.agency}` |
    | **Year** | {parsed.year} |
    | **DOY** | {parsed.doy} |
    | **Hour:Minute** | {parsed.hour:02d}:{parsed.minute:02d} |
    | **Period** | `{parsed.period}` ({parsed.batch_duration}) |
    | **Sampling** | `{parsed.sampling}` ({parsed.sampling_interval}) |
    | **Content** | `{parsed.content}` |
    | **File type** | `{parsed.file_type}` |
    | **Reconstructed** | `{parsed.name}` |

    The model is frozen (immutable) and round-trips perfectly:
    `CanVODFilename.from_filename(parsed.name)` produces an identical object.
    """)
    return


@app.cell
def _():
    from canvod.virtualiconvname import BUILTIN_PATTERNS, match_pattern

    return BUILTIN_PATTERNS, match_pattern


@app.cell
def _(BUILTIN_PATTERNS, mo):
    _rows = []
    for _name, _pat in BUILTIN_PATTERNS.items():
        _globs = ", ".join(f"`{g}`" for g in _pat.file_globs)
        _rows.append(f"| `{_name}` | {_globs} |")

    mo.md(f"""
    ## Built-in filename patterns

    `BUILTIN_PATTERNS` is a registry of named regex patterns for different
    GNSS filename conventions.  The `match_pattern()` function tries each
    in order (or a specific one by name).

    | Pattern | Glob(s) |
    |---------|---------|
    {chr(10).join(_rows)}
    """)
    return


@app.cell
def _(match_pattern, mo):
    _examples = [
        "ROSA01TUW_R_20250010000_15M_05S_AA.rnx",
        "ROSR01TUW_R_20250010000_15M_05S_AA.sbf",
    ]

    _rows = []
    for _fn in _examples:
        _result = match_pattern(_fn, pattern_name="auto")
        if _result:
            _pat, _m = _result
            _rows.append(f"| `{_fn}` | `{_pat.name}` |")
        else:
            _rows.append(f"| `{_fn}` | *no match* |")

    mo.md(f"""
    ### Auto-detection

    ```python
    from canvod.virtualiconvname import match_pattern

    pattern, match = match_pattern("ROSA01TUW_R_20250010000_15M_05S_AA.rnx")
    ```

    | Filename | Matched pattern |
    |----------|----------------|
    {chr(10).join(_rows)}
    """)
    return


@app.cell
def _(CanVODFilename, ROSALIA_CANOPY_DIR, mo):
    _files = sorted(ROSALIA_CANOPY_DIR.glob("25001/*.rnx"))

    _first_five = []
    for _f in _files[:5]:
        _p = CanVODFilename.from_filename(_f.name)
        _first_five.append(
            f"| `{_f.name}` | {_p.hour:02d}:{_p.minute:02d} | `{_p.period}` |"
        )

    _last = CanVODFilename.from_filename(_files[-1].name)

    mo.md(f"""
    ## Test data: one full day

    The canopy receiver directory contains **{len(_files)}** RINEX files
    covering DOY 2025-001 (1 January 2025).

    | File | Start (UTC) | Period |
    |------|-------------|--------|
    {chr(10).join(_first_five)}
    | ... | | |
    | `{_files[-1].name}` | {_last.hour:02d}:{_last.minute:02d} | `{_last.period}` |

    The file period (`{_last.period}`) and total count are determined
    by the receiver configuration.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Pre-pipeline validation

    Before any data is read, the `DataDirectoryValidator` performs a
    **hard gate** check on the file inventory:

    1. **Name mapping**: every file must match a known pattern and produce
       a valid `CanVODFilename`.  Unrecognised files (e.g. log files,
       temporary files) are flagged.

    2. **Temporal overlap detection**: files covering the same time window
       (e.g. a daily file alongside 15-minute files for the same day) are
       flagged as overlaps.  Overlapping data would cause duplicate
       observations in the store.

    3. **Consistency checks**: receiver type, site ID, and agency must be
       consistent across all files in a directory.

    If validation fails, the pipeline **refuses to proceed**.  This prevents
    silent data corruption from misconfigured directories.

    ```python
    from canvod.virtualiconvname import DataDirectoryValidator

    validator = DataDirectoryValidator()
    report = validator.validate_receiver(
        site_naming=site_config,
        receiver_naming=receiver_config,
        receiver_type="canopy",
        receiver_base_dir=data_dir,
    )

    if report.is_valid:
        # Safe to proceed with ingestion
        ...
    else:
        # report.unmatched, report.overlaps contain diagnostics
        ...
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Filename virtualisation

    The `FilenameMapper` bridges the gap between physical files on disk
    (which may use arbitrary naming) and the canonical convention.

    This is essential for sites that receive data from third-party operators
    who use their own naming schemes (RINEX v2 short names, Septentrio
    native names, etc.).  The mapper:

    1. Discovers all files matching known patterns
    2. Maps each to its canonical `CanVODFilename`
    3. Returns `VirtualFile` objects that pair the physical path with the
       canonical name

    Downstream code only sees canonical names, ensuring consistent
    behaviour regardless of how files were originally named.

    ```python
    from canvod.virtualiconvname import FilenameMapper

    mapper = FilenameMapper(
        site_naming=site_config,
        receiver_naming=receiver_config,
        receiver_type="canopy",
        receiver_base_dir=data_dir,
    )

    # Discover all files
    virtual_files = mapper.discover_all()

    # Or for a specific date
    virtual_files = mapper.discover_for_date(year=2025, doy=1)

    for vf in virtual_files:
        print(f"{vf.physical_path.name} -> {vf.canonical_str}")
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    With canonical naming and pre-pipeline validation, data integrity is
    guaranteed before any processing begins.  Every file is unambiguously
    identified, and temporal overlaps or naming inconsistencies are caught
    at the gate.

    **Next**: [02 — RINEX Reading](./02_rinex_reading.py)

    *canVODpy — Apache 2.0*
    """)
    return


if __name__ == "__main__":
    app.run()
