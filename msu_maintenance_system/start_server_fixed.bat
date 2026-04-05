@echo off
echo Setting up environment for Windows Authentication...
set SECRET_KEY=test-key-123456789012345678901234567890
set DB_SERVER=DESKTOP-IO9GJQS\SQLEXPRESS
set DB_NAME=CentralServices_AM_DB
set DB_USER=
set DB_PASSWORD=
echo Environment variables set
echo Starting MSU Maintenance System...
python run.py
