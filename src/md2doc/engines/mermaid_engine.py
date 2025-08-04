"""
Mermaid渲染引擎

提供Mermaid图表的渲染功能：
- 支持多种渲染方式（在线/本地）
- 高质量图片输出
- 主题和样式配置
- 错误处理和降级方案
"""

import base64
import requests
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from .base import BaseRenderEngine
from .chart_detector import ChartInfo, ChartType
from ..utils.helpers import ensure_directory
from ..utils.image_processor import ImageProcessor, create_default_processor


class MermaidTheme(Enum):
    """Mermaid主题枚举"""
    DEFAULT = "default"
    NEUTRAL = "neutral"
    DARK = "dark"
    FOREST = "forest"
    BASE = "base"


class MermaidOutputFormat(Enum):
    """输出格式枚举"""
    PNG = "png"
    SVG = "svg"
    PDF = "pdf"


@dataclass
class MermaidRenderConfig:
    """Mermaid渲染配置"""
    theme: MermaidTheme = MermaidTheme.DEFAULT
    output_format: MermaidOutputFormat = MermaidOutputFormat.PNG
    width: int = 800
    height: int = 600
    background: str = "white"
    scale: float = 1.0
    quality: int = 90  # 对PNG有效
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "theme": self.theme.value,
            "format": self.output_format.value,
            "width": self.width,
            "height": self.height,
            "background": self.background,
            "scale": self.scale,
            "quality": self.quality
        }


class MermaidRenderError(Exception):
    """Mermaid渲染错误"""
    pass


