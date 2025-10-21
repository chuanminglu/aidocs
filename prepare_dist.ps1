# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    准备 md2docx 分发包

.DESCRIPTION
    将所有必要的文件整理到 dist 目录，准备分发
    
.NOTES
    作者: AI Assistant
    日期: 2025-01-16
#>

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  md2docx 分发包准备工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 确保 dist 目录存在
if (-not (Test-Path ".\dist")) {
    Write-Host "📁 创建 dist 目录..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path ".\dist" | Out-Null
}

Write-Host "📂 工作目录: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

# 定义需要复制的文件
$filesToCopy = @(
    @{
        Source = ".\vscode-tasks-portable.json"
        Dest = ".\dist\vscode-tasks.json"
        Description = "VSCode 任务配置"
        Required = $false
    },
    @{
        Source = ".\import_tasks.ps1"
        Dest = ".\dist\import_tasks.ps1"
        Description = "任务导入脚本"
        Required = $false
    }
)

# 检查并复制文件
Write-Host "🔄 准备文件..." -ForegroundColor Cyan
Write-Host ""

$copiedCount = 0
$skippedCount = 0

foreach ($file in $filesToCopy) {
    if (Test-Path $file.Source) {
        Write-Host "  ✓ 复制: $($file.Description)" -ForegroundColor Green
        Write-Host "    从: $($file.Source)" -ForegroundColor Gray
        Write-Host "    到: $($file.Dest)" -ForegroundColor Gray
        
        Copy-Item -Path $file.Source -Destination $file.Dest -Force
        $copiedCount++
    } else {
        if ($file.Required) {
            Write-Host "  ✗ 缺失: $($file.Description) - $($file.Source)" -ForegroundColor Red
            Write-Host "    这是必需文件！" -ForegroundColor Red
        } else {
            Write-Host "  - 跳过: $($file.Description) - $($file.Source)" -ForegroundColor Yellow
            $skippedCount++
        }
    }
    Write-Host ""
}

# 检查关键文件
Write-Host "🔍 检查关键文件..." -ForegroundColor Cyan
Write-Host ""

$criticalFiles = @(
    @{ Path = ".\dist\md2docx.exe"; Name = "主程序 (md2docx.exe)" },
    @{ Path = ".\dist\README.md"; Name = "使用说明 (README.md)" },
    @{ Path = ".\dist\快速开始.md"; Name = "快速入门 (快速开始.md)" },
    @{ Path = ".\dist\index.md"; Name = "索引文件 (index.md)" },
    @{ Path = ".\dist\分发说明.md"; Name = "分发指南 (分发说明.md)" }
)

$allCriticalPresent = $true

foreach ($file in $criticalFiles) {
    if (Test-Path $file.Path) {
        $size = (Get-Item $file.Path).Length
        $sizeStr = if ($size -gt 1MB) {
            "$([math]::Round($size / 1MB, 2)) MB"
        } elseif ($size -gt 1KB) {
            "$([math]::Round($size / 1KB, 2)) KB"
        } else {
            "$size 字节"
        }
        Write-Host "  ✓ $($file.Name) - $sizeStr" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $($file.Name) - 缺失" -ForegroundColor Red
        $allCriticalPresent = $false
    }
}

Write-Host ""

# 列出 dist 目录内容
Write-Host "📦 dist 目录内容:" -ForegroundColor Cyan
Write-Host ""

$distFiles = Get-ChildItem -Path ".\dist" | Sort-Object Name
$totalSize = 0

foreach ($file in $distFiles) {
    $size = $file.Length
    $totalSize += $size
    
    $sizeStr = if ($size -gt 1MB) {
        "$([math]::Round($size / 1MB, 2)) MB"
    } elseif ($size -gt 1KB) {
        "$([math]::Round($size / 1KB, 2)) KB"
    } else {
        "$size 字节"
    }
    
    $icon = if ($file.Extension -eq ".exe") { "⚙️" }
            elseif ($file.Extension -eq ".md") { "📄" }
            elseif ($file.Extension -eq ".json") { "⚙️" }
            elseif ($file.Extension -eq ".ps1") { "📜" }
            else { "📁" }
    
    Write-Host "  $icon $($file.Name) - $sizeStr" -ForegroundColor White
}

$totalSizeMB = [math]::Round($totalSize / 1MB, 2)
Write-Host ""
Write-Host "  总计: $($distFiles.Count) 个文件，$totalSizeMB MB" -ForegroundColor Cyan

# 总结
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ 准备完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "📊 统计信息:" -ForegroundColor Cyan
Write-Host "  - 已复制文件: $copiedCount" -ForegroundColor White
Write-Host "  - 跳过文件: $skippedCount" -ForegroundColor White
Write-Host "  - dist 文件总数: $($distFiles.Count)" -ForegroundColor White
Write-Host "  - dist 总大小: $totalSizeMB MB" -ForegroundColor White
Write-Host ""

if ($allCriticalPresent) {
    Write-Host "✅ 所有关键文件都已准备就绪！" -ForegroundColor Green
    Write-Host ""
    Write-Host "📦 可以分发的内容:" -ForegroundColor Cyan
    Write-Host "  1. 仅主程序: dist\md2docx.exe + dist\快速开始.md" -ForegroundColor White
    Write-Host "  2. 完整包: 整个 dist 目录" -ForegroundColor White
    Write-Host "  3. 压缩包: 将 dist 目录压缩为 zip" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 建议:" -ForegroundColor Yellow
    Write-Host "  - 最小分发: 约 20 MB (仅 exe + 快速开始)" -ForegroundColor White
    Write-Host "  - 完整分发: 约 $totalSizeMB MB (包含所有文档)" -ForegroundColor White
} else {
    Write-Host "⚠️  部分关键文件缺失，请检查！" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 提示:" -ForegroundColor Cyan
    Write-Host "  - 运行 .\build_exe.ps1 生成 md2docx.exe" -ForegroundColor White
    Write-Host "  - 确保所有文档文件都已创建" -ForegroundColor White
}

Write-Host ""

# 询问是否创建压缩包
Write-Host "是否创建压缩包? (y/n): " -ForegroundColor Cyan -NoNewline
$createZip = Read-Host

if ($createZip -eq "y" -or $createZip -eq "Y") {
    $zipName = "md2docx_v1.0_$(Get-Date -Format 'yyyyMMdd').zip"
    $zipPath = ".\$zipName"
    
    Write-Host ""
    Write-Host "📦 创建压缩包..." -ForegroundColor Yellow
    
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    
    Compress-Archive -Path ".\dist\*" -DestinationPath $zipPath
    
    $zipSize = (Get-Item $zipPath).Length
    $zipSizeMB = [math]::Round($zipSize / 1MB, 2)
    
    Write-Host "✅ 压缩包创建成功！" -ForegroundColor Green
    Write-Host "   文件: $zipPath" -ForegroundColor White
    Write-Host "   大小: $zipSizeMB MB" -ForegroundColor White
    Write-Host ""
    Write-Host "📤 可以直接分发这个压缩包！" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  准备工作完成，祝分发顺利！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
