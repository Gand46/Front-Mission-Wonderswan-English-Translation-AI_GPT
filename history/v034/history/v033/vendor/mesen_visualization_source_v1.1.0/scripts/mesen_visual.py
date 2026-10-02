#!/usr/bin/env python3
"""Prepare, probe, capture and launch Mesen 2.1.1 reproducibly on Linux."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LUA = ROOT / "templates" / "capture_preview.lua"
MINIMAL_SETTINGS = ROOT / "config" / "settings.json"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class MesenError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_file(value: str | Path, label: str, executable: bool = False) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise MesenError(f"{label} not found: {path}")
    if executable and not os.access(path, os.X_OK):
        raise MesenError(f"{label} is not executable: {path}")
    return path


def ensure_profile(mesen: Path, create: bool = False) -> Path:
    profile = mesen.parent / "settings.json"
    if profile.is_file():
        try:
            parsed = json.loads(profile.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise MesenError(f"invalid portable profile {profile}: {exc}") from exc
        if not isinstance(parsed, dict):
            raise MesenError(f"portable profile must contain a JSON object: {profile}")
        return profile
    if not create:
        raise MesenError(
            f"portable profile missing: {profile}; run prepare_mesen.sh or add {{}}"
        )
    try:
        shutil.copyfile(MINIMAL_SETTINGS, profile)
    except OSError as exc:
        raise MesenError(f"could not create portable profile {profile}: {exc}") from exc
    return profile


def png_geometry(path: Path) -> tuple[int, int]:
    """Decode the complete PNG so a truncated header can never pass QA."""
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError as exc:
        raise MesenError("Pillow is required to validate Mesen PNG captures") from exc
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            image.load()
            return image.size
    except (OSError, ValueError, UnidentifiedImageError) as exc:
        raise MesenError(f"invalid or truncated PNG produced by Mesen: {path}: {exc}") from exc


def normalize_wonderswan(path: Path) -> tuple[Path | None, tuple[int, int]]:
    geometry = png_geometry(path)
    width, height = geometry
    if (width, height) == (224, 144):
        return None, geometry
    if (width, height) != (237, 144):
        raise MesenError(
            "cannot safely normalize WonderSwan capture with geometry "
            f"{width}x{height}; expected 224x144 or the verified 237x144 layout"
        )
    try:
        from PIL import Image
    except ImportError as exc:
        raise MesenError(
            "Pillow is required to normalize a WonderSwan capture; "
            "install requirements.txt or omit --normalize-wonderswan"
        ) from exc
    raw = path.with_name(path.stem + ".raw" + path.suffix)
    if raw.exists():
        raise MesenError(f"refusing to overwrite existing raw capture: {raw}")
    path.replace(raw)
    with Image.open(raw) as image:
        image.crop((0, 0, 224, 144)).convert("RGB").save(path)
    if png_geometry(path) != (224, 144):
        raise MesenError("normalized WonderSwan capture is not 224x144")
    return raw, geometry


def system_libstdcpp() -> Path | None:
    compiler = shutil.which("g++")
    if compiler is None:
        return None
    try:
        result = subprocess.run(
            [compiler, "-print-file-name=libstdc++.so.6"],
            text=True, capture_output=True, timeout=5, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    candidate = Path(result.stdout.strip()).resolve()
    return candidate if result.returncode == 0 and candidate.is_file() else None


def runtime_environment() -> dict[str, str]:
    environment = os.environ.copy()
    library = system_libstdcpp()
    if library is not None:
        values = [str(library)]
        if environment.get("LD_PRELOAD"):
            values.append(environment["LD_PRELOAD"])
        environment["LD_PRELOAD"] = ":".join(values)
    return environment


def prepare(args: argparse.Namespace) -> int:
    archive = resolve_file(args.zip, "Mesen ZIP")
    destination = Path(args.dest).expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    mesen = destination / "Mesen"
    if mesen.exists() and not args.reuse:
        raise MesenError(
            f"destination already contains Mesen: {mesen}; use --reuse to keep it"
        )
    if not mesen.exists():
        with zipfile.ZipFile(archive) as source:
            candidates = [name for name in source.namelist() if Path(name).name == "Mesen"]
            if len(candidates) != 1:
                raise MesenError("Mesen ZIP must contain exactly one file named Mesen")
            info = source.getinfo(candidates[0])
            if info.is_dir():
                raise MesenError("Mesen entry in ZIP is a directory")
            with source.open(info) as input_stream, mesen.open("xb") as output_stream:
                shutil.copyfileobj(input_stream, output_stream)
    mesen.chmod(mesen.stat().st_mode | 0o755)
    profile = ensure_profile(mesen, create=True)
    result = {
        "status": "ready",
        "mesen": str(mesen),
        "mesen_sha256": sha256(mesen),
        "profile": str(profile),
        "profile_sha256": sha256(profile),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def unix_socket_supported() -> tuple[bool, str | None]:
    temporary_root = os.environ.get("MESEN_TEMP_DIR")
    try:
        context = tempfile.TemporaryDirectory(
            prefix="mesen-socket-probe-", dir=temporary_root
        )
    except OSError as exc:
        return False, f"temporary directory unavailable: {exc}"
    with context as temporary:
        path = str(Path(temporary) / "socket")
        probe = None
        try:
            probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            probe.bind(path)
        except OSError as exc:
            return False, f"{exc.__class__.__name__}: {exc}"
        finally:
            if probe is not None:
                probe.close()
    return True, None


def display_usable(environment: dict[str, str]) -> tuple[bool, str]:
    display = environment.get("DISPLAY")
    if not display:
        return False, "DISPLAY is not set"
    xdpyinfo = shutil.which("xdpyinfo")
    if xdpyinfo is not None:
        try:
            result = subprocess.run(
                [xdpyinfo], env=environment, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, timeout=5, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return False, f"xdpyinfo failed: {exc}"
        return result.returncode == 0, f"xdpyinfo exit={result.returncode}"
    return False, "DISPLAY is set but cannot be verified because xdpyinfo is unavailable"


def executable_format(path: Path) -> tuple[bool, str]:
    if not path.is_file():
        return False, "file is missing"
    if not os.access(path, os.X_OK):
        return False, "execute permission is missing"
    try:
        with path.open("rb") as stream:
            magic = stream.read(5)
    except OSError as exc:
        return False, str(exc)
    if magic[:4] != b"\x7fELF":
        return False, "not an ELF executable"
    if len(magic) < 5 or magic[4] != 2:
        return False, "not a 64-bit ELF executable"
    return True, "64-bit ELF executable"


def run_process(command: list[str], cwd: Path, environment: dict[str, str],
                timeout: int) -> tuple[subprocess.CompletedProcess[str], bool]:
    """Run a process in its own session and terminate every descendant on timeout."""
    try:
        process = subprocess.Popen(
            command, cwd=cwd, env=environment, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
        )
    except OSError as exc:
        raise MesenError(f"could not start process: {exc}") from exc
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        return subprocess.CompletedProcess(command, process.returncode, stdout, stderr), False
    except subprocess.TimeoutExpired as exc:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, stderr = process.communicate()
        partial_stdout = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        partial_stderr = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        # communicate() may return the complete buffered content; avoid duplicating it.
        if partial_stdout and partial_stdout not in stdout:
            stdout = partial_stdout + stdout
        if partial_stderr and partial_stderr not in stderr:
            stderr = partial_stderr + stderr
        return subprocess.CompletedProcess(command, 124, stdout, stderr), True


def probe(args: argparse.Namespace) -> int:
    if args.timeout < 1:
        raise MesenError("--timeout must be a positive integer")
    mesen = Path(args.mesen).expanduser().resolve()
    profile = mesen.parent / "settings.json"
    profile_valid = False
    profile_error = None
    if profile.is_file():
        try:
            profile_valid = isinstance(json.loads(profile.read_text(encoding="utf-8")), dict)
            if not profile_valid:
                profile_error = "settings.json is not a JSON object"
        except (OSError, json.JSONDecodeError) as exc:
            profile_error = str(exc)
    binary_ok, binary_detail = executable_format(mesen)
    if args.create_profile and binary_ok and not profile.is_file():
        try:
            profile = ensure_profile(mesen, create=True)
            profile_valid = True
            profile_error = None
        except MesenError as exc:
            profile_error = str(exc)
    socket_ok, socket_error = unix_socket_supported()
    display_ok, display_detail = display_usable(os.environ.copy())
    prerequisites_ready = binary_ok and profile_valid
    active_test = None
    active_exit = None
    active_log = None
    if args.rom and prerequisites_ready:
        rom = resolve_file(args.rom, "ROM")
        probe_lua = ROOT / "templates" / "probe_test_runner.lua"
        command = [
            str(mesen), "--testRunner", f"--timeout={args.timeout}",
            "--enableStdout", "--doNotSaveSettings", str(probe_lua), str(rom),
        ]
        completed, supervisor_timeout = run_process(
            command, mesen.parent, runtime_environment(), args.timeout + 5
        )
        active_exit = completed.returncode
        active_log = (completed.stdout or "") + (completed.stderr or "")
        active_test = completed.returncode == 0 and not supervisor_timeout
    result = {
        "mesen": str(mesen),
        "mesen_exists": mesen.is_file(),
        "mesen_executable": mesen.is_file() and os.access(mesen, os.X_OK),
        "mesen_binary_format_valid": binary_ok,
        "mesen_binary_format_detail": binary_detail,
        "portable_profile": str(profile),
        "portable_profile_exists": profile.is_file(),
        "portable_profile_valid": profile_valid,
        "portable_profile_error": profile_error,
        "test_runner_prerequisites_ready": prerequisites_ready,
        "test_runner_ready_without_display": active_test,
        "active_probe_performed": args.rom is not None and prerequisites_ready,
        "active_probe_exit": active_exit,
        "active_probe_log": active_log,
        "display": os.environ.get("DISPLAY"),
        "display_usable": display_ok,
        "display_detail": display_detail,
        "xvfb_available": shutil.which("Xvfb") is not None,
        "unix_socket_supported": socket_ok,
        "unix_socket_error": socket_error,
        "gui_possible": display_ok or (shutil.which("Xvfb") is not None and socket_ok),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.rom:
        return 0 if active_test else 2
    return 0 if prerequisites_ready else 2


def capture(args: argparse.Namespace) -> int:
    mesen = resolve_file(args.mesen, "Mesen", executable=True)
    binary_ok, binary_detail = executable_format(mesen)
    if not binary_ok:
        raise MesenError(f"invalid Mesen executable: {binary_detail}")
    profile = ensure_profile(mesen, create=True)
    rom = resolve_file(args.rom, "ROM")
    lua = resolve_file(args.lua or DEFAULT_LUA, "Lua script")
    output = Path(args.output).expanduser().resolve()
    if args.frame < 1 or args.timeout < 1 or args.timeout_grace < 1:
        raise MesenError("--frame, --timeout and --timeout-grace must be positive integers")
    output.parent.mkdir(parents=True, exist_ok=True)
    report_path = output.with_suffix(".json")
    log_path = output.with_suffix(".log")
    lua_report = output.with_name(output.stem + ".lua.json")
    raw_candidate = output.with_name(output.stem + ".raw" + output.suffix)
    inputs = {mesen, profile, rom, lua}
    targets = (output, raw_candidate, report_path, log_path, lua_report)
    if len(set(targets)) != len(targets):
        raise MesenError("capture output names collide with each other")
    collisions = inputs.intersection(targets)
    if collisions:
        raise MesenError(
            "capture outputs must not overwrite inputs: "
            + ", ".join(str(path) for path in sorted(collisions))
        )
    for target in targets:
        if target.exists():
            if not args.overwrite:
                raise MesenError(f"refusing to overwrite existing file: {target}")
            if not target.is_file():
                raise MesenError(f"refusing to replace non-file output: {target}")
            target.unlink()
    environment = runtime_environment()
    environment.update({
        "MESEN_CAPTURE_PATH": str(output),
        "MESEN_LUA_REPORT": str(lua_report),
        "MESEN_CAPTURE_FRAME": str(args.frame),
    })
    command = [
        str(mesen),
        "--testRunner",
        f"--timeout={args.timeout}",
        "--enableStdout",
        "--doNotSaveSettings",
        "--debug.scriptWindow.allowIoOsAccess=true",
        str(lua),
        str(rom),
    ]
    started = time.monotonic()
    result, supervisor_timed_out = run_process(
        command, mesen.parent, environment, args.timeout + args.timeout_grace
    )
    log_path.write_text((result.stdout or "") + (result.stderr or ""), encoding="utf-8")
    capture_exists = output.is_file()
    raw_path = None
    source_geometry = None
    capture_geometry = None
    validation_error = None
    if capture_exists:
        try:
            if args.normalize_wonderswan:
                raw_path, source_geometry = normalize_wonderswan(output)
            else:
                source_geometry = png_geometry(output)
            capture_geometry = png_geometry(output)
        except MesenError as exc:
            validation_error = str(exc)
    elif supervisor_timed_out:
        validation_error = "capture was not produced before the Python supervisor timeout"
    elif result.returncode == 255:
        validation_error = "capture was not produced before the likely internal Mesen timeout"
    else:
        validation_error = "capture was not produced"
    mesen_timeout_likely = (
        result.returncode == 255 and not capture_exists and not supervisor_timed_out
    )
    passed = result.returncode == 0 and capture_exists and validation_error is None
    report = {
        "schema": 1,
        "generated_at_utc": utc_now(),
        "mode": "testRunner framebuffer capture",
        "passed": passed,
        "timed_out": supervisor_timed_out or mesen_timeout_likely,
        "timeout_source": (
            "python_supervisor" if supervisor_timed_out else
            "mesen_internal_likely" if mesen_timeout_likely else None
        ),
        "process_exit": result.returncode,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "mesen": str(mesen),
        "mesen_sha256": sha256(mesen),
        "profile": str(profile),
        "profile_sha256": sha256(profile),
        "rom": str(rom),
        "rom_sha256": sha256(rom),
        "lua": str(lua),
        "lua_sha256": sha256(lua),
        "capture": str(output),
        "capture_exists": capture_exists,
        "capture_sha256": sha256(output) if capture_exists and validation_error is None else None,
        "capture_geometry": list(capture_geometry) if capture_geometry else None,
        "source_geometry": list(source_geometry) if source_geometry else None,
        "raw_capture": str(raw_path) if raw_path else None,
        "raw_capture_sha256": sha256(raw_path) if raw_path else None,
        "lua_report": str(lua_report) if lua_report.is_file() else None,
        "log": str(log_path),
        "validation_error": validation_error,
        "command": command,
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if passed else 2


def choose_x_display() -> int:
    for number in range(90, 120):
        if not Path(f"/tmp/.X11-unix/X{number}").exists():
            return number
    raise MesenError("no free X display found in range :90-:119")


def start_xvfb(environment: dict[str, str]) -> tuple[subprocess.Popen[bytes], str]:
    xvfb = shutil.which("Xvfb")
    if xvfb is None:
        raise MesenError("Xvfb is not installed")
    socket_ok, socket_error = unix_socket_supported()
    if not socket_ok:
        raise MesenError(f"environment blocks Unix sockets required by Xvfb: {socket_error}")
    number = choose_x_display()
    display = f":{number}"
    process = subprocess.Popen(
        [xvfb, display, "-screen", "0", "1280x720x24", "-nolisten", "tcp"],
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    socket_path = Path(f"/tmp/.X11-unix/X{number}")
    for _ in range(50):
        if process.poll() is not None:
            stderr = (process.stderr.read() if process.stderr else b"").decode("utf-8", "replace")
            raise MesenError(f"Xvfb stopped before becoming ready: {stderr.strip()}")
        if socket_path.exists():
            return process, display
        time.sleep(0.1)
    process.terminate()
    raise MesenError("Xvfb did not create its X11 socket within 5 seconds")


def gui(args: argparse.Namespace) -> int:
    mesen = resolve_file(args.mesen, "Mesen", executable=True)
    binary_ok, binary_detail = executable_format(mesen)
    if not binary_ok:
        raise MesenError(f"invalid Mesen executable: {binary_detail}")
    ensure_profile(mesen, create=True)
    rom = resolve_file(args.rom, "ROM")
    lua = resolve_file(args.lua, "Lua script") if args.lua else None
    environment = runtime_environment()
    xvfb_process = None
    usable, detail = display_usable(environment)
    if args.xvfb == "always" or (args.xvfb == "auto" and not usable):
        xvfb_process, display = start_xvfb(environment)
        environment["DISPLAY"] = display
    elif not usable:
        raise MesenError(f"GUI requires a usable DISPLAY: {detail}")
    command = [str(mesen)]
    if lua is not None:
        command.extend(["--debug.scriptWindow.allowIoOsAccess=true", str(lua)])
    command.append(str(rom))
    try:
        if args.timeout:
            result, timed_out = run_process(
                command, mesen.parent, environment, args.timeout
            )
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)
            if timed_out:
                print("error: GUI timeout reached", file=sys.stderr)
                return 124
            return result.returncode
        result = subprocess.run(command, cwd=mesen.parent, env=environment, check=False)
        return result.returncode
    finally:
        if xvfb_process is not None:
            xvfb_process.send_signal(signal.SIGTERM)
            try:
                xvfb_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                xvfb_process.kill()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare", help="extract Mesen and create a portable profile")
    prepare_parser.add_argument("--zip", required=True)
    prepare_parser.add_argument("--dest", required=True)
    prepare_parser.add_argument("--reuse", action="store_true")
    prepare_parser.set_defaults(function=prepare)

    probe_parser = subparsers.add_parser("probe", help="diagnose capture and GUI readiness")
    probe_parser.add_argument("--mesen", required=True)
    probe_parser.add_argument("--rom", help="run an active headless test with this ROM")
    probe_parser.add_argument("--timeout", type=int, default=5)
    probe_parser.add_argument("--create-profile", action="store_true")
    probe_parser.set_defaults(function=probe)

    capture_parser = subparsers.add_parser("capture", help="capture a framebuffer through testRunner")
    capture_parser.add_argument("--mesen", required=True)
    capture_parser.add_argument("--rom", required=True)
    capture_parser.add_argument("--lua")
    capture_parser.add_argument("--output", required=True)
    capture_parser.add_argument("--frame", type=int, default=180)
    capture_parser.add_argument("--timeout", type=int, default=30)
    capture_parser.add_argument("--timeout-grace", type=int, default=5)
    capture_parser.add_argument("--normalize-wonderswan", action="store_true")
    capture_parser.add_argument("--overwrite", action="store_true")
    capture_parser.set_defaults(function=capture)

    gui_parser = subparsers.add_parser("gui", help="open Mesen using DISPLAY or Xvfb")
    gui_parser.add_argument("--mesen", required=True)
    gui_parser.add_argument("--rom", required=True)
    gui_parser.add_argument("--lua")
    gui_parser.add_argument("--xvfb", choices=("auto", "always", "never"), default="auto")
    gui_parser.add_argument("--create-profile", action="store_true", help=argparse.SUPPRESS)
    gui_parser.add_argument("--timeout", type=int, default=0,
                            help="stop GUI after N seconds; 0 waits until it closes")
    gui_parser.set_defaults(function=gui)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.function(args))
    except MesenError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
