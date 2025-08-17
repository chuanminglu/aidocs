"""
图表渲染引擎模块

支持多种图表类型的检测和渲染：
- base: 基础引擎接口
- chart_detector: 图表检测器
- Mermaid图表渲染 (待实现)
- PlantUML图表渲染 (待实现)
"""

from .base import BaseEngine, BaseRenderEngine, ConversionResult
from .chart_detector import ChartDetector, ChartInfo, ChartType
from .mermaid_engine import MermaidEngine, MermaidTheme, MermaidOutputFormat, MermaidRenderConfig
from .plantuml_engine import PlantUMLEngine, PlantUMLTheme, PlantUMLOutputFormat, PlantUMLRenderConfig
from .multi_engine_manager import MultiRenderEngineManager, RenderStrategy

__all__ = [
    'BaseEngine',
    'BaseRenderEngine',
    'ConversionResult',
    'ChartDetector',
    'ChartInfo',
    'ChartType',
    'MermaidEngine',
    'MermaidTheme',
    'MermaidOutputFormat',
    'MermaidRenderConfig',
    'PlantUMLEngine',
    'PlantUMLTheme',
    'PlantUMLOutputFormat',
    'PlantUMLRenderConfig',
    'MultiRenderEngineManager',
    'RenderStrategy'
]
