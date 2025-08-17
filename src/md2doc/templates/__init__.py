"""
文档模板模块

提供不同风格的Word文档模板：
- manager: 模板管理器
- standard: 标准文档模板 (待实现)
- business: 商务文档模板 (待实现)
- technical: 技术文档模板 (待实现)
"""

from .manager import DocumentTemplate, TemplateManager

__all__ = ['DocumentTemplate', 'TemplateManager']
