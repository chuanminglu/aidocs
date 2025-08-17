"""
MD2DOC 核心模块

包含主要的转换逻辑：
- config: 配置管理器
- parser: Markdown解析器
- generator: Word生成器
- converter: 主转换器
"""

from .config import ConfigManager
from .parser import MarkdownParser, ParseResult, MarkdownElement, HeadingElement, ParagraphElement, ListElement, CodeBlockElement, ChartElement, TableElement
from .generator import WordDocumentGenerator
from .converter import MD2DocConverter, ConversionError

__all__ = [
    'ConfigManager', 
    'MarkdownParser', 'ParseResult', 'MarkdownElement', 
    'HeadingElement', 'ParagraphElement', 'ListElement', 
    'CodeBlockElement', 'ChartElement', 'TableElement',
    'WordDocumentGenerator',
    'MD2DocConverter', 'ConversionError'
]
