# Check if Docker Desktop service is running
$service = Get-Service -Name "com.docker.service" -ErrorAction SilentlyContinue

if ($null -eq $service) {
    Write-Host "CRITICAL: Docker Desktop Service is not installed." -ForegroundColor Red
} elseif ($service.Status -ne "Running") {
    Write-Host "WARNING: Docker Desktop Service is $($service.Status). Attempting to start..." -ForegroundColor Yellow
    Start-Service -Name "com.docker.service" -ErrorAction SilentlyContinue
} else {
    Write-Host "SUCCESS: Docker Desktop Service is running." -ForegroundColor Green
}

# Check for Docker CLI
try {
    docker version | Out-Null
    Write-Host "SUCCESS: Docker CLI is responding." -ForegroundColor Green
} catch {
    Write-Host "ERROR: Docker CLI failed. Ensure Docker Desktop is open and finished starting." -ForegroundColor Red
}

Write-Host "`nRecommendation:"
Write-Host "1. Open the 'Docker Desktop' application from your Start menu."
Write-Host "2. Wait for the whale icon in the taskbar to stop animating and turn solid green."
Write-Host "3. If using WSL 2, ensure it is enabled in Docker Desktop settings."
