# MD2DOC项目说明文档

> 📝 **文档版本**: v1.0  
> 📅 **更新时间**: 2025年8月1日  
> 👤 **维护者**: 项目开发团队  
> 🎯 **用途**: AI上下文管理、项目状态跟踪、功能说明

---

## 🎯 项目概述

### 产品定位
MD2DOC是一个**智能化的Markdown到Word文档转换工具**，专注于将技术文档从Markdown格式高质量地转换为专业的Word文档，特别支持图表渲染、代码高亮、表格处理等技术文档常见元素。

### 核心价值
- 🚀 **提升文档交付效率**: 自动化转换流程，减少手工排版时间
- 📊 **专业图表支持**: 支持Mermaid、PlantUML等流行图表语言
- 🎨 **保持格式一致性**: 确保转换后的Word文档格式规范统一
- 🔧 **技术文档友好**: 针对技术文档的特殊需求进行优化

---

## 🏗️ 技术架构

### 整体架构
```
MD2DOC系统架构
├── 输入层 (Markdown文件)
├── 解析层 (MarkdownParser)
├── 渲染层 (多引擎渲染系统)
│   ├── Mermaid渲染引擎
│   ├── PlantUML渲染引擎
│   └── 多引擎管理器
├── 生成层 (WordDocumentGenerator)
└── 输出层 (Word文档)
```

### 核心模块

#### 1. 核心处理模块 (`src/md2doc/core/`)
- **`parser.py`** (210行): Markdown解析器，支持标准语法和扩展语法
- **`generator.py`** (249行): Word文档生成器，集成图表渲染功能
- **`converter.py`** (150行): 转换协调器，统一转换流程
- **`config.py`** (76行): 配置管理系统

#### 2. 图表渲染引擎 (`src/md2doc/engines/`)
- **`mermaid_engine.py`** (190行): Mermaid图表渲染引擎
- **`plantuml_engine.py`** (141行): PlantUML图表渲染引擎  
- **`multi_engine_manager.py`** (144行): 多引擎管理器，支持降级策略
- **`chart_detector.py`** (164行): 图表检测器，识别各种图表类型
- **`base.py`** (33行): 渲染引擎基类和接口定义

#### 3. 工具模块 (`src/md2doc/utils/`)
- **`helpers.py`** (31行): 通用工具函数
- **`logger.py`** (101行): 日志管理系统

#### 4. 命令行接口 (`src/md2doc/cli/`)
- **`main.py`** (25行): CLI入口和命令处理

---

## 🚀 核心功能

### ✅ 已实现功能

#### 基础文档转换
- [x] **Markdown标准语法**: 标题、段落、列表、链接、图片
- [x] **代码块处理**: 语法高亮、代码块格式化
- [x] **表格转换**: Markdown表格到Word表格的转换
- [x] **文本格式**: 粗体、斜体、删除线等格式保持

#### 图表渲染系统 (重点功能)
- [x] **Mermaid图表支持**: 
  - 在线渲染 (mermaid.ink)
  - 本地渲染 (mmdc CLI)
  - 支持流程图、序列图、甘特图等
- [x] **PlantUML图表支持**:
  - 多服务器在线渲染
  - 本地PlantUML工具支持
  - 支持UML各种图表类型
- [x] **智能降级策略**: 在线→本地→占位符的三级降级
- [x] **网络状态检测**: 自动检测网络可用性
- [x] **图表缓存机制**: 避免重复渲染，提升性能

#### 文档生成
- [x] **Word文档创建**: 基于python-docx库
- [x] **样式管理**: 标题样式、字体配置、页面边距
- [x] **图片插入**: 渲染后的图表自动插入文档
- [x] **格式优化**: 专业的文档排版

### 🔄 技术特性

#### 多引擎渲染架构
- **可扩展性**: 基于BaseRenderEngine的插件式架构
- **容错性**: 完善的异常处理和降级机制  
- **性能优化**: 引擎实例缓存、网络状态缓存
- **配置化**: 支持不同渲染策略和参数配置

