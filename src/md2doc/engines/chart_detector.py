"""
图表检测引擎

提供图表代码块的检测和分类功能：
- 支持多种图表类型识别
- 提取图表元数据
- 分类图表代码块
- 为后续渲染提供基础
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class ChartType(Enum):
    """图表类型枚举"""
    MERMAID = "mermaid"
    PLANTUML = "plantuml"
    FLOWCHART = "flowchart" 
    SEQUENCE = "sequence"
    GANTT = "gantt"
    CLASS_DIAGRAM = "class"
    ER_DIAGRAM = "er"
    UNKNOWN = "unknown"


@dataclass
class ChartInfo:
    """图表信息"""
    chart_type: ChartType
    content: str
    language: str = ""
    title: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    line_number: int = 0
    raw_block: str = ""
    
    @property
    def subtype(self) -> str:
        """获取图表子类型"""
        return self.config.get('subtype', '') if self.config else ''
    
    @property
    def syntax_valid(self) -> bool:
        """获取语法验证状态"""
        return self.config.get('syntax_valid', True) if self.config else True
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """获取图表元数据"""
        return self.config.get('metadata', {}) if self.config else {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "chart_type": self.chart_type.value,
            "content": self.content,
            "language": self.language,
            "title": self.title,
            "config": self.config or {},
            "line_number": self.line_number,
            "raw_block": self.raw_block
        }


class ChartDetector:
    """图表检测器"""
    
    def __init__(self):
        """初始化检测器"""
        self._init_patterns()
    
    def _init_patterns(self):
        """初始化检测模式"""
        # 代码块基础模式
        self.code_block_pattern = re.compile(
            r'```(\w+)?\s*\n(.*?)\n```',
            re.DOTALL | re.MULTILINE
        )
        
        # Mermaid图表模式
        self.mermaid_patterns = {
            ChartType.MERMAID: re.compile(r'```mermaid\s*\n(.*?)\n```', re.DOTALL),
            'flowchart': re.compile(r'(flowchart|graph)\s+(TD|TB|BT|RL|LR)', re.IGNORECASE),
            'sequence': re.compile(r'sequenceDiagram', re.IGNORECASE),
            'class': re.compile(r'classDiagram', re.IGNORECASE),
            'er': re.compile(r'erDiagram', re.IGNORECASE),
            'gantt': re.compile(r'gantt', re.IGNORECASE),
            'pie': re.compile(r'pie\s+title', re.IGNORECASE),
            'gitgraph': re.compile(r'gitGraph', re.IGNORECASE)
        }
        
        # PlantUML图表模式
        self.plantuml_patterns = {
            ChartType.PLANTUML: re.compile(r'```plantuml\s*\n(.*?)\n```', re.DOTALL),
            'uml_start': re.compile(r'@startuml', re.IGNORECASE),
            'uml_end': re.compile(r'@enduml', re.IGNORECASE),
            'class': re.compile(r'class\s+\w+', re.IGNORECASE),
            'sequence': re.compile(r'actor\s+\w+|participant\s+\w+', re.IGNORECASE),
            'activity': re.compile(r'@startactivity|:.*?;', re.IGNORECASE),
            'component': re.compile(r'@startcomponent|\[.*?\]', re.IGNORECASE)
        }
        
        # 其他图表类型模式
        self.other_patterns = {
            'graphviz': re.compile(r'```(dot|graphviz)\s*\n(.*?)\n```', re.DOTALL),
            'chart_js': re.compile(r'```chart\s*\n(.*?)\n```', re.DOTALL),
            'd3': re.compile(r'```d3\s*\n(.*?)\n```', re.DOTALL)
        }
        
        # 图表标题提取模式
        self.title_patterns = [
            re.compile(r'title\s*[:\s]\s*(.+)', re.IGNORECASE),
            re.compile(r'%%\s*title\s*[:\s]\s*(.+)', re.IGNORECASE),
            re.compile(r'#\s*(.+)', re.IGNORECASE)  # Markdown标题
        ]
    
    def detect_chart(self, content: str, language_hint: Optional[str] = None) -> Optional[ChartInfo]:
        """检测单个代码块是否为图表
        
        Args:
            content: 代码块内容
            language_hint: 语言提示（如 'mermaid', 'plantuml' 等）
            
        Returns:
            ChartInfo对象如果检测到图表，否则返回None
        """
        # 创建一个临时代码块对象
        block = {
            'content': content.strip(),
            'language': language_hint or '',
            'start_line': 1,
            'end_line': len(content.split('\n')) + 1,
            'raw_block': content  # 添加原始代码块内容
        }
        
        return self._analyze_code_block(block)
    
    def detect_charts_in_text(self, text: str) -> List[ChartInfo]:
        """检测文本中的所有图表
        
        Args:
            text: 要检测的文本
            
        Returns:
            检测到的图表信息列表
        """
        charts = []
        
        # 找到所有代码块
        code_blocks = self._find_code_blocks(text)
        
        for block in code_blocks:
            chart_info = self._analyze_code_block(block)
            if chart_info and chart_info.chart_type != ChartType.UNKNOWN:
                charts.append(chart_info)
        
        return charts
    
    def _find_code_blocks(self, text: str) -> List[Dict[str, Any]]:
        """找到文本中的所有代码块
        
        Args:
            text: 源文本
            
        Returns:
            代码块信息列表
        """
        blocks = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 检测代码块开始
            if line.startswith('```'):
                language = line[3:].strip()
                start_line = i
                content_lines = []
                
                # 查找代码块结束
                i += 1
                while i < len(lines):
                    if lines[i].strip() == '```':
                        # 找到结束标记
                        end_line = i
                        content = '\n'.join(content_lines)
                        raw_block = '\n'.join(lines[start_line:end_line + 1])
                        
                        blocks.append({
                            'language': language,
                            'content': content,
                            'start_line': start_line,
                            'end_line': end_line,
                            'raw_block': raw_block
                        })
                        break
                    else:
                        content_lines.append(lines[i])
                    i += 1
            
            i += 1
        
        return blocks
    
    def _analyze_code_block(self, block: Dict[str, Any]) -> Optional[ChartInfo]:
        """分析代码块，判断是否为图表
        
        Args:
            block: 代码块信息
            
        Returns:
            图表信息，如果不是图表则返回None
        """
        language = block['language'].lower()
        content = block['content']
        
        # 首先尝试内容模式匹配，这比语言提示更准确
        chart_info = self._detect_by_content_patterns(block)
        if chart_info:
            return chart_info
        
        # 如果内容检测失败，再根据语言标签进行分析
        if language == 'mermaid':
            return self._analyze_mermaid_chart(block)
        elif language in ['plantuml', 'puml']:
            return self._analyze_plantuml_chart(block)
        elif language in ['dot', 'graphviz']:
            return ChartInfo(
                chart_type=ChartType.UNKNOWN,
                content=content,
                language=language,
                line_number=block['start_line'],
                raw_block=block['raw_block'],
                title=self._extract_title(content)
            )
        
        return None
    
    def _analyze_mermaid_chart(self, block: Dict[str, Any]) -> ChartInfo:
        """分析Mermaid图表
        
        Args:
            block: 代码块信息
            
        Returns:
            Mermaid图表信息
        """
        content = block['content']
        
        # 确定Mermaid子类型
        chart_subtype = self._detect_mermaid_subtype(content)
        
        return ChartInfo(
            chart_type=ChartType.MERMAID,
            content=content,
            language='mermaid',
            title=self._extract_title(content),
            config={'subtype': chart_subtype},
            line_number=block['start_line'],
            raw_block=block['raw_block']
        )
    
    def _analyze_plantuml_chart(self, block: Dict[str, Any]) -> ChartInfo:
        """分析PlantUML图表
        
        Args:
            block: 代码块信息
            
        Returns:
            PlantUML图表信息
        """
        content = block['content']
        
        # 确定PlantUML子类型
        chart_subtype = self._detect_plantuml_subtype(content)
        
        return ChartInfo(
            chart_type=ChartType.PLANTUML,
            content=content,
            language='plantuml',
            title=self._extract_title(content),
            config={'subtype': chart_subtype},
            line_number=block['start_line'],
            raw_block=block['raw_block']
        )
    
    def _detect_by_content_patterns(self, block: Dict[str, Any]) -> Optional[ChartInfo]:
        """通过内容模式检测图表类型
        
        Args:
            block: 代码块信息
            
        Returns:
            图表信息或None
        """
        content = block['content']
        
        # 检测PlantUML
        if self.plantuml_patterns['uml_start'].search(content):
            return self._analyze_plantuml_chart(block)
        
        # 检测Mermaid关键词
        for pattern_name, pattern in self.mermaid_patterns.items():
            if pattern_name != ChartType.MERMAID and pattern.search(content):
                return ChartInfo(
                    chart_type=ChartType.MERMAID,
                    content=content,
                    language=block['language'] or 'mermaid',
                    title=self._extract_title(content),
                    config={'subtype': pattern_name},
                    line_number=block['start_line'],
                    raw_block=block['raw_block']
                )
        
        return None
    
    def _detect_mermaid_subtype(self, content: str) -> str:
        """检测Mermaid子类型
        
        Args:
            content: 图表内容
            
        Returns:
            子类型名称
        """
        content_lower = content.lower()
        
        if 'sequencediagram' in content_lower:
            return 'sequence'
        elif 'classdiagram' in content_lower:
            return 'class'
        elif 'erdiagram' in content_lower:
            return 'er'
        elif 'gantt' in content_lower:
            return 'gantt'
        elif 'pie' in content_lower and 'title' in content_lower:
            return 'pie'
        elif 'gitgraph' in content_lower:
            return 'gitgraph'
        elif any(keyword in content_lower for keyword in ['flowchart', 'graph']):
            return 'flowchart'
        else:
            return 'unknown'
    
    def _detect_plantuml_subtype(self, content: str) -> str:
        """检测PlantUML子类型
        
        Args:
            content: 图表内容
            
        Returns:
            子类型名称
        """
        content_lower = content.lower()
        
        # 检测时序图：有箭头符号或participant关键字
        if (any(keyword in content_lower for keyword in ['actor', 'participant']) or
            any(arrow in content for arrow in ['->', '-->', '->>'])):
            return 'sequence'
        elif '@startactivity' in content_lower or ':' in content and ';' in content:
            return 'activity'
        elif 'class ' in content_lower:
            return 'class'
        elif '@startcomponent' in content_lower or '[' in content and ']' in content:
            return 'component'
        elif '@startmindmap' in content_lower:
            return 'mindmap'
        elif '@startusecase' in content_lower or 'usecase' in content_lower:
            return 'usecase'
        else:
            return 'unknown'
    
    def _extract_title(self, content: str) -> Optional[str]:
        """提取图表标题
        
        Args:
            content: 图表内容
            
        Returns:
            标题文本或None
        """
        for pattern in self.title_patterns:
            match = pattern.search(content)
            if match:
                return match.group(1).strip()
        
        return None
    
    def get_supported_chart_types(self) -> List[str]:
        """获取支持的图表类型
        
        Returns:
            支持的图表类型列表
        """
        return [chart_type.value for chart_type in ChartType if chart_type != ChartType.UNKNOWN]
    
    def validate_chart_syntax(self, chart_info: ChartInfo) -> Tuple[bool, Optional[str]]:
        """验证图表语法
        
        Args:
            chart_info: 图表信息
            
        Returns:
            (是否有效, 错误信息)
        """
        if chart_info.chart_type == ChartType.MERMAID:
            return self._validate_mermaid_syntax(chart_info.content)
        elif chart_info.chart_type == ChartType.PLANTUML:
            return self._validate_plantuml_syntax(chart_info.content)
        
        return True, None
    
    def _validate_mermaid_syntax(self, content: str) -> Tuple[bool, Optional[str]]:
        """验证Mermaid语法
        
        Args:
            content: Mermaid内容
            
        Returns:
            (是否有效, 错误信息)
        """
        # 基础语法检查
        if not content.strip():
            return False, "Mermaid内容为空"
        
        # 检查是否有基本的图表类型声明
        content_lower = content.lower()
        valid_starts = [
            'flowchart', 'graph', 'sequencediagram', 'classdiagram',
            'erdiagram', 'gantt', 'pie', 'gitgraph'
        ]
        
        if not any(start in content_lower for start in valid_starts):
            return False, "未找到有效的Mermaid图表类型声明"
        
        return True, None
    
    def _validate_plantuml_syntax(self, content: str) -> Tuple[bool, Optional[str]]:
        """验证PlantUML语法
        
        Args:
            content: PlantUML内容
            
        Returns:
            (是否有效, 错误信息)
        """
        # 检查开始和结束标记
        if '@startuml' not in content.lower():
            return False, "缺少@startuml开始标记"
        
        if '@enduml' not in content.lower():
            return False, "缺少@enduml结束标记"
        
        return True, None
