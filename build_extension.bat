@echo off
setlocal
cd /d "%~dp0"
call local_paths.bat

if not exist "%BLENDER_EXE%" (
    echo ERROR: Blender not found at %BLENDER_EXE%
    echo Edit local_paths.bat to set BLENDER_EXE
    exit /b 1
)

echo Building Blender Extension...
"%BLENDER_EXE%" --factory-startup --background --command extension build
