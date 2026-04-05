# Maintenance Management System (MSU)

Flask-based maintenance request and operations system for Midlands State University.

## Quick start (local)

1. Install [Python 3.10+](https://www.python.org/downloads/) (check “Add to PATH”).
2. Open a terminal in `msu_maintenance_system`.
3. Run `run_app.bat` (Windows) or `powershell -ExecutionPolicy Bypass -File scripts/start.ps1`.
4. Open [http://127.0.0.1:5000](http://127.0.0.1:5000).  
   Default SQLite demo users use password from env `MSU_DEMO_PASSWORD` (see `.env.example`); default is `ChangeMeAfterClone123!` until you change it.

## Windows installer (MSI)

1. Install [WiX Toolset v3](https://github.com/wixtoolset/wix3/releases) (sets `%WIX%`, or install under `Program Files (x86)\WiX Toolset v3.14`).
2. From the repo root, run:

```powershell
powershell -ExecutionPolicy Bypass -File installer\build_msi.ps1 -Version 1.0.0
```

3. Output: `installer\dist\MSU_Maintenance_System_<version>.msi`.

The MSI installs the app under **Program Files** and adds a Start Menu shortcut. **Python 3.10+ (64-bit)** must still be installed on the PC. The first run creates a virtual environment and SQLite data under `%LOCALAPPDATA%\MSUMaintenance` (writable location for non-admin users).

## Full setup EXE (Python + MSI)

To ship **one installer** that installs the official **Python 3.12 x64** runtime when it is not already registered (per-machine `HKLM\SOFTWARE\Python\PythonCore\3.12\InstallPath`), then installs the MSI:

```powershell
powershell -ExecutionPolicy Bypass -File installer\build_bundle.ps1 -Version 1.0.0
```

- Downloads the Python installer to `installer\cache\` on first build (re-used after that).
- Output: `installer\dist\MSU_Maintenance_System_Setup_<version>.exe`.

If Python 3.12 is already installed for all users, the bundle **skips** the Python step and only runs the MSI. Users who rely only on the Microsoft Store Python or a non-standard layout may still get the bundled Python installer; that is usually harmless.

## Mobile apps (Android + iOS)

A **Capacitor** WebView shell lives in **`mobile/`**: set **`server.url`** in `mobile/capacitor.config.json` to your **HTTPS** site.

- **One-click setup:** `cd mobile` → `npm run setup` (or `Setup-All.bat` on Windows).
- **CI:** GitHub Actions build a **debug APK** and verify **iOS** project generation — see workflows `mobile-android.yml` and `mobile-ios.yml`.

Full steps: **`mobile/README.md`**.

## Configuration

Copy `.env.example` to `.env` and set `SECRET_KEY`, database variables, and optional `MSU_DEMO_PASSWORD`.

Details: see `msu_maintenance_system/README.md`.

## Repository

Upstream: [github.com/NigelRodrick/Maintainance-Management-MSU](https://github.com/NigelRodrick/Maintainance-Management-MSU)
