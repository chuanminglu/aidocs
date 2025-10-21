# VSCode 任务配置使用指南

## 📋 概述

本文档说明如何在新的 VSCode 环境中导入和使用 Markdown 转 Word 的任务配置。

## 🚀 快速开始

### 方法 1: 自动导入（推荐）

1. **复制任务配置文件**
   ```powershell
   # 将 vscode-tasks-portable.json 复制到 .vscode 目录
   Copy-Item vscode-tasks-portable.json .vscode/tasks.json
   ```

2. **重启 VSCode** 或重新加载窗口
   - 按 `Ctrl+Shift+P`
   - 输入 "Reload Window"
   - 回车确认

3. **开始使用**
   - 打开任意 `.md` 文件
   - 按 `Ctrl+Shift+B` 执行默认构建任务
   - 或按 `Ctrl+Shift+P` → 输入 "Run Task"

### 方法 2: 手动合并

如果已有 `tasks.json` 文件，需要手动合并：

1. **打开现有的 tasks.json**
   ```
   .vscode/tasks.json
   ```

2. **复制任务配置**
   - 打开 `vscode-tasks-portable.json`
   - 复制 `tasks` 数组中的所有任务
   - 粘贴到现有 `tasks.json` 的 `tasks` 数组中

3. **保存文件**

## 📚 可用任务列表

### 1. MD转DOCX：使用绿色版EXE - 当前文件 ⭐

**快捷键**: `Ctrl+Shift+B` (默认构建任务)

**功能**: 转换当前打开的 Markdown 文件为 Word 文档

**输出**: 与源文件相同目录，同名 `.docx` 文件

**使用场景**: 最常用，快速转换单个文件

```
示例:
打开: C:\Docs\report.md
输出: C:\Docs\report.docx
```

### 2. MD转DOCX：使用绿色版EXE - 指定输出目录

**功能**: 转换当前文件到工作区的 `output` 目录

**输出**: `${workspaceFolder}/output/文件名.docx`

**使用场景**: 统一管理所有转换结果

```
示例:
打开: C:\Project\docs\api.md
输出: C:\Project\output\api.docx
```

### 3. MD转DOCX：批量转换当前目录

**功能**: 转换当前文件所在目录的所有 `.md` 文件

**输出**: 各文件同目录下的 `.docx` 文件

**使用场景**: 批量转换同一目录的文档

```
示例:
当前目录: C:\Docs\
  - file1.md → file1.docx
  - file2.md → file2.docx
  - file3.md → file3.docx
```

### 4. MD转DOCX：批量转换整个工作区

**功能**: 递归转换整个工作区的所有 `.md` 文件

**输出**: 各文件所在目录

**使用场景**: 一次性转换项目所有文档

⚠️ **注意**: 大型项目可能需要较长时间

### 5. 打开 md2docx.exe 所在目录

**功能**: 在文件资源管理器中打开 `dist` 目录

**使用场景**: 快速访问 exe 文件，便于分发

### 6. 查看 md2docx.exe 帮助信息

**功能**: 显示命令行使用帮助

**使用场景**: 查看所有可用选项和参数

### 7. 复制 md2docx.exe 到桌面

**功能**: 将 exe 文件复制到桌面

**使用场景**: 方便拖放文件进行转换

### 8. 创建 md2docx 批处理脚本

**功能**: 在 `dist` 目录创建 `batch_convert.bat` 脚本

**使用场景**: 在没有 VSCode 的环境中批量转换

## 🎯 使用方法

### 方式 1: 通过命令面板 (推荐)

1. 打开要转换的 `.md` 文件
2. 按 `Ctrl+Shift+P` 打开命令面板
3. 输入 `Run Task` 或 `运行任务`
4. 从列表中选择需要的任务
5. 回车执行

![命令面板截图](task-command-palette.png)

### 方式 2: 使用快捷键

**默认构建任务** (最常用):
```
Ctrl+Shift+B
```

