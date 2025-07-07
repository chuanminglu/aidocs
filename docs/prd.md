# AI文档管理系统 - 产品需求文档 (PRD)

## 1. 产品概述

### 1.1 产品名称
AI文档管理系统 (AI Document Management System)

### 1.2 产品愿景
创建一个智能化的个人文档管理平台，支持从时间维度和专业领#### 3.2.2 导入导出功能
- **多格式支持**：Markdown、Word、PDF、TXT等
- **Word文档支持**：
  - 支持读取.docx和.doc格式文件
  - 将Word文档转换为Markdown格式进行编辑
  - 支持保存为Word格式输出
  - Word文档大纲结构自动识别和导航
  - 只读模式浏览Word文档原格式
- **批量导入**：支持现有文档批量导入和分类
- **导出功能**：支持按条件导出文档集合行双重索引和快速检索，帮助用户高效管理日常工作思路、研究成果和知识积累。

### 1.3 产品定位
面向知识工作者的个人文档管理工具，特别适用于研究人员、技术专家、顾问等需要长期积累和频繁查找专业知识的用户。

## 2. 用户需求分析

### 2.1 目标用户
- 技术研究人员
- 项目经理
- 咨询顾问
- 知识工作者
- 学生和学者

### 2.2 用户痛点
- 文档分散存储，难以统一管理
- 缺乏有效的分类和标签系统
- 难以根据时间和专业领域快速定位文档
- 无法追踪思维演进过程
- 缺乏关联性发现机制

### 2.3 核心需求
1. **双维度索引**：时间维度 + 专业领域维度
2. **快速检索**：支持全文搜索和标签过滤
3. **知识关联**：自动发现和建立文档间的关联关系
4. **版本管理**：追踪文档和思维的演进过程
5. **智能分类**：自动标签和分类建议

## 3. 功能需求

### 3.1 核心功能

#### 3.1.1 文档组织架构
```
AI文档s/
├── 时间维度/
│   ├── 2024/
│   │   ├── 01-January/
│   │   │   ├── 日报/
│   │   │   ├── 周报/
│   │   │   └── 月报/
│   │   └── ...
│   └── 2025/
├── 专业维度/
│   ├── DevOps/
│   │   ├── 质量工程/
│   │   ├── 持续集成/
│   │   ├── 监控运维/
│   │   └── 自动化部署/
│   ├── 人工智能/
│   │   ├── 机器学习/
│   │   ├── 深度学习/
│   │   └── 自然语言处理/
│   └── 项目管理/
├── 索引系统/
│   ├── 标签索引/
│   ├── 时间索引/
│   └── 关联图谱/
└── 模板库/
```

#### 3.1.2 文档模板管理系统
- **可视化模板编辑器**：类似现代IDE的编辑体验，支持拖拽组件、实时预览
- **富文本编辑模式**：支持Markdown、HTML、Word等多种格式编辑
- **模板变量系统**：支持动态变量、占位符、函数调用等高级功能
- **版本控制**：完整的模板版本管理和差异比较
- **分类管理**：层次化的模板分类和标签系统
- **协作功能**：模板分享、评论、建议编辑等团队协作功能
- **AI增强**：智能模板优化、内容建议、变量推荐
- **多格式输出**：支持导出为Markdown、HTML、Word、PDF等格式

#### 3.1.3 双维度索引系统
- **时间索引**：按年/月/日/周组织文档
- **专业索引**：按技术领域、项目、主题分类
- **交叉索引**：支持文档同时出现在多个维度下
- **智能标签**：自动生成和建议标签

#### 3.1.4 搜索与发现
- **全文搜索**：支持关键词、短语、正则表达式搜索
- **多维过滤**：按时间、标签、类型、大小等条件过滤
- **关联推荐**：基于内容相似度推荐相关文档
- **智能聚合**：自动聚合相关主题的文档

#### 3.1.5 知识图谱
- **概念关联**：自动识别文档中的概念和实体
- **关系发现**：发现文档间的引用、相似、演进关系
- **可视化展示**：图形化展示知识网络
- **路径分析**：追踪思维演进路径

### 3.2 模板管理功能

#### 3.2.1 模板编辑器
- **三面板设计**：左侧目录树 + 中间大纲导航 + 右侧编辑器/预览区
- **大纲导航功能**：类似Word的文档目录导航，支持标题层级显示、点击跳转、实时同步
  - 自动识别文档标题结构（H1-H6）
  - 树形结构显示文档大纲
  - 点击大纲节点快速跳转到对应内容
  - 编辑器光标位置与大纲导航实时同步
  - 支持大纲节点的折叠/展开
  - 提供大纲搜索和过滤功能
