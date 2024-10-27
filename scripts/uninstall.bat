@echo off
setlocal

:: Set the desired Python version
set "desired_version=3.11.7"

:: Check if a Python is installed and its version
for /f "delims=" %%i in ('python --version 2^>nul') do (
    set "installed_version=%%i"
)

:: Compare installed version with desired version
if "%installed_version%"=="" (
    echo Python is not installed. Uninstall was successful.
    goto :end
) else (
    echo Manual uninstall process beginning. Opening control pannel.
    start appwiz.cpl
    echo.
    echo Manual Insstructions
    echo 1.   Click on the installed python.
    echo 2.   When requested to make changes click yes.
    echo.
    echo Click on uninstall.bat again to confirm python has been uninstalled.
)

:end
echo.
echo uninstall.bat has completed.
pause
endlocal