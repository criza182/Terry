$ErrorActionPreference = "Stop"

Write-Host "Downloading FFmpeg (approx. 80MB)..." -ForegroundColor Cyan
$url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$zipFile = "ffmpeg.zip"
$extractPath = "ffmpeg_temp"

# 1. Download
Invoke-WebRequest -Uri $url -OutFile $zipFile

# 2. Extract
Write-Host "Extracting..." -ForegroundColor Cyan
Expand-Archive -Path $zipFile -DestinationPath $extractPath -Force

# 3. Locate bin folder
$binSource = Get-ChildItem -Path $extractPath -Recurse -Filter "bin" -Directory | Select-Object -First 1

if ($binSource) {
    Write-Host "Setting up..." -ForegroundColor Cyan
    # Create local bin directory if not exists
    if (!(Test-Path "bin")) { New-Item -ItemType Directory -Path "bin" | Out-Null }
    
    # Move exe files to root/bin
    Copy-Item -Path "$($binSource.FullName)\*.exe" -Destination "bin" -Force
    
    Write-Host "FFmpeg installed successfully to folder 'bin'!" -ForegroundColor Green
} else {
    Write-Host "Failed to find bin folder in archive." -ForegroundColor Red
}

# 4. Cleanup
Write-Host "Cleaning up..."
Remove-Item -Path $zipFile -Force
Remove-Item -Path $extractPath -Recurse -Force

Write-Host "Done! You can now run start_terry.bat" -ForegroundColor Green
Start-Sleep -Seconds 3