- **可视化编辑**：拖拽式组件编辑，支持文本、标题、列表、表格等组件
- **源码编辑**：Monaco Editor级别的编辑体验，支持语法高亮和智能提示
- **多模式切换**：源码模式、富文本模式、分屏模式、全屏模式
- **主题系统**：支持多种预览主题（GitHub、学术、商务等）

#### 3.2.2 模板组织系统
- **层次化分类**：工作模板、研究模板、项目模板等多级分类
- **标签系统**：支持多标签、标签颜色、使用统计
- **搜索功能**：模板名称、内容、标签的全文搜索
- **收藏功能**：个人收藏夹和团队共享收藏
- **使用统计**：模板使用频率、评分、推荐指数

#### 3.2.3 模板变量系统
- **变量类型**：文本、日期、选择、占位符、函数调用等
- **智能变量**：自动获取用户信息、系统信息、环境变量
- **条件变量**：根据条件显示不同内容
- **循环变量**：支持列表数据的循环渲染
- **函数支持**：内置函数库，支持自定义函数

#### 3.2.4 协作与分享
- **模板分享**：生成分享链接，支持权限控制
- **协作编辑**：多人同时编辑，实时同步
- **评论系统**：行级评论、建议编辑、讨论区
- **版本控制**：完整的版本历史、差异比较、回滚功能
- **团队模板库**：部门级、公司级模板共享

### 3.3 辅助功能

#### 3.3.1 AI智能功能
- **模板优化建议**：AI分析模板结构和内容，提供优化建议
- **内容生成**：根据描述自动生成模板框架
- **变量推荐**：智能识别可参数化的内容，建议变量设置
- **智能补全**：编辑时的智能内容补全和建议
- **模板推荐**：基于使用习惯和内容相似度的智能推荐

#### 3.3.2 导入导出功能
- **多格式支持**：Markdown、Word、PDF、TXT等
- **批量导入**：支持现有文档批量导入和分类
- **导出功能**：支持按条件导出文档集合

#### 3.3.3 系统集成功能
- **Git集成**：模板版本控制和协作开发
- **外部编辑器**：支持调用外部编辑器（VS Code、Word等）
- **插件系统**：支持第三方插件扩展功能
- **API接口**：提供完整的REST API用于集成

#### 3.3.4 API服务管理
- **服务控制**：在GUI界面中提供API服务的启动、停止、重启功能
- **状态监控**：实时显示API服务运行状态和健康检查
- **配置管理**：支持API服务的基础配置修改（端口、地址等）
- **虚拟环境支持**：确保API服务在项目虚拟环境中运行
- **错误处理**：提供API服务异常时的诊断和恢复建议
- **用户体验**：通过图形界面操作，无需手动命令行管理

## 4. 技术架构

### 4.1 技术栈
- **前端**：PyQt6 + Python (桌面应用)
- **后端**：FastAPI + SQLAlchemy + SQLite/PostgreSQL
- **搜索引擎**：Whoosh 或 Elasticsearch
- **AI服务**：DeepSeek API + 本地嵌入模型
- **版本控制**：Git
- **数据处理**：Pandas + NumPy
- **文本处理**：jieba + transformers
- **Word文档处理**：python-docx + docx2txt

### 4.2 系统架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户界面层    │    │   应用逻辑层    │    │   数据存储层    │
│  PyQt6 GUI      │◄──►│  FastAPI Server │◄──►│   SQLite DB     │
│  主窗口界面     │    │  业务逻辑层     │    │   文件系统      │
│  搜索组件       │    │  AI服务集成     │    │   搜索索引      │
│  知识图谱组件   │    │  索引管理器     │    │   向量数据库    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 4.3 核心组件架构
```
AI文档管理系统
├── gui/                    # PyQt6 用户界面
│   ├── main_window.py     # 主窗口
│   ├── template_editor.py # 模板编辑器（核心组件）
│   ├── template_manager.py # 模板管理器
│   ├── search_widget.py   # 搜索组件
│   ├── graph_widget.py    # 知识图谱组件
│   ├── document_editor.py # 文档编辑器
│   └── preview_widget.py  # 预览组件
├── api/                   # FastAPI 后端服务
│   ├── main.py           # API 主入口
│   ├── routers/          # API 路由
│   ├── models/           # 数据模型
│   └── services/         # 业务逻辑
├── core/                 # 核心功能模块
│   ├── document_manager.py # 文档管理
│   ├── template_engine.py  # 模板引擎（核心组件）
│   ├── template_manager.py # 模板管理器
│   ├── search_engine.py   # 搜索引擎
│   ├── ai_service.py      # AI 服务
│   ├── collaboration.py  # 协作功能
│   ├── word_parser.py     # Word文档解析器（新增）
│   └── index_manager.py   # 索引管理
└── data/                 # 数据存储
    ├── documents.db      # SQLite 数据库
    ├── templates/        # 模板文件存储（核心目录）
    │   ├── system/       # 系统默认模板
    │   ├── user/         # 用户自定义模板
    │   ├── shared/       # 共享模板
    │   └── versions/     # 模板版本历史
    ├── search_index/     # 搜索索引
    └── embeddings/       # 向量嵌入
```

