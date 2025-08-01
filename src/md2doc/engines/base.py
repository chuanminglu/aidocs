"""
基础转换引擎

定义转换引擎的基础接口：
- BaseEngine: 转换引擎基类
- BaseRenderEngine: 图表渲染引擎基类
- ConversionResult: 转换结果类
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union, Tuple
from pathlib import Path


class ConversionResult:
    """转换结果"""
    
    def __init__(self, success: bool, output_path: Optional[Path] = None, 
                 error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """初始化转换结果
        
        Args:
            success: 是否转换成功
            output_path: 输出文件路径
            error: 错误信息
            metadata: 元数据
        """
        self.success = success
        self.output_path = output_path
        self.error = error
        self.metadata = metadata or {}


class BaseEngine(ABC):
    """转换引擎基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化引擎
        
        Args:
            config: 配置信息
        """
        self.config = config
    
    @abstractmethod
    def convert(self, input_path: Path, output_path: Path) -> ConversionResult:
        """转换文档
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            
        Returns:
            转换结果
        """
        pass
    
    @abstractmethod
    def supports_format(self, format_type: str) -> bool:
        """检查是否支持指定格式
        
        Args:
            format_type: 格式类型
            
        Returns:
            是否支持
        """
        pass


class BaseRenderEngine(ABC):
    """图表渲染引擎基类"""
    
    def __init__(self):
        """初始化渲染引擎"""
        pass
    
    @abstractmethod
    def can_render(self, chart_info) -> bool:
        """检查是否能渲染指定图表
        
        Args:
            chart_info: 图表信息
            
        Returns:
            是否能渲染
        """
        pass
    
    @abstractmethod
    def render(self, chart_info, output_path: Optional[Path] = None) -> Union[bytes, Path]:
        """渲染图表
        
        Args:
            chart_info: 图表信息
            output_path: 输出路径（可选）
            
        Returns:
            渲染结果（字节数据或文件路径）
        """
        pass
    
    @abstractmethod
    def validate_chart(self, chart_info) -> Tuple[bool, Optional[str]]:
        """验证图表语法
        
        Args:
            chart_info: 图表信息
            
        Returns:
            (是否有效, 错误信息)
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> list:
        """获取支持的输出格式
        
        Returns:
            支持的格式列表
        """
        pass
