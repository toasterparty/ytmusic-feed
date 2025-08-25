@echo off

@REM net session >nul 2>&1
@REM if %errorlevel% neq 0 (
@REM     echo Need admin privileges; Restarting...
@REM     powershell -command "Start-Process '%~f0' -Verb runAs"
@REM     exit /b
@REM )
@REM echo Running as admin

set "SCRIPT_DIR=%~dp0"
set "REPO_DIR=%SCRIPT_DIR%\..\.."
set "VENV_DIR=%REPO_DIR%\.venv"
set "PY=%VENV_DIR%\Scripts\python"
set PY_VER=3.13

cd "%REPO_DIR%"

py -%PY_VER% --version >nul 2>&1
if errorlevel 1 (
    echo Python %PY_VER% is not installed. Please install it from https://www.python.org/downloads/
    exit /b 1
)

"%PY%" --version >nul 2>&1
if errorlevel 1 (
    if exist "%VENV_DIR%" (
        echo Removing existing virtual enviornment...
        rmdir /s /q "%VENV_DIR%"
    )
    echo Creating new virtual enviornment...
    py -%PY_VER% -m venv .venv
)

echo Updating packages...
"%PY%" -m pip install -qq --upgrade pip
"%PY%" -m pip install -qq -r requirements.txt

echo Running ytmusic-feed...
cd "%REPO_DIR%"
"%PY%" -m ytmusic-feed %*
