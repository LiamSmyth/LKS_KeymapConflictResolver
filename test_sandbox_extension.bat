@echo off
setlocal
cd /d "%~dp0"
call local_paths.bat

echo ==================================================
echo  LKS Keymap Conflict Resolver — Sandbox Extension Test
echo ==================================================

python -m addon_tools.test_sandbox --config "%~dp0addon_config.toml" %*
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% neq 0 (
    echo.
    echo Sandbox test FAILED.
)
pause
exit /b %EXIT_CODE%