### 4.4 数据模型
```python
# SQLAlchemy 数据模型
from sqlalchemy import Column, String, DateTime, Text, JSON, Float, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(String, primary_key=True)
    title = Column(String(255))
    content = Column(Text)
    file_path = Column(String(500))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    tags = Column(JSON)  # 存储标签数组
    category = Column(String(100))
    summary = Column(Text)
    metadata = Column(JSON)
    embedding = Column(JSON)  # 存储文档向量嵌入

class Template(Base):
    __tablename__ = 'templates'
    
    id = Column(String, primary_key=True)
    name = Column(String(255))
    description = Column(Text)
    category = Column(String(100))
    subcategory = Column(String(100))
    content = Column(Text)
    variables = Column(JSON)  # 模板变量定义
    metadata = Column(JSON)   # 模板元数据
    version = Column(String(50))
    author = Column(String(100))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    usage_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    tags = Column(JSON)
    preview_image = Column(String(500))
    is_public = Column(Boolean, default=False)
    is_system = Column(Boolean, default=False)

class TemplateVersion(Base):
    __tablename__ = 'template_versions'
    
    id = Column(String, primary_key=True)
    template_id = Column(String)
    version = Column(String(50))
    content = Column(Text)
    comment = Column(Text)
    created_at = Column(DateTime)
    created_by = Column(String(100))

class TemplateShare(Base):
    __tablename__ = 'template_shares'
    
    id = Column(String, primary_key=True)
    template_id = Column(String)
    shared_by = Column(String(100))
    shared_with = Column(String(100))
    permissions = Column(JSON)  # 权限设置
    created_at = Column(DateTime)
    expires_at = Column(DateTime)

class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(String, primary_key=True)
    name = Column(String(100), unique=True)
    category = Column(String(50))
    description = Column(Text)
    color = Column(String(7))
    usage_count = Column(Integer, default=0)

class DocumentRelation(Base):
    __tablename__ = 'document_relations'
    
    id = Column(String, primary_key=True)
    source_doc_id = Column(String)
    target_doc_id = Column(String)
    relation_type = Column(String(50))
    confidence = Column(Float)
    created_at = Column(DateTime)
```

## 5. 用户界面设计

### 5.1 主界面布局
```
┌─────────────────────────────────────────────────────────────────┐
│  AI文档管理系统                                     🔍 搜索框   │
├─────────────────────────────────────────────────────────────────┤
│ 📁 时间维度 │ 📊 专业维度 │ � 模板库 │ �🔗 知识图谱 │ 📝 新建 │ ⚙️ │
├─────────────┼─────────────┼─────────┼────────────┼────────┼──┤
│             │             │         │            │        │  │
│  📅 2024    │  💻 DevOps  │ 🏢 工作  │    图谱    │  模板  │设│
│  ├─12月     │  ├─质量工程 │ ├─日报   │    可视化  │  选择  │置│
│  ├─11月     │  ├─CI/CD    │ ├─周报   │    展示    │  界面  │管│
│  └─10月     │  └─监控     │ └─月报   │            │        │理│
│             │             │         │            │        │  │
│  📈 AI      │  🚀 项目    │ 🔬 研究  │            │        │  │
│  ├─机器学习 │  ├─Alpha    │ ├─技术   │            │        │  │
│  └─NLP      │  └─Beta     │ ├─分析   │            │        │  │
│             │             │ └─笔记   │            │        │  │
│             │             │         │            │        │  │
│             │             │ 👤 个人  │            │        │  │
│             │             │ ├─我的   │            │        │  │
│             │             │ └─收藏   │            │        │  │
└─────────────┴─────────────┴─────────┴────────────┴────────┴──┘
```

