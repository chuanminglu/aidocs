# AI文档管理系统

## 项目概述

AI文档管理系统是一个智能化的个人文档管理平台，支持从时间维度和专业领域维度进行双重索引和快速检索。采用现代化的桌面应用架构，集成AI能力，提供高效的文档管理体验。

## 技术架构

- **桌面客户端**: PyQt6 (现代化桌面界面)
- **后端API**: FastAPI (高性能异步API)
- **数据库**: SQLAlchemy + PostgreSQL/SQLite
- **AI服务**: DeepSeek API (智能文档处理)
- **搜索引擎**: Elasticsearch/Whoosh (全文检索)
- **文件存储**: 本地文件系统 + 云存储扩展

## 项目结构

```
aidocs/
├── src/                    # 源代码
│   ├── gui/               # PyQt6 桌面客户端
│   │   ├── main_window.py
│   │   ├── dialogs/
│   │   ├── widgets/
│   │   └── resources/
│   ├── api/               # FastAPI 后端服务
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── dependencies/
│   ├── core/              # 核心业务逻辑
│   │   ├── document_manager.py
│   │   ├── template_manager.py
│   │   ├── search_engine.py
│   │   └── ai_service.py
│   └── utils/             # 工具函数
├── data/                  # 数据存储
│   ├── documents/         # 文档存储
│   ├── templates/         # 模板库
│   ├── database/          # 数据库文件
│   └── cache/             # 缓存文件
├── config/                # 配置文件
├── tests/                 # 测试文件
├── docs/                  # 文档说明
└── scripts/               # 辅助脚本
```

## 快速开始

**重要：本项目严格要求在虚拟环境中开发和运行！**

### 第一步：创建虚拟环境

```powershell
# 自动创建和配置虚拟环境
.\scripts\setup_venv.ps1
```

### 第二步：启动应用

```powershell
# 启动所有服务（推荐）
.\scripts\dev_start.ps1 -Service all

# 或者分别启动
.\scripts\dev_start.ps1 -Service api    # 仅启动API服务
.\scripts\dev_start.ps1 -Service gui    # 仅启动桌面客户端
```

### 开发模式

```powershell
# 开发模式（自动重载）
.\scripts\dev_start.ps1 -Service all -Dev

# 或者手动启动
.\aidocs-env\Scripts\Activate.ps1               # 激活虚拟环境
uvicorn src.api.main:app --reload --port 8000   # 启动API服务
python src/gui/main_window.py --dev             # 启动桌面客户端
```

### 虚拟环境管理

详细的虚拟环境管理指南请参考：[虚拟环境管理文档](docs/virtual_environment.md)

## 功能特性

### 阶段1 - MVP功能 (当前)

- [x] 基础文件结构
- [ ] 文档模板系统
- [ ] 分类与标签
- [ ] 基础搜索
- [ ] Web界面

### 阶段2 - 增强功能

- [ ] 高级搜索
- [ ] 知识图谱
- [ ] AI增强
- [ ] 协作功能

### 阶段3 - 高级功能

- [ ] 移动端适配
- [ ] 插件系统
- [ ] API接口
- [ ] 云同步

## 开发指南

详细的开发指南请参考 [开发文档](docs/development.md)

## 许可证

MIT License
