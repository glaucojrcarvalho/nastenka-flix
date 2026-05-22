@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0update-series-metadata.ps1" %*
