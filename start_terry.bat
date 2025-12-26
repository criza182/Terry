@echo off
echo Starting Terry AI...
cd /d "%~dp0"

:: 1. Cek Lokal (Folder bin di dalam project)
if exist "%~dp0bin\ffmpeg.exe" (
    echo [INFO] Menggunakan FFmpeg lokal dari folder 'bin'.
    set "PATH=%~dp0bin;%PATH%"
    goto :Run
)

:: 2. Cek Global (Windows PATH)
where ffmpeg >nul 2>nul
if %errorlevel% equ 0 goto :Run

:: 3. Jika tidak ada keduanya, tawarkan install otomatis
echo [ERROR] FFmpeg tidak ditemukan!
echo.
echo Terry butuh FFmpeg. Saya bisa mendownloadnya untuk Anda (80MB).
echo.
set /p choice="Download FFmpeg otomatis sekarang? (Y/N): "
if /i "%choice%"=="Y" (
    powershell -ExecutionPolicy Bypass -File "%~dp0setup_ffmpeg.ps1"
    :: Cek lagi setelah install
    if exist "%~dp0bin\ffmpeg.exe" (
        set "PATH=%~dp0bin;%PATH%"
        goto :Run
    )
)

echo.
echo [GAGAL] Mohon install FFmpeg manual atau jalankan script ini lagi.
pause
exit /b

:Run

call venv\Scripts\activate
python main.py
pause
