#!/usr/bin/env pwsh
<#
.SYNOPSIS
    aidocs项目快速设置脚本 - 跨平台支持

.DESCRIPTION
    自动检测操作系统并配置aidocs项目开发环境
    支持Windows、macOS、Linux

.EXAMPLE
    # Windows PowerShell
    .\setup-dev-env.ps1
    
    # Linux/macOS
    pwsh setup-dev-env.ps1
#>

param(
    [switch]$Force,
    [switch]$SkipPoetry,
    [switch]$Verbose
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    
    $colorMap = @{
        "Red" = [ConsoleColor]::Red
        "Green" = [ConsoleColor]::Green
        "Yellow" = [ConsoleColor]::Yellow
        "Blue" = [ConsoleColor]::Blue
        "Cyan" = [ConsoleColor]::Cyan
        "Magenta" = [ConsoleColor]::Magenta
        "White" = [ConsoleColor]::White
    }
    
    Write-Host $Message -ForegroundColor $colorMap[$Color]
}

# 检测操作系统
function Get-OperatingSystem {
    if ($IsWindows -or $env:OS -eq "Windows_NT") {
        return "Windows"
    }
    elseif ($IsLinux) {
        return "Linux"
    }
    elseif ($IsMacOS) {
        return "macOS"
    }
    else {
        return "Unknown"
    }
}

# 检查命令是否存在
function Test-Command {
    param([string]$Command)
    
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# 安装Poetry
function Install-Poetry {
    param([string]$OS)
    
    Write-ColorOutput "🔧 检查Poetry安装状态..." "Blue"
    
    if (Test-Command "poetry") {
        $poetryVersion = poetry --version
        Write-ColorOutput "✅ Poetry已安装: $poetryVersion" "Green"
        return
    }
    
    if ($SkipPoetry) {
        Write-ColorOutput "⚠️  跳过Poetry安装（--SkipPoetry参数）" "Yellow"
        return
    }
    
    Write-ColorOutput "📦 正在安装Poetry..." "Blue"
    
    switch ($OS) {
        "Windows" {
            try {
                $installScript = Invoke-WebRequest -Uri "https://install.python-poetry.org" -UseBasicParsing
                $installScript.Content | python -
                
                # 添加到PATH (当前会话)
                $poetryPath = "$env:APPDATA\Python\Scripts"
                if (Test-Path $poetryPath) {
                    $env:PATH = "$poetryPath;$env:PATH"
                }
            }
            catch {
                Write-ColorOutput "❌ Poetry安装失败，请手动安装: https://python-poetry.org/docs/#installation" "Red"
                exit 1
            }
        }
        "macOS" {
            if (Test-Command "brew") {
                brew install poetry
            } else {
                curl -sSL https://install.python-poetry.org | python3 -
            }
        }
        "Linux" {
            curl -sSL https://install.python-poetry.org | python3 -
        }
        default {
            Write-ColorOutput "❌ 不支持的操作系统: $OS" "Red"
            exit 1
        }
    }
    
    Write-ColorOutput "✅ Poetry安装完成" "Green"
}

# 配置项目环境
function Setup-ProjectEnvironment {
    Write-ColorOutput "🔧 配置项目环境..." "Blue"
    
    # 检查是否在项目根目录
    if (-not (Test-Path "pyproject.toml")) {
        Write-ColorOutput "❌ 请在项目根目录运行此脚本" "Red"
        exit 1
    }
    
    # 安装依赖
    Write-ColorOutput "📦 安装项目依赖..." "Blue"
    poetry install
    
    # 验证安装
    Write-ColorOutput "🔍 验证环境..." "Blue"
    poetry run python -c "import sys; print(f'Python版本: {sys.version}')"
    poetry run python -c "import fastapi; print('FastAPI导入成功')"
    poetry run python -c "from docx import Document; print('python-docx导入成功')"
    
    Write-ColorOutput "✅ 环境配置完成" "Green"
}

# 测试VS Code任务
function Test-VSCodeTasks {
    Write-ColorOutput "🔧 测试VS Code任务配置..." "Blue"
    
    if (-not (Test-Path ".vscode/tasks.json")) {
        Write-ColorOutput "❌ VS Code任务文件不存在" "Red"
        return
    }
    
    # 解析tasks.json
    try {
        $tasksContent = Get-Content ".vscode/tasks.json" -Raw | ConvertFrom-Json
        $taskCount = $tasksContent.tasks.Count
        Write-ColorOutput "✅ 发现 $taskCount 个VS Code任务" "Green"
        
        # 列出任务
        Write-ColorOutput "📋 可用任务:" "Cyan"
        foreach ($task in $tasksContent.tasks) {
            Write-ColorOutput "   • $($task.label): $($task.detail)" "White"
        }
    }
    catch {
        Write-ColorOutput "⚠️  无法解析tasks.json文件" "Yellow"
    }
}

# 生成配置报告
function Show-ConfigurationReport {
    param([string]$OS)
    
    Write-ColorOutput "`n🎉 环境配置完成报告" "Green"
    Write-ColorOutput "===================" "Green"
    Write-ColorOutput "操作系统: $OS" "White"
    Write-ColorOutput "Python版本: $(python --version 2>$null)" "White"
    Write-ColorOutput "Poetry版本: $(poetry --version 2>$null)" "White"
    Write-ColorOutput "项目路径: $(Get-Location)" "White"
    
    Write-ColorOutput "`n📚 下一步操作:" "Cyan"
    Write-ColorOutput "1. 在VS Code中打开项目: code ." "White"
    Write-ColorOutput "2. 按Ctrl+Shift+P打开命令面板" "White"
    Write-ColorOutput "3. 输入'Tasks: Run Task'选择任务" "White"
    Write-ColorOutput "4. 尝试运行'Poetry: 查看依赖'验证环境" "White"
    
    Write-ColorOutput "`n📖 更多信息请参考: docs/跨平台tasks配置说明.md" "Blue"
}

# 主函数
function Main {
    Write-ColorOutput "🚀 aidocs项目环境设置" "Cyan"
    Write-ColorOutput "====================" "Cyan"
    
    $OS = Get-OperatingSystem
    Write-ColorOutput "检测到操作系统: $OS" "Blue"
    
    # 检查Python
    if (-not (Test-Command "python")) {
        Write-ColorOutput "❌ Python未安装或未添加到PATH" "Red"
        Write-ColorOutput "请安装Python 3.9+: https://www.python.org/downloads/" "Yellow"
        exit 1
    }
    
    try {
        # 安装Poetry
        Install-Poetry -OS $OS
        
        # 配置项目环境
        Setup-ProjectEnvironment
        
        # 测试VS Code任务
        Test-VSCodeTasks
        
        # 显示配置报告
        Show-ConfigurationReport -OS $OS
        
        Write-ColorOutput "`n✅ 设置完成！" "Green"
    }
    catch {
        Write-ColorOutput "`n❌ 设置过程中出现错误: $($_.Exception.Message)" "Red"
        if ($Verbose) {
            Write-ColorOutput "详细错误信息:" "Red"
            Write-ColorOutput $_.Exception.ToString() "Red"
        }
        exit 1
    }
}

# 脚本入口
if ($MyInvocation.InvocationName -ne '.') {
    Main
}