class MermaidEngine(BaseRenderEngine):
    """Mermaid渲染引擎"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化Mermaid引擎
        
        Args:
            config: 渲染配置
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 默认配置
        self.config = MermaidRenderConfig()
        if config:
            self._update_config(config)
        
        # 渲染方式配置
        self.prefer_local = config.get('prefer_local', False) if config else False
        self.online_timeout = config.get('online_timeout', 30) if config else 30
        self.cache_enabled = config.get('cache_enabled', True) if config else True
        
        # 在线渲染服务配置
        self.online_services = {
            'mermaid_ink': 'https://mermaid.ink/img/',
            'mermaid_live': 'https://mermaid-js.github.io/mermaid-live-editor/edit'
        }
        
        # 检查本地工具可用性
        self.local_available = self._check_local_tools()
        
        # 初始化图片处理器
        self.image_processor = create_default_processor()
        
    def _update_config(self, config: Dict[str, Any]):
        """更新渲染配置
        
        Args:
            config: 配置字典
        """
        if 'theme' in config:
            theme_value = config['theme']
            if isinstance(theme_value, str):
                try:
                    self.config.theme = MermaidTheme(theme_value)
                except ValueError:
                    self.logger.warning(f"无效的主题: {theme_value}, 使用默认主题")
            
        if 'output_format' in config:
            format_value = config['output_format']
            if isinstance(format_value, str):
                try:
                    self.config.output_format = MermaidOutputFormat(format_value.lower())
                except ValueError:
                    self.logger.warning(f"无效的输出格式: {format_value}, 使用PNG")
        
        # 更新其他配置
        for key in ['width', 'height', 'background', 'scale', 'quality']:
            if key in config:
                setattr(self.config, key, config[key])
    
    def _check_local_tools(self) -> bool:
        """检查本地Mermaid工具是否可用
        
        Returns:
            本地工具是否可用
        """
        try:
            # 检查mermaid-cli (mmdc)
            result = subprocess.run(['mmdc', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.logger.info("发现本地Mermaid CLI工具")
                return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        try:
            # 检查npx + @mermaid-js/mermaid-cli
            result = subprocess.run(['npx', 'mmdc', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.logger.info("发现NPX Mermaid CLI工具")
                return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        self.logger.info("未找到本地Mermaid工具，将使用在线渲染")
        return False
    
    def can_render(self, chart_info: ChartInfo) -> bool:
        """检查是否能渲染指定图表
        
        Args:
            chart_info: 图表信息
            
        Returns:
            是否能渲染
        """
        return chart_info.chart_type == ChartType.MERMAID
    
    def render(self, chart_info: ChartInfo, output_path: Optional[Path] = None) -> Union[bytes, Path]:
        """渲染Mermaid图表
        
        Args:
            chart_info: 图表信息
            output_path: 输出路径（可选）
            
        Returns:
            渲染结果（字节数据或文件路径）
        """
        if not self.can_render(chart_info):
            raise MermaidRenderError(f"无法渲染非Mermaid图表: {chart_info.chart_type}")
        
        self.logger.info(f"开始渲染Mermaid图表: {chart_info.subtype}")
        
        try:
            # 优先使用本地渲染
            if self.prefer_local and self.local_available:
                return self._render_local(chart_info, output_path)
            else:
                return self._render_online(chart_info, output_path)
                
        except Exception as e:
            self.logger.error(f"Mermaid渲染失败: {e}")
            
            # 尝试降级方案
            if self.prefer_local:
                self.logger.info("尝试在线渲染作为降级方案")
                try:
                    return self._render_online(chart_info, output_path)
                except Exception as fallback_error:
                    self.logger.error(f"降级渲染也失败: {fallback_error}")
                    raise MermaidRenderError(f"所有渲染方式都失败: {e}")
            else:
                self.logger.info("尝试本地渲染作为降级方案")
                if self.local_available:
                    try:
                        return self._render_local(chart_info, output_path)
                    except Exception as fallback_error:
                        self.logger.error(f"降级渲染也失败: {fallback_error}")
                
                raise MermaidRenderError(f"渲染失败: {e}")
    
    def _render_local(self, chart_info: ChartInfo, output_path: Optional[Path] = None) -> Union[bytes, Path]:
        """使用本地工具渲染
        
        Args:
            chart_info: 图表信息
            output_path: 输出路径
            
        Returns:
            渲染结果
        """
        self.logger.debug("使用本地工具渲染Mermaid图表")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as temp_input:
            temp_input.write(chart_info.content)
            input_path = Path(temp_input.name)
        
        try:
            # 确定输出文件
            if output_path:
                final_output = output_path
            else:
                temp_output = tempfile.NamedTemporaryFile(
                    suffix=f'.{self.config.output_format.value}', 
                    delete=False
                )
                temp_output.close()
                final_output = Path(temp_output.name)
            
            # 构建命令
            cmd = self._build_local_command(input_path, final_output)
            
            # 执行渲染
            self.logger.debug(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                raise MermaidRenderError(f"本地渲染失败: {result.stderr}")
            
            # 处理渲染结果
            if output_path:
                # 优化图片用于Word文档
                optimized_path = self.image_processor.optimize_for_word(final_output)
                if optimized_path != final_output:
                    # 如果生成了优化版本，替换原文件
                    final_output.unlink()
                    optimized_path.rename(final_output)
                return final_output
            else:
                # 优化图片并返回字节数据
                optimized_path = self.image_processor.optimize_for_word(final_output)
                with open(optimized_path, 'rb') as f:
                    image_data = f.read()
                # 清理优化后的临时文件
                if optimized_path != final_output:
                    optimized_path.unlink()
                return image_data
        
        finally:
            # 清理临时文件
            try:
                input_path.unlink()
                if not output_path and final_output.exists():
                    final_output.unlink()
            except Exception as e:
                self.logger.warning(f"清理临时文件失败: {e}")
    
    def _build_local_command(self, input_path: Path, output_path: Path) -> list:
        """构建本地渲染命令
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            
        Returns:
            命令列表
        """
        # 尝试直接使用mmdc
        cmd = ['mmdc', '-i', str(input_path), '-o', str(output_path)]
        
        # 添加主题
        if self.config.theme != MermaidTheme.DEFAULT:
            cmd.extend(['-t', self.config.theme.value])
        
        # 添加背景色
        if self.config.background != "white":
            cmd.extend(['-b', self.config.background])
        
        # 添加尺寸
        cmd.extend(['-w', str(self.config.width)])
        cmd.extend(['-H', str(self.config.height)])
        
        # 添加比例
        if self.config.scale != 1.0:
            cmd.extend(['-s', str(self.config.scale)])
        
        return cmd
    
    def _render_online(self, chart_info: ChartInfo, output_path: Optional[Path] = None) -> Union[bytes, Path]:
        """使用在线服务渲染
        
        Args:
            chart_info: 图表信息
            output_path: 输出路径
            
        Returns:
            渲染结果
        """
        self.logger.debug("使用在线服务渲染Mermaid图表")
        
        # 首先尝试mermaid.ink
        try:
            return self._render_with_mermaid_ink(chart_info, output_path)
        except Exception as e:
            self.logger.warning(f"mermaid.ink渲染失败: {e}")
            
            # 可以在这里添加其他在线服务的尝试
            raise MermaidRenderError("所有在线渲染服务都不可用")
    
    def _render_with_mermaid_ink(self, chart_info: ChartInfo, output_path: Optional[Path] = None) -> Union[bytes, Path]:
        """使用mermaid.ink渲染
        
        Args:
            chart_info: 图表信息
            output_path: 输出路径
            
        Returns:
            渲染结果
        """
        # 编码图表内容
        encoded_content = base64.b64encode(chart_info.content.encode('utf-8')).decode('ascii')
        
        # 构建URL
        base_url = self.online_services['mermaid_ink']
        url = f"{base_url}{encoded_content}"
        
        # 添加参数
        params = {}
        if self.config.theme != MermaidTheme.DEFAULT:
            params['theme'] = str(self.config.theme.value)  # 确保转换为字符串
        if self.config.background != "white":
            params['bgColor'] = str(self.config.background)  # 确保转换为字符串
        
        # 发送请求
        self.logger.debug(f"请求URL: {url}")
        response = requests.get(url, params=params, timeout=self.online_timeout)
        response.raise_for_status()
        
        # 检查响应类型
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise MermaidRenderError(f"服务器返回非图片内容: {content_type}")
        
        # 处理结果
        image_data = response.content
        
        if output_path:
            ensure_directory(output_path.parent)
            # 先保存原始图片到临时文件
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_file.write(image_data)
                temp_path = Path(temp_file.name)
            
            try:
                # 优化图片
                optimized_path = self.image_processor.optimize_for_word(temp_path)
                if optimized_path != temp_path:
                    # 移动优化后的图片到目标位置
                    optimized_path.rename(output_path)
                    temp_path.unlink()  # 清理原始临时文件
                else:
                    # 如果没有优化，直接移动原文件
                    temp_path.rename(output_path)
                
                return output_path
            finally:
                # 确保清理临时文件
                if temp_path.exists():
                    temp_path.unlink()
        else:
            # 保存到临时文件并优化
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_file.write(image_data)
                temp_path = Path(temp_file.name)
            
            try:
                # 优化图片
                optimized_path = self.image_processor.optimize_for_word(temp_path)
                with open(optimized_path, 'rb') as f:
                    optimized_data = f.read()
                
                # 清理临时文件
                if optimized_path != temp_path:
                    optimized_path.unlink()
                
                return optimized_data
            finally:
                # 确保清理临时文件
                if temp_path.exists():
                    temp_path.unlink()
    
    def get_supported_formats(self) -> list:
        """获取支持的输出格式
        
        Returns:
            支持的格式列表
        """
        if self.local_available:
            return ['png', 'svg', 'pdf']
        else:
            return ['png', 'svg']  # 在线服务通常支持这些格式
    
    def validate_chart(self, chart_info: ChartInfo) -> Tuple[bool, Optional[str]]:
        """验证图表语法
        
        Args:
            chart_info: 图表信息
            
        Returns:
            (是否有效, 错误信息)
        """
        content = chart_info.content.strip()
        
        # 基础验证
        if not content:
            return False, "图表内容为空"
        
        # 检查基本语法结构
        lines = content.split('\n')
        valid_starts = [
            'graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
            'stateDiagram', 'erDiagram', 'gantt', 'pie', 'gitgraph'
        ]
        
        first_line = lines[0].strip().lower()
        if not any(first_line.startswith(start.lower()) for start in valid_starts):
            return False, f"未识别的图表类型开始: {first_line}"
        
        # 更详细的验证可以在这里添加
        return True, None
    
    def get_render_info(self) -> Dict[str, Any]:
        """获取渲染器信息
        
        Returns:
            渲染器信息
        """
        return {
            "name": "MermaidEngine",
            "version": "1.0.0",
            "supported_types": ["mermaid"],
            "local_available": self.local_available,
            "supported_formats": self.get_supported_formats(),
            "config": self.config.to_dict()
        }
