@echo off
setlocal
cd /d "%~dp0"
call local_paths.bat
set SCRIPT=%~dp0tests\blender_test_runner.py

if not exist "%BLENDER_EXE%" (
    echo ERROR: Blender not found at %BLENDER_EXE%
    echo Edit local_paths.bat to set BLENDER_EXE
    pause
    exit /b 1
)

echo ==================================================
echo  LKS Keymap Conflict Resolver — Headless Test Suite
echo  Blender: %BLENDER_EXE%
echo ==================================================

set BLENDER_USER_SCRIPTS=%BLENDER_USER_SCRIPTS%
"%BLENDER_EXE%" --background --factory-startup --addons lks_keymap_conflict_resolver --python "%SCRIPT%"
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% neq 0 (
    echo.
    echo Headless tests FAILED.
)
pause
exit /b %EXIT_CODE%
