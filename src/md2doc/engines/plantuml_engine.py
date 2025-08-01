"""
PlantUML渲染引擎

提供PlantUML图表的渲染功能：
- 支持多种渲染方式（在线/本地）
- 高质量图片输出
- 多种图表类型支持
- 错误处理和降级方案
"""

import base64
import zlib
import requests
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from .base import BaseRenderEngine
from .chart_detector import ChartInfo, ChartType
from ..utils.helpers import ensure_directory


class PlantUMLTheme(Enum):
    """PlantUML主题枚举"""
    DEFAULT = "default"
    BLUEPRINT = "blueprint"
    CERULEAN = "cerulean"
    CERULEAN_OUTLINE = "cerulean-outline"
    DARKULA = "darkula"
    HACKER = "hacker"
    LIGHTGRAY = "lightgray"
    PLAIN = "plain"
    SANDSTONE = "sandstone"
    SILVER = "silver"
    TOY = "toy"


class PlantUMLOutputFormat(Enum):
    """输出格式枚举"""
    PNG = "png"
    SVG = "svg"
    TXT = "txt"


@dataclass
class PlantUMLRenderConfig:
    """PlantUML渲染配置"""
    theme: PlantUMLTheme = PlantUMLTheme.DEFAULT
    output_format: PlantUMLOutputFormat = PlantUMLOutputFormat.PNG
    scale: float = 1.0
    dpi: int = 96
    charset: str = "UTF-8"