这将执行 "MD转DOCX：使用绿色版EXE - 当前文件" 任务

### 方式 3: 通过菜单

1. 点击顶部菜单 `Terminal` → `Run Task...`
2. 选择任务
3. 执行

### 方式 4: 通过任务快捷入口

在底部状态栏可能显示任务快捷入口（需要安装任务相关插件）

## 🔧 自定义配置

### 修改默认输出目录

编辑 `.vscode/tasks.json`，找到对应任务：

```json
{
  "label": "MD转DOCX：使用绿色版EXE - 当前文件",
  "args": [
    "${file}",
    "-o",
    "D:/MyDocs/${fileBasenameNoExtension}.docx"  // 改为自定义路径
  ]
}
```

### 添加自定义任务

在 `tasks` 数组中添加新任务：

```json
{
  "label": "我的自定义转换任务",
  "type": "shell",
  "command": "${workspaceFolder}/dist/md2docx.exe",
  "args": [
    "${file}",
    "-o",
    "自定义路径/${fileBasenameNoExtension}.docx"
  ],
  "group": "build",
  "problemMatcher": []
}
```

### 修改快捷键

创建或编辑 `.vscode/keybindings.json`:

```json
[
  {
    "key": "ctrl+alt+m",
    "command": "workbench.action.tasks.runTask",
    "args": "MD转DOCX：使用绿色版EXE - 当前文件"
  }
]
```

## 📝 VSCode 变量说明

任务配置中使用了以下 VSCode 变量：

| 变量 | 说明 | 示例 |
|------|------|------|
| `${workspaceFolder}` | 工作区根目录 | `C:\Projects\MyProject` |
| `${file}` | 当前打开的文件完整路径 | `C:\Projects\MyProject\docs\api.md` |
| `${fileDirname}` | 当前文件所在目录 | `C:\Projects\MyProject\docs` |
| `${fileBasename}` | 当前文件名（含扩展名） | `api.md` |
| `${fileBasenameNoExtension}` | 当前文件名（不含扩展名） | `api` |
| `${fileExtname}` | 当前文件扩展名 | `.md` |

