@echo off

@REM :: Set the certificate path variable in AppData
@REM set CERT_PATH=%AppData%\my_cert.pem

@REM :: Check if the certificate exists
@REM if not exist "%CERT_PATH%" (
@REM     echo Certificate not found at %CERT_PATH%. Please ensure the certificate is in the correct location.
@REM     exit /b 1
@REM )

:: Check if requirements.txt exists
if not exist "requirements.txt" (
    echo requirements.txt file not found. Please ensure it exists in the current directory.
    exit /b 1
)

:: Check if venv exists, if not create it
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

:: Install dependencies using the certificate
echo Installing dependencies with certificate...
pip install --cert "%CERT_PATH%" -r requirements.txt

echo Environment setup complete!
