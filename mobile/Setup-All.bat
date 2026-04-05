@echo off
cd /d "%~dp0"
echo MSU Maintenance mobile - automated setup
node scripts\setup.cjs
if errorlevel 1 pause