#### 渲染策略
```python
# 示例：Mermaid渲染策略配置
strategies = [
    RenderStrategy(engine_class=MermaidEngine, config={'online_first': True}, priority=0, network_required=True),
    RenderStrategy(engine_class=MermaidEngine, config={'online_first': False}, priority=1, network_required=False)
]
```

---

## 📊 开发进展

### 第一阶段: 基础架构 ✅ (已完成)
- **任务1.1**: 核心类设计和架构 ✅
- **任务1.2**: 基础配置管理 ✅  
- **任务1.3**: 日志系统搭建 ✅
- **任务1.4**: Markdown解析器基础 ✅
- **任务1.5**: Word生成器基础 ✅

### 第二阶段: 图表渲染引擎 🚧 (进行中)
- **任务2.1**: 图表代码块检测 ✅
- **任务2.2**: Mermaid渲染引擎基础 ✅
- **任务2.3**: 在线渲染备选方案 ✅
- **任务2.4**: 图片处理和缓存 ⏳ (下一步)
- **任务2.5**: PlantUML渲染引擎 ✅ (提前完成)
- **任务2.6**: 错误处理和日志完善 ⏳

### 当前进度统计
- **总体进度**: 约50% (基础架构完成，图表渲染核心完成)
- **代码量**: 1641行 (核心代码)
- **测试覆盖率**: 41% (持续提升中)
- **关键功能**: Mermaid/PlantUML双引擎渲染系统已就绪

---

## 🧪 测试状况

### 测试架构
```
tests/
├── md2doc/
│   ├── core/          # 核心模块测试
│   ├── engines/       # 渲染引擎测试
│   │   ├── test_mermaid_engine.py
│   │   ├── test_plantuml_engine.py
│   │   └── test_multi_engine_manager.py
│   └── integration/   # 集成测试
│       ├── test_mermaid_word_integration.py
│       └── test_plantuml_word_integration.py
```

### 测试覆盖情况
- **核心生成器**: 63% 覆盖率
- **Mermaid引擎**: 48% 覆盖率  
- **PlantUML引擎**: 40% 覆盖率
- **多引擎管理器**: 19% 覆盖率
- **图表检测器**: 43% 覆盖率

### 关键测试用例
- ✅ Mermaid在线渲染集成测试通过
- ✅ PlantUML引擎初始化测试通过
- ✅ 多引擎管理器初始化测试通过
- ✅ Word文档生成集成测试通过

---

## 📁 项目结构

### 核心目录结构
```
src/md2doc/
├── __init__.py                 # 包初始化
├── cli/                        # 命令行接口
│   ├── __init__.py
│   └── main.py                 # CLI主程序
├── core/                       # 核心处理模块
│   ├── __init__.py
│   ├── config.py               # 配置管理
│   ├── converter.py            # 转换协调器
│   ├── generator.py            # Word文档生成器
│   └── parser.py               # Markdown解析器
├── engines/                    # 渲染引擎模块
│   ├── __init__.py
│   ├── base.py                 # 基础引擎接口
│   ├── chart_detector.py       # 图表检测器
│   ├── mermaid_engine.py       # Mermaid渲染引擎
│   ├── multi_engine_manager.py # 多引擎管理器
│   └── plantuml_engine.py      # PlantUML渲染引擎
├── templates/                  # 模板管理
│   ├── __init__.py
│   └── manager.py
└── utils/                      # 工具模块
    ├── __init__.py
    ├── helpers.py              # 通用工具
    └── logger.py               # 日志管理
```

### 配置和文档
```
根目录/
├── requirements.txt            # Python依赖
├── pyproject.toml             # 项目配置
├── README.md                  # 项目说明
└── docs/                      # 项目文档
    ├── md2doc-tasks.md        # 任务规划文档
    ├── prd.md                 # 产品需求文档
    └── md2doc说明文档.md      # 本文档
```

---

## 🔧 技术栈

### 核心依赖
- **Python 3.11+**: 主要开发语言
- **python-docx**: Word文档生成库
- **markdown**: Markdown解析基础库
- **requests**: HTTP客户端，用于在线渲染
- **Pillow**: 图像处理库

