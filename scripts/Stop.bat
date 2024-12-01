@echo off
echo Stopping app.py...

:: Find and terminate the Python process running app.py
for /f "tokens=2 delims=," %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV /NH') do (
    for /f "tokens=*" %%j in ('wmic process where "ProcessId=%%i and CommandLine like '%%app.py%%'" get ProcessId /value 2^>nul') do (
        set PID=%%i
        taskkill /PID %%i /F
        echo Stopped app.py process with PID %%i.
    )
)

:: Confirmation or fallback
if not defined PID (
    echo No running app.py process found.
) else (
    echo app.py process stopped successfully.
)

pause
