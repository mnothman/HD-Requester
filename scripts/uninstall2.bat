@echo off
:: Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process cmd -Argument '/c \"%~f0\"' -Verb RunAs"
    exit /b
)

:: Inform the user
echo Uninstalling Pip...

:: Check if pip is installed and uninstall it
where pip >nul 2>&1
if %errorlevel% equ 0 (
    echo Pip is installed. Uninstalling...
    python -m pip uninstall pip -y
    echo Pip has been uninstalled.
) else (
    echo Pip is not installed.
)

:: Inform the user
echo Uninstalling Python...

:: Check if Python is installed and uninstall it
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo Python is installed. Uninstalling...
    choco uninstall python --force
    echo Python has been uninstalled.
) else (
    echo Python is not installed.
)

:: Inform the user
echo Uninstalling Chocolatey...

:: Remove Chocolatey folder
if exist "C:\ProgramData\chocolatey" (
    rmdir /s /q "C:\ProgramData\chocolatey"
    echo Chocolatey has been uninstalled.
) else (
    echo Chocolatey is not installed.
)

:: Remove Chocolatey from the PATH
setx PATH "%PATH:C:\ProgramData\chocolatey\bin;=%" >nul

echo Chocolatey has been removed from the PATH.

:: Inform the user to restart the console
echo Please restart your command line or PowerShell session for changes to take effect.
pause