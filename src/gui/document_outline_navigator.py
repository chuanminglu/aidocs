"""
文档大纲导航器
实现文档结构解析和大纲树形控件功能，支持Markdown和Word文档
"""
import re
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QPushButton, QLineEdit, QCheckBox, QComboBox,
    QMenu, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QFont

# 导入Word解析器
try:
    from src.core.word_parser import WordDocumentParser, OutlineItem as WordOutlineItem
    WORD_SUPPORT_AVAILABLE = True
except ImportError:
    WORD_SUPPORT_AVAILABLE = False
    WordOutlineItem = None


class OutlineItem:
    """大纲项数据类"""
    
    def __init__(self, text: str, level: int, line_number: int, item_type: str = "heading"):
        self.text = text.strip()
        self.level = level
        self.line_number = line_number
        self.item_type = item_type  # heading, list, code_block, etc.
        self.children: List['OutlineItem'] = []
        self.parent: Optional['OutlineItem'] = None
    
    def add_child(self, child: 'OutlineItem'):
        """添加子项"""
        child.parent = self
        self.children.append(child)
    
    def get_display_text(self) -> str:
        """获取显示文本"""
        prefix = "  " * (self.level - 1) if self.level > 1 else ""
        type_prefix = {
            "heading": "",
            "list": "• ",
            "code_block": "⚡ ",
            "table": "📊 ",
            "quote": "❝ "
        }.get(self.item_type, "")
        return f"{prefix}{type_prefix}{self.text}"


