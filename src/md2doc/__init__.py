"""
MD2DOC - Markdown到Word文档转换工具

专业的Markdown到Word转换解决方案，支持：
1. 图表代码自动渲染为图片（Mermaid、PlantUML）
2. 完整的格式映射转换（粗体、斜体、链接等）
3. 企业级文档模板和样式
4. 批量转换和命令行工具

使用示例：
```python
from md2doc.core import ConfigManager, MarkdownParser, WordDocumentGenerator
from md2doc.cli import main

# 完整转换流程
config = ConfigManager()
parser = MarkdownParser()
generator = WordDocumentGenerator(config)

# 解析和生成
result = parser.parse(markdown_content)
document = generator.generate_from_parse_result(result, "output.docx")

# 命令行使用
main(['input.md', '-o', 'output.docx'])
```
"""

__version__ = "0.1.0"
__author__ = "AI文档团队"
__description__ = "专业的Markdown到Word文档转换工具"

# 导入已实现的模块
from .core import ConfigManager, MarkdownParser, ParseResult, WordDocumentGenerator, MD2DocConverter, ConversionError
from .cli import main

# 主要接口
__all__ = [
    'ConfigManager',
    'MarkdownParser', 
    'ParseResult',
    'WordDocumentGenerator',
    'MD2DocConverter',
    'ConversionError',
    'main',
    '__version__',
    '__author__',
    '__description__'
]
