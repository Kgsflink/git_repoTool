@echo off
REM -----------------------------------------------
REM Script to download git_up.exe and set environment path
REM -----------------------------------------------

REM Define variables
set "URL=https://github.com/Kgsflink/git_repoTool/raw/main/git_up.exe"
set "DEST_DIR=C:\Program Files\github"
set "DEST_FILE=%DEST_DIR%\git_up.exe"

REM Create the destination directory if it doesn't exist
if not exist "%DEST_DIR%" (
    echo Creating directory %DEST_DIR%
    mkdir "%DEST_DIR%"
) else (
    echo Directory %DEST_DIR% already exists.
)

REM Download the file using PowerShell
echo Downloading git_up.exe to %DEST_FILE%
powershell -Command "Invoke-WebRequest -Uri '%URL%' -OutFile '%DEST_FILE%'"

REM Check if the download was successful
if exist "%DEST_FILE%" (
    echo Download successful: %DEST_FILE%
) else (
    echo ERROR: Failed to download the file. Exiting script.
    pause
    exit /b 1
)

REM Add the folder to the system PATH (requires admin privileges)
echo Adding %DEST_DIR% to the system PATH
setx /M PATH "%PATH%;%DEST_DIR%"

REM Confirm the update
echo PATH has been updated. You may need to restart the command prompt for changes to take effect.

REM Verify the installation
where git_up.exe

echo Script execution complete.
pause
