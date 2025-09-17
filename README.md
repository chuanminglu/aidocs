# AI文档管理系统 🚀

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Poetry](https://img.shields.io/badge/Poetry-管理依赖-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)
![跨平台](https://img.shields.io/badge/跨平台-Windows%20%7C%20macOS%20%7C%20Linux-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

*一个现代化的AI驱动文档管理系统 - 支持跨平台开发*

</div>

## ✨ 项目简介

AI文档管理系统是一个**功能完整**的智能文档管理平台，专为个人和团队的文档管理需求而设计。系统采用现代化的桌面应用架构，提供直观的用户界面和强大的功能支持。

**🆕 现已支持跨平台开发！** 无论您使用Windows、macOS还是Linux，都能享受一致的开发体验。

### 🎯 核心特性

- **📝 Word文档支持**: 完整的Word文档编辑、解析和大纲导航
- **🖥️ 现代桌面界面**: 基于PyQt6的现代化用户界面
- **🔍 智能搜索**: 支持全文搜索和语义搜索
- **📊 大纲导航**: 自动解析文档结构，提供树形导航
- **🏷️ 标签分类**: 灵活的标签和分类系统
- **📋 模板管理**: 内置丰富的文档模板
- **🔄 实时同步**: 支持实时编辑和保存
- **🌐 API支持**: RESTful API接口支持
- **🚀 跨平台兼容**: Windows/macOS/Linux统一开发环境

## � 快速开始

### 方法1：自动化设置（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd aidocs

# 运行自动化设置脚本
.\setup-dev-env.ps1  # Windows
pwsh setup-dev-env.ps1  # macOS/Linux
```

### 方法2：手动设置

1. **安装Poetry**
   ```bash
   # Windows
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   
   # macOS
   brew install poetry
   
   # Linux
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **安装依赖**
   ```bash
   poetry install
   ```

3. **VS Code配置**
   ```bash
   code .  # 打开项目
   # Ctrl+Shift+P → Tasks: Run Task → Poetry: 查看依赖
   ```

## 💻 VS Code 开发环境

本项目已配置完整的VS Code开发环境，支持跨平台使用。

### 🎯 可用任务

在VS Code中按 `Ctrl+Shift+P` → `Tasks: Run Task` 可以使用以下任务：

#### 📄 文档转换
- **MD转DOCX：当前文件** - 转换当前Markdown文件为Word文档
- **MD转DOCX：选择文件转换** - 选择文件进行转换

#### 🛠️ Poetry管理
- **Poetry: 安装依赖** - 安装项目依赖
- **Poetry: 添加依赖** - 添加新的Python包
- **Poetry: 查看依赖** - 显示已安装包列表
- **Poetry: 运行测试** - 执行项目测试
- **Poetry: 代码格式化** - 使用Black格式化代码
- **Poetry: 代码检查** - 使用Flake8检查代码

#### 🧹 系统维护
- **删除文件** - 跨平台文件删除（Windows/Unix）
- **刷新工作空间** - 刷新文件状态
- **工作空间清理** - 清理临时文件

### 📚 详细说明

更多配置信息请参考：[跨平台tasks配置说明](docs/跨平台tasks配置说明.md)

## �🛠️ 技术栈

### 依赖管理
- **Poetry**: 现代Python依赖管理和构建工具
- **跨平台支持**: Windows、macOS、Linux

### 前端 (桌面客户端)
- **PyQt6**: 现代化跨平台桌面应用框架
- **Python-docx**: Word文档处理
- **Markdown**: 轻量级标记语言支持

### 后端 (API服务)
- **FastAPI**: 高性能异步Web框架
- **SQLAlchemy**: 数据库ORM
- **SQLite**: 轻量级数据库
- **Whoosh**: 全文搜索引擎

### 开发工具
- **Git**: 版本控制
- **PowerShell**: 自动化脚本
- **VS Code**: 推荐开发环境

## 📁 项目结构

```
aidocs/
├── 📁 src/                    # 源代码
│   ├── 🖥️ gui/               # PyQt6 桌面客户端
│   │   ├── main_window.py    # 主窗口
│   │   ├── document_editor.py # 文档编辑器
│   │   ├── document_outline_navigator.py # 大纲导航器
│   │   ├── template_manager_gui.py # 模板管理器
│   │   └── find_replace_dialog.py # 查找替换对话框
│   ├── 🌐 api/               # FastAPI 后端服务
│   │   ├── main.py          # API主入口
│   │   ├── routers/         # API路由
│   │   ├── models/          # 数据模型
│   │   └── schemas/         # 数据结构
│   ├── 🔧 core/              # 核心业务逻辑
│   │   ├── word_parser.py   # Word文档解析器
│   │   ├── template_manager.py # 模板管理器
│   │   ├── ai_service.py    # AI服务
│   │   └── database.py      # 数据库操作
│   └── 🛠️ utils/             # 工具函数
├── 📄 data/                  # 数据存储
│   ├── documents/           # 文档存储
│   ├── templates/           # 模板库
│   ├── database/            # 数据库文件
│   └── cache/               # 缓存文件
├── ⚙️ config/                # 配置文件
├── 📚 docs/                  # 项目文档
├── 🔨 scripts/               # 辅助脚本
└── 📋 requirements.txt       # 依赖列表
```

## 🚀 快速开始

### 📋 系统要求

- **Python 3.12+**
- **Windows 10/11** (推荐)
- **4GB RAM** (最低)
- **500MB** 硬盘空间

### ⚡ 一键启动

**重要提醒**: 本项目必须在虚拟环境中运行！

```powershell
# 1. 克隆项目
git clone https://github.com/chuanminglu/aidocs.git
cd aidocs

# 2. 自动创建虚拟环境并安装依赖
.\scripts\setup_venv.ps1

# 3. 启动完整应用
.\scripts\dev_start.ps1 -Service all
```

### 🔧 开发模式

```powershell
# 开发模式（支持热重载）
.\scripts\dev_start.ps1 -Service all -Dev

# 分别启动各服务
.\scripts\dev_start.ps1 -Service api    # 仅启动API服务
.\scripts\dev_start.ps1 -Service gui    # 仅启动桌面客户端
```

### 🎯 手动启动

```powershell
# 激活虚拟环境
.\aidocs-env\Scripts\Activate.ps1

# 启动API服务
uvicorn src.api.main:app --reload --port 8000

# 启动桌面客户端
python src/gui/main_window.py
```

## 📱 功能特性

### ✅ 已完成功能

- **📝 Word文档支持**
  - 完整的.docx文档解析和编辑
  - 自动大纲结构识别
  - 支持中英文内容
  - 多级备用解析器

- **🖥️ 桌面应用界面**
  - 现代化PyQt6界面
  - 文档编辑器（支持Markdown和Word）
  - 大纲导航器（树形结构）
  - 查找替换功能
  - 模板管理器

- **🌐 API服务**
  - FastAPI后端服务
  - RESTful API接口
  - 数据库集成
  - 文档管理接口

- **🔍 搜索功能**
  - 全文搜索支持
  - 智能大纲导航
  - 实时内容过滤

### 🔄 开发路线图

#### 第一阶段 - 核心功能 (✅ 已完成)
- [x] 项目架构搭建
- [x] Word文档解析器
- [x] 桌面应用界面
- [x] 大纲导航功能
- [x] 基础文档编辑
- [x] API服务集成

#### 第二阶段 - 增强功能 (🔄 进行中)
- [ ] Whoosh全文搜索引擎
- [ ] 智能搜索功能
- [ ] 文档模板系统完善
- [ ] 标签分类系统
- [ ] 数据库优化

#### 第三阶段 - 高级功能 (📋 计划中)
- [ ] AI智能助手集成
- [ ] 知识图谱构建
- [ ] 协作功能
- [ ] 云同步支持
- [ ] 移动端适配

## 📖 使用指南

### 💡 Word文档使用建议

1. **推荐格式**: 使用标准的.docx格式
2. **文档结构**: 使用内置标题样式（标题1、标题2等）
3. **内容规范**: 避免复杂的嵌入对象和表格
4. **编码要求**: 使用UTF-8编码，支持中英文

详细使用指南请参考: [Word文档支持说明](docs/Word文档支持说明.md)

### 🎨 界面功能

- **文档编辑**: 左侧主编辑区域，支持Markdown和Word文档
- **大纲导航**: 右侧大纲树，自动解析文档结构
- **菜单栏**: 文件操作、编辑功能、API服务管理
- **工具栏**: 常用功能快捷按钮

## 🔧 开发指南

### 📝 开发环境配置

1. **Python版本**: 3.12+
2. **虚拟环境**: 必须使用项目自带的虚拟环境
3. **IDE推荐**: VS Code + Python扩展
4. **代码规范**: PEP 8

### 🏗️ 项目结构说明

- **src/gui/**: PyQt6桌面应用代码
- **src/api/**: FastAPI后端服务代码
- **src/core/**: 核心业务逻辑（文档解析、模板管理等）
- **data/**: 数据存储目录
- **docs/**: 项目文档和说明
- **scripts/**: 自动化脚本

### 🧪 测试和调试

```powershell
# 启动开发模式
.\scripts\dev_start.ps1 -Service all -Dev

# 检查API服务状态
curl http://localhost:8000/health

# 查看日志
Get-Content logs/app.log -Wait
```

### 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 相关文档

- [PRD产品需求文档](docs/prd.md)
- [任务管理文档](docs/tasks.md)
- [Word文档支持说明](docs/Word文档支持说明.md)
- [项目进度跟踪](docs/项目进度跟踪.md)
- [系统设计文档](docs/文档模板管理系统设计.md)

## 🐛 问题反馈

如果您在使用过程中遇到问题，请通过以下方式反馈：

1. [GitHub Issues](https://github.com/chuanminglu/aidocs/issues)
2. 邮件: chuanminglu@example.com

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👥 贡献者

感谢所有为这个项目做出贡献的开发者！

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个星标！**

Made with ❤️ by [chuanminglu](https://github.com/chuanminglu)

</div>
