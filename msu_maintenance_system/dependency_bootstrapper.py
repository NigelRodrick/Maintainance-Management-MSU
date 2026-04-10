"""
MSU dependency bootstrapper.

Purpose:
- Check for required Python modules on the local machine.
- Install missing modules using pip.
- Launch desktop_launcher.py once dependencies are available.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path


REQUIRED_IMPORTS = [
    "dotenv",
    "flask",
    "flask_sqlalchemy",
    "flask_login",
    "flask_migrate",
    "flask_limiter",
    "flask_jwt_extended",
    "flask_wtf",
    "flask_talisman",
    "redis",
    "celery",
    "pandas",
    "pyodbc",
    "openpyxl",
    "matplotlib",
    "numpy",
    "seaborn",
    "scipy",
    "plotly",
    "pydantic",
    "email_validator",
    "sklearn",
    "joblib",
    "waitress",
]


def _repo_root() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(os.environ.get("MSU_REPO_ROOT", "")).resolve()
        if base.exists():
            return base
    return Path(__file__).resolve().parent.parent


def _requirements_file(root: Path) -> Path:
    req = root / "packaging" / "requirements-exe.txt"
    if not req.exists():
        raise FileNotFoundError(f"Missing requirements file: {req}")
    return req


def _missing_imports() -> list[str]:
    missing = []
    for mod in REQUIRED_IMPORTS:
        if importlib.util.find_spec(mod) is None:
            missing.append(mod)
    return missing


def _run(cmd: list[str]) -> None:
    print(">", " ".join(cmd), flush=True)
    subprocess.check_call(cmd)


def _install_missing(root: Path) -> None:
    missing = _missing_imports()
    if not missing:
        print("All required dependencies already installed.", flush=True)
        return

    print("Missing modules detected:", ", ".join(missing), flush=True)
    req = _requirements_file(root)
    py = sys.executable

    try:
        _run([py, "-m", "pip", "--version"])
    except Exception:
        _run([py, "-m", "ensurepip", "--upgrade"])

    _run([py, "-m", "pip", "install", "--upgrade", "pip"])
    _run([py, "-m", "pip", "install", "-r", str(req)])


def _launch_app(root: Path) -> int:
    launcher = root / "msu_maintenance_system" / "desktop_launcher.py"
    if not launcher.exists():
        raise FileNotFoundError(f"Missing launcher: {launcher}")

    env = os.environ.copy()
    env.setdefault("MSU_INSTANCE_DIR", str(root / "msu_maintenance_system" / "instance"))
    env.setdefault("MSU_REPORTS_DIR", str(root / "msu_maintenance_system" / "reports"))

    return subprocess.call([sys.executable, str(launcher)], env=env, cwd=str(root))


def main() -> int:
    try:
        root = _repo_root()
        print(f"Using project root: {root}", flush=True)
        _install_missing(root)
        return _launch_app(root)
    except Exception as exc:
        print(f"Bootstrapper failed: {exc}", flush=True)
        try:
            input("Press Enter to close...")
        except EOFError:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
