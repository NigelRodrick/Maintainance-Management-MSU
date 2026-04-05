# -*- mode: python ; coding: utf-8 -*-
# From repo root: pyinstaller packaging/msu_maintenance.spec --noconfirm
import os

SPEC_DIR = os.path.dirname(os.path.abspath(SPECPATH))
ROOT = os.path.dirname(SPEC_DIR)
APP = os.path.join(ROOT, "msu_maintenance_system")

block_cipher = None

hidden = [
    "config",
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
]

a = Analysis(
    [os.path.join(APP, "desktop_launcher.py")],
    pathex=[APP],
    binaries=[],
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
