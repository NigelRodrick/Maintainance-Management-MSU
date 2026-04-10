# -*- mode: python ; coding: utf-8 -*-
# From repo root: pyinstaller packaging/msu_maintenance.spec --noconfirm
import os


def _find_repo_root():
    """Resolve repo root. On GitHub Actions the clone is often one level below GITHUB_WORKSPACE
    (e.g. D:\\a\\<repo>\\<repo>\\msu_maintenance_system), so we also search subdirs and walk."""
    launcher = os.path.join("msu_maintenance_system", "desktop_launcher.py")

    def has_app(root):
        return os.path.isfile(os.path.join(root, launcher))

    ws = os.environ.get("GITHUB_WORKSPACE", "").strip()
    if ws:
        ws = os.path.abspath(ws)
        if has_app(ws):
            return ws
        try:
            for name in sorted(os.listdir(ws)):
                sub = os.path.join(ws, name)
                if os.path.isdir(sub) and has_app(sub):
                    return sub
        except OSError:
            pass
        # Odd layouts: bounded search under workspace
        max_depth = 6
        for dirpath, dirnames, filenames in os.walk(ws):
            rel = os.path.relpath(dirpath, ws)
            depth = 0 if rel == "." else rel.count(os.sep) + 1
            if depth > max_depth:
                dirnames[:] = []
                continue
            if (
                "desktop_launcher.py" in filenames
                and os.path.basename(dirpath) == "msu_maintenance_system"
            ):
                return os.path.dirname(dirpath)

    d = os.path.dirname(os.path.abspath(SPECPATH))
    for _ in range(12):
        if has_app(d):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    raise RuntimeError(
        "Cannot find msu_maintenance_system/desktop_launcher.py; "
        "set GITHUB_WORKSPACE to the repo root or run pyinstaller from a normal checkout."
    )


ROOT = _find_repo_root()
APP = os.path.join(ROOT, "msu_maintenance_system")

block_cipher = None

hidden = [
    "config",
    "env_bootstrap",
    "dotenv",
    "pyodbc",
    "sqlalchemy.dialects.mssql",
    "sqlalchemy.dialects.mssql.pyodbc",
    "sqlalchemy.dialects.mssql.base",
    "waitress",
    "engineio",
    "kombu",
    "billiard",
    "vine",
    "celery.fixups",
    "celery.loaders",
    "celery.app",
    "redis",
    "limits",
    "flask_limiter",
    "email_validator",
    "pydantic",
    "jwt",
    "openpyxl",
    "sklearn",
    "sklearn.utils._cython_blas",
    "sklearn.neighbors._typedefs",
    "sklearn.utils._heap",
    "sklearn.utils._sorting",
    "sklearn.utils._vector_sentinel",
]

try:
    from PyInstaller.utils.hooks import collect_submodules

    hidden += collect_submodules("app")
except Exception:
    pass

datas = [
    (os.path.join(APP, "templates"), "templates"),
    (os.path.join(APP, "static"), "static"),
    # Shipped inside the EXE: copy to %LOCALAPPDATA%\MSUMaintenance\.env for SQL Server.
    (os.path.join(ROOT, "packaging", "sql_connection.env.example"), "packaging"),
]

binaries = []
try:
    from PyInstaller.utils.hooks import collect_all

    _pyodbc_d, _pyodbc_b, _pyodbc_h = collect_all("pyodbc")
    datas += _pyodbc_d
    binaries += _pyodbc_b
    hidden += _pyodbc_h
except Exception:
    pass

a = Analysis(
    [os.path.join(APP, "desktop_launcher.py")],
    pathex=[APP],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "playwright", "jupyter"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="MSU_Maintenance",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
