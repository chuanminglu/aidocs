"""
文档模板管理器

管理Word文档模板：
- DocumentTemplate: 文档模板类
- TemplateManager: 模板管理器
"""

from typing import Dict, Any, Optional
from pathlib import Path


class DocumentTemplate:
    """文档模板"""
    
    def __init__(self, name: str, template_path: Optional[Path] = None):
        """初始化文档模板
        
        Args:
            name: 模板名称
            template_path: 模板文件路径
        """
        self.name = name
        self.template_path = template_path
        self.styles: Dict[str, Any] = {}
    
    def add_style(self, style_name: str, style_config: Dict[str, Any]) -> None:
        """添加样式配置
        
        Args:
            style_name: 样式名称
            style_config: 样式配置
        """
        self.styles[style_name] = style_config


class TemplateManager:
    """模板管理器"""
    
    def __init__(self):
        """初始化模板管理器"""
        self.templates: Dict[str, DocumentTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """加载默认模板"""
        # 标准模板
        standard = DocumentTemplate("standard")
        standard.add_style("heading1", {"font_size": 18, "bold": True})
        standard.add_style("heading2", {"font_size": 16, "bold": True})
        standard.add_style("normal", {"font_size": 12})
        self.templates["standard"] = standard
        
        # 技术文档模板
        technical = DocumentTemplate("technical")
        technical.add_style("heading1", {"font_size": 16, "bold": True})
        technical.add_style("code", {"font_name": "Consolas", "font_size": 10})
        self.templates["technical"] = technical
    
    def get_template(self, name: str) -> Optional[DocumentTemplate]:
        """获取模板
        
        Args:
            name: 模板名称
            
        Returns:
            文档模板
        """
        return self.templates.get(name)
    
    def register_template(self, template: DocumentTemplate) -> None:
        """注册模板
        
        Args:
            template: 文档模板
        """
        self.templates[template.name] = template