更多变量参考: [VSCode Variables Reference](https://code.visualstudio.com/docs/editor/variables-reference)

## 🚚 迁移到新环境

### 完整迁移步骤

1. **复制必要文件**
   ```
   项目目录/
   ├── dist/
   │   ├── md2docx.exe          ← 必需
   │   └── README.md            ← 可选（使用说明）
   ├── .vscode/
   │   └── tasks.json           ← 从 vscode-tasks-portable.json 复制
   └── vscode-tasks-portable.json  ← 备份文件
   ```

2. **调整路径（如需要）**
   
   如果 `md2docx.exe` 不在 `dist` 目录，需要修改 `tasks.json` 中的路径：
   
   ```json
   "command": "${workspaceFolder}/你的路径/md2docx.exe"
   ```

3. **测试任务**
   
   打开一个 `.md` 文件，按 `Ctrl+Shift+B` 测试

### 最小化迁移

如果只需要基本功能：

1. 只复制 `md2docx.exe` 到新环境
2. 手动创建 `.vscode/tasks.json`，只添加最常用的任务
3. 或者直接在命令行使用 `md2docx.exe`

## ⚙️ 常见问题

### Q: 任务列表为空？

**A**: 
1. 检查 `tasks.json` 是否在 `.vscode` 目录下
2. 检查 JSON 格式是否正确（使用 VSCode 的 JSON 验证）
3. 重新加载窗口: `Ctrl+Shift+P` → "Reload Window"

### Q: 执行任务时提示找不到 exe 文件？

**A**: 
1. 检查 `dist/md2docx.exe` 是否存在
2. 检查 `tasks.json` 中的路径是否正确
3. 使用绝对路径替代变量（用于调试）

### Q: 如何查看任务执行输出？

**A**: 
任务执行时会自动打开终端面板显示输出。也可以：
1. 按 `Ctrl+` ` 打开终端
2. 选择 "任务 - xxx" 标签页

### Q: 如何停止正在执行的任务？

**A**: 
1. 在终端面板中点击垃圾桶图标
2. 或使用 `Ctrl+C` 中断任务

### Q: 能否在其他编辑器中使用这些任务？

**A**: 
这些任务是 VSCode 特定的。其他编辑器需要：
- 直接使用命令行运行 `md2docx.exe`
- 或使用编辑器自己的任务系统

### Q: 任务配置文件在 Git 中如何处理？

**A**: 
建议做法：
- 提交 `vscode-tasks-portable.json` 到仓库（作为模板）
- `.vscode/tasks.json` 可以提交（团队共享）
- 或添加到 `.gitignore`（个人配置）

## 💡 最佳实践

### 1. 工作区组织

```
项目目录/
├── docs/              ← Markdown 源文件
│   ├── api.md
│   └── guide.md
├── output/            ← 转换后的 Word 文件
│   ├── api.docx
│   └── guide.docx
├── dist/
│   └── md2docx.exe
└── .vscode/
    └── tasks.json
```

### 2. 使用任务组合

创建复合任务执行多个步骤：

```json
{
  "label": "转换并打开输出目录",
  "dependsOrder": "sequence",
  "dependsOn": [
    "MD转DOCX：使用绿色版EXE - 当前文件",
    "打开 md2docx.exe 所在目录"
  ],
  "problemMatcher": []
}
```

### 3. 添加前置检查

```json
{
  "label": "转换前检查",
  "type": "shell",
  "command": "if (Test-Path '${file}') { Write-Host '文件存在，开始转换' } else { Write-Host '文件不存在'; exit 1 }",
  "problemMatcher": []
}
```

### 4. 输出目录自动创建

```json
{
  "label": "MD转DOCX：自动创建输出目录",
  "type": "shell",
  "command": "New-Item -ItemType Directory -Force -Path '${workspaceFolder}/output'; & '${workspaceFolder}/dist/md2docx.exe' '${file}' -o '${workspaceFolder}/output/${fileBasenameNoExtension}.docx'",
  "problemMatcher": []
}
```

## 📖 进阶技巧

### 监听文件变化自动转换

虽然任务系统不直接支持，但可以结合 VSCode 插件：

1. 安装 "Run on Save" 插件
2. 配置 `settings.json`:

```json
{
  "emeraldwalk.runonsave": {
    "commands": [
      {
        "match": "\\.md$",
        "cmd": "${workspaceFolder}/dist/md2docx.exe ${file}"
      }
    ]
  }
}
```

### 创建任务菜单

在 `.vscode/tasks.json` 中组织任务：

```json
{
  "version": "2.0.0",
  "tasks": [
    // 第一组：单文件转换
    { "label": "📄 单文件：当前目录输出", ... },
    { "label": "📄 单文件：output目录输出", ... },
    
    // 第二组：批量转换
    { "label": "📁 批量：当前目录", ... },
    { "label": "📁 批量：整个工作区", ... },
    
    // 第三组：工具任务
    { "label": "🔧 打开exe目录", ... },
    { "label": "🔧 查看帮助", ... }
  ]
}
```

使用 emoji 让任务列表更直观！

## 📚 相关资源

- [VSCode Tasks 官方文档](https://code.visualstudio.com/docs/editor/tasks)
- [VSCode Variables Reference](https://code.visualstudio.com/docs/editor/variables-reference)
- [md2docx.exe 使用说明](dist/README.md)

---

## 🎓 学习路径

1. ✅ **入门**: 使用默认任务转换单个文件
2. ✅ **进阶**: 自定义输出路径和任务
3. ✅ **高级**: 创建任务组合和自动化工作流
4. ✅ **专家**: 集成到 CI/CD 流程

---

**祝使用愉快！** 🚀

如有问题，请参考 [常见问题](#-常见问题) 或查看 [md2docx.exe 使用说明](dist/README.md)。
