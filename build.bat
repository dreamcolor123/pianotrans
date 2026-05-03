@echo off
REM ============================================================
REM PianoTrans 全量打包脚本
REM 运行前确保:
REM   1. 项目 venv 已激活 (PyCharm Terminal 自动处理)
REM   2. pyinstaller 已安装
REM   3. 模型权重已下载到 %USERPROFILE%\piano_transcription_inference_data\
REM ============================================================

setlocal enabledelayedexpansion

echo ============================================================
echo PianoTrans Full Build
echo ============================================================

REM ---- 0. 装 PyInstaller (如果还没装) ----
python -m pip install pyinstaller --quiet

REM ---- 1. 清理旧构建 ----
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM ---- 2. 拷贝运行时 hook 到项目目录 ----
REM (pyi_rth_torch.py 和 PianoTrans.spec 应该已经在项目根目录)
echo [1/4] Running PyInstaller...
pyinstaller --noconfirm PianoTrans.spec

if errorlevel 1 (
    echo ERROR: PyInstaller failed!
    exit /b 1
)

REM ---- 3. 下载 ffmpeg ----
echo [2/4] Downloading ffmpeg...
set "FFMPEG_DIR=dist\PianoTrans\ffmpeg"
if not exist "%FFMPEG_DIR%" mkdir "%FFMPEG_DIR%"

REM 检查是否已有 ffmpeg.exe (可能在 PATH 里)
for %%X in (ffmpeg.exe) do (
    set "FFMPEG_PATH=%%~$PATH:X"
)
if defined FFMPEG_PATH (
    echo   Found ffmpeg at: !FFMPEG_PATH!
    copy /y "!FFMPEG_PATH!" "%FFMPEG_DIR%\ffmpeg.exe" >nul
) else (
    echo   Downloading ffmpeg from gyandev...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'build\ffmpeg.zip'; Expand-Archive -Path 'build\ffmpeg.zip' -DestinationPath 'build\ffmpeg_tmp'; $ffdir = Get-ChildItem 'build\ffmpeg_tmp' | Select-Object -First 1; Copy-Item \"build\ffmpeg_tmp\$ffdir\bin\ffmpeg.exe\" '%FFMPEG_DIR%\ffmpeg.exe'}"
)

if not exist "%FFMPEG_DIR%\ffmpeg.exe" (
    echo WARNING: Could not find/download ffmpeg.exe!
    echo   Audio loading may fail. Install ffmpeg and re-run this script.
)

REM ---- 4. 拷贝模型权重 ----
echo [3/4] Copying model checkpoint...
set "CKPT_DIR=dist\PianoTrans\piano_transcription_inference_data"
if not exist "%CKPT_DIR%" mkdir "%CKPT_DIR%"

set "CKPT=%USERPROFILE%\piano_transcription_inference_data\note_F1=0.9677_pedal_F1=0.9186.pth"
if exist "%CKPT%" (
    copy /y "%CKPT%" "%CKPT_DIR%\" >nul
    echo   Checkpoint copied.
) else (
    echo   WARNING: Checkpoint not found at %CKPT%
    echo   Download it manually from:
    echo   https://zenodo.org/record/4034264/files/CRNN_note_F1%%3D0.9677_pedal_F1%%3D0.9186.pth?download=1
    echo   and place it in %CKPT_DIR%
)

REM ---- 5. 拷贝启动脚本 ----
echo [4/4] Creating launcher...

(
echo @echo off
echo REM PianoTrans Launcher
echo REM 确保 PATH 包含 CUDA DLL 目录
echo cd /d "%%~dp0"
echo set "PATH=%%~dp0%%CD%%\torch\lib;%%~dp0;%%PATH%%"
echo set "PYTHONPATH=%%~dp0"
echo start "" "%%~dp0PianoTrans.exe" %%*
) > "dist\PianoTrans\PianoTrans.bat"

REM ---- 输出信息 ----
echo.
echo ============================================================
echo Build complete!
echo.
echo Output: dist\PianoTrans\
echo Size: (check with: dir /s dist\PianoTrans\)
echo.
echo To test:  dist\PianoTrans\PianoTrans.bat D:/path/to/audio.wav
echo To dist:  7z a PianoTrans.7z dist\PianoTrans\
echo ============================================================

endlocal
