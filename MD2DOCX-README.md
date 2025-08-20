# MD2DOCX - Markdown到Word转换工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

专业的Markdown到Word文档转换工具，特别优化技术文档转换需求。

## ⭐ 主要特性

- 🚀 **完整格式支持** - 标题、段落、列表、表格、代码块、链接等
- 💻 **代码友好** - 完美保留代码块换行和格式
- 📊 **图表渲染** - 支持Mermaid、PlantUML图表自动渲染
- 🎨 **专业样式** - 微软雅黑字体、统一排版、美观布局
- ⚡ **智能优化** - 根据内容类型智能处理格式
- 🔧 **VS Code集成** - 完美集成VS Code任务系统，支持快捷键操作

## 🚀 快速开始

### 安装依赖

```bash
pip install python-docx pillow lxml PyYAML Markdown loguru
```

### 基础使用

```bash
# 推荐：使用优化版本（完美处理代码块换行）
python md2docx_optimized.py input.md -o output.docx

# 标准版本
python md2docx.py input.md -o output.docx
```

### VS Code集成使用（推荐⭐⭐⭐⭐⭐）

#### 🔧 使用方法：
1. **打开Markdown文件**
2. **按 `Ctrl+Shift+P`** 打开命令面板
3. **输入 "Tasks: Run Task"**
4. **选择以下任务之一：**
   - `MD转DOCX：当前文件` - 转换当前打开的文件
   - `MD转DOCX：选择文件转换` - 选择任意文件转换

#### ⌨️ 快捷键：
- **`Ctrl+Shift+D`** - 转换当前打开的Markdown文件（仅在Markdown文件中有效）
- **`Ctrl+Alt+D`** - 选择文件进行转换

## 📋 版本对比

| 功能 | 标准版本 | 优化版本 ⭐ |
|------|----------|------------|
| 基础转换 | ✅ | ✅ |
| 图表渲染 | ✅ | ✅ |
| 表格处理 | ✅ | ✅ |
| 代码块换行 | ❌ | ✅ |
| 命令行格式 | ❌ | ✅ |
| VS Code集成 | ❌ | ✅ |

**推荐使用优化版本**，特别是处理技术文档时。

## 📖 支持的格式

### 基础语法
- 标题 (`# ## ###`)
- 粗体斜体 (`**bold** *italic*`)
- 代码 (`` `code` ``)
- 链接 (`[text](url)`)

### 代码块
````markdown
```python
def hello():
    print("Hello, World!")
```
````

### 表格
```markdown
| 列1 | 列2 | 列3 |
|-----|:---:|----:|
| 左 | 中 | 右 |
```

### 图表
````markdown
```mermaid
graph TD
    A --> B
    B --> C
```
````

## 🎯 功能特点详解

### ✅ 优化特性：
- **完美保留代码块换行** - 代码格式完全保持
- **支持PlantUML/Mermaid图表** - 自动渲染为图片
- **表格格式美观** - 自动调整表格样式
- **中文文件名支持** - 完全支持中文路径和文件名
- **微软雅黑字体** - 默认使用微软雅黑，显示效果佳
- **专业文档布局** - 自动设置页眉页脚、页码等

### � 支持的内容类型：
- 标题（H1-H6）
- 段落和换行
- **粗体**和*斜体*
- 代码块和行内代码
- 列表（有序/无序）
- 表格
- 链接和图片
- 引用块
- 分割线
- PlantUML图表
- Mermaid图表

## 🔧 VS Code集成配置

### 任务配置

项目已预配置 `tasks.json` 文件，包含两个任务：

1. **当前文件转换** - 使用 `${file}` 变量转换当前打开的文件
2. **选择文件转换** - 使用输入提示选择任意文件进行转换

### VS Code设置优化

已配置以下优化设置：

```json
{
    // Markdown预览优化
    "markdown.preview.breaks": true,
    "markdown.preview.linkify": true,
    
    // 任务自动检测
    "task.autoDetect": "on",
    
    // Markdown编辑器优化
    "[markdown]": {
        "editor.wordWrap": "on",
        "editor.minimap.enabled": false,
        "files.trimTrailingWhitespace": false
    }
}
```

### 操作流程示例

#### 场景1：转换当前编辑的文件
```
1. 打开 .md 文件
2. 按 Ctrl+Shift+D
3. 查看转换结果
```

#### 场景2：从命令面板选择任务
```
1. 按 Ctrl+Shift+P
2. 输入 "Tasks: Run Task"
3. 选择转换任务
4. 等待转换完成
```

### 最佳实践建议

#### 日常使用推荐：
1. **编辑时转换**：使用 `Ctrl+Shift+D` 快速转换当前文件
2. **任务选择**：使用 `Ctrl+Shift+P` → "Tasks: Run Task"
3. **默认构建**：设置为默认构建任务，使用 `Ctrl+Shift+B`

#### 🔥 专业提示：
- **快捷键记忆**：`Ctrl+Shift+D` 专用于Markdown转换
- **键盘操作流**：`Ctrl+Shift+P` → 输入 "task" → 选择任务
- **设置默认任务**：可在tasks.json中设置 `"isDefault": true`

## �📁 项目结构

```
md2docx/
├── md2docx.py                    # 标准版本
├── md2docx_optimized.py          # 优化版本 ⭐
├── docs/
│   └── MD2DOCX使用指南.md         # 完整文档
├── .vscode/                      # VS Code配置
│   ├── tasks.json               # 任务配置
│   ├── keybindings.json         # 快捷键配置
│   └── settings.json            # 工作区设置
└── src/
    └── md2doc/
        ├── core/                 # 核心转换模块
        ├── engines/              # 图表渲染引擎
        └── utils/                # 工具函数
```

## 🎯 使用场景

- **技术文档** - API文档、开发指南
- **培训材料** - 课程文档、操作手册  
- **项目报告** - 进度汇总、技术分析
- **VS Code开发** - 编辑器内一键转换

## 🐛 故障排除

### 常见问题

**Q: 代码块换行显示不正确？**
A: 使用优化版本 `md2docx_optimized.py`

**Q: 图表显示为代码？**
A: 确保安装图表渲染依赖

**Q: VS Code任务无法运行？**
A: 检查Python环境和文件路径是否正确

### Python环境问题
```bash
# 确保Python环境已激活
.\aidocs-env\Scripts\activate

# 检查依赖包
pip list | findstr python-docx
pip list | findstr markdown
```

### 编码问题
- 确保Markdown文件保存为UTF-8编码
- 使用VS Code时会自动处理编码问题

### 路径问题
- 使用绝对路径避免相对路径问题
- 中文路径需要使用引号包围

## � 完整文档

详细使用指南请参考：[MD2DOCX使用指南](docs/MD2DOCX使用指南.md)

## �📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🚀 快速体验

```bash
# 创建测试文件
echo "# 测试文档

## 代码示例
\`\`\`python
print('Hello, MD2DOCX!')
\`\`\`" > test.md

# 方法1：命令行转换
python md2docx_optimized.py test.md

# 方法2：VS Code中按 Ctrl+Shift+D

# 查看生成的 test.docx 文件
```

## 📞 支持和反馈

如遇到问题或有改进建议，请：
1. 检查控制台输出的详细错误信息
2. 确认文件路径和权限
3. 提交问题报告时请包含：
   - 错误信息
   - 输入文件示例
   - 系统环境信息

---

⭐ **推荐使用优化版本配合VS Code获得最佳体验！**
