# AI文档管理系统 - 虚拟环境安装脚本
# 此脚本用于在Windows系统上创建和配置Python虚拟环境

param(
    [string]$PythonVersion = "3.11",
    [string]$VenvName = "aidocs-env"
)

Write-Host "AI文档管理系统 - 虚拟环境安装脚本" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# 检查Python版本
Write-Host "检查Python版本..." -ForegroundColor Yellow
$pythonCmd = "python"
try {
    $currentVersion = & $pythonCmd --version 2>&1
    Write-Host "当前Python版本: $currentVersion" -ForegroundColor Cyan
} catch {
    Write-Host "错误: 未找到Python，请先安装Python $PythonVersion 或更高版本" -ForegroundColor Red
    exit 1
}

# 检查是否已存在虚拟环境
$venvPath = ".\$VenvName"
if (Test-Path $venvPath) {
    Write-Host "检测到已存在虚拟环境: $venvPath" -ForegroundColor Yellow
    $response = Read-Host "是否删除现有虚拟环境并重新创建? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "删除现有虚拟环境..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $venvPath
    } else {
        Write-Host "跳过虚拟环境创建，使用现有环境" -ForegroundColor Cyan
        & "$venvPath\Scripts\Activate.ps1"
        Write-Host "虚拟环境已激活" -ForegroundColor Green
        exit 0
    }
}

# 创建虚拟环境
Write-Host "创建虚拟环境: $VenvName" -ForegroundColor Yellow
& $pythonCmd -m venv $VenvName

if (-not $?) {
    Write-Host "错误: 虚拟环境创建失败" -ForegroundColor Red
    exit 1
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"

# 升级pip
Write-Host "升级pip..." -ForegroundColor Yellow
& "$venvPath\Scripts\pip.exe" install --upgrade pip

# 安装依赖
Write-Host "安装项目依赖..." -ForegroundColor Yellow
& "$venvPath\Scripts\pip.exe" install -r requirements.txt

if (-not $?) {
    Write-Host "错误: 依赖安装失败" -ForegroundColor Red
    exit 1
}

# 验证安装
Write-Host "验证关键依赖安装..." -ForegroundColor Yellow
$criticalPackages = @("PyQt6", "fastapi", "sqlalchemy", "pydantic")
foreach ($package in $criticalPackages) {
    try {
        & "$venvPath\Scripts\pip.exe" show $package | Out-Null
        Write-Host "✓ $package 已安装" -ForegroundColor Green
    } catch {
        Write-Host "✗ $package 未安装或有问题" -ForegroundColor Red
    }
}

Write-Host "" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "虚拟环境设置完成！" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "使用说明:" -ForegroundColor Cyan
Write-Host "1. 激活虚拟环境: .\$VenvName\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. 停用虚拟环境: deactivate" -ForegroundColor White
Write-Host "3. 启动后端API: python src/api/main.py" -ForegroundColor White
Write-Host "4. 启动桌面客户端: python src/gui/main_window.py" -ForegroundColor White
Write-Host ""
Write-Host "注意: 所有开发和运行都必须在虚拟环境中进行！" -ForegroundColor Yellow
