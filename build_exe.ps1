# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    将 md2docx_optimized.py 打包成独立的 exe 文件

.DESCRIPTION
    使用 PyInstaller 将 Markdown 转 Word 工具打包成绿色版 exe 文件
    
.NOTES
    作者: AI Assistant
    日期: 2025-01-16
#>

# 设置错误处理
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Markdown 转 Word 工具 - EXE 打包" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查虚拟环境
if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "❌ 未找到虚拟环境，请先运行 setup_venv.ps1 创建虚拟环境" -ForegroundColor Red
    exit 1
}

# 激活虚拟环境
Write-Host "🔧 激活虚拟环境..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# 检查 PyInstaller 是否已安装
Write-Host "🔍 检查 PyInstaller..." -ForegroundColor Yellow
$pyinstallerInstalled = & python -m pip list | Select-String "pyinstaller"

if (-not $pyinstallerInstalled) {
    Write-Host "📦 安装 PyInstaller..." -ForegroundColor Yellow
    & python -m pip install pyinstaller
    Write-Host "✅ PyInstaller 安装完成" -ForegroundColor Green
} else {
    Write-Host "✅ PyInstaller 已安装" -ForegroundColor Green
}

# 清理之前的构建
Write-Host ""
Write-Host "🧹 清理旧的构建文件..." -ForegroundColor Yellow
if (Test-Path ".\build") {
    Remove-Item -Path ".\build" -Recurse -Force
    Write-Host "  - 删除 build 目录" -ForegroundColor Gray
}
if (Test-Path ".\dist") {
    Remove-Item -Path ".\dist" -Recurse -Force
    Write-Host "  - 删除 dist 目录" -ForegroundColor Gray
}

# 开始打包
Write-Host ""
Write-Host "📦 开始打包 exe 文件..." -ForegroundColor Cyan
Write-Host "   这可能需要几分钟时间，请耐心等待..." -ForegroundColor Gray
Write-Host ""

try {
    # 使用 spec 文件打包
    & pyinstaller --clean md2docx.spec
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✅ 打包成功！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    # 检查生成的文件
    $exePath = ".\dist\md2docx.exe"
    if (Test-Path $exePath) {
        $fileSize = (Get-Item $exePath).Length
        $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
        
        Write-Host "📁 生成的文件:" -ForegroundColor Cyan
        Write-Host "   路径: $exePath" -ForegroundColor White
        Write-Host "   大小: $fileSizeMB MB" -ForegroundColor White
        Write-Host ""
        
        Write-Host "💡 使用方法:" -ForegroundColor Yellow
        Write-Host "   1. 将 md2docx.exe 复制到任意目录" -ForegroundColor White
        Write-Host "   2. 在命令行中运行:" -ForegroundColor White
        Write-Host "      md2docx.exe input.md" -ForegroundColor Gray
        Write-Host "      md2docx.exe input.md -o output.docx" -ForegroundColor Gray
        Write-Host "   3. 或者直接拖放 .md 文件到 exe 上" -ForegroundColor White
        Write-Host ""
        
        Write-Host "🎯 绿色版特点:" -ForegroundColor Green
        Write-Host "   ✓ 无需安装 Python" -ForegroundColor White
        Write-Host "   ✓ 无需安装依赖包" -ForegroundColor White
        Write-Host "   ✓ 可直接运行" -ForegroundColor White
        Write-Host "   ✓ 可随意复制到其他电脑" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "❌ 未找到生成的 exe 文件" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ 打包失败: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 故障排除:" -ForegroundColor Yellow
    Write-Host "   1. 确保虚拟环境已正确创建" -ForegroundColor White
    Write-Host "   2. 确保所有依赖包已安装 (pip install -r requirements.txt)" -ForegroundColor White
    Write-Host "   3. 检查是否有杀毒软件干扰" -ForegroundColor White
    Write-Host "   4. 尝试以管理员权限运行" -ForegroundColor White
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  打包流程完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
