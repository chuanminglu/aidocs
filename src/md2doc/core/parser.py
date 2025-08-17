"""
Markdown解析器

提供Markdown文档的解析功能：
- 标题层级解析
- 段落和文本解析
- 列表解析
- 代码块解析
- 图表代码检测
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from ..engines.chart_detector import ChartDetector


class ElementType(Enum):
    """元素类型枚举"""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    CODE_BLOCK = "code_block"
    CHART = "chart"
    TABLE = "table"
    QUOTE = "quote"
    IMAGE = "image"
    LINK = "link"


@dataclass
class MarkdownElement:
    """Markdown元素基类"""
    type: ElementType
    content: str
    line_number: int
    raw_text: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HeadingElement(MarkdownElement):
    """标题元素"""
    level: int = 1
    
    def __post_init__(self):
        self.type = ElementType.HEADING


@dataclass
class ParagraphElement(MarkdownElement):
    """段落元素"""
    
    def __post_init__(self):
        self.type = ElementType.PARAGRAPH


@dataclass
class ListElement(MarkdownElement):
    """列表元素"""
    items: List[str] = field(default_factory=list)
    list_type: str = "unordered"  # "ordered" or "unordered"
    
    def __post_init__(self):
        self.type = ElementType.LIST


@dataclass
class CodeBlockElement(MarkdownElement):
    """代码块元素"""
    language: str = ""
    
    def __post_init__(self):
        self.type = ElementType.CODE_BLOCK


@dataclass
class ChartElement(MarkdownElement):
    """图表元素"""
    chart_type: str = ""  # "mermaid", "plantuml", etc.
    
    def __post_init__(self):
        self.type = ElementType.CHART


@dataclass
class TableElement(MarkdownElement):
    """表格元素"""
    headers: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)
    
    def __post_init__(self):
        self.type = ElementType.TABLE


@dataclass
class ParseResult:
    """解析结果"""
    elements: List[MarkdownElement] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def headings(self) -> List[HeadingElement]:
        """获取所有标题"""
        return [e for e in self.elements if isinstance(e, HeadingElement)]
    
    @property
    def paragraphs(self) -> List[ParagraphElement]:
        """获取所有段落"""
        return [e for e in self.elements if isinstance(e, ParagraphElement)]
    
    @property
    def lists(self) -> List[ListElement]:
        """获取所有列表"""
        return [e for e in self.elements if isinstance(e, ListElement)]
    
    @property
    def code_blocks(self) -> List[CodeBlockElement]:
        """获取所有代码块"""
        return [e for e in self.elements if isinstance(e, CodeBlockElement)]
    
    @property
    def charts(self) -> List[ChartElement]:
        """获取所有图表"""
        return [e for e in self.elements if isinstance(e, ChartElement)]
    
    @property
    def tables(self) -> List[TableElement]:
        """获取所有表格"""
        return [e for e in self.elements if isinstance(e, TableElement)]


class MarkdownParser:
    """Markdown解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self._chart_detector = ChartDetector()
        # 保留原有的图表类型列表用于向后兼容
        self._chart_types = ["mermaid", "plantuml", "graphviz", "chart"]
        
    def parse(self, content: str) -> ParseResult:
        """解析Markdown内容
        
        Args:
            content: Markdown文本内容
            
        Returns:
            解析结果
        """
        result = ParseResult()
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            line_number = i + 1
            
            # 跳过空行
            if not line.strip():
                i += 1
                continue
            
            # 解析标题
            if line.startswith('#'):
                element = self._parse_heading(line, line_number)
                if element:
                    result.elements.append(element)
                i += 1
                continue
            
            # 解析代码块
            if line.strip().startswith('```'):
                element, consumed_lines = self._parse_code_block(lines, i)
                if element:
                    result.elements.append(element)
                i += consumed_lines
                continue
            
            # 解析列表
            if re.match(r'^[\s]*[-*+]\s', line) or re.match(r'^[\s]*\d+\.\s', line):
                element, consumed_lines = self._parse_list(lines, i)
                if element:
                    result.elements.append(element)
                i += consumed_lines
                continue
            
            # 解析表格
            if '|' in line and i + 1 < len(lines) and '|' in lines[i + 1]:
                element, consumed_lines = self._parse_table(lines, i)
                if element:
                    result.elements.append(element)
                i += consumed_lines
                continue
            
            # 解析段落
            element, consumed_lines = self._parse_paragraph(lines, i)
            if element:
                result.elements.append(element)
            i += consumed_lines
        
        # 添加统计信息到元数据
        result.metadata = {
            "total_elements": len(result.elements),
            "headings_count": len(result.headings),
            "paragraphs_count": len(result.paragraphs),
            "lists_count": len(result.lists),
            "code_blocks_count": len(result.code_blocks),
            "charts_count": len(result.charts),
            "tables_count": len(result.tables)
        }
        
        return result
    
    def _parse_heading(self, line: str, line_number: int) -> Optional[HeadingElement]:
        """解析标题"""
        match = re.match(r'^(#{1,6})\s+(.+)', line)
        if match:
            level = len(match.group(1))
            content = match.group(2).strip()
            return HeadingElement(
                type=ElementType.HEADING,
                content=content,
                line_number=line_number,
                raw_text=line,
                level=level
            )
        return None
    
    def _parse_code_block(self, lines: List[str], start_index: int) -> tuple:
        """解析代码块"""
        start_line = lines[start_index]
        
        # 检查是否是代码块开始
        match = re.match(r'^```(\w*)', start_line.strip())
        if not match:
            return None, 1
        
        language = match.group(1) or ""
        code_lines = []
        
        # 寻找代码块结束
        i = start_index + 1
        while i < len(lines):
            if lines[i].strip() == '```':
                break
            code_lines.append(lines[i])
            i += 1
        
        if i >= len(lines):
            # 没有找到结束标记，视为普通段落
            return None, 1
        
        content = '\n'.join(code_lines)
        raw_text = '\n'.join(lines[start_index:i+1])
        
        # 使用新的图表检测器检测是否是图表代码
        chart_info = self._chart_detector.detect_chart(content, language)
        
        if chart_info:
            # 创建图表元素
            element = ChartElement(
                type=ElementType.CHART,
                content=content,
                line_number=start_index + 1,
                raw_text=raw_text,
                chart_type=chart_info.chart_type.value,
                attributes={
                    'syntax': chart_info.syntax_valid,
                    'subtype': chart_info.subtype,
                    'metadata': chart_info.metadata
                }
            )
        else:
            # 创建普通代码块元素
            element = CodeBlockElement(
                type=ElementType.CODE_BLOCK,
                content=content,
                line_number=start_index + 1,
                raw_text=raw_text,
                language=language
            )
        
        return element, i - start_index + 1
    
    def _parse_list(self, lines: List[str], start_index: int) -> tuple:
        """解析列表"""
        list_items = []
        i = start_index
        first_line = lines[i]
        
        # 确定列表类型
        is_ordered = bool(re.match(r'^[\s]*\d+\.\s', first_line))
        list_type = "ordered" if is_ordered else "unordered"
        
        # 收集列表项
        while i < len(lines):
            line = lines[i]
            
            # 检查是否是列表项
            if is_ordered:
                match = re.match(r'^[\s]*\d+\.\s+(.+)', line)
            else:
                match = re.match(r'^[\s]*[-*+]\s+(.+)', line)
            
            if match:
                list_items.append(match.group(1).strip())
                i += 1
            elif line.strip() == "":
                # 空行可能分隔列表项
                i += 1
                if i < len(lines) and lines[i].strip():
                    # 下一行不是空行，检查是否继续列表
                    next_line = lines[i]
                    if is_ordered:
                        if not re.match(r'^[\s]*\d+\.\s', next_line):
                            break
                    else:
                        if not re.match(r'^[\s]*[-*+]\s', next_line):
                            break
            else:
                break
        
        if list_items:
            content = '\n'.join([f"- {item}" for item in list_items])
            element = ListElement(
                type=ElementType.LIST,
                content=content,
                line_number=start_index + 1,
                raw_text='\n'.join(lines[start_index:i]),
                items=list_items,
                list_type=list_type
            )
            return element, i - start_index
        
        return None, 1
    
    def _parse_table(self, lines: List[str], start_index: int) -> tuple:
        """解析表格"""
        table_lines = []
        i = start_index
        
        # 收集表格行
        while i < len(lines) and '|' in lines[i]:
            table_lines.append(lines[i])
            i += 1
        
        if len(table_lines) < 2:
            return None, 1
        
        # 解析表头
        header_line = table_lines[0]
        headers = [cell.strip() for cell in header_line.split('|') if cell.strip()]
        
        # 跳过分隔行（第二行）
        rows = []
        for line in table_lines[2:]:
            row = [cell.strip() for cell in line.split('|') if cell.strip()]
            if row:
                rows.append(row)
        
        element = TableElement(
            type=ElementType.TABLE,
            content='\n'.join(table_lines),
            line_number=start_index + 1,
            raw_text='\n'.join(table_lines),
            headers=headers,
            rows=rows
        )
        
        return element, len(table_lines)
    
    def _parse_paragraph(self, lines: List[str], start_index: int) -> tuple:
        """解析段落"""
        paragraph_lines = []
        i = start_index
        
        # 收集段落行（直到空行或特殊标记）
        while i < len(lines):
            line = lines[i]
            
            # 如果是空行，结束段落
            if not line.strip():
                break
            
            # 如果是特殊标记（标题、列表等），结束段落
            if (line.startswith('#') or 
                line.strip().startswith('```') or
                re.match(r'^[\s]*[-*+]\s', line) or
                re.match(r'^[\s]*\d+\.\s', line) or
                '|' in line):
                break
            
            paragraph_lines.append(line)
            i += 1
        
        if paragraph_lines:
            content = ' '.join(line.strip() for line in paragraph_lines)
            element = ParagraphElement(
                type=ElementType.PARAGRAPH,
                content=content,
                line_number=start_index + 1,
                raw_text='\n'.join(paragraph_lines)
            )
            return element, len(paragraph_lines)
        
        return None, 1
