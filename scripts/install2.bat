@echo off
:: Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process cmd -Argument '/c \"%~f0\"' -Verb RunAs"
    exit /b
)

:: Set execution policy for PowerShell
echo Installing Chocolatey...
powershell -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"

:: Wait for Chocolatey installation to complete
echo Waiting for installation to finish...
timeout /t 5 /nobreak >nul

:: Check if Chocolatey was installed successfully
choco --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Chocolatey installation failed. Please check the error messages above.
    pause
    exit /b
)

echo Chocolatey installed successfully!

:: Update Chocolatey
echo Updating Chocolatey...
choco upgrade chocolatey -y

:: Install Python (latest version)
echo Installing Python...
choco install python -y

:: Check if Python was installed successfully
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python installation failed. Please check the error messages above.
    pause
    exit /b
)

echo Python installed successfully!

:: Install pip using get-pip.py
echo Installing pip...
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

:: Check if pip was installed successfully
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Pip installation failed. Please check the error messages above.
    pause
    exit /b
)

echo Pip installed successfully!
pause