### 5.2 模板编辑器界面
```
┌─────────────────────────────────────────────────────────────────┐
│  模板编辑器 - 日报模板                       � 保存 👁️ 预览 ❌ │
├─────────────────────────────────────────────────────────────────┤
│ 📁 模板目录     │        📝 编辑区         │    👁️ 预览区      │
│ ├─🏢 工作模板   │ # 日报模板               │ ┌─────────────────┐ │
│ │ ├─📊 日报    │ **日期**: {date}         │ │ 日报模板        │ │
│ │ ├─📈 周报    │ **作者**: {author}       │ │ 日期: 2025-07-04│ │
│ │ └─📋 月报    │                          │ │ 作者: 用户      │ │
│ ├─🔬 研究模板   │ ## 今日目标             │ │                 │ │
│ │ ├─📝 技术    │ - [ ] 目标1             │ │ 今日目标        │ │
│ │ ├─📊 分析    │ - [ ] 目标2             │ │ □ 目标1         │ │
│ │ └─📄 笔记    │                          │ │ □ 目标2         │ │
│ └─👤 我的模板   │ ## 工作内容             │ │                 │ │
│                 │ {work_content}           │ │ 工作内容        │ │
├─────────────────┼──────────────────────────┼─────────────────────┤
│ ⚙️ 模板属性     │ 📝 源码 | 🎨 富文本 | 📱分屏 │   🎨 主题切换    │
│ 名称: 日报模板  │                          │ GitHub | 学术 | 商务│
│ 分类: 工作模板  │                          │                     │
│ 标签: #日报     │                          │                     │
│ ┌─────────────┐ │                          │                     │
│ │ 🔧 变量管理 │ │                          │                     │
│ │ {date}      │ │                          │                     │
│ │ {author}    │ │                          │                     │
│ │ {weather}   │ │                          │                     │
│ └─────────────┘ │                          │                     │
└─────────────────┴──────────────────────────┴─────────────────────┘
```

### 5.3 搜索界面
- 智能搜索建议和自动补全
- 多维度过滤器（模板、文档、标签、时间）
- 结果按相关度和使用频率排序
- 支持模板和文档的统一搜索
- 搜索结果预览功能

### 5.4 知识图谱界面
- 交互式图形展示文档和模板关联
- 节点和边的详细信息展示
- 支持缩放、平移、筛选功能
- 路径高亮和关系追踪
- 模板使用关系可视化

## 6. 实施计划

### 6.1 第一阶段（MVP）- 2周
- [x] 基础文件夹结构创建
- [x] 文档模板系统
- [x] 简单的分类和标签功能
- [x] 基础搜索功能

### 6.2 第二阶段（增强版）- 4周
- [ ] 数据库集成
- [ ] 高级搜索和过滤
- [ ] AI智能分类和标签
- [ ] 基础关联发现
- ✅ **Word文档支持基础功能** - 已完成
  - ✅ Word文档读取和解析
  - ✅ 转换为Markdown编辑模式
  - ✅ 大纲导航支持
  - ✅ GUI编辑器集成
  - ✅ 保存为Word格式功能

### 6.3 第三阶段（完整版）- 6周
- [ ] 知识图谱可视化
- [ ] 智能推荐系统
- [ ] 协作功能
- [ ] 性能优化
- [ ] **Word文档支持完整功能**
  - Word格式保存和导出
  - 复杂Word文档处理
  - Word文档批量转换
  - 格式保持和样式处理

## 7. 成功指标

### 7.1 功能指标
- 文档检索速度 < 500ms
- 标签准确率 > 85%
- 关联推荐准确率 > 80%
- 支持文档数量 > 10,000

### 7.2 用户体验指标
- 文档创建时间 < 30s
- 搜索结果满意度 > 90%
- 系统响应时间 < 200ms
- 用户学习成本 < 30分钟

## 8. 风险与挑战

### 8.1 技术风险
- AI服务的稳定性和成本
- 大规模文档的性能问题
- 搜索精度的平衡
- Word文档格式兼容性问题

### 8.2 缓解策略
- 本地AI模型备选方案
- 分片和缓存策略
- 多重搜索算法结合
- Word文档隔离处理模块

## 9. 后续规划

### 9.1 功能扩展
- 移动端应用
- 云端同步
- 团队协作版本
- 插件系统

### 9.2 生态建设
- 开发者API
- 第三方集成
- 社区模板库
- 用户社区

---

**文档版本**: v1.0  
**创建日期**: 2025年7月4日  
**最后更新**: 2025年7月4日  
**负责人**: AI Assistant  
**状态**: 待评审
