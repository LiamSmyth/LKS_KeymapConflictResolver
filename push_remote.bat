@echo off
setlocal
cd /d "%~dp0"
call local_paths.bat

set /p commit_msg="Enter commit message: "
if "%commit_msg%"=="" (
    echo Commit message cannot be empty.
    exit /b 1
)

python -m addon_tools.publish_to_github --config "%~dp0addon_config.toml" --message "%commit_msg%"
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% neq 0 (
    echo.
    echo Push FAILED.
)
pause
exit /b %EXIT_CODE%
