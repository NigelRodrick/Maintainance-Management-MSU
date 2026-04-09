# -*- mode: python ; coding: utf-8 -*-
# From repo root: pyinstaller packaging/msu_dependency_bootstrap.spec --noconfirm
import os


def _find_repo_root():
    launcher = os.path.join("msu_maintenance_system", "dependency_bootstrapper.py")
    d = os.path.dirname(os.path.abspath(SPECPATH))
    for _ in range(12):
        if os.path.isfile(os.path.join(d, launcher)):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    raise RuntimeError("Cannot find msu_maintenance_system/dependency_bootstrapper.py")


ROOT = _find_repo_root()
APP = os.path.join(ROOT, "msu_maintenance_system")

a = Analysis(
    [os.path.join(APP, "dependency_bootstrapper.py")],
    pathex=[APP],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "playwright", "jupyter"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="MSU_Dependency_Bootstrapper",
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
