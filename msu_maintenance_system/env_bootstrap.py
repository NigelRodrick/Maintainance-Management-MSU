"""
Load .env files before config reads os.environ (SQLite vs SQL Server, secrets).

Order:
  1. msu_maintenance_system/.env
  2. repository root .env (parent directory)
  3. %LOCALAPPDATA%\\MSUMaintenance\\.env (override — packaged/desktop overrides)
"""
from __future__ import annotations

import os
from pathlib import Path


def load_msu_environment() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    here = Path(__file__).resolve().parent
    repo_root = here.parent
    candidates = [
        (here / ".env", False),
        (repo_root / ".env", False),
    ]
    local = os.environ.get("LOCALAPPDATA", "").strip()
    if local:
        candidates.append((Path(local) / "MSUMaintenance" / ".env", True))

    for path, override in candidates:
        if path.is_file():
            load_dotenv(path, override=override)
