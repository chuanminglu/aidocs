# Markdown 转 Word 工具 - 打包说明

## 打包成 EXE 可执行文件

本工具支持打包成独立的 exe 文件，无需安装 Python 环境即可运行。

### 📦 快速打包

#### Windows PowerShell

```powershell
# 执行打包脚本
.\build_exe.ps1
```

打包完成后，exe 文件位于 `dist\md2docx.exe`

### 🎯 绿色版特点

- ✅ **无需安装 Python** - 不需要在目标机器上安装 Python 环境
- ✅ **无需安装依赖** - 所有依赖库已打包进 exe 文件
- ✅ **一键运行** - 双击即可运行，或拖放文件
- ✅ **绿色便携** - 可以复制到 U 盘或其他电脑直接使用
- ✅ **体积优化** - 使用 UPX 压缩，减小文件体积

### 📝 使用方法

#### 方法 1: 命令行运行

```powershell
# 基本用法（自动生成输出文件名）
.\md2docx.exe input.md

# 指定输出文件名
.\md2docx.exe input.md -o output.docx

# 查看帮助
.\md2docx.exe --help
```

#### 方法 2: 拖放文件

直接将 `.md` 文件拖放到 `md2docx.exe` 图标上，自动转换并在同目录下生成 `.docx` 文件。

### 🔧 打包配置说明

#### spec 文件配置

打包配置文件为 `md2docx.spec`，主要配置项：

```python
# 主程序文件
['md2docx_optimized.py']

# 隐藏导入的模块（PyInstaller 自动检测不到的）
hiddenimports = [
    'docx',           # python-docx 核心库
    'markdown',       # Markdown 解析
    'plantuml',       # PlantUML 图表
    'PIL',            # 图像处理
    # ... 更多依赖
]

# 打包选项
console=True,      # 显示控制台窗口（方便查看转换进度）
upx=True,          # 使用 UPX 压缩（减小文件体积）
onefile=True,      # 打包成单个 exe 文件
```

#### 自定义配置

如需修改打包配置，编辑 `md2docx.spec` 文件：

```python
# 添加图标
icon='icon.ico'

# 修改 exe 名称
name='md2word'

# 不显示控制台窗口（适合 GUI 版本）
console=False
```

### 📊 打包流程

```mermaid
graph LR
    A[源代码] --> B[PyInstaller 分析]
    B --> C[收集依赖]
    C --> D[打包资源]
    D --> E[UPX 压缩]
    E --> F[生成 exe]
```

1. **分析依赖** - PyInstaller 自动分析 Python 代码依赖
2. **收集模块** - 收集所有需要的 Python 模块和库
3. **打包资源** - 将代码、库、资源打包成单一文件
4. **压缩优化** - 使用 UPX 压缩减小体积
5. **生成 exe** - 输出最终的可执行文件

### 🛠️ 故障排除

#### 问题 1: 打包失败

```
ModuleNotFoundError: No module named 'xxx'
```

**解决方法**: 在 `md2docx.spec` 的 `hiddenimports` 列表中添加缺失的模块

```python
hiddenimports = [
    # 原有模块...
    'xxx',  # 添加缺失的模块
]
```

#### 问题 2: exe 文件太大

**解决方法**:
1. 确保 `upx=True` 已启用
2. 在 `excludes` 中排除不需要的大型库

```python
excludes=['tkinter', 'matplotlib', 'numpy', 'pandas']
```

#### 问题 3: 运行时缺少文件

如果程序运行时提示缺少配置文件或资源文件：

```python
# 在 spec 文件中添加数据文件
datas = [
    ('config/*.yml', 'config'),
    ('data/templates/*', 'data/templates'),
]
```

#### 问题 4: 杀毒软件误报

部分杀毒软件可能将打包的 exe 识别为可疑程序：

- 添加到杀毒软件白名单
- 使用代码签名证书签名 exe 文件
- 向杀毒软件厂商报告误报

### 📋 手动打包步骤

如果不使用 `build_exe.ps1` 脚本，也可以手动打包：

```powershell
# 1. 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 2. 安装 PyInstaller
pip install pyinstaller

# 3. 清理旧文件
Remove-Item -Path build, dist -Recurse -Force -ErrorAction SilentlyContinue

# 4. 执行打包
pyinstaller --clean md2docx.spec

# 5. 测试生成的 exe
.\dist\md2docx.exe --help
```

### 🎨 添加图标（可选）

1. 准备一个 `.ico` 格式的图标文件
2. 修改 `md2docx.spec`:

```python
exe = EXE(
    # ... 其他配置
    icon='path/to/icon.ico',
)
```

3. 重新打包

### 📦 分发建议

#### 单文件分发

最简单的方式，直接分发 `md2docx.exe`:

```
md2docx.exe         # 约 20-30 MB
```

#### 压缩分发

使用 zip 或 7z 压缩可进一步减小分发体积：

```powershell
# 创建 zip 包
Compress-Archive -Path .\dist\md2docx.exe -DestinationPath md2docx_v1.0.zip
```

#### 创建安装程序（可选）

使用 NSIS、Inno Setup 等工具创建安装程序：

- 添加快捷方式
- 注册文件关联（.md 文件右键菜单）
- 添加到环境变量 PATH

### ✅ 测试清单

打包完成后，建议进行以下测试：

- [ ] 在没有 Python 环境的机器上测试
- [ ] 测试基本的 Markdown 转换功能
- [ ] 测试包含图表的文档转换
- [ ] 测试包含表格的文档转换
- [ ] 测试包含代码块的文档转换
- [ ] 测试中文文件名处理
- [ ] 测试命令行参数
- [ ] 测试拖放文件功能

### 📚 相关资源

- [PyInstaller 官方文档](https://pyinstaller.org/)
- [UPX 压缩工具](https://upx.github.io/)
- [NSIS 安装程序制作](https://nsis.sourceforge.io/)

### 🔄 更新打包版本

当代码更新后重新打包：

```powershell
# 清理并重新打包
.\build_exe.ps1
```

建议在文件名中包含版本号：

```python
# 在 spec 文件中
name='md2docx_v1.0',
```

---

**注意**: 首次打包可能需要较长时间（5-10分钟），后续打包会更快。
