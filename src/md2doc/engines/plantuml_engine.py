"""
PlantUML渲染引擎

提供PlantUML图表的渲染功能：
- 支持多种渲染方式（在线/本地）
- 高质量图片输出
- 多种图表类型支持
- 错误处理和降级方案
"""

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
from ..utils.image_processor import create_default_processor


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
        
        # 初始化图片处理器
        self.image_processor = create_default_processor()
        
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
            
            # 构建高质量URL（使用高DPI）
            format_suffix = self.config.output_format.value
            
            for server in self.online_servers:
                try:
                    # 构建多种高质量PNG URL格式
                    urls_to_try = []
                    
                    # 基于测试结果优化URL构建策略
                    if format_suffix == "png":
                        # 优先使用最稳定的dpng格式（测试证明最可靠）
                        urls_to_try.append({
                            "url": f"{server}/dpng/{encoded_code}",
                            "format": "png", 
                            "description": "高质量PNG (dpng格式)"
                        })
                        
                        # 尝试更高的DPI设置（基于Context7研究和测试）
                        for dpi in [300, 400, 200]:  # 优先尝试更高DPI
                            urls_to_try.append({
                                "url": f"{server}/png/{encoded_code}?dpi={dpi}",
                                "format": "png",
                                "description": f"高DPI PNG ({dpi} DPI)"
                            })
                        
                        # 标准PNG作为最后备选
                        urls_to_try.append({
                            "url": f"{server}/png/{encoded_code}",
                            "format": "png",
                            "description": "标准PNG"
                        })
                    else:
                        # 其他格式保持原样
                        urls_to_try.append({
                            "url": f"{server}/{format_suffix}/{encoded_code}",
                            "format": format_suffix,
                            "description": f"标准{format_suffix.upper()}"
                        })
                    
                    # 依次尝试不同的URL格式
                    response = None
                    successful_url = None
                    used_format = None
                    
                    for url_info in urls_to_try:
                        try:
                            url = url_info["url"]
                            format_type = url_info["format"]
                            description = url_info["description"]
                            
                            self.logger.info(f"尝试在线渲染PlantUML: {description} - {url}")
                            
                            # 增加重试机制和更长的超时时间
                            max_retries = 2
                            for retry in range(max_retries):
                                try:
                                    response = requests.get(url, timeout=45)  # 增加超时时间
                                    response.raise_for_status()
                                    
                                    # 检查响应内容
                                    if len(response.content) >= 100:  # 有效响应
                                        successful_url = url
                                        used_format = format_type
                                        self.logger.info(f"成功使用格式: {description}")
                                        break
                                    else:
                                        self.logger.warning(f"响应内容太小: {len(response.content)} bytes")
                                        
                                except requests.exceptions.HTTPError as http_err:
                                    if retry < max_retries - 1:
                                        self.logger.warning(f"HTTP错误 (重试 {retry+1}/{max_retries}): {http_err}")
                                        continue
                                    else:
                                        raise http_err
                                        
                            if successful_url:
                                break
                                
                        except Exception as url_error:
                            self.logger.debug(f"URL {url} 失败: {url_error}")
                            continue
                    
                    if response is None or successful_url is None:
                        continue  # 尝试下一个服务器
                        
                    self.logger.info(f"成功使用格式: {used_format} - {successful_url}")
                        
                    # PNG格式：直接保存
                    file_suffix = '.png' if used_format == 'png' else f'.{used_format}'
                    with tempfile.NamedTemporaryFile(suffix=file_suffix, delete=False) as temp_file:
                        temp_file.write(response.content)
                        temp_path = Path(temp_file.name)
                    
                    try:
                        # 优化图片（仅对PNG格式）
                        if used_format == 'png':
                            optimized_path = self.image_processor.optimize_for_word(temp_path)
                            if optimized_path != temp_path:
                                # 移动优化后的图片到目标位置
                                optimized_path.rename(output_path)
                                temp_path.unlink()  # 清理原始临时文件
                            else:
                                # 如果没有优化，直接移动原文件
                                temp_path.rename(output_path)
                        else:
                            # 其他格式直接移动
                            temp_path.rename(output_path)
                    finally:
                        # 确保清理临时文件
                        if temp_path.exists():
                            temp_path.unlink()
                        
                    self.logger.info(f"PlantUML渲染成功 ({used_format}格式): {output_path}")
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
        try:
            # 确保代码有正确的开始和结束标记
            code = plantuml_code.strip()
            if not code.startswith('@start'):
                code = '@startuml\n' + code + '\n@enduml'
            
            # 使用官方PlantUML编码方法
            encoded = self._plantuml_encode_official(code)
            
            # 优先使用原始代码，不进行简化
            # 只有在编码极长(>5000字符)且在线服务无法处理时才考虑简化
            if len(encoded) > 5000:  # 大幅提高阈值，优先保持原始图表
                self.logger.warning(f"PlantUML编码较长({len(encoded)}字符)，但将尝试使用原始代码")
                # 注释掉自动简化逻辑，保持原始图表
                # simplified_code = self._simplify_plantuml_content(code)
                # encoded = self._plantuml_encode_official(simplified_code)
                # self.logger.info(f"简化后编码长度: {len(encoded)}字符")
            
            self.logger.info(f"PlantUML编码完成: {len(code)}字符 -> {len(encoded)}字符")
            return encoded
            
        except Exception as e:
            self.logger.error(f"PlantUML编码失败: {e}")
            # 降级到最简单的图表
            return self._get_fallback_encoding()
    
    def _plantuml_encode_official(self, text: str) -> str:
        """官方PlantUML编码方法
        
        Args:
            text: PlantUML源码
            
        Returns:
            编码后的字符串
        """
        # 标准PlantUML编码表
        plantuml_alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
        
        # 压缩并移除zlib头尾
        compressed = zlib.compress(text.encode('utf-8'))[2:-4]
        
        # 转换为PlantUML的base64变体
        result = ""
        for i in range(0, len(compressed), 3):
            chunk = compressed[i:i+3]
            
            if len(chunk) == 3:
                val = (chunk[0] << 16) + (chunk[1] << 8) + chunk[2]
                result += plantuml_alphabet[(val >> 18) & 0x3F]
                result += plantuml_alphabet[(val >> 12) & 0x3F] 
                result += plantuml_alphabet[(val >> 6) & 0x3F]
                result += plantuml_alphabet[val & 0x3F]
            elif len(chunk) == 2:
                val = (chunk[0] << 16) + (chunk[1] << 8)
                result += plantuml_alphabet[(val >> 18) & 0x3F]
                result += plantuml_alphabet[(val >> 12) & 0x3F]
                result += plantuml_alphabet[(val >> 6) & 0x3F]
            elif len(chunk) == 1:
                val = chunk[0] << 16
                result += plantuml_alphabet[(val >> 18) & 0x3F]
                result += plantuml_alphabet[(val >> 12) & 0x3F]
        
        return result
    
    def _simplify_plantuml_content(self, code: str) -> str:
        """简化PlantUML内容，移除复杂元素
        
        Args:
            code: 原始PlantUML代码
            
        Returns:
            简化后的代码
        """
        try:
            lines = code.split('\n')
            
            # 检测图表类型和主要结构
            has_activity = any('start' in line or 'stop' in line or ':' in line.strip() for line in lines)
            has_sequence = any('->' in line for line in lines)
            has_class = any('class' in line for line in lines)
            
            # 如果是活动图，创建简化的活动图
            if has_activity:
                return """@startuml
title 流程图
start
:需求分析;
:系统设计;
:开发实现;
:测试验证;
:部署上线;
stop
@enduml"""
            
            # 如果是时序图，创建简化的时序图
            elif has_sequence:
                return """@startuml
title 时序图
用户 -> 系统: 请求
系统 -> 数据库: 查询
数据库 -> 系统: 返回结果
系统 -> 用户: 响应
@enduml"""
            
            # 如果是类图，创建简化的类图
            elif has_class:
                return """@startuml
title 类图
class 用户 {
  +登录()
  +操作()
}
class 系统 {
  +处理()
  +响应()
}
用户 --> 系统
@enduml"""
            
            # 默认创建最简单的流程图
            else:
                return """@startuml
title 流程图
start
:开始;
:处理;
:结束;
stop
@enduml"""
                
        except Exception as e:
            self.logger.warning(f"PlantUML内容简化失败: {e}")
            # 返回最基本的图表
            return """@startuml
start
:流程;
stop
@enduml"""
    
    def _get_fallback_encoding(self) -> str:
        """获取降级编码（最简单的图表）
        
        Returns:
            降级编码字符串
        """
        fallback_code = """@startuml
Alice -> Bob: Hello
Bob -> Alice: Hi
@enduml"""
        try:
            return self._plantuml_encode_official(fallback_code)
        except Exception:
            return "SyfFKj2rKt3CoKnELR1Io4ZDoSa70000"  # 硬编码的安全降级
        
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
