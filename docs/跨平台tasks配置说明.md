# 跨平台Tasks配置说明

## 概述

本项目的VS Code tasks配置已优化为跨电脑、跨平台共享。无论在Windows、macOS还是Linux上，都能正常使用项目的构建和开发任务。

## 配置特点

### ✅ 跨平台兼容性
- **相对路径**：使用`${workspaceFolder}`变量，避免硬编码绝对路径
- **Poetry统一**：所有Python任务都通过Poetry执行，确保环境一致性
- **平台特定任务**：为不同操作系统提供专门的任务

### ✅ Git版本控制
- `.vscode/tasks.json`现已纳入Git版本控制
- 团队成员克隆项目后即可使用统一的任务配置
- 任务配置的修改会自动同步到所有团队成员

## 可用任务列表

### 📄 文档转换任务
1. **MD转DOCX：当前文件** (默认构建任务)
   - 快捷键：`Ctrl+Shift+P` → `Tasks: Run Build Task`
   - 功能：将当前打开的Markdown文件转换为Word文档

2. **MD转DOCX：选择文件转换**
   - 功能：选择特定Markdown文件进行转换

### 🛠️ Poetry管理任务
3. **Poetry: 安装依赖**
   - 功能：安装项目所有依赖包
   - 命令：`poetry install`

4. **Poetry: 添加依赖**
   - 功能：添加新的Python包依赖
   - 支持交互式输入包名

5. **Poetry: 查看依赖**
   - 功能：显示已安装的依赖包列表
   - 命令：`poetry show`

6. **Poetry: 运行测试**
   - 功能：使用pytest运行项目测试
   - 命令：`poetry run pytest tests/ -v`

7. **Poetry: 代码格式化**
   - 功能：使用Black格式化代码
   - 命令：`poetry run black .`

8. **Poetry: 代码检查**
   - 功能：使用Flake8检查代码质量
   - 命令：`poetry run flake8 .`

### 🧹 系统维护任务
9. **删除文件 (Windows)**
   - 功能：Windows PowerShell删除文件
   - 命令：`Remove-Item -Force -Recurse`

10. **删除文件 (Unix/Linux/macOS)**
    - 功能：Unix系统删除文件
    - 命令：`rm -rf`

11. **刷新工作空间**
    - 功能：刷新工作空间文件状态

12. **工作空间清理**
    - 功能：跨平台清理临时文件

## 使用方法

### 方法1：命令面板
1. 按 `Ctrl+Shift+P` (Windows/Linux) 或 `Cmd+Shift+P` (macOS)
2. 输入 `Tasks: Run Task`
3. 选择要执行的任务

### 方法2：快捷键
- **默认构建任务**：`Ctrl+Shift+B` (Windows/Linux) 或 `Cmd+Shift+B` (macOS)
- **运行测试任务**：`Ctrl+Shift+P` → `Tasks: Run Test Task`

### 方法3：状态栏
- 点击VS Code底部状态栏的构建按钮

## 新电脑设置步骤

### 1. 克隆项目
```bash
git clone <repository-url>
cd aidocs
```

### 2. 安装Poetry（如果未安装）
```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. 安装项目依赖
```bash
poetry install
```

### 4. 打开VS Code
```bash
code .
```

### 5. 验证任务配置
- 按 `Ctrl+Shift+P` → `Tasks: Run Task`
- 选择 "Poetry: 查看依赖" 验证环境配置

## 平台特定注意事项

### Windows
- 确保已安装PowerShell 5.0+
- Poetry路径需要添加到系统PATH

### macOS
- 可能需要安装Xcode Command Line Tools
- 使用Homebrew安装Poetry：`brew install poetry`

### Linux
- 确保Python 3.9+已安装
- 部分发行版需要额外安装python3-venv

## 故障排除

### 常见问题

1. **Poetry未找到**
   ```bash
   # 检查Poetry安装
   poetry --version
   
   # 如果未安装，按照上述安装步骤重新安装
   ```

2. **Python版本不匹配**
   ```bash
   # 检查Python版本
   python --version
   
   # Poetry会自动管理虚拟环境
   poetry env info
   ```

3. **依赖安装失败**
   ```bash
   # 清理并重新安装
   poetry env remove python
   poetry install
   ```

4. **VS Code任务不显示**
   - 确保在项目根目录打开VS Code
   - 检查`.vscode/tasks.json`文件是否存在
   - 重启VS Code

## 最佳实践

### 1. 统一开发环境
- 所有团队成员使用相同的Poetry版本
- 定期同步`poetry.lock`文件

### 2. 任务配置维护
- 修改任务配置后及时提交到Git
- 添加新任务时更新本文档

### 3. 文档同步
- 保持本说明文档与实际配置同步
- 记录平台特定的配置差异

## 扩展配置

如需添加新的任务，请按以下格式编辑`.vscode/tasks.json`：

```json
{
    "label": "任务名称",
    "type": "shell",
    "command": "poetry",
    "args": ["run", "python", "script.py"],
    "group": "build",
    "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "new"
    },
    "detail": "任务描述",
    "problemMatcher": [],
    "options": {
        "cwd": "${workspaceFolder}"
    }
}
```

## 更新日志

- **2025-09-17**：初始版本，支持跨平台共享
- **未来计划**：添加Docker支持、CI/CD集成任务

---

**技术支持**：如遇问题，请查看项目Issues或联系项目维护者。