"""
多渲染引擎管理器

统一管理多种图表渲染引擎，提供：
- 自动引擎选择
- 降级渲染策略
- 统一错误处理
- 网络状态检测
"""

import logging
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Type
from dataclasses import dataclass

from .base import BaseRenderEngine
from .mermaid_engine import MermaidEngine
from .plantuml_engine import PlantUMLEngine, PlantUMLRenderConfig
from .chart_detector import ChartInfo, ChartType


@dataclass
class RenderStrategy:
    """渲染策略配置"""
    engine_class: Type[BaseRenderEngine]
    config: Optional[dict] = None
    priority: int = 0  # 优先级，数字越小优先级越高
    fallback_on_failure: bool = True
    network_required: bool = True


class MultiRenderEngineManager:
    """多渲染引擎管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.logger = logging.getLogger(__name__)
        
        # 网络状态
        self._network_available = None
        self._last_network_check = 0
        self._network_check_interval = 30  # 30秒
        
        # 引擎注册表
        self.engines: Dict[ChartType, List[RenderStrategy]] = {}
        
        # 初始化默认策略
        self._register_default_strategies()
        
        # 实例化的引擎缓存
        self._engine_instances: Dict[str, BaseRenderEngine] = {}
        
    def _register_default_strategies(self):
        """注册默认渲染策略"""
        # Mermaid渲染策略
        self.engines[ChartType.MERMAID] = [
            RenderStrategy(
                engine_class=MermaidEngine,
                config={'online_first': True},
                priority=0,
                network_required=True
            ),
            RenderStrategy(
                engine_class=MermaidEngine,
                config={'online_first': False},
                priority=1,
                network_required=False
            )
        ]
        
        # PlantUML渲染策略
        self.engines[ChartType.PLANTUML] = [
            RenderStrategy(
                engine_class=PlantUMLEngine,
                config={},
                priority=0,
                network_required=True
            )
        ]
        
    def register_strategy(self, chart_type: ChartType, strategy: RenderStrategy):
        """注册新的渲染策略
        
        Args:
            chart_type: 图表类型
            strategy: 渲染策略
        """
        if chart_type not in self.engines:
            self.engines[chart_type] = []
            
        self.engines[chart_type].append(strategy)
        # 按优先级排序
        self.engines[chart_type].sort(key=lambda s: s.priority)
        
    def render(self, chart_info: ChartInfo, output_path: Optional[Path] = None) -> Tuple[bool, Optional[Path], Optional[str]]:
        """渲染图表
        
        Args:
            chart_info: 图表信息
            output_path: 输出路径
            
        Returns:
            (是否成功, 输出路径, 错误信息)
        """
        chart_type = chart_info.chart_type
        
        if chart_type not in self.engines:
            return False, None, f"不支持的图表类型: {chart_type}"
            
        strategies = self.engines[chart_type]
        network_available = self._check_network_status()
        
        last_error = None
        
        for strategy in strategies:
            # 检查网络需求
            if strategy.network_required and not network_available:
                self.logger.debug(f"跳过需要网络的策略: {strategy.engine_class.__name__}")
                continue
                
            try:
                # 获取或创建引擎实例
                engine = self._get_engine_instance(strategy)
                
                if not engine.can_render(chart_info):
                    continue
                    
                # 尝试渲染
                success, rendered_path, error = engine.render(chart_info, output_path)
                
                if success:
                    self.logger.info(f"渲染成功: {strategy.engine_class.__name__}")
                    return True, rendered_path, None
                    
                last_error = error
                self.logger.warning(f"渲染失败 {strategy.engine_class.__name__}: {error}")
                
                if not strategy.fallback_on_failure:
                    break
                    
            except Exception as e:
                error_msg = f"引擎异常 {strategy.engine_class.__name__}: {e}"
                self.logger.error(error_msg)
                last_error = error_msg
                
                if not strategy.fallback_on_failure:
                    break
                    
        return False, None, last_error or "所有渲染策略都失败了"
        
    def _get_engine_instance(self, strategy: RenderStrategy) -> BaseRenderEngine:
        """获取引擎实例
        
        Args:
            strategy: 渲染策略
            
        Returns:
            引擎实例
        """
        # 创建唯一键
        engine_key = f"{strategy.engine_class.__name__}_{hash(str(strategy.config))}"
        
        if engine_key not in self._engine_instances:
            # 创建新实例
            try:
                if strategy.engine_class == MermaidEngine:
                    # MermaidEngine接受字典配置
                    self._engine_instances[engine_key] = MermaidEngine(strategy.config)
                elif strategy.engine_class == PlantUMLEngine:
                    # PlantUMLEngine需要PlantUMLRenderConfig
                    if isinstance(strategy.config, dict):
                        config = PlantUMLRenderConfig()
                        # 应用配置覆盖
                        for key, value in strategy.config.items():
                            if hasattr(config, key):
                                setattr(config, key, value)
                    else:
                        config = strategy.config
                    self._engine_instances[engine_key] = PlantUMLEngine(config)
                else:
                    # 其他引擎类型
                    self._engine_instances[engine_key] = strategy.engine_class()
            except Exception as e:
                self.logger.error(f"创建引擎实例失败 {strategy.engine_class.__name__}: {e}")
                # 使用默认配置创建
                if strategy.engine_class == MermaidEngine:
                    self._engine_instances[engine_key] = MermaidEngine()
                elif strategy.engine_class == PlantUMLEngine:
                    self._engine_instances[engine_key] = PlantUMLEngine()
                else:
                    self._engine_instances[engine_key] = strategy.engine_class()
                
        return self._engine_instances[engine_key]
        
    def _check_network_status(self) -> bool:
        """检查网络状态
        
        Returns:
            网络是否可用
        """
        current_time = time.time()
        
        # 缓存检查结果
        if (self._network_available is not None and 
            current_time - self._last_network_check < self._network_check_interval):
            return self._network_available
            
        # 进行网络检查
        try:
            # 快速检查几个可靠的服务
            test_urls = [
                'https://www.google.com',
                'https://www.github.com',
                'https://httpbin.org/status/200'
            ]
            
            for url in test_urls:
                try:
                    response = requests.head(url, timeout=3)
                    if response.status_code < 400:
                        self._network_available = True
                        self._last_network_check = current_time
                        self.logger.debug("网络连接正常")
                        return True
                except requests.RequestException:
                    continue
                    
            self._network_available = False
            self._last_network_check = current_time
            self.logger.warning("网络连接不可用")
            return False
            
        except Exception as e:
            self.logger.error(f"网络状态检查失败: {e}")
            self._network_available = False
            return False
            
    def get_available_engines(self, chart_type: ChartType) -> List[str]:
        """获取可用的引擎列表
        
        Args:
            chart_type: 图表类型
            
        Returns:
            可用引擎名称列表
        """
        if chart_type not in self.engines:
            return []
            
        network_available = self._check_network_status()
        available = []
        
        for strategy in self.engines[chart_type]:
            if strategy.network_required and not network_available:
                continue
                
            engine_name = strategy.engine_class.__name__
            if strategy.config:
                engine_name += f" ({strategy.config})"
            available.append(engine_name)
            
        return available
        
    def validate_chart(self, chart_info: ChartInfo) -> Tuple[bool, Optional[str]]:
        """验证图表
        
        Args:
            chart_info: 图表信息
            
        Returns:
            (是否有效, 错误信息)
        """
        chart_type = chart_info.chart_type
        
        if chart_type not in self.engines:
            return False, f"不支持的图表类型: {chart_type}"
            
        # 尝试用第一个可用引擎验证
        strategies = self.engines[chart_type]
        network_available = self._check_network_status()
        
        for strategy in strategies:
            if strategy.network_required and not network_available:
                continue
                
            try:
                engine = self._get_engine_instance(strategy)
                return engine.validate_chart(chart_info.content)
            except Exception as e:
                self.logger.error(f"验证失败 {strategy.engine_class.__name__}: {e}")
                continue
                
        return False, "没有可用的验证引擎"
        
    def clear_cache(self):
        """清理引擎缓存"""
        self._engine_instances.clear()
        self._network_available = None
        self.logger.info("引擎缓存已清理")
