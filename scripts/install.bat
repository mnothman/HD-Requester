@echo off
setlocal

:: Set the desired Python version
set "desired_version=3.13.0"

:: Check if Python is installed and its version
for /f "tokens=2 delims= " %%i in ('py --version 2^>nul') do (
    set "installed_version=%%i"
)

:: Compare installed version with desired version
if "%installed_version%"=="" (
    echo Python is not installed. Downloading installer...
    goto :download_installer
) else (
    echo Installed version: %installed_version%
    echo Checking if it matches the desired version...
    if "%installed_version%"=="%desired_version%" (
        echo Required version of Python is installed.
        goto :install_requirements
    ) else (
        echo Installed version does not match the desired version.
        goto :download_installer
    )
)

:install_requirements
:: Install requirements from requirements.txt in the folder above
set "requirements_file=..\requirements.txt"
if exist "%requirements_file%" (
    echo Checking for installed packages from %requirements_file%...
    set "install_required=0"
    
    for /f "tokens=1 delims==" %%i in ('findstr /r /v "^#" "%requirements_file%"') do (
        if not "%%i"=="" (
            pip show %%i >nul 2>&1
            if errorlevel 1 (
                echo Package %%i is not installed.
                echo Installing missing requirements from %requirements_file%...
                pip install -r "%requirements_file%"
                goto :end
            ) else (
                echo Package %%i is already installed.
            )
        )
    )

) else (
    echo requirements.txt not found in the parent directory.
)

goto :end

:download_installer
:: Download the Python installer (update the URL to the desired version)
set "installer_url=https://www.python.org/ftp/python/%desired_version%/python-%desired_version%-amd64.exe"
set "installer_name=python-installer.exe"

:: Check if the installer already exists
if exist "%installer_name%" (
    echo Installer %installer_name% already exists. Skipping download.
) else (
    echo Downloading Python installer from %installer_url%...
    powershell -Command "try { Invoke-WebRequest -Uri '%installer_url%' -OutFile '%installer_name%' } catch { exit 1 }"
    
    :: Check if the download was successful
    if exist "%installer_name%" (
        echo Download completed successfully.
    ) else (
        echo Failed to download Python installer.
        goto :end
    )
)

echo.
echo Manual Instructions 
echo 1.   Click on python installer.
echo 2.   Click on "Use admin ..." and "Add python.exe ..." at the bottom.
echo 3.   Then click on "Install Now".
echo 4.   If prompted about making changes then click yes.
echo 5.   When prompted about "Disable path length limit", click on close on bottom.
echo.
echo Python should be installed. Use install.bat to confirm and to install all requirements.

goto :end

:end
echo.
echo install.bat has completed.
pause
endlocal