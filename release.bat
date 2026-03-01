@echo off
setlocal
cd /d "%~dp0"
call local_paths.bat

echo ==================================================
echo  LKS Keymap Conflict Resolver (Dev) — Release Workflow
echo ==================================================

python -m addon_tools.release --config "%~dp0addon_config.toml"
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% neq 0 (
    echo.
    echo Release FAILED.
)
pause
exit /b %EXIT_CODE%
