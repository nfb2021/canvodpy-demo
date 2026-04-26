# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvod-virtualiconvname>=0.2.2",
#   "marimo>=0.21.1",
# ]
#
# [tool.marimo.opengraph]
# title = "01 · Naming Convention & Validation"
# description = "Parse and validate GNSS filenames against the IGS/RINEX naming convention. Explore the structured metadata encoded in every canVODpy filename."
# ///

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
    return mo.Html("""
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <div style="overflow-x:auto;padding:1rem 0.5rem;margin:0.5rem 0;">
    <svg viewBox="0 0 880 304" xmlns="http://www.w3.org/2000/svg" style="display:block;min-width:820px;width:100%;">
      <rect x="203" y="29" width="114" height="54" rx="5" fill="none" stroke="#1b4332" stroke-width="1.5" opacity="0.35"/>
      <rect x="347" y="29" width="138" height="54" rx="5" fill="none" stroke="#1b4332" stroke-width="1.5" opacity="0.35"/>
      <rect x="206" y="32" width="36" height="48" fill="#1b4332"/>
      <rect x="242" y="32" width="12" height="48" fill="#2d6a4f"/>
      <rect x="254" y="32" width="24" height="48" fill="#40916c"/>
      <rect x="278" y="32" width="36" height="48" fill="#2d6a4f"/>
      <rect x="314" y="32" width="36" height="48" fill="#d8f3dc"/>
      <rect x="350" y="32" width="48" height="48" fill="#1b4332"/>
      <rect x="398" y="32" width="36" height="48" fill="#2d6a4f"/>
      <rect x="434" y="32" width="48" height="48" fill="#40916c"/>
      <rect x="482" y="32" width="12" height="48" fill="#e9f5ee"/>
      <rect x="494" y="32" width="36" height="48" fill="#52b788"/>
      <rect x="530" y="32" width="12" height="48" fill="#e9f5ee"/>
      <rect x="542" y="32" width="36" height="48" fill="#74c69d"/>
      <rect x="578" y="32" width="12" height="48" fill="#e9f5ee"/>
      <rect x="590" y="32" width="24" height="48" fill="#95d5b2"/>
      <rect x="614" y="32" width="12" height="48" fill="#e9f5ee"/>
      <rect x="626" y="32" width="36" height="48" fill="#b7e4c7"/>
      <rect x="672" y="32" width="36" height="48" fill="rgba(212,237,218,0.30)" stroke="#52b788" stroke-width="1" stroke-dasharray="4,3"/>
      <text font-family="'Fira Code',monospace" font-size="20" font-weight="500" dominant-baseline="central" text-anchor="middle" x="224" y="56" fill="white">ROS</text>
      <text font-family="'Fira Code',monospace" font-size="20" font-weight="500" dominant-baseline="central" text-anchor="middle" x="248" y="56" fill="white">R</text>
      <text font-family="'Fira Code',monospace" font-size="20" font-weight="500" dominant-baseline="central" text-anchor="middle" x="266" y="56" fill="white">01</text>
      <text font-family="'Fira Code',monospace" font-size="20" font-weight="500" dominant-baseline="central" text-anchor="middle" x="296" y="56" fill="white">TUW</text>
      <text font-family="'Fira Code',monospace" font-size="20" font-weight="500" dominant-baseline="central" text-anchor="middle" x="332" y="56" fill="#2d6a4f">_R_</text>
      <text font-family="'Fira Code',monospace" font-size="20" font-weight="500" dominant-baseline="central" text-anchor="middle" x="374" y="56" fill="white">2025</text>
      <text font-family="'Fira Code',monospace" font-size="20" font-weight="500" dominant-baseline="central" text-anchor="middle" x="416" y="56" fill="white">001</text>
      <text font-family="'Fira Code',monospace" font-size="20" font-weight="500" dominant-baseline="central" text-anchor="middle" x="458" y="56" fill="white">0000</text>
      <text font-family="'Fira Code',monospace" font-size="20" font-weight="500" dominant-baseline="central" text-anchor="middle" x="488" y="56" fill="#74c69d">_</text>
      <text font-family="'Fira Code',monospace" font-size="20" font-weight="500" dominant-baseline="central" text-anchor="middle" x="512" y="56" fill="#1b2e22">15M</text>
      <text font-family="'Fira Code',monospace" font-size="20" font-weight="500" dominant-baseline="central" text-anchor="middle" x="536" y="56" fill="#74c69d">_</text>
      <text font-family="'Fira Code',monospace" font-size="20" font-weight="500" dominant-baseline="central" text-anchor="middle" x="560" y="56" fill="#1b2e22">05S</text>
      <text font-family="'Fira Code',monospace" font-size="20" font-weight="500" dominant-baseline="central" text-anchor="middle" x="584" y="56" fill="#74c69d">_</text>
      <text font-family="'Fira Code',monospace" font-size="20" font-weight="500" dominant-baseline="central" text-anchor="middle" x="602" y="56" fill="#1b2e22">AA</text>
      <text font-family="'Fira Code',monospace" font-size="20" font-weight="500" dominant-baseline="central" text-anchor="middle" x="620" y="56" fill="#74c69d">.</text>
      <text font-family="'Fira Code',monospace" font-size="20" font-weight="500" dominant-baseline="central" text-anchor="middle" x="644" y="56" fill="#1b2e22">rnx</text>
      <text font-family="'Fira Code',monospace" font-size="20" font-weight="500" dominant-baseline="central" text-anchor="middle" x="690" y="56" fill="#40916c">.gz</text>
      <text x="690" y="25" fill="#74c69d" font-family="'Fira Code',monospace" font-size="8" text-anchor="middle" letter-spacing="0.08em">optional</text>
      <line x1="690" y1="27" x2="690" y2="31" stroke="#74c69d" stroke-width="0.8"/>
      <line x1="260" y1="80" x2="122" y2="164" stroke="#2d6a4f" stroke-width="1" opacity="0.55"/>
      <line x1="332" y1="80" x2="228" y2="164" stroke="#40916c" stroke-width="1" opacity="0.55"/>
      <line x1="416" y1="80" x2="334" y2="164" stroke="#2d6a4f" stroke-width="1" opacity="0.55"/>
      <line x1="512" y1="80" x2="440" y2="164" stroke="#52b788" stroke-width="1" opacity="0.60"/>
      <line x1="560" y1="80" x2="546" y2="164" stroke="#74c69d" stroke-width="1" opacity="0.60"/>
      <line x1="602" y1="80" x2="652" y2="164" stroke="#95d5b2" stroke-width="1" opacity="0.65"/>
      <line x1="644" y1="80" x2="758" y2="164" stroke="#b7e4c7" stroke-width="1" opacity="0.70"/>
      <rect x="74"  y="164" width="96" height="76" rx="6" fill="#f4f9f6"/><rect x="74"  y="164" width="96" height="76" rx="6" fill="white" stroke="#1b4332" stroke-width="1.2"/><rect x="74"  y="164" width="96" height="24" rx="6" fill="#1b4332"/><rect x="74"  y="176" width="96" height="12" fill="#1b4332"/>
      <text x="122" y="180" fill="white"   font-family="'Space Grotesk',sans-serif" font-size="10" font-weight="600" text-anchor="middle">Station Block</text>
      <text x="122" y="199" fill="#40916c" font-family="'Fira Code',monospace" font-size="8.5" text-anchor="middle">9 chars</text>
      <text x="122" y="213" fill="#1b2e22" font-family="'Space Grotesk',sans-serif" font-size="9" text-anchor="middle">SIT · T · NN · AGC</text>
      <text x="122" y="228" fill="#52b788" font-family="'Fira Code',monospace" font-size="8" text-anchor="middle">e.g. ROSR01TUW</text>
      <rect x="180" y="164" width="96" height="76" rx="6" fill="#f4f9f6"/><rect x="180" y="164" width="96" height="76" rx="6" fill="white" stroke="#2d6a4f" stroke-width="1.2"/><rect x="180" y="164" width="96" height="24" rx="6" fill="#2d6a4f"/><rect x="180" y="176" width="96" height="12" fill="#2d6a4f"/>
      <text x="228" y="180" fill="white"   font-family="'Space Grotesk',sans-serif" font-size="10" font-weight="600" text-anchor="middle">Data Source</text>
      <text x="228" y="199" fill="#40916c" font-family="'Fira Code',monospace" font-size="8.5" text-anchor="middle">3 chars · literal</text>
      <text x="228" y="213" fill="#1b2e22" font-family="'Space Grotesk',sans-serif" font-size="9" text-anchor="middle">Receiver = _R_</text>
      <text x="228" y="228" fill="#52b788" font-family="'Fira Code',monospace" font-size="8" text-anchor="middle">always _R_</text>
      <rect x="286" y="164" width="96" height="76" rx="6" fill="#f4f9f6"/><rect x="286" y="164" width="96" height="76" rx="6" fill="white" stroke="#1b4332" stroke-width="1.2"/><rect x="286" y="164" width="96" height="24" rx="6" fill="#1b4332"/><rect x="286" y="176" width="96" height="12" fill="#1b4332"/>
      <text x="334" y="180" fill="white"   font-family="'Space Grotesk',sans-serif" font-size="10" font-weight="600" text-anchor="middle">Start Epoch</text>
      <text x="334" y="199" fill="#40916c" font-family="'Fira Code',monospace" font-size="8.5" text-anchor="middle">11 chars</text>
      <text x="334" y="213" fill="#1b2e22" font-family="'Space Grotesk',sans-serif" font-size="9" text-anchor="middle">YYYY · DOY · HHMM</text>
      <text x="334" y="228" fill="#52b788" font-family="'Fira Code',monospace" font-size="8" text-anchor="middle">e.g. 20250010000</text>
      <rect x="392" y="164" width="96" height="76" rx="6" fill="#f4f9f6"/><rect x="392" y="164" width="96" height="76" rx="6" fill="white" stroke="#52b788" stroke-width="1.2"/><rect x="392" y="164" width="96" height="24" rx="6" fill="#52b788"/><rect x="392" y="176" width="96" height="12" fill="#52b788"/>
      <text x="440" y="180" fill="#1b2e22" font-family="'Space Grotesk',sans-serif" font-size="10" font-weight="600" text-anchor="middle">Period</text>
      <text x="440" y="199" fill="#40916c" font-family="'Fira Code',monospace" font-size="8.5" text-anchor="middle">3 chars</text>
      <text x="440" y="213" fill="#1b2e22" font-family="'Space Grotesk',sans-serif" font-size="9" text-anchor="middle">File duration</text>
      <text x="440" y="228" fill="#2d6a4f" font-family="'Fira Code',monospace" font-size="8" text-anchor="middle">15M · 01H · 01D</text>
      <rect x="498" y="164" width="96" height="76" rx="6" fill="#f4f9f6"/><rect x="498" y="164" width="96" height="76" rx="6" fill="white" stroke="#74c69d" stroke-width="1.2"/><rect x="498" y="164" width="96" height="24" rx="6" fill="#74c69d"/><rect x="498" y="176" width="96" height="12" fill="#74c69d"/>
      <text x="546" y="180" fill="#1b2e22" font-family="'Space Grotesk',sans-serif" font-size="10" font-weight="600" text-anchor="middle">Sampling</text>
      <text x="546" y="199" fill="#40916c" font-family="'Fira Code',monospace" font-size="8.5" text-anchor="middle">3 chars</text>
      <text x="546" y="213" fill="#1b2e22" font-family="'Space Grotesk',sans-serif" font-size="9" text-anchor="middle">Obs. interval</text>
      <text x="546" y="228" fill="#2d6a4f" font-family="'Fira Code',monospace" font-size="8" text-anchor="middle">05S · 30S · 01S</text>
      <rect x="604" y="164" width="96" height="76" rx="6" fill="#f4f9f6"/><rect x="604" y="164" width="96" height="76" rx="6" fill="white" stroke="#95d5b2" stroke-width="1.2"/><rect x="604" y="164" width="96" height="24" rx="6" fill="#95d5b2"/><rect x="604" y="176" width="96" height="12" fill="#95d5b2"/>
      <text x="652" y="180" fill="#1b2e22" font-family="'Space Grotesk',sans-serif" font-size="10" font-weight="600" text-anchor="middle">Content</text>
      <text x="652" y="199" fill="#40916c" font-family="'Fira Code',monospace" font-size="8.5" text-anchor="middle">2 chars</text>
      <text x="652" y="213" fill="#1b2e22" font-family="'Space Grotesk',sans-serif" font-size="9" text-anchor="middle">Content code</text>
      <text x="652" y="228" fill="#2d6a4f" font-family="'Fira Code',monospace" font-size="8" text-anchor="middle">always AA</text>
      <rect x="710" y="164" width="96" height="76" rx="6" fill="#f4f9f6"/><rect x="710" y="164" width="96" height="76" rx="6" fill="white" stroke="#b7e4c7" stroke-width="1.2"/><rect x="710" y="164" width="96" height="24" rx="6" fill="#b7e4c7"/><rect x="710" y="176" width="96" height="12" fill="#b7e4c7"/>
      <text x="758" y="180" fill="#1b2e22" font-family="'Space Grotesk',sans-serif" font-size="10" font-weight="600" text-anchor="middle">Format</text>
      <text x="758" y="199" fill="#40916c" font-family="'Fira Code',monospace" font-size="8.5" text-anchor="middle">3–4 chars</text>
      <text x="758" y="213" fill="#1b2e22" font-family="'Space Grotesk',sans-serif" font-size="9" text-anchor="middle">File format ext.</text>
      <text x="758" y="228" fill="#2d6a4f" font-family="'Fira Code',monospace" font-size="8" text-anchor="middle">rnx · sbf · ubx</text>
      <line x1="24" y1="252" x2="856" y2="252" stroke="rgba(45,106,79,0.12)" stroke-width="0.8"/>
      <rect x="24"  y="257" width="12" height="12" rx="2" fill="#1b4332"/><text x="40"  y="267" fill="#1b2e22" font-family="'Fira Code',monospace" font-size="8.5">Station</text>
      <rect x="104" y="257" width="12" height="12" rx="2" fill="#2d6a4f"/><text x="120" y="267" fill="#1b2e22" font-family="'Fira Code',monospace" font-size="8.5">Source</text>
      <rect x="184" y="257" width="12" height="12" rx="2" fill="#1b4332"/><text x="200" y="267" fill="#1b2e22" font-family="'Fira Code',monospace" font-size="8.5">Epoch</text>
      <rect x="264" y="257" width="12" height="12" rx="2" fill="#52b788"/><text x="280" y="267" fill="#1b2e22" font-family="'Fira Code',monospace" font-size="8.5">Period / Sampling</text>
      <rect x="424" y="257" width="12" height="12" rx="2" fill="#95d5b2"/><text x="440" y="267" fill="#1b2e22" font-family="'Fira Code',monospace" font-size="8.5">Content</text>
      <rect x="504" y="257" width="12" height="12" rx="2" fill="#b7e4c7"/><text x="520" y="267" fill="#1b2e22" font-family="'Fira Code',monospace" font-size="8.5">Format</text>
      <rect x="584" y="257" width="12" height="12" rx="2" fill="none" stroke="#52b788" stroke-dasharray="3,2" stroke-width="1"/><text x="600" y="267" fill="#74c69d" font-family="'Fira Code',monospace" font-size="8.5">Optional</text>
      <rect x="672" y="257" width="12" height="12" rx="2" fill="#e9f5ee" stroke="rgba(45,106,79,0.20)" stroke-width="0.8"/><text x="688" y="267" fill="#74c69d" font-family="'Fira Code',monospace" font-size="8.5">Separator</text>
      <text x="24" y="292" fill="#95d5b2" font-family="'Fira Code',monospace" font-size="7.5" letter-spacing="0.06em">* T: R = reference receiver (above canopy)  ·  A = active receiver (below canopy)</text>
    </svg>
    </div>
    """)


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
