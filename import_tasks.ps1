# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    快速导入 md2docx VSCode 任务配置

.DESCRIPTION
    自动将 vscode-tasks-portable.json 复制到 .vscode/tasks.json
    如果已存在 tasks.json，会提示是否备份和覆盖

.NOTES
    作者: AI Assistant
    日期: 2025-01-16
#>

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VSCode 任务配置导入工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查源文件
$sourceFile = ".\vscode-tasks-portable.json"
if (-not (Test-Path $sourceFile)) {
    Write-Host "❌ 错误: 未找到源文件 $sourceFile" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host "✅ 找到配置文件: $sourceFile" -ForegroundColor Green

# 检查 .vscode 目录
$vscodeDir = ".\.vscode"
if (-not (Test-Path $vscodeDir)) {
    Write-Host "📁 创建 .vscode 目录..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $vscodeDir | Out-Null
    Write-Host "✅ .vscode 目录创建成功" -ForegroundColor Green
}

# 检查目标文件
$targetFile = ".\.vscode\tasks.json"
$needBackup = $false

if (Test-Path $targetFile) {
    Write-Host ""
    Write-Host "⚠️  检测到已存在的 tasks.json 文件" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "请选择操作:" -ForegroundColor Cyan
    Write-Host "  [1] 备份现有文件并覆盖（推荐）" -ForegroundColor White
    Write-Host "  [2] 直接覆盖（不备份）" -ForegroundColor White
    Write-Host "  [3] 取消操作" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "请输入选项 (1/2/3)"
    
    switch ($choice) {
        "1" {
            $needBackup = $true
            Write-Host ""
            Write-Host "✅ 将备份现有文件" -ForegroundColor Green
        }
        "2" {
            Write-Host ""
            Write-Host "⚠️  将直接覆盖（不备份）" -ForegroundColor Yellow
        }
        "3" {
            Write-Host ""
            Write-Host "❌ 操作已取消" -ForegroundColor Red
            exit 0
        }
        default {
            Write-Host ""
            Write-Host "❌ 无效的选项，操作已取消" -ForegroundColor Red
            exit 1
        }
    }
}

# 执行备份
if ($needBackup) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = ".\.vscode\tasks.json.backup.$timestamp"
    
    Write-Host ""
    Write-Host "📦 备份现有文件..." -ForegroundColor Yellow
    Copy-Item -Path $targetFile -Destination $backupFile
    Write-Host "✅ 备份完成: $backupFile" -ForegroundColor Green
}

# 复制文件
Write-Host ""
Write-Host "📋 复制任务配置..." -ForegroundColor Yellow
Copy-Item -Path $sourceFile -Destination $targetFile -Force
Write-Host "✅ 任务配置已导入" -ForegroundColor Green

# 验证文件
if (Test-Path $targetFile) {
    $fileSize = (Get-Item $targetFile).Length
    Write-Host "✅ 文件验证通过 (大小: $fileSize 字节)" -ForegroundColor Green
} else {
    Write-Host "❌ 文件导入失败" -ForegroundColor Red
    exit 1
}

# 检查 md2docx.exe
Write-Host ""
Write-Host "🔍 检查 md2docx.exe..." -ForegroundColor Yellow
$exeFile = ".\dist\md2docx.exe"
if (Test-Path $exeFile) {
    $exeSize = (Get-Item $exeFile).Length
    $exeSizeMB = [math]::Round($exeSize / 1MB, 2)
    Write-Host "✅ 找到 md2docx.exe (大小: $exeSizeMB MB)" -ForegroundColor Green
} else {
    Write-Host "⚠️  未找到 md2docx.exe" -ForegroundColor Yellow
    Write-Host "   如需使用任务，请先执行 .\build_exe.ps1 打包" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ 导入完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "📚 可用的任务:" -ForegroundColor Cyan
Write-Host "  1. MD转DOCX：使用绿色版EXE - 当前文件 (快捷键: Ctrl+Shift+B)" -ForegroundColor White
Write-Host "  2. MD转DOCX：使用绿色版EXE - 指定输出目录" -ForegroundColor White
Write-Host "  3. MD转DOCX：批量转换当前目录" -ForegroundColor White
Write-Host "  4. MD转DOCX：批量转换整个工作区" -ForegroundColor White
Write-Host "  5. 打开 md2docx.exe 所在目录" -ForegroundColor White
Write-Host "  6. 查看 md2docx.exe 帮助信息" -ForegroundColor White
Write-Host "  7. 复制 md2docx.exe 到桌面" -ForegroundColor White
Write-Host "  8. 创建 md2docx 批处理脚本" -ForegroundColor White
Write-Host ""

Write-Host "💡 使用方法:" -ForegroundColor Yellow
Write-Host "  1. 打开任意 .md 文件" -ForegroundColor White
Write-Host "  2. 按 Ctrl+Shift+P 打开命令面板" -ForegroundColor White
Write-Host "  3. 输入 'Run Task' 或 '运行任务'" -ForegroundColor White
Write-Host "  4. 选择要执行的任务" -ForegroundColor White
Write-Host ""
Write-Host "  或者直接按 Ctrl+Shift+B 执行默认转换任务" -ForegroundColor White
Write-Host ""

Write-Host "📖 详细文档:" -ForegroundColor Cyan
Write-Host "  - VSCODE_TASKS_GUIDE.md (任务使用指南)" -ForegroundColor White
Write-Host "  - dist\README.md (md2docx.exe 使用说明)" -ForegroundColor White
Write-Host ""

Write-Host "🔄 下一步:" -ForegroundColor Yellow
Write-Host "  1. 重新加载 VSCode 窗口 (Ctrl+Shift+P → 'Reload Window')" -ForegroundColor White
Write-Host "  2. 或者重启 VSCode" -ForegroundColor White
Write-Host ""

# 询问是否立即重新加载窗口
Write-Host "是否立即重新加载 VSCode 窗口? (y/n): " -ForegroundColor Cyan -NoNewline
$reload = Read-Host

if ($reload -eq "y" -or $reload -eq "Y") {
    Write-Host ""
    Write-Host "💡 请在 VSCode 中按 Ctrl+Shift+P，输入 'Reload Window' 并执行" -ForegroundColor Yellow
    Write-Host "   (PowerShell 脚本无法直接重新加载 VSCode 窗口)" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  配置导入完成，祝使用愉快！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
