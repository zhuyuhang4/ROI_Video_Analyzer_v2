@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM =========================================================
REM ROI Video Analyzer v2.0 Build Script (Windows, Conda-friendly)
REM Entry: main.py
REM NOTE: Run this in CMD. If you're in PowerShell:
REM       cmd /c build.bat
REM =========================================================

chcp 65001 >nul

echo ============================================================
echo  ROI Video Analyzer v2.0 - Build (PyInstaller onefile)
echo  Entry: main.py
echo ============================================================
echo.

REM ====== (1) Check current conda env ======
echo [INFO] Current Conda Env: %CONDA_DEFAULT_ENV%

if defined CONDA_DEFAULT_ENV (
    echo [INFO] Conda environment already activated: %CONDA_DEFAULT_ENV%
) else (
    echo [WARN] No conda environment activated.
    echo [WARN] Continue without conda activation...
)

REM ====== (2) Verify python ======
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH. Check your environment.
    pause
    exit /b 1
)

echo [INFO] Python:
python -c "import sys; print(sys.executable)"
python --version
echo.

REM ====== (3) Check imports (install if missing) ======
call :check_import cv2 opencv-python
call :check_import PyQt5 PyQt5
call :check_import pyqtgraph pyqtgraph
call :check_import numpy numpy
call :check_import ffmpegcv ffmpegcv
call :check_import matplotlib matplotlib
call :check_import PyInstaller pyinstaller

echo.
echo [INFO] Cleaning old build artifacts...
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist "__pycache__" rd /s /q "__pycache__"
del /q *.spec 2>nul

echo.
echo [INFO] Running PyInstaller (onefile)...
echo.

python -m PyInstaller ^
    --name "ROI_Video_Analyzer_v2" ^
    --onefile ^
    --windowed ^
    --clean ^
    --noconfirm ^
    --collect-submodules ffmpegcv ^
    --collect-data ffmpegcv ^
    --collect-submodules pyqtgraph ^
    --collect-data pyqtgraph ^
    --collect-submodules matplotlib ^
    --collect-data matplotlib ^
    --hidden-import PyQt5.sip ^
    --hidden-import PyQt5.QtCore ^
    --hidden-import PyQt5.QtGui ^
    --hidden-import PyQt5.QtWidgets ^
    --hidden-import cv2 ^
    --hidden-import cv2.cv2 ^
    --hidden-import numpy ^
    --hidden-import app ^
    --hidden-import styles ^
    --hidden-import video_label ^
    --hidden-import side_panel ^
    --hidden-import threshold_widget ^
    --hidden-import export_worker ^
    --exclude-module scipy ^
    --exclude-module pandas ^
    --exclude-module tkinter ^
    main.py

if errorlevel 1 (
    echo.
    echo [ERROR] PyInstaller failed.
    echo [TIP] Try running build.py (spec onedir) for better Qt/ffmpegcv stability.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [DONE] Build finished!
echo [INFO] Output: dist\ROI_Video_Analyzer_v2.exe
echo ============================================================
echo.
pause
exit /b 0


REM =========================================================
REM Function: check import and install pip package
REM =========================================================
:check_import
set IMPORT_NAME=%1
set PIP_NAME=%2

echo [CHECK] %PIP_NAME%  (import %IMPORT_NAME%) ...
python -c "import %IMPORT_NAME%" >nul 2>&1
if errorlevel 1 (
    echo   -^> missing, installing: %PIP_NAME%
    python -m pip install %PIP_NAME% --quiet
    if errorlevel 1 (
        echo   -^> [ERROR] pip install failed: %PIP_NAME%
        exit /b 1
    ) else (
        echo   -^> [OK] installed: %PIP_NAME%
    )
) else (
    echo   -^> [OK] already installed
)
exit /b 0