class PlantUMLEngine(BaseRenderEngine):
    """PlantUML图表渲染引擎"""
    
    def __init__(self, config: Optional[PlantUMLRenderConfig] = None):
        """初始化PlantUML引擎
        
        Args:
            config: PlantUML渲染配置
        """
        self.config = config or PlantUMLRenderConfig()
        self.logger = logging.getLogger(__name__)
        
        # 在线服务配置
        self.online_servers = [
            "https://www.plantuml.com/plantuml",
            "https://plantuml.github.io/plantuml-core",
            "http://www.plantuml.com/plantuml"  # HTTP备份
        ]
        
        # 本地工具检测
        self.local_available = self._check_local_plantuml()
        
    def can_render(self, chart_info: ChartInfo) -> bool:
        """检查是否可以渲染指定图表
        
        Args:
            chart_info: 图表信息
            
        Returns:
            是否可以渲染
        """
        return chart_info.chart_type == ChartType.PLANTUML
        
    def render(self, chart_info: ChartInfo, output_path: Optional[Path] = None) -> Tuple[bool, Optional[Path], Optional[str]]:
        """渲染PlantUML图表
        
        Args:
            chart_info: 图表信息
            output_path: 输出路径，如果为None则自动生成
            
        Returns:
            (是否成功, 输出路径, 错误信息)
        """
        if not self.can_render(chart_info):
            return False, None, f"不支持的图表类型: {chart_info.chart_type}"
            
        # 准备输出路径
        if output_path is None:
            output_dir = Path(tempfile.gettempdir()) / "plantuml_cache"
            ensure_directory(output_dir)
            output_path = output_dir / f"chart_{hash(chart_info.content)}.{self.config.output_format.value}"
        
        # 如果文件已存在且内容匹配，直接返回
        if output_path.exists():
            self.logger.info(f"使用缓存的PlantUML图表: {output_path}")
            return True, output_path, None
            
        # 尝试在线渲染
        success, error = self._render_online(chart_info.content, output_path)
        if success:
            return True, output_path, None
            
        # 尝试本地渲染
        if self.local_available:
            success, error = self._render_local(chart_info.content, output_path)
            if success:
                return True, output_path, None
                
        # 创建错误占位符
        placeholder_path = self._create_error_placeholder(output_path, error or "渲染失败")
        return False, placeholder_path, error
        
    def _render_online(self, plantuml_code: str, output_path: Path) -> Tuple[bool, Optional[str]]:
        """在线渲染PlantUML图表
        
        Args:
            plantuml_code: PlantUML代码
            output_path: 输出路径
            
        Returns:
            (是否成功, 错误信息)
        """
        try:
            # 编码PlantUML代码
            encoded_code = self._encode_plantuml(plantuml_code)
            
            # 构建URL
            format_suffix = self.config.output_format.value
            
            for server in self.online_servers:
                try:
                    url = f"{server}/{format_suffix}/{encoded_code}"
                    self.logger.info(f"尝试在线渲染PlantUML: {server}")
                    
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    
                    # 检查响应内容
                    if len(response.content) < 100:  # 可能是错误响应
                        continue
                        
                    # 保存图片
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                        
                    self.logger.info(f"PlantUML在线渲染成功: {output_path}")
                    return True, None
                    
                except requests.RequestException as e:
                    self.logger.warning(f"PlantUML在线渲染失败 {server}: {e}")
                    continue
                    
            return False, "所有在线服务器都不可用"
            
        except Exception as e:
            self.logger.error(f"PlantUML在线渲染异常: {e}")
            return False, str(e)
            
    def _render_local(self, plantuml_code: str, output_path: Path) -> Tuple[bool, Optional[str]]:
        """本地渲染PlantUML图表
        
        Args:
            plantuml_code: PlantUML代码
            output_path: 输出路径
            
        Returns:
            (是否成功, 错误信息)
        """
        try:
            # 创建临时输入文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False, encoding='utf-8') as f:
                f.write(plantuml_code)
                input_path = Path(f.name)
                
            try:
                # 构建命令
                cmd = [
                    'plantuml',
                    '-charset', self.config.charset,
                    '-t' + self.config.output_format.value,
                    str(input_path)
                ]
                
                # 执行渲染
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    # 移动生成的文件到目标位置
                    generated_path = input_path.with_suffix(f'.{self.config.output_format.value}')
                    if generated_path.exists():
                        generated_path.rename(output_path)
                        self.logger.info(f"PlantUML本地渲染成功: {output_path}")
                        return True, None
                        
                return False, f"PlantUML命令执行失败: {result.stderr}"
                
            finally:
                # 清理临时文件
                if input_path.exists():
                    input_path.unlink()
                    
        except subprocess.TimeoutExpired:
            return False, "PlantUML渲染超时"
        except Exception as e:
            self.logger.error(f"PlantUML本地渲染异常: {e}")
            return False, str(e)
            
    def _encode_plantuml(self, plantuml_code: str) -> str:
        """编码PlantUML代码为URL安全格式
        
        Args:
            plantuml_code: PlantUML源码
            
        Returns:
            编码后的字符串
        """
        # PlantUML编码算法
        # 1. 压缩
        compressed = zlib.compress(plantuml_code.encode('utf-8'))
        
        # 2. Base64编码
        encoded = base64.b64encode(compressed).decode('ascii')
        
        # 3. URL安全转换
        encoded = encoded.replace('+', '-').replace('/', '_')
        
        return encoded
        
    def _check_local_plantuml(self) -> bool:
        """检查本地PlantUML工具是否可用
        
        Returns:
            是否可用
        """
        try:
            result = subprocess.run(['plantuml', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            available = result.returncode == 0
            if available:
                self.logger.info("检测到本地PlantUML工具")
            else:
                self.logger.info("本地PlantUML工具不可用")
            return available
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.logger.info("本地PlantUML工具不可用")
            return False
            
    def _create_error_placeholder(self, output_path: Path, error_msg: str) -> Path:
        """创建错误占位符图片
        
        Args:
            output_path: 输出路径
            error_msg: 错误消息
            
        Returns:
            占位符文件路径
        """
        # 创建简单的错误占位符（文本文件）
        placeholder_path = output_path.with_suffix('.txt')
        with open(placeholder_path, 'w', encoding='utf-8') as f:
            f.write(f"PlantUML渲染失败\n错误: {error_msg}\n")
            
        self.logger.warning(f"创建PlantUML错误占位符: {placeholder_path}")
        return placeholder_path
        
    def validate_chart(self, chart_code: str) -> Tuple[bool, Optional[str]]:
        """验证PlantUML图表代码
        
        Args:
            chart_code: 图表代码
            
        Returns:
            (是否有效, 错误信息)
        """
        if not chart_code.strip():
            return False, "图表代码为空"
            
        # 基本语法检查
        lines = chart_code.strip().split('\n')
        has_start = any(line.strip().startswith('@start') for line in lines)
        has_end = any(line.strip().startswith('@end') for line in lines)
        
        if not (has_start and has_end):
            return False, "PlantUML代码缺少@start或@end标记"
            
        return True, None
        
    def get_supported_formats(self) -> list[str]:
        """获取支持的输出格式
        
        Returns:
            支持的格式列表
        """
        return [fmt.value for fmt in PlantUMLOutputFormat]
