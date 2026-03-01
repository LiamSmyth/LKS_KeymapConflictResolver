@echo off
setlocal
cd /d "%~dp0"
call local_paths.bat

echo Setting up junctions for LKS Keymap Conflict Resolver (Dev)...

python -m addon_tools.setup_junctions --config "%~dp0addon_config.toml"
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% neq 0 (
    echo.
    echo Junction setup had errors.
)
pause
exit /b %EXIT_CODE%
