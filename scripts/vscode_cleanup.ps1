# VS Code 工作空间清理脚本
# 用于解决 VS Code 文件删除后重启恢复的问题

param(
    [string]$WorkspacePath = (Get-Location).Path
)

Write-Host "开始清理 VS Code 工作空间缓存和临时文件..." -ForegroundColor Green

# 1. 清理 VS Code 工作空间状态缓存
$userDataDir = "$env:APPDATA\Code\User\workspaceStorage"
if (Test-Path $userDataDir) {
    Write-Host "清理工作空间存储缓存..." -ForegroundColor Yellow
    $workspaceHash = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($WorkspacePath)).Replace("/", "_").Replace("+", "-")
    $workspaceCacheDir = Get-ChildItem $userDataDir | Where-Object { $_.Name -like "*$workspaceHash*" }
    if ($workspaceCacheDir) {
        $workspaceCacheDir | ForEach-Object {
            Write-Host "删除缓存目录: $($_.FullName)" -ForegroundColor Cyan
            Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

# 2. 清理最近文件记录
$recentFilesPath = "$env:APPDATA\Code\User\globalStorage\storage.json"
if (Test-Path $recentFilesPath) {
    Write-Host "更新最近文件记录..." -ForegroundColor Yellow
    $backupPath = "$recentFilesPath.backup"
    Copy-Item $recentFilesPath $backupPath -Force
}

# 3. 清理项目根目录的临时文件
Write-Host "清理项目临时文件..." -ForegroundColor Yellow
$tempPatterns = @("*.tmp", "*.temp", "*~", ".#*", "#*#")
foreach ($pattern in $tempPatterns) {
    Get-ChildItem -Path $WorkspacePath -Filter $pattern -Recurse | Remove-Item -Force -ErrorAction SilentlyContinue
}

# 4. 强制删除指定文件（如果提供了参数）
if ($args.Count -gt 0) {
    Write-Host "强制删除指定文件..." -ForegroundColor Yellow
    foreach ($file in $args) {
        if (Test-Path $file) {
            Write-Host "删除文件: $file" -ForegroundColor Red
            Remove-Item $file -Force -ErrorAction SilentlyContinue
        }
    }
}

# 5. 清理 Git 未跟踪的文件
if (Test-Path ".git") {
    Write-Host "清理 Git 未跟踪的文件..." -ForegroundColor Yellow
    git clean -fd
}

# 6. 重新启动文件监控
Write-Host "重新初始化文件监控..." -ForegroundColor Green
Stop-Process -Name "Code" -ErrorAction SilentlyContinue
Start-Sleep 2

Write-Host "VS Code 工作空间清理完成!" -ForegroundColor Green
Write-Host "建议重新启动 VS Code 以确保更改生效。" -ForegroundColor Yellow
