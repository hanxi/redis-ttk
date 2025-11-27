@echo off
REM Redis-TTK Windows Build Script for GitHub Actions

echo [INFO] Starting Redis-TTK Windows build process...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    exit /b 1
)
echo [INFO] Python check passed

REM Check PDM
pdm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PDM is not installed, please run: pip install pdm
    exit /b 1
)
echo [INFO] PDM check passed

REM Clean old build files
echo [INFO] Cleaning old build files...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
echo [INFO] Build files cleaned

REM Install build dependencies
echo [INFO] Installing build dependencies...
pdm lock
if errorlevel 1 (
    echo [ERROR] PDM lock failed
    exit /b 1
)

pdm install -dG build
if errorlevel 1 (
    echo [ERROR] Build dependencies installation failed
    exit /b 1
)
echo [INFO] Build dependencies installed

REM Check spec file
echo [INFO] Checking PyInstaller spec file...
if not exist build.spec (
    echo [ERROR] build.spec file not found
    echo [INFO] Please ensure build.spec exists in project root
    exit /b 1
)
echo [INFO] Found build.spec file

REM Build application
echo [INFO] Building application...
pdm run pyinstaller build.spec --clean --noconfirm
if errorlevel 1 (
    echo [ERROR] Build failed
    exit /b 1
)
echo [INFO] Application build completed

REM Fix executable name
echo [INFO] Fixing executable name...
if exist "dist\Redis-TTK.exe" (
    if not exist "dist\redis-ttk.exe" (
        move "dist\Redis-TTK.exe" "dist\redis-ttk.exe"
        echo [INFO] Renamed Redis-TTK.exe to redis-ttk.exe
    )
) else if exist "dist\main.exe" (
    move "dist\main.exe" "dist\redis-ttk.exe"
    echo [INFO] Renamed main.exe to redis-ttk.exe
)

REM Verify executable
echo [INFO] Verifying executable...
if exist "dist\redis-ttk.exe" (
    dir "dist\redis-ttk.exe"
    echo [SUCCESS] Windows executable verified
) else (
    echo [ERROR] Executable not found for verification
    if exist dist (
        echo [INFO] Contents of dist directory:
        dir dist
    )
    exit /b 1
)

REM Show results
echo.
echo [INFO] Build Results:
if exist "dist\redis-ttk.exe" (
    echo SUCCESS: Executable created at dist\redis-ttk.exe
) else (
    echo ERROR: No executable found
    exit /b 1
)

echo.
echo [INFO] Usage:
echo 1. Double-click redis-ttk.exe to run
echo 2. Or run from command line: redis-ttk.exe

echo [SUCCESS] Build process completed successfully!
