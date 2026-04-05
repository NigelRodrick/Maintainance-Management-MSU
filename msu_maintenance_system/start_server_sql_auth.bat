@echo off
echo Setting up environment for SQL Server Authentication...
set SECRET_KEY=test-key-123456789012345678901234567890
set DB_SERVER=DESKTOP-IO9GJQS\SQLEXPRESS
set DB_NAME=CentralServices_AM_DB
set DB_USER=munyamash
set DB_PASSWORD=nowayout
echo Environment variables set with SQL Server authentication
echo Starting MSU Maintenance System...
python run.py
