"""
配置管理器

处理转换器的配置信息，包括：
- 文档样式配置
- 图表渲染配置  
- 输出格式配置
- YAML配置文件支持
- 环境变量支持
"""

from typing import Dict, Any, Optional
from pathlib import Path
import os


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or Path("config/md2doc.json")
        self._config: Dict[str, Any] = {}
        self._load_default_config()
        self._load_config_file()
        self._load_environment_variables()
        
    def _load_default_config(self):
        """加载默认配置"""
        self._config = {
            "document": {
                "font_name": "微软雅黑",
                "font_size": 12,
                "line_spacing": 1.15,
                "margin": {
                    "top": 2.54,
                    "bottom": 2.54,
                    "left": 3.17,
                    "right": 3.17
                }
            },
            "charts": {
                "mermaid": {
                    "theme": "default",
                    "background": "white",
                    "width": 800,
                    "height": 600,
                    "cli_path": "mmdc"
                },
                "plantuml": {
                    "server_url": "http://www.plantuml.com/plantuml",
                    "format": "png"
                }
            },
            "output": {
                "format": "docx",
                "preserve_styles": True,
                "image_dpi": 300,
                "image_quality": "high"
            },
            "logging": {
                "level": "INFO",
                "file": "logs/md2doc.log",
                "console": True
            }
        }
    
    def _load_config_file(self):
        """加载配置文件"""
        if not self.config_path.exists():
            return
            
        try:
            if self.config_path.suffix.lower() in ['.yml', '.yaml']:
                import yaml
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f) or {}
            else:
                import json
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
            
            self._deep_merge(self._config, file_config)
            
        except Exception as e:
            print(f"Warning: Failed to load config file {self.config_path}: {e}")
    
    def _load_environment_variables(self):
        """加载环境变量配置"""
        env_mappings = {
            'MD2DOC_FONT_NAME': 'document.font_name',
            'MD2DOC_FONT_SIZE': 'document.font_size',
            'MD2DOC_MERMAID_THEME': 'charts.mermaid.theme',
            'MD2DOC_MERMAID_CLI': 'charts.mermaid.cli_path',
            'MD2DOC_OUTPUT_DPI': 'output.image_dpi',
            'MD2DOC_LOG_LEVEL': 'logging.level'
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value:
                if env_value.isdigit():
                    env_value = int(env_value)
                elif env_value.replace('.', '', 1).isdigit():
                    env_value = float(env_value)
                elif env_value.lower() in ['true', 'false']:
                    env_value = env_value.lower() == 'true'
                
                self.set(config_key, env_value)
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """深度合并字典"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def validate(self) -> bool:
        """验证配置的完整性"""
        required_keys = [
            'document.font_name',
            'document.font_size',
            'charts.mermaid.theme',
            'output.format'
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                print(f"Error: Required config key '{key}' is missing")
                return False
        
        font_size = self.get('document.font_size')
        if not isinstance(font_size, (int, float)) or font_size <= 0:
            print("Error: document.font_size must be a positive number")
            return False
        
        return True
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()
    
    def reset_to_defaults(self) -> None:
        """重置为默认配置"""
        self._config.clear()
        self._load_default_config()
        self._load_environment_variables()