### 开发工具
- **pytest**: 测试框架
- **pytest-cov**: 测试覆盖率
- **pytest-mock**: 测试模拟
- **black**: 代码格式化
- **flake8**: 代码质量检查

### 外部服务
- **mermaid.ink**: Mermaid在线渲染服务
- **plantuml.com**: PlantUML在线渲染服务
- **mmdc CLI**: Mermaid本地渲染工具 (可选)
- **plantuml.jar**: PlantUML本地渲染工具 (可选)

---

## 📋 配置说明

### 渲染引擎配置
```python
# Mermaid配置示例
mermaid_config = {
    'theme': 'default',
    'background': 'white', 
    'width': 800,
    'height': 600
}

# PlantUML配置示例  
plantuml_config = {
    'theme': 'default',
    'output_format': 'png',
    'dpi': 96
}
```

### 文档生成配置
```python
document_config = {
    'font_name': '微软雅黑',
    'font_size': 12,
    'chart': {
        'max_width': 6.0,  # 英寸
        'cache_dir': 'temp/charts'
    }
}
```

---

## 🎯 下一步计划

### 短期目标 (任务2.4)
- [ ] **图片处理模块**: 创建 `utils/image_processor.py`
- [ ] **图片尺寸优化**: 实现智能尺寸调整
- [ ] **缓存机制**: 完善图片缓存和清理
- [ ] **格式转换**: 支持多种图片格式输出

### 中期目标
- [ ] **错误处理完善**: 更好的错误提示和恢复机制
- [ ] **性能优化**: 并发渲染、缓存优化
- [ ] **扩展语法支持**: 更多Markdown扩展语法
- [ ] **模板系统**: 支持自定义Word模板

### 长期目标
- [ ] **Web界面**: 提供Web版本的转换服务
- [ ] **批量处理**: 支持批量文档转换
- [ ] **更多图表引擎**: 支持D3.js、Graphviz等
- [ ] **云服务集成**: 集成云存储和在线协作

---

## 🐛 已知问题

### 当前限制
1. **测试覆盖率**: 目前41%，目标是80%+
2. **网络依赖**: 在线渲染依赖网络连接
3. **图片质量**: 部分复杂图表的渲染质量待优化
4. **错误处理**: 部分边缘情况的错误处理待完善

### 待解决技术债务
- [ ] 减少lint警告
- [ ] 完善类型注解
- [ ] 优化内存使用
- [ ] 提升渲染速度

---

## 📚 相关文档

### 核心文档
- **`docs/md2doc-prd.md`**: 产品需求文档，定义功能需求和用户故事
- **`docs/md2doc-tasks.md`**: 任务规划文档，详细的开发计划和进度跟踪
- **`docs/md2doc说明文档.md`**: 本文档，项目总览和上下文管理

### 开发文档
- **`README.md`**: 项目介绍和快速开始指南
- **`tests/`**: 测试用例，展示API使用方法
- **源码注释**: 详细的代码注释和文档字符串

---

## 🤝 团队协作

### AI上下文管理使用指南
1. **项目状态查询**: 使用本文档了解当前进展和技术状况
2. **任务规划参考**: 结合 `md2doc-tasks.md` 了解具体任务
3. **功能需求确认**: 参考 `md2doc-prd.md` 了解产品定位
4. **代码理解**: 通过架构图和模块说明快速定位代码
5. **测试现状**: 了解测试覆盖情况和质量状况

### 工作流程
1. **接手工作**: 查看本文档 → 检查任务进度 → 了解当前状态
2. **开发新功能**: 参考架构设计 → 编写代码 → 添加测试
3. **问题排查**: 查看已知问题 → 检查日志 → 分析测试结果
4. **交接工作**: 更新进度状态 → 记录新的问题 → 提交代码

---

**📝 文档更新说明**: 此文档应随项目进展持续更新，建议每完成一个主要任务后更新相应章节。

---

*最后更新: 2025年8月1日 - 任务2.3完成，准备开始任务2.4*
