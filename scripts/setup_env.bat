@echo off
setlocal

:: Get the directory where the batch script is located
set "SCRIPT_DIR=%~dp0"

@REM Set the certificate path variable to the project directory (uncomment if needed)
@REM set "CERT_PATH=%SCRIPT_DIR%resources\tls-ca-bundle.pem"

:: Check for 'UI' argument to select the appropriate requirements file
set "REQUIREMENTS_FILE=requirements.txt"
if /I "%1"=="UI" (
    set "REQUIREMENTS_FILE=requirements_UI.txt"
)

:: Verify that the chosen requirements file exists
if not exist "%SCRIPT_DIR%..\%REQUIREMENTS_FILE%" (
    echo %REQUIREMENTS_FILE% not found. Please ensure it exists in the correct directory.
    exit /b 1
)

:: Check if virtual environment exists, if not create it
if not exist "%SCRIPT_DIR%..\venv" (
    echo Creating virtual environment...
    python -m venv "%SCRIPT_DIR%..\venv"
)

:: Activate the virtual environment
echo Activating virtual environment...
call "%SCRIPT_DIR%..\venv\Scripts\activate"

:: Install dependencies, with certificate if CERT_PATH is defined
echo Installing dependencies from %REQUIREMENTS_FILE%...
if defined CERT_PATH (
    echo Using certificate at %CERT_PATH%
    pip install --cert "%CERT_PATH%" -r "%SCRIPT_DIR%..\%REQUIREMENTS_FILE%"
) else (
    pip install -r "%SCRIPT_DIR%..\%REQUIREMENTS_FILE%"
)

if errorlevel 1 (
    echo Failed to install dependencies. Please check the certificate or internet connection.
    exit /b 1
)

echo Environment setup complete!
endlocal