class DocumentParser:
    """文档解析器，支持Markdown、HTML和Word文档"""
    
    def __init__(self):
        # Markdown标题正则
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        # HTML标题正则
        self.html_heading_pattern = re.compile(r'<h([1-6])[^>]*>([^<]+)</h[1-6]>', re.IGNORECASE)
        # 列表项正则
        self.list_pattern = re.compile(r'^[\s]*[-*+]\s+(.+)$', re.MULTILINE)
        # 代码块正则
        self.code_block_pattern = re.compile(r'^```[^\n]*\n?([^`]+)```', re.MULTILINE)
        # 表格正则
        self.table_pattern = re.compile(r'^\|.+\|$', re.MULTILINE)
        # 引用正则
        self.quote_pattern = re.compile(r'^>\s+(.+)$', re.MULTILINE)
        
        # Word解析器
        self.word_parser = None
        if WORD_SUPPORT_AVAILABLE:
            self.word_parser = WordDocumentParser()
    
    def parse_document(self, content: str, doc_type: str = "markdown", file_path: Optional[str] = None) -> List[OutlineItem]:
        """解析文档内容"""
        if doc_type.lower() == "word" and self.word_parser and file_path:
            return self.parse_word_document(file_path)
        elif doc_type.lower() == "markdown":
            return self.parse_markdown(content)
        elif doc_type.lower() in ["html", "htm"]:
            return self.parse_html(content)
        else:
            return self.parse_plain_text(content)
    
    def parse_word_document(self, file_path: str) -> List[OutlineItem]:
        """解析Word文档"""
        if not self.word_parser:
            return []
        
        try:
            # 使用Word解析器获取大纲
            word_outline_items = self.word_parser.get_outline_items(file_path)
            
            # 转换为本地OutlineItem格式
            outline_items = []
            for word_item in word_outline_items:
                outline_item = OutlineItem(
                    text=word_item.text,
                    level=word_item.level,
                    line_number=word_item.line_number,
                    item_type="heading"
                )
                outline_items.append(outline_item)
            
            return self.build_hierarchy(outline_items)
            
        except Exception as e:
            print(f"解析Word文档失败: {e}")
            return []
    
    def parse_markdown(self, content: str) -> List[OutlineItem]:
        """解析Markdown文档 - 优化版本"""
        items = []
        lines = content.split('\n')
        in_code_block = False
        table_started = False
        
        for i, line in enumerate(lines, 1):
            # 检查代码块状态
            if line.strip().startswith('```'):
                in_code_block = self._handle_code_block(line, i, in_code_block, items)
                continue
            
            # 在代码块内跳过解析
            if in_code_block:
                continue
            
            # 解析各种内容类型
            if self._parse_heading(line, i, items):
                table_started = False
                continue
            
            if self._parse_list_item(line, i, items):
                table_started = False
                continue
            
            if self._parse_table(line, i, items, table_started):
                table_started = True
                continue
            else:
                table_started = False
            
            if self._parse_quote(line, i, items):
                continue
        
        return self.build_hierarchy(items)
    
    def _handle_code_block(self, line: str, line_num: int, in_code_block: bool, items: List[OutlineItem]) -> bool:
        """处理代码块"""
        if not in_code_block:
            code_title = line.strip()[3:].strip()
            if code_title:
                items.append(OutlineItem(f"代码块: {code_title}", 7, line_num, "code_block"))
            return True
        return False
    
    def _parse_heading(self, line: str, line_num: int, items: List[OutlineItem]) -> bool:
        """解析标题"""
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            items.append(OutlineItem(text, level, line_num, "heading"))
            return True
        return False
    
    def _parse_list_item(self, line: str, line_num: int, items: List[OutlineItem]) -> bool:
        """解析列表项"""
        list_match = re.match(r'^[\s]*[-*+]\s+(.+)$', line)
        if list_match:
            text = list_match.group(1).strip()
            indent = len(line) - len(line.lstrip())
            indent_level = max(1, indent // 2) + 6
            items.append(OutlineItem(text, indent_level, line_num, "list"))
            return True
        return False
    
    def _parse_table(self, line: str, line_num: int, items: List[OutlineItem], table_started: bool) -> bool:
        """解析表格"""
        if re.match(r'^\|.+\|$', line.strip()):
            if not table_started and not re.match(r'^\|[\s:|-]+\|$', line.strip()):
                items.append(OutlineItem("表格", 7, line_num, "table"))
                return True
        return False
    
    def _parse_quote(self, line: str, line_num: int, items: List[OutlineItem]) -> bool:
        """解析引用"""
        quote_match = re.match(r'^>\s+(.+)$', line)
        if quote_match:
            text = quote_match.group(1).strip()
            if len(text) > 30:
                text = text[:30] + "..."
            items.append(OutlineItem(f"引用: {text}", 7, line_num, "quote"))
            return True
        return False
    
    def parse_html(self, content: str) -> List[OutlineItem]:
        """解析HTML文档"""
        items = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 解析HTML标题
            heading_match = re.search(r'<h([1-6])[^>]*>([^<]+)</h[1-6]>', line, re.IGNORECASE)
            if heading_match:
                level = int(heading_match.group(1))
                text = heading_match.group(2).strip()
                items.append(OutlineItem(text, level, i, "heading"))
        
        return self.build_hierarchy(items)
    
    def parse_plain_text(self, content: str) -> List[OutlineItem]:
        """解析纯文本文档"""
        items = []
        lines = content.split('\n')
        paragraph_count = 0
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and len(line) < 100:  # 可能是标题
                if any(char.isupper() for char in line) or line.endswith(':'):
                    items.append(OutlineItem(line, 1, i, "heading"))
            elif line:
                paragraph_count += 1
                if paragraph_count % 5 == 1:  # 每5段显示一个
                    preview = line[:50] + "..." if len(line) > 50 else line
                    items.append(OutlineItem(f"段落 {paragraph_count}: {preview}", 2, i, "paragraph"))
        
        return items
    
    def build_hierarchy(self, items: List[OutlineItem]) -> List[OutlineItem]:
        """构建层次结构"""
        if not items:
            return []
        
        root_items = []
        stack = []
        
        for item in items:
            # 清理栈，移除比当前项级别高的项
            while stack and stack[-1].level >= item.level:
                stack.pop()
            
            # 如果栈不为空，当前项是栈顶项的子项
            if stack:
                stack[-1].add_child(item)
            else:
                root_items.append(item)
            
            # 将当前项推入栈
            stack.append(item)
        
        return root_items


class OutlineTreeWidget(QTreeWidget):
    """大纲树形控件"""
    
    # 自定义信号
    item_jumped = pyqtSignal(int)  # 跳转到行号
    item_edited = pyqtSignal(str, str)  # 编辑项目 (原文本, 新文本)
    structure_changed = pyqtSignal()  # 结构改变
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_context_menu()
        self.current_line = 0
        self.outline_items = []
    
    def init_ui(self):
        """初始化界面"""
        self.setHeaderLabels(["大纲", "行号"])
        self.setAlternatingRowColors(True)
        self.setRootIsDecorated(True)
        self.setExpandsOnDoubleClick(True)
        
        # 设置列宽
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        
        # 连接信号
        self.itemClicked.connect(self.on_item_clicked)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
    
    def setup_context_menu(self):
        """设置右键菜单"""
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        
        # 跳转到位置
        jump_action = QAction("跳转到此位置", self)
        jump_action.triggered.connect(lambda: self.jump_to_item(item))
        menu.addAction(jump_action)
        
        # 编辑标题
        edit_action = QAction("编辑标题", self)
        edit_action.triggered.connect(lambda: self.edit_item(item))
        menu.addAction(edit_action)
        
        menu.addSeparator()
        
        # 展开/折叠
        if item.childCount() > 0:
            if item.isExpanded():
                collapse_action = QAction("折叠", self)
                collapse_action.triggered.connect(lambda: item.setExpanded(False))
                menu.addAction(collapse_action)
            else:
                expand_action = QAction("展开", self)
                expand_action.triggered.connect(lambda: item.setExpanded(True))
                menu.addAction(expand_action)
        
        # 展开所有/折叠所有
        menu.addSeparator()
        expand_all_action = QAction("展开所有", self)
        expand_all_action.triggered.connect(self.expandAll)
        menu.addAction(expand_all_action)
        
        collapse_all_action = QAction("折叠所有", self)
        collapse_all_action.triggered.connect(self.collapseAll)
        menu.addAction(collapse_all_action)
        
        menu.exec(self.mapToGlobal(position))
    
    def on_item_clicked(self, item, column):
        """项目点击事件"""
        line_number = item.data(0, Qt.ItemDataRole.UserRole)
        if line_number:
            self.item_jumped.emit(line_number)
    
    def on_item_double_clicked(self, item, column):
        """项目双击事件"""
        self.edit_item(item)
    
    def jump_to_item(self, item):
        """跳转到项目"""
        line_number = item.data(0, Qt.ItemDataRole.UserRole)
        if line_number:
            self.item_jumped.emit(line_number)
    
    def edit_item(self, item):
        """编辑项目"""
        # TODO: 实现在线编辑功能
        QMessageBox.information(self, "提示", "编辑功能正在开发中...")
    
    def update_outline(self, outline_items: List[OutlineItem]):
        """更新大纲"""
        self.clear()
        self.outline_items = outline_items
        self._populate_tree(outline_items, None)
        self.expandAll()
    
    def _populate_tree(self, items: List[OutlineItem], parent_widget_item):
        """填充树形结构"""
        for item in items:
            if parent_widget_item:
                widget_item = QTreeWidgetItem(parent_widget_item)
            else:
                widget_item = QTreeWidgetItem(self)
            
            widget_item.setText(0, item.text)
            widget_item.setText(1, str(item.line_number))
            widget_item.setData(0, Qt.ItemDataRole.UserRole, item.line_number)
            
            # 设置图标和样式
            self._set_item_style(widget_item, item)
            
            # 递归添加子项
            if item.children:
                self._populate_tree(item.children, widget_item)
    
    def _set_item_style(self, widget_item: QTreeWidgetItem, outline_item: OutlineItem):
        """设置项目样式"""
        font = QFont()
        
        if outline_item.item_type == "heading":
            if outline_item.level <= 2:
                font.setBold(True)
                font.setPointSize(10)
            elif outline_item.level <= 4:
                font.setPointSize(9)
            else:
                font.setPointSize(8)
        elif outline_item.item_type == "list":
            font.setItalic(True)
            font.setPointSize(8)
        elif outline_item.item_type == "code_block":
            font.setFamily("Courier")
            font.setPointSize(8)
        
        widget_item.setFont(0, font)
    
    def highlight_current_line(self, line_number: int):
        """高亮当前行"""
        self.current_line = line_number
        
        # 清除之前的高亮
        for i in range(self.topLevelItemCount()):
            self._clear_highlight(self.topLevelItem(i))
        
        # 查找并高亮当前行对应的项目
        target_item = self._find_item_by_line(line_number)
        if target_item:
            target_item.setBackground(0, self.palette().highlight())
            target_item.setBackground(1, self.palette().highlight())
            self.scrollToItem(target_item)
    
    def _clear_highlight(self, item: Optional[QTreeWidgetItem]):
        """清除高亮"""
        if item is None:
            return
        
        item.setBackground(0, self.palette().base())
        item.setBackground(1, self.palette().base())
        
        for i in range(item.childCount()):
            child = item.child(i)
            if child:
                self._clear_highlight(child)
    
    def _find_item_by_line(self, line_number: int) -> Optional[QTreeWidgetItem]:
        """根据行号查找项目"""
        def search_item(item: QTreeWidgetItem) -> Optional[QTreeWidgetItem]:
            item_line = item.data(0, Qt.ItemDataRole.UserRole)
            if item_line and item_line <= line_number:
                # 检查是否是最接近的项目
                closest = item
                for i in range(item.childCount()):
                    child = item.child(i)
                    if child:
                        child_result = search_item(child)
                        if child_result:
                            child_line = child_result.data(0, Qt.ItemDataRole.UserRole)
                            if child_line and child_line <= line_number:
                                closest = child_result
                return closest
            return None
        
        best_match = None
        best_line = 0
        
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item:
                result = search_item(item)
                if result:
                    result_line = result.data(0, Qt.ItemDataRole.UserRole)
                    if result_line and result_line <= line_number and result_line > best_line:
                        best_match = result
                        best_line = result_line
        
        return best_match


class DocumentOutlineNavigator(QWidget):
    """文档大纲导航器"""
    
    # 自定义信号
    jump_to_line = pyqtSignal(int)  # 跳转到行号
    outline_updated = pyqtSignal()  # 大纲更新
    
    def __init__(self):
        super().__init__()
        self.parser = DocumentParser()
        self.current_content = ""
        self.current_doc_type = "markdown"
        self.current_file_path = None  # 添加文件路径支持
        self.auto_refresh = True
        self.refresh_timer = QTimer()
        self.init_ui()
        self.setup_timer()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 顶部控制栏
        control_layout = QHBoxLayout()
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索大纲...")
        self.search_input.textChanged.connect(self.filter_outline)
        control_layout.addWidget(QLabel("搜索:"))
        control_layout.addWidget(self.search_input)
        
        # 刷新按钮
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_outline)
        control_layout.addWidget(self.refresh_btn)
        
        # 自动刷新复选框
        self.auto_refresh_cb = QCheckBox("自动刷新")
        self.auto_refresh_cb.setChecked(True)
        self.auto_refresh_cb.toggled.connect(self.toggle_auto_refresh)
        control_layout.addWidget(self.auto_refresh_cb)
        
        layout.addLayout(control_layout)
        
        # 文档类型选择
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("文档类型:"))
        self.doc_type_combo = QComboBox()
        doc_types = ["Markdown", "HTML", "纯文本"]
        if WORD_SUPPORT_AVAILABLE:
            doc_types.insert(-1, "Word文档")  # 在纯文本前插入
        self.doc_type_combo.addItems(doc_types)
        self.doc_type_combo.currentTextChanged.connect(self.on_doc_type_changed)
        type_layout.addWidget(self.doc_type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # 大纲树
        self.outline_tree = OutlineTreeWidget()
        self.outline_tree.item_jumped.connect(self.jump_to_line.emit)
        layout.addWidget(self.outline_tree)
        
        # 统计信息
        self.stats_label = QLabel("统计: 0 个项目")
        self.stats_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(self.stats_label)
        
        self.setLayout(layout)
    
    def setup_timer(self):
        """设置定时器"""
        self.refresh_timer.setSingleShot(True)
        self.refresh_timer.timeout.connect(self.refresh_outline)
    
    def update_content(self, content: str, doc_type: Optional[str] = None, file_path: Optional[str] = None):
        """更新文档内容"""
        self.current_content = content
        self.current_file_path = file_path
        
        if doc_type:
            self.current_doc_type = doc_type.lower()
            # 更新界面上的文档类型选择
            type_map = {"markdown": 0, "html": 1, "txt": 2, "plain": 2}
            if WORD_SUPPORT_AVAILABLE:
                type_map["word"] = 2
                type_map["docx"] = 2
                type_map["doc"] = 2
            index = type_map.get(self.current_doc_type, 0)
            self.doc_type_combo.setCurrentIndex(index)
        
        if self.auto_refresh:
            # 延迟刷新，避免频繁更新
            self.refresh_timer.start(500)
    
    def refresh_outline(self):
        """刷新大纲"""
        # 对于Word文档，即使内容为空也可能有结构
        if not self.current_content.strip() and self.current_doc_type != "word":
            self.outline_tree.clear()
            self.stats_label.setText("统计: 0 个项目")
            return
        
        try:
            # 解析文档
            outline_items = self.parser.parse_document(
                self.current_content, 
                self.current_doc_type,
                self.current_file_path
            )
            
            # 更新树形控件
            self.outline_tree.update_outline(outline_items)
            
            # 更新统计信息
            total_items = self._count_items(outline_items)
            headings = sum(1 for item in self._flatten_items(outline_items) if item.item_type == "heading")
            self.stats_label.setText(f"统计: {total_items} 个项目, {headings} 个标题")
            
            # 发送信号
            self.outline_updated.emit()
            
        except Exception as e:
            print(f"刷新大纲失败: {e}")
            QMessageBox.warning(self, "警告", f"解析文档失败: {str(e)}")
    
    def filter_outline(self, text: str):
        """过滤大纲"""
        def filter_item(item: QTreeWidgetItem, filter_text: str) -> bool:
            # 检查当前项是否匹配
            matches = filter_text.lower() in item.text(0).lower()
            
            # 检查子项
            child_matches = False
            for i in range(item.childCount()):
                child = item.child(i)
                if child and filter_item(child, filter_text):
                    child_matches = True
            
            # 显示/隐藏项目
            visible = matches or child_matches or not filter_text
            item.setHidden(not visible)
            
            return visible
        
        # 过滤所有顶级项目
        for i in range(self.outline_tree.topLevelItemCount()):
            item = self.outline_tree.topLevelItem(i)
            if item:
                filter_item(item, text)
    
    def toggle_auto_refresh(self, enabled: bool):
        """切换自动刷新"""
        self.auto_refresh = enabled
        if enabled:
            self.refresh_outline()
    
    def on_doc_type_changed(self, type_text: str):
        """文档类型改变"""
        type_map = {"Markdown": "markdown", "HTML": "html", "纯文本": "plain"}
        self.current_doc_type = type_map.get(type_text, "markdown")
        if self.current_content:
            self.refresh_outline()
    
    def highlight_current_line(self, line_number: int):
        """高亮当前行"""
        self.outline_tree.highlight_current_line(line_number)
    
    def _count_items(self, items: List[OutlineItem]) -> int:
        """计算项目总数"""
        count = len(items)
        for item in items:
            count += self._count_items(item.children)
        return count
    
    def _flatten_items(self, items: List[OutlineItem]) -> List[OutlineItem]:
        """扁平化项目列表"""
        result = []
        for item in items:
            result.append(item)
            result.extend(self._flatten_items(item.children))
        return result
    
    def get_outline_statistics(self) -> Dict[str, Any]:
        """获取大纲统计信息"""
        if not self.outline_tree.outline_items:
            return {"total": 0, "by_type": {}, "by_level": {}}
        
        flattened = self._flatten_items(self.outline_tree.outline_items)
        
        # 按类型统计
        by_type = {}
        for item in flattened:
            by_type[item.item_type] = by_type.get(item.item_type, 0) + 1
        
        # 按级别统计
        by_level = {}
        for item in flattened:
            if item.item_type == "heading":
                by_level[f"H{item.level}"] = by_level.get(f"H{item.level}", 0) + 1
        
        return {
            "total": len(flattened),
            "by_type": by_type,
            "by_level": by_level
        }
