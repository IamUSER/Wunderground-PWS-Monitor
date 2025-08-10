@echo off
TITLE Enhanced Weather Monitor CLI

:: This command calls the python interpreter and tells it to run the script.
:: %~dp0 automatically expands to the folder path of THIS batch file.
:: The full path to the script is constructed by combining %~dp0 and the script's name.
python "%~dp0weather_monitor_enhanced.py" "[STATION-ID]"