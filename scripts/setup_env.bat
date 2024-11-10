@echo off
setlocal

:: Get the directory where the batch script is located
set SCRIPT_DIR=%~dp0

@REM :: Set the certificate path variable to the project directory
@REM set CERT_PATH=%SCRIPT_DIR%\resources\tls-ca-bundle.pem

@REM :: Check if the certificate exists
@REM if not exist "%CERT_PATH%" (
@REM     echo Certificate not found at %CERT_PATH%. Please ensure the certificate is in the correct location.
@REM     exit /b 1
@REM )

:: Check if requirements.txt exists
if not exist "%SCRIPT_DIR%..\requirements.txt" (
    echo requirements.txt file not found. Please ensure it exists in the correct directory.
    exit /b 1
)

:: Check if venv exists, if not create it
if not exist "%SCRIPT_DIR%..\venv" (
    echo Creating virtual environment...
    python -m venv "%SCRIPT_DIR%..\venv"
)

:: Activate the virtual environment
echo Activating virtual environment...
call "%SCRIPT_DIR%..\venv\Scripts\activate"

:: Install dependencies using the certificate
echo Installing dependencies with certificate...
pip install --cert "%CERT_PATH%" -r "%SCRIPT_DIR%..\requirements.txt"

echo Environment setup complete!
endlocal
