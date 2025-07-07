# AI文档管理系统 - 开发环境启动脚本
# 此脚本用于在虚拟环境中启动开发服务器

param(
    [string]$Service = "all",  # all, api, gui
    [string]$VenvName = "aidocs-env",
    [switch]$Dev = $false
)

Write-Host "AI文档管理系统 - 开发环境启动脚本" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# 检查虚拟环境
$venvPath = ".\$VenvName"
if (-not (Test-Path $venvPath)) {
    Write-Host "错误: 虚拟环境不存在，请先运行 scripts\setup_venv.ps1" -ForegroundColor Red
    exit 1
}

# 激活虚拟环境
Write-Host "激活虚拟环境: $VenvName" -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"

# 检查是否在虚拟环境中
$pythonPath = & "$venvPath\Scripts\python.exe" -c "import sys; print(sys.prefix)"
$currentPath = Get-Location
if (-not $pythonPath.Contains($currentPath)) {
    Write-Host "警告: 请确保在虚拟环境中运行" -ForegroundColor Yellow
}

# 启动服务
switch ($Service.ToLower()) {
    "api" {
        Write-Host "启动FastAPI后端服务..." -ForegroundColor Cyan
        if ($Dev) {
            Write-Host "开发模式: 自动重载已启用" -ForegroundColor Yellow
            & "$venvPath\Scripts\uvicorn.exe" src.api.main:app --reload --host 0.0.0.0 --port 8000
        } else {
            & "$venvPath\Scripts\python.exe" src/api/main.py
        }
    }
    "gui" {
        Write-Host "启动PyQt6桌面客户端..." -ForegroundColor Cyan
        if ($Dev) {
            Write-Host "开发模式: 调试信息已启用" -ForegroundColor Yellow
            & "$venvPath\Scripts\python.exe" src/gui/main_window.py --dev
        } else {
            & "$venvPath\Scripts\python.exe" src/gui/main_window.py
        }
    }
    "all" {
        Write-Host "启动所有服务..." -ForegroundColor Cyan
        Write-Host "注意: 在生产环境中，建议分别启动各服务" -ForegroundColor Yellow
        
        # 启动API服务（后台）
        Start-Job -Name "APIServer" -ScriptBlock {
            param($venvPath)
            & "$venvPath\Scripts\python.exe" src/api/main.py
        } -ArgumentList $venvPath
        
        Write-Host "API服务已在后台启动" -ForegroundColor Green
        Start-Sleep -Seconds 2
        
        # 启动GUI客户端（前台）
        Write-Host "启动桌面客户端..." -ForegroundColor Cyan
        & "$venvPath\Scripts\python.exe" src/gui/main_window.py
    }
    default {
        Write-Host "错误: 无效的服务类型。可选值: all, api, gui" -ForegroundColor Red
        Write-Host "用法: .\scripts\dev_start.ps1 -Service <all|api|gui> [-Dev]" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "开发服务器已启动！" -ForegroundColor Green
Write-Host "API地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API文档: http://localhost:8000/docs" -ForegroundColor Cyan
