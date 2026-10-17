# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvodpy",
#   "marimo>=0.21.1",
#   "pyyaml==6.0.3",
# ]
#
# [tool.uv.sources]
# canvodpy = { git = "https://github.com/nfb2021/canvodpy.git", subdirectory = "canvodpy", rev = "064ba56bf46794fa66007dd58f805bfcf9227949" }
#
# [tool.marimo.opengraph]
# title = "22 · Stores on S3"
# description = "Write, read and share canVODpy stores in an S3 bucket: a run on S3, credentials from the environment only, two runs on one store at the same time, settings rebuilt from a store, and what is different from a local folder."
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium", app_title="Stores on S3", css_file="canvod_nordic.css",
    html_head_file="canvod_head.html"
)


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
    <p align="center" class="canvod-logo">
      <img class="canvod-logo-light" src="https://raw.githubusercontent.com/nfb2021/canvodpy/main/docs/assets/logo/canvodpy_logo_bright_mode.svg" alt="canVODpy logo" width="280">
      <img class="canvod-logo-dark" src="https://raw.githubusercontent.com/nfb2021/canvodpy/main/docs/assets/logo/canvodpy_logo_dark_mode.svg" alt="canVODpy logo" width="280">
    </p>

    # Stores on S3

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/nfb2021/canvodpy-demo/blob/main/22_s3_stores.py?mode=edit)

    A canVODpy store can live in an S3 bucket instead of a local folder.
    S3 is the storage interface of most cloud and institutional object
    stores, so a store there can be written by computers in several places
    and read by anyone who has access, without copying it first.

    The only change in the settings is the stores folder:

    ```yaml
    processing:
      storage:
        stores_root_dir: s3://my-bucket/stores
    ```

    This notebook writes a site's GNSS store and VOD store into a bucket
    from the demo data, reads them in place, and shows what a store on S3
    does differently from a local folder: two runs may write one store at
    the same time, and maintenance is a dry run only.

    ## What you need

    An S3 bucket. Without one, run RustFS, a free S3 emulator, on your
    own machine: it is what the canVODpy S3 tests use. With
    [colima](https://github.com/abiosoft/colima) (or any Docker), in one
    terminal:

    ```bash
    colima start
    export AWS_ACCESS_KEY_ID="$(openssl rand -hex 12)"
    export AWS_SECRET_ACCESS_KEY="$(openssl rand -hex 24)"
    docker run --detach --name canvod-rustfs \
        --publish 127.0.0.1:9000:9000 \
        --env AWS_ACCESS_KEY_ID --env AWS_SECRET_ACCESS_KEY \
        --entrypoint /bin/sh rustfs/rustfs:1.0.0-rc.6 -c \
        'mkdir -p /data/canvod-demo && exec rustfs --access-key "$AWS_ACCESS_KEY_ID" --secret-key "$AWS_SECRET_ACCESS_KEY" /data'
    uvx marimo edit --sandbox 22_s3_stores.py
    ```

    The two keys are made up on the spot; the emulator accepts them
    because it was started with them. Start marimo from the same terminal,
    so the notebook sees them. `docker rm --force canvod-rustfs` removes
    the emulator and everything written to it.

    For a real bucket, set its credentials in the environment before you
    start marimo (below says which variables) and enter the bucket and its
    endpoint here.
    """
    )

    return (mo,)


@app.cell
def _(mo):
    import os

    bucket = mo.ui.text(
        value=os.environ.get("CANVOD_DEMO_S3_URL", "s3://canvod-demo/notebook"),
        label="Bucket and prefix (s3://bucket/prefix)",
        full_width=True,
    )
    endpoint = mo.ui.text(
        value=os.environ.get("AWS_ENDPOINT_URL", "http://127.0.0.1:9000"),
        label="Endpoint (empty for AWS)",
        full_width=True,
    )
    region = mo.ui.text(
        value=os.environ.get("AWS_REGION", "us-east-1"), label="Region"
    )
    path_style = mo.ui.checkbox(
        value=os.environ.get("CANVOD_S3_PATH_STYLE", "1").lower()
        in {"1", "true", "yes", "on"},
        label="Bucket in the request path (RustFS, Ceph; not AWS)",
    )

    mo.vstack(
        [
            mo.md(
                r"""
    ## Your S3 endpoint

    The notebook writes everything under a new prefix inside this one, so
    it never touches what is already in the bucket.
    """
            ),
            bucket,
            endpoint,
            mo.hstack([region, path_style], justify="start"),
        ]
    )
    return bucket, endpoint, os, path_style, region


@app.cell
def _(bucket, endpoint, mo, os, path_style, region):
    import socket
    from pathlib import Path
    from urllib.parse import urlparse

    from canvod.store_metadata import store_exists

    stores_url = bucket.value.strip().rstrip("/")

    # Where the service is and how to address it: not secret, so the
    # notebook may set them. The credentials it only reads.
    if endpoint.value.strip():
        os.environ["AWS_ENDPOINT_URL"] = endpoint.value.strip()
        # Without credentials, don't wait for the AWS machine metadata.
        os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
    else:
        os.environ.pop("AWS_ENDPOINT_URL", None)
    os.environ["AWS_REGION"] = region.value.strip()
    os.environ["CANVOD_S3_PATH_STYLE"] = "1" if path_style.value else "0"

    def _problem() -> str | None:
        parts = urlparse(stores_url)
        if parts.scheme != "s3" or not parts.netloc or not parts.path.strip("/"):
            return f"`{stores_url}` is not an `s3://bucket/prefix` URL."
        has_keys = os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get(
            "AWS_SECRET_ACCESS_KEY"
        )
        has_files = (Path.home() / ".aws" / "credentials").is_file()
        if not (has_keys or os.environ.get("AWS_PROFILE") or has_files):
            return (
                "No S3 credentials in the environment: set "
                "`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` (or "
                "`AWS_PROFILE`) and start marimo again from that terminal."
            )
        if endpoint.value.strip():
            url = urlparse(endpoint.value.strip())
            port = url.port or (443 if url.scheme == "https" else 80)
            try:
                socket.create_connection((url.hostname, port), timeout=3).close()
            except OSError:
                return f"Nothing answers at `{endpoint.value.strip()}`."
        try:
            store_exists(f"{stores_url}/reachable")
        except Exception as error:  # noqa: BLE001 - shown to the reader
            return str(error)
        return None

    problem = _problem()
    mo.stop(
        problem is not None,
        mo.callout(
            mo.md(
                f"""
    **No S3 endpoint to write to.** {problem}

    Start RustFS as shown at the top of the notebook, or enter a bucket
    whose credentials are in the environment. The rest of the notebook
    runs once the endpoint answers.
    """
            ),
            kind="warn",
        ),
    )
    mo.callout(mo.md(f"S3 answers; the stores go below `{stores_url}`."), kind="success")
    return Path, stores_url


@app.cell
def _(Path, os, stores_url):
    import contextlib
    import getpass
    import io
    import re
    import shutil
    import subprocess
    import sys
    import tempfile
    import uuid
    from datetime import UTC, datetime

    import yaml

    from canvod.utils import testing
    from canvodpy import demo_data

    SITE = "rosalia_v3_04"
    ANALYSIS = "canopy_01_vs_reference_01"
    DAY = "2025001"
    RECEIVERS = {
        "reference_01": "01_reference/01_GNSS/01_raw",
        "canopy_01": "02_canopy/01_GNSS/01_raw",
    }

    root = demo_data("rinex")
    demo_data("aux")
    work = Path(tempfile.mkdtemp(prefix="canvodpy_s3_demo_"))
    # A new prefix for each session of the notebook.
    session_url = f"{stores_url}/{datetime.now(UTC):%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}"

    def settings(folder, *, data_root, stores, **changes):
        """Write a settings file into ``folder/config``; return that folder.

        Every run in this notebook has its own data, logs and auxiliary
        files (a folder on its machine), and the stores on S3.
        """
        aux = folder / "aux_data"
        for kind in ("01_SP3", "02_CLK"):
            shutil.copytree(root / "aux_data" / kind, aux / kind, dirs_exist_ok=True)
        receiver = {"reader_format": "rinex3"}
        content = {
            "sites": {
                SITE: {
                    "store_description": (
                        "GNSS-T store on S3, written by the canVODpy demo "
                        "notebook from the Rosalia RINEX v3.04 demo data."
                    ),
                    "description": "Beech forest GNSS-T research site, demo data.",
                    "country": "AT",
                    "latitude": 47.7,
                    "longitude": 16.3,
                    "altitude_m": 680.0,
                    "gnss_site_data_root": str(data_root),
                    "receivers": {
                        "reference_01": {
                            "type": "reference",
                            "directory": RECEIVERS["reference_01"],
                            "paired_canopies": "all",
                            **receiver,
                        },
                        "canopy_01": {
                            "type": "canopy",
                            "directory": RECEIVERS["canopy_01"],
                            **receiver,
                        },
                    },
                    "vod_analyses": {
                        ANALYSIS: {
                            "canopy_receiver": "canopy_01",
                            "reference_receiver": "reference_01",
                        }
                    },
                }
            },
            "processing": {
                "metadata": {
                    "author": testing.PERSON_NAME,
                    "email": testing.PERSON_EMAIL,
                    "orcid": testing.PERSON_ORCID,
                    "institution": testing.INSTITUTION,
                    "institution_ror": "https://ror.org/" + testing.INSTITUTION_ROR,
                    "department": testing.DEPARTMENT,
                    "research_group": testing.RESEARCH_GROUP,
                    "website": testing.WEBSITE,
                    "license": "CC-BY-4.0",
                    "publisher": testing.PUBLISHER,
                    "publisher_url": testing.WEBSITE,
                    "naming_authority": testing.NAMING_AUTHORITY,
                },
                "storage": {
                    "stores_root_dir": stores,
                    "aux_data_dir": str(aux),
                    "shared_aux_cache_dir": None,
                },
                "logging": {"log_dir": str(folder / "logs")},
                **changes,
            },
        }
        config_dir = folder / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        (config_dir / "canvod-settings.yaml").write_text(
            yaml.safe_dump(content, sort_keys=False)
        )
        return config_dir

    def site_data(folder, files):
        """The demo files ``files`` (a slice) of each receiver, linked into ``folder``."""
        for directory in RECEIVERS.values():
            day = folder / directory / DAY[2:]
            day.mkdir(parents=True)
            for f in sorted((root / "rinex_v3_04" / "01_Rosalia" / directory / DAY[2:]).iterdir())[files]:
                (day / f.name).symlink_to(f)
        return folder

    def clean(text):
        """``text`` without this machine's folders, user and host name."""
        for folder in {str(work), str(work.resolve()), str(Path.home())}:
            text = text.replace(folder, "…")
        return re.sub(
            rf"\b{re.escape(getpass.getuser())}@\S+?(?=[,\s])",
            "<you>@<this machine>",
            text,
        )

    canvodpy_cli = shutil.which("canvodpy", path=str(Path(sys.executable).parent))

    def start_cli(*args, config_dir):
        """Start the canvodpy command line as a process of its own.

        Its output goes to a file next to ``config_dir``, so two processes
        run side by side without waiting for anyone to read it.
        """
        output = (config_dir.parent / "output.txt").open("w")
        process = subprocess.Popen(
            [canvodpy_cli, *args],
            env={
                **os.environ,
                "CANVOD_CONFIG_DIR": str(config_dir),
                "NO_COLOR": "1",
                "COLUMNS": "100",
            },
            cwd=config_dir,
            stdout=output,
            stderr=subprocess.STDOUT,
            text=True,
        )
        process.output_path = Path(output.name)
        output.close()
        return process

    def finish_cli(process):
        """Exit code and output of a process ``start_cli`` started."""
        code = process.wait(timeout=1800)
        return code, clean(process.output_path.read_text())

    def cli(*args, config_dir):
        """Run the canvodpy command line; its exit code and output."""
        return finish_cli(start_cli(*args, config_dir=config_dir))

    def block(text):
        """``text`` without its leading and trailing blank lines."""
        return text.strip("\n")

    def message(output, start):
        """The error message in a run's output that starts with ``start``.

        It ends before the log line of the error, which repeats it.
        """
        lines = output[output.find(start):].splitlines() if start in output else []
        kept = []
        for line in lines:
            if not line.strip() or "\x1b[" in line or "uncaught_exception" in line:
                break
            kept.append(line)
        return "\n".join(kept) or output[-1500:]

    @contextlib.contextmanager
    def quiet():
        """Keep the messages a run prints (its auxiliary files) out of the cell."""
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            yield

    config_dir = settings(
        work / "notebook",
        data_root=root / "rinex_v3_04" / "01_Rosalia",
        stores=session_url,
    )
    os.environ["CANVOD_CONFIG_DIR"] = str(config_dir)
    return (
        ANALYSIS,
        DAY,
        SITE,
        block,
        clean,
        cli,
        config_dir,
        contextlib,
        finish_cli,
        message,
        quiet,
        session_url,
        settings,
        site_data,
        start_cli,
        work,
    )


@app.cell
def _(ANALYSIS, DAY, SITE, block, contextlib, mo, quiet, session_url, work):
    from canvodpy import Site

    # The run starts in a folder that is no uv project, so it records no
    # lockfile; "The lockfile in its own commit" below says why.
    with contextlib.chdir(work), quiet():
        site = Site(SITE)
        with site.pipeline(n_workers=2) as pipe:
            gnss = pipe.process_date(DAY)
        vod = site.vod.compute_bulk(ANALYSIS, write=True)

    _rows = "\n".join(
        f"| `{name}` | {ds.sizes['epoch']} | {ds.sizes['sid']} |"
        for name, ds in gnss.items()
    )
    mo.md(
        f"""
    ## A run that writes its stores on S3

    The settings above (written in code into a temporary folder) put the
    stores below a new prefix of your bucket. Everything else is a normal
    run of the site pipeline on the demo data, and the VOD computed from
    the GNSS store:

    ```python
    from canvodpy import Site

    site = Site("{SITE}")
    with site.pipeline(n_workers=2) as pipe:
        gnss = pipe.process_date("{DAY}")
    vod = site.vod.compute_bulk("{ANALYSIS}", write=True)
    ```

    | Store | Where |
    |-------|-------|
    | GNSS store | `{site.gnss_store_path}` |
    | VOD store | `{site.vod_store_path}` |

    | GNSS store group | Epochs | Signals |
    |------------------|--------|---------|
    {block(_rows)}

    The VOD of `{ANALYSIS}` has {vod.sizes['epoch']} epochs of
    {vod.sizes['sid']} signals.

    The raw files, the orbits and clocks, the logs and the run history
    stay on the machine that runs: only the stores are on S3. The prefix
    of this session is `{session_url}`.
    """
    )
    return Site, site


@app.cell
def _(block, config_dir, mo, os, site, work):
    from canvod.store_metadata import open_repository, read_metadata

    def _commit_metadata(path):
        return "\n".join(
            str(snapshot.metadata)
            for snapshot in open_repository(path).ancestry(branch="main")
        )

    _secrets = {
        name: os.environ[name]
        for name in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN")
        if os.environ.get(name)
    }
    _places = {
        "The settings file": (config_dir / "canvod-settings.yaml").read_text(),
        "The GNSS store's metadata": read_metadata(site.gnss_store_path).model_dump_json(),
        "The VOD store's metadata": read_metadata(site.vod_store_path).model_dump_json(),
        "The GNSS store's commits": _commit_metadata(site.gnss_store_path),
        "The VOD store's commits": _commit_metadata(site.vod_store_path),
        "The run's log files": "\n".join(
            p.read_text(errors="replace")
            for p in (work / "notebook" / "logs").rglob("*")
            if p.is_file() and p.suffix != ".sqlite"
        ),
    }
    _found = "\n".join(
        f"| {place} | {', '.join(f'`{n}`' for n, v in _secrets.items() if v in text) or 'none'} |"
        for place, text in _places.items()
    )
    mo.md(
        f"""
    ## Credentials: from the environment only

    canVODpy reads the S3 credentials only from the environment
    (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`, or `AWS_PROFILE`) or
    from the shared AWS files (`~/.aws/credentials`, `~/.aws/config`); the
    region and the endpoint come from `AWS_REGION` and `AWS_ENDPOINT_URL`.
    The settings file has no place for them, and neither the stores, their
    commits nor the logs record them. A store shared with others never
    hands out your keys.

    `CANVOD_S3_PATH_STYLE=1` puts the bucket in the request path
    (`http://endpoint/bucket/...`) instead of the host name
    (`http://bucket.endpoint/...`): self-hosted services such as RustFS
    or Ceph expect it, AWS does not.

    The credentials of this session, looked for everywhere the run wrote:

    | Where | Credentials found |
    |-------|-------------------|
    {block(_found)}
    """
    )
    return open_repository, read_metadata


@app.cell
def _(ANALYSIS, mo, site):
    canopy = site.gnss_store.read_group("canopy_01", drop_empty=True)
    vod_ds = site.vod_store.read_group(f"tau_omega/{ANALYSIS}", drop_empty=True)
    _visible = int(canopy["SNR"].notnull().any("epoch").sum())
    mo.vstack(
        [
            mo.md(
                f"""
    ## Reading a store in place

    A store on S3 opens like a local one, and `xarray` reads it lazily:
    only the chunks a computation needs travel over the network. Nothing
    is copied first.

    ```python
    canopy = site.gnss_store.read_group("canopy_01", drop_empty=True)
    vod = site.vod_store.read_group("tau_omega/{ANALYSIS}", drop_empty=True)
    ```

    The canopy receiver saw {_visible} of the {canopy.sizes['sid']} signals
    of the store on this day:
    """
            ),
            canopy,
            mo.md(
                "And the VOD store, where each analysis is a group below "
                "the name of its VOD calculator:"
            ),
            vod_ds,
        ]
    )
    return


@app.cell
def _(DAY, SITE, block, cli, message, mo, session_url, settings, work):
    _config = settings(
        work / "other_settings",
        data_root=work / "notebook",
        stores=session_url,
        icechunk={"compression_level": 9},
    )
    _code, _output = cli(
        "run", "--site", SITE, "--start", DAY, "--end", DAY, "--no-vod",
        config_dir=_config,
    )
    mo.md(
        f"""
    ## Content settings: fixed for each store

    The settings that shape a store's data (which signals and
    observables are kept, the orbit products, the preprocessing, the
    compression, the chunk sizes, ...) are the store's **content
    settings**. The run that creates a store records them, and every
    later run that writes to it must have the same ones. This matters
    most on S3, where runs on other machines write to the same store.

    A second run with another compression level (exit code {_code}):

    ```text
    {block(message(_output, "The settings of this run differ"))}
    ```

    Nothing was written. Use the store's settings, or write to a new
    store.
    """
    )
    return


@app.cell
def _(
    DAY,
    SITE,
    block,
    finish_cli,
    mo,
    open_repository,
    session_url,
    settings,
    site_data,
    start_cli,
    work,
):
    import time

    _stores = f"{session_url}/two-runs"
    # Run A has the first 6 files of each receiver, run B files 3 to 10:
    # the files 3 to 6 are in both.
    _a = settings(work / "a", data_root=site_data(work / "a" / "data", slice(0, 6)), stores=_stores)
    _b = settings(work / "b", data_root=site_data(work / "b" / "data", slice(2, 10)), stores=_stores)
    _start = time.monotonic()
    _runs = [
        start_cli("run", "--site", SITE, "--start", DAY, "--end", DAY, "--no-vod", config_dir=c)
        for c in (_a, _b)
    ]
    _codes = [finish_cli(run)[0] for run in _runs]
    _seconds = time.monotonic() - _start

    _gnss = f"{_stores}/{SITE}/rinex"
    _history = list(open_repository(_gnss).ancestry(branch="main"))
    _rows = "\n".join(
        f"| {s.written_at:%H:%M:%S.%f}"[:-3] + f" | {s.message.split(' (run=')[0]} |"
        for s in reversed(_history)
    )
    from canvod.store import MyIcechunkStore

    _store = MyIcechunkStore(_gnss)
    _epochs = {
        group: _store.read_group(group, drop_empty=True)["epoch"].values
        for group in _store.list_groups()
    }
    _counts = "\n".join(
        f"| `{group}` | {len(e)} | {len(set(e))} |" for group, e in _epochs.items()
    )
    mo.md(
        f"""
    ## Two runs on one store at the same time

    On S3, several runs may write one store at the same time, for example
    one machine per receiver, or a backfill next to the daily run. Here
    two `canvodpy run` processes start together on a store that doesn't
    exist yet, each with its own files of the same day: run A the first
    6 files of each receiver, run B files 3 to 10, so 4 files are in both.
    They finished with exit codes {_codes[0]} and {_codes[1]}, in
    {_seconds:.0f} s.

    - **One creates the store, the other joins it.** Only one creation
      commit can land; the other run waits for the store's metadata and
      writes into that store, after checking its content settings.
    - **Commits rebase.** A commit made while the other run committed is
      placed on top of the other's (S3's conditional writes guarantee
      that no commit is lost), then retried if it touches the same data.
    - **No epoch twice.** A file the other run stored already is skipped.

    The store's history, oldest first:

    | Time (UTC) | Commit |
    |------------|--------|
    {block(_rows)}

    | Group | Epochs | Different epochs |
    |-------|--------|------------------|
    {block(_counts)}

    On a local folder, commits take turns instead: each holds a lock file
    in the store's folder, because Icechunk on a local file system can
    lose one of two commits made at the same moment.
    """
    )
    return


@app.cell
def _(
    DAY,
    SITE,
    block,
    finish_cli,
    message,
    mo,
    session_url,
    settings,
    site_data,
    start_cli,
    work,
):
    _stores = f"{session_url}/overlap"
    _c = settings(work / "c", data_root=site_data(work / "c" / "data", slice(0, 4)), stores=_stores)
    _data_d = site_data(work / "d" / "data", slice(0, 4))
    # Run D's canopy file of 00:15 differs from run C's: one header line
    # is changed, the observations are the same.
    _file = sorted((_data_d / "02_canopy/01_GNSS/01_raw" / DAY[2:]).iterdir())[1]
    _text = _file.resolve().read_text()
    _old = "NO FURTHER PHASE SHIFT APPLIED IN THE RINEX ENCODER."
    _file.unlink()
    _file.write_text(_text.replace(_old, "A CHANGED COPY OF THIS FILE.".ljust(len(_old))))
    _d = settings(work / "d", data_root=_data_d, stores=_stores)

    _runs = [
        start_cli("run", "--site", SITE, "--start", DAY, "--end", DAY, "--no-vod", config_dir=c)
        for c in (_c, _d)
    ]
    _results = [finish_cli(run) for run in _runs]
    _stopped = [(code, out) for code, out in _results if code != 0]
    mo.md(
        f"""
    ### A file with other content for the same epochs stops a run

    Two runs again, with the same four files of the day, except that one
    of run D's files has other content (a changed header line). Whichever
    run commits that file second finds the epochs filled by a file with
    another hash, and stops for this receiver-day instead of choosing one
    of the two (exit codes {', '.join(str(code) for code, _ in _results)}):

    ```text
    {block(message(_stopped[0][1], "Receiver 'canopy_01'")) if _stopped else 'Both runs finished: run them again.'}
    ```
    """
    )
    return


@app.cell
def _(DAY, Path, SITE, Site, block, contextlib, mo, open_repository, quiet, site):
    _notebook = Path(__file__).parent
    _in_project = (_notebook / "pyproject.toml").is_file() and (_notebook / "uv.lock").is_file()
    if _in_project:
        # A run from the notebook's folder, a uv project: its lockfile is
        # new to the store. All files are stored already, so the run
        # writes no data.
        with contextlib.chdir(_notebook), quiet(), Site(SITE).pipeline(n_workers=2) as _pipe:
            _pipe.process_date(DAY)
    _history = list(open_repository(site.gnss_store_path).ancestry(branch="main"))
    _rows = "\n".join(
        f"| `{s.id[:12]}` | {s.message.split(' (run=')[0]} |" for s in reversed(_history)
    )
    _found = (
        "The first run above started outside a uv project, so it stored no "
        "lockfile. A second run (in this cell) started in the notebook's folder, a "
        "uv project: its lockfile is new to the store, so the run stored it "
        "first, in a commit of its own, and then found every file stored."
        if any(s.message == "Store the lockfile in use" for s in _history)
        else (
            "This session runs outside a uv project, so no lockfile was "
            "stored. Run the notebook inside a clone of the demo repository "
            "(`uv run marimo edit 22_s3_stores.py`) to see the commit."
        )
    )
    mo.md(
        f"""
    ## The lockfile in its own commit

    Each commit records the software and the settings it was made with.
    When a run starts in a uv project, the store also keeps the project's
    `pyproject.toml` and `uv.lock`, so the environment can be rebuilt
    exactly. The texts are stored once for each lockfile: a run whose
    lockfile the store doesn't hold yet stores it in a commit of its own
    (`Store the lockfile in use`) before its data. That way, two runs with
    the same new lockfile don't both write it into their data commits and
    conflict.

    {_found}

    | Snapshot | Commit |
    |----------|--------|
    {block(_rows)}
    """
    )
    return


@app.cell
def _(block, cli, config_dir, mo, site, work):
    _fresh = work / "fresh_worker"
    _code, _output = cli(
        "config", "init", "--config-dir", str(_fresh),
        "--from-store", str(site.gnss_store_path), "--no-interactive",
        config_dir=config_dir,
    )
    _written = (_fresh / "canvod-settings.yaml").read_text()
    mo.md(
        f"""
    ## A fresh worker gets its settings from the store

    A store on S3 records its content settings, so another machine
    doesn't need a copy of anyone's settings file to write into it:

    ```bash
    canvodpy config init --from-store {site.gnss_store_path}
    ```

    writes a settings file with the store's content settings, the site and
    its receivers, and the stores folder taken from the URL (exit code
    {_code}). What belongs to the new machine (its data folders, logs,
    auxiliary file folders and its user) is `TODO`, for its owner to fill
    in; `canvodpy config validate` lists each one. Credentials are never
    written: the command lists the environment variables to set instead.
    The same works for a local store, to reproduce how a store you were
    given was made.

    ```yaml
    {block(_written)}
    ```
    """
    )
    return


@app.cell
def _(SITE, block, cli, config_dir, mo):
    _code, _output = cli("store", "maintain", SITE, "--execute", config_dir=config_dir)
    mo.md(
        f"""
    ## Maintenance on S3 is a dry run only

    Maintenance removes old snapshots and the data only they refer to.
    On a local folder, `canvodpy store maintain --execute` does it. On S3,
    another machine may be writing to the store at that moment, so
    canVODpy refuses `--execute`: it reports what maintenance would do,
    changes nothing, and exits with code {_code}, so a scheduled job
    notices that no maintenance was done:

    ```text
    {block(_output)}
    ```
    """
    )
    return


@app.cell
def _(block, clean, contextlib, mo, read_metadata, site):
    import io as _io

    from canvod.store_metadata import show_metadata

    _buffer = _io.StringIO()
    with contextlib.redirect_stdout(_buffer):
        show_metadata(str(site.gnss_store_path), section="identity")
    _meta = read_metadata(site.gnss_store_path)
    mo.md(
        f"""
    ## The metadata of a store on S3

    The metadata functions take an `s3://` URL like a folder, so the
    description of a shared store is read in place:

    ```python
    from canvod.store_metadata import show_metadata

    show_metadata("{site.gnss_store_path}", section="identity")
    ```

    ```text
    {block(clean(_buffer.getvalue()))}
    ```

    The settings recorded with the store keep its location:
    `processing.storage.stores_root_dir` is
    `{_meta.config.processing["storage"]["stores_root_dir"]}`.
    For a local folder of stores, a run also writes a STAC catalog of the
    stores next to them; for stores on S3 it doesn't yet.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## On S3 and in a local folder

    | | Local folder | S3 |
    |---|---|---|
    | Runs writing one store at the same time | commits take turns (lock file) | commits rebase on each other |
    | Credentials | file permissions | environment or `~/.aws` only |
    | `store maintain --execute` | runs | dry run only |
    | STAC catalog of the stores | written | not yet |
    | Run history and logs | on the machine that runs | on the machine that runs |

    The S3 service must support conditional writes (`If-Match` and
    `If-None-Match`); most do, but check before choosing one.
    """
    )
    return


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
    ---

    **Previous**: [21 · Your Own VOD Calculator](./21_plugins.py)

    *canVODpy · Apache 2.0*
    """
    )

    return


if __name__ == "__main__":
    app.run()
