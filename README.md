# Maintenance Management System (MSU)

Flask-based maintenance request and operations system for Midlands State University.

## Quick start (local)

1. Install [Python 3.10+](https://www.python.org/downloads/) (check “Add to PATH”).
2. Open a terminal in `msu_maintenance_system`.
3. Run `run_app.bat` (Windows) or `powershell -ExecutionPolicy Bypass -File scripts/start.ps1`.
4. Open [http://127.0.0.1:5000](http://127.0.0.1:5000).  
   Default SQLite demo users use password from env `MSU_DEMO_PASSWORD` (see `.env.example`); default is `ChangeMeAfterClone123!` until you change it.

## Configuration

Copy `.env.example` to `.env` and set `SECRET_KEY`, database variables, and optional `MSU_DEMO_PASSWORD`.

Details: see `msu_maintenance_system/README.md`.

## Repository

Upstream: [github.com/NigelRodrick/Maintainance-Management-MSU](https://github.com/NigelRodrick/Maintainance-Management-MSU)
