"""
样式查看器组件
支持Word文档中的样式信息显示和预览
"""
from typing import List, Dict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QFrame, QGroupBox, QListWidget, QListWidgetItem,
    QPushButton, QSplitter, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor, QBrush

from src.core.enhanced_word_parser import StyleInfo, ParagraphInfo


class StyleViewer(QWidget):
    """样式查看器组件"""
    
    # 信号
    style_selected = pyqtSignal(str)  # 样式被选中
    style_applied = pyqtSignal(str)   # 样式被应用
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.styles_data = {}
        self.paragraphs_data = []
        self.current_style = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 主分割器
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.main_splitter)
        
        # 左侧：样式列表
        self.create_style_list()
        self.main_splitter.addWidget(self.style_list_frame)
        
        # 右侧：样式预览和详情
        self.create_preview_area()
        self.main_splitter.addWidget(self.preview_frame)
        
        # 设置分割器比例
        self.main_splitter.setSizes([200, 400])
        
    def create_style_list(self):
        """创建样式列表区域"""
        self.style_list_frame = QGroupBox("样式列表")
        layout = QVBoxLayout(self.style_list_frame)
        
        # 过滤选项
        filter_layout = QHBoxLayout()
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["所有样式", "段落样式", "字符样式", "表格样式"])
        self.filter_combo.currentTextChanged.connect(self.filter_styles)
        filter_layout.addWidget(self.filter_combo)
        
        self.show_used_only_cb = QCheckBox("仅显示使用的样式")
        self.show_used_only_cb.toggled.connect(self.filter_styles)
        filter_layout.addWidget(self.show_used_only_cb)
        
        layout.addLayout(filter_layout)
        
        # 样式列表
        self.style_list = QListWidget()
        self.style_list.itemClicked.connect(self.on_style_selected)
        layout.addWidget(self.style_list)
        
        # 应用按钮
        self.apply_btn = QPushButton("应用样式")
        self.apply_btn.clicked.connect(self.apply_style)
        self.apply_btn.setEnabled(False)
        layout.addWidget(self.apply_btn)
        
    def create_preview_area(self):
        """创建预览区域"""
        self.preview_frame = QFrame()
        layout = QVBoxLayout(self.preview_frame)
        
        # 样式预览
        self.preview_group = QGroupBox("样式预览")
        preview_layout = QVBoxLayout(self.preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setPlainText("这是样式预览文本。This is a style preview text.")
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(self.preview_group)
        
        # 样式详情
        self.details_group = QGroupBox("样式详情")
        details_layout = QVBoxLayout(self.details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(200)
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(self.details_group)
        
        # 使用情况
        self.usage_group = QGroupBox("使用情况")
        usage_layout = QVBoxLayout(self.usage_group)
        
        self.usage_list = QListWidget()
        self.usage_list.setMaximumHeight(150)
        usage_layout.addWidget(self.usage_list)
        
        layout.addWidget(self.usage_group)
        
    def load_styles(self, styles_data: Dict[str, StyleInfo], paragraphs_data: List[ParagraphInfo]):
        """加载样式数据"""
        self.styles_data = styles_data
        self.paragraphs_data = paragraphs_data
        
        # 更新样式列表
        self.update_style_list()
        
        # 清空预览
        self.clear_preview()
        
    def update_style_list(self):
        """更新样式列表"""
        self.style_list.clear()
        
        # 获取过滤条件
        filter_type = self.filter_combo.currentText()
        show_used_only = self.show_used_only_cb.isChecked()
        
        # 统计样式使用情况
        used_styles = self.get_used_styles()
        
        for style_name, style_info in self.styles_data.items():
            # 应用过滤
            if show_used_only and style_name not in used_styles:
                continue
                
            # 类型过滤（这里简化处理，根据样式名称判断）
            if filter_type != "所有样式":
                if filter_type == "段落样式" and not self.is_paragraph_style(style_name):
                    continue
                elif filter_type == "字符样式" and not self.is_character_style(style_name):
                    continue
                elif filter_type == "表格样式" and not self.is_table_style(style_name):
                    continue
            
            # 创建列表项
            item = QListWidgetItem(style_name)
            item.setData(Qt.ItemDataRole.UserRole, style_info)
            
            # 设置预览样式
            self.set_item_preview_style(item, style_info)
            
            # 显示使用次数
            if style_name in used_styles:
                count = used_styles[style_name]
                item.setText(f"{style_name} ({count})")
            
            self.style_list.addItem(item)
            
    def get_used_styles(self) -> Dict[str, int]:
        """获取使用的样式统计"""
        used_styles = {}
        
        for paragraph in self.paragraphs_data:
            # 这里简化处理，假设有样式名称信息
            style_name = getattr(paragraph, 'style_name', '正文')
            used_styles[style_name] = used_styles.get(style_name, 0) + 1
            
        return used_styles
        
    def is_paragraph_style(self, style_name: str) -> bool:
        """判断是否为段落样式"""
        paragraph_keywords = ['标题', '正文', '段落', '列表', '引用']
        return any(keyword in style_name for keyword in paragraph_keywords)
        
    def is_character_style(self, style_name: str) -> bool:
        """判断是否为字符样式"""
        character_keywords = ['强调', '字符', '超链接', '代码']
        return any(keyword in style_name for keyword in character_keywords)
        
    def is_table_style(self, style_name: str) -> bool:
        """判断是否为表格样式"""
        table_keywords = ['表格', '网格', '列表']
        return any(keyword in style_name for keyword in table_keywords)
        
    def set_item_preview_style(self, item: QListWidgetItem, style_info: StyleInfo):
        """设置列表项预览样式"""
        font = QFont()
        
        if style_info.font_name:
            font.setFamily(style_info.font_name)
        if style_info.font_size and style_info.font_size > 0:
            font.setPointSize(min(style_info.font_size, 16))  # 限制最大字号
        if style_info.bold:
            font.setBold(True)
        if style_info.italic:
            font.setItalic(True)
        if style_info.underline:
            font.setUnderline(True)
            
        item.setFont(font)
        
        # 设置文本颜色
        if style_info.color:
            try:
                color = QColor(style_info.color)
                item.setForeground(QBrush(color))
            except Exception:
                pass
                
        # 设置背景色
        if style_info.background_color:
            try:
                color = QColor(style_info.background_color)
                item.setBackground(QBrush(color))
            except Exception:
                pass
                
    def on_style_selected(self, item: QListWidgetItem):
        """样式被选中"""
        style_info = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(style_info, StyleInfo):
            self.current_style = item.text().split(' (')[0]  # 去掉使用次数
            self.show_style_preview(style_info)
            self.show_style_details(style_info)
            self.show_style_usage(self.current_style)
            self.apply_btn.setEnabled(True)
            self.style_selected.emit(self.current_style)
            
    def show_style_preview(self, style_info: StyleInfo):
        """显示样式预览"""
        # 应用样式到预览文本
        cursor = self.preview_text.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        
        # 创建字符格式
        char_format = QTextCharFormat()
        
        if style_info.font_name:
            char_format.setFontFamily(style_info.font_name)
        if style_info.font_size and style_info.font_size > 0:
            char_format.setFontPointSize(style_info.font_size)
        if style_info.bold:
            char_format.setFontWeight(QFont.Weight.Bold)
        if style_info.italic:
            char_format.setFontItalic(True)
        if style_info.underline:
            char_format.setFontUnderline(True)
        if style_info.color:
            try:
                color = QColor(style_info.color)
                char_format.setForeground(color)
            except Exception:
                pass
        if style_info.background_color:
            try:
                color = QColor(style_info.background_color)
                char_format.setBackground(color)
            except Exception:
                pass
                
        cursor.mergeCharFormat(char_format)
        
    def show_style_details(self, style_info: StyleInfo):
        """显示样式详情"""
        details = []
        
        if style_info.font_name:
            details.append(f"字体: {style_info.font_name}")
        if style_info.font_size:
            details.append(f"字号: {style_info.font_size}pt")
        if style_info.bold:
            details.append("加粗: 是")
        if style_info.italic:
            details.append("斜体: 是")
        if style_info.underline:
            details.append("下划线: 是")
        if style_info.color:
            details.append(f"文本颜色: {style_info.color}")
        if style_info.background_color:
            details.append(f"背景色: {style_info.background_color}")
        if style_info.alignment:
            details.append(f"对齐方式: {style_info.alignment}")
        if style_info.indent > 0:
            details.append(f"缩进: {style_info.indent}")
            
        self.details_text.setPlainText('\n'.join(details))
        
    def show_style_usage(self, style_name: str):
        """显示样式使用情况"""
        self.usage_list.clear()
        
        usage_count = 0
        for i, paragraph in enumerate(self.paragraphs_data):
            # 这里简化处理，假设有样式名称信息
            paragraph_style = getattr(paragraph, 'style_name', '正文')
            if paragraph_style == style_name:
                usage_count += 1
                preview_text = paragraph.text[:50] + "..." if len(paragraph.text) > 50 else paragraph.text
                item = QListWidgetItem(f"段落 {i+1}: {preview_text}")
                self.usage_list.addItem(item)
                
        if usage_count == 0:
            item = QListWidgetItem("此样式未被使用")
            self.usage_list.addItem(item)
            
    def apply_style(self):
        """应用样式"""
        if self.current_style:
            self.style_applied.emit(self.current_style)
            
    def filter_styles(self):
        """过滤样式"""
        self.update_style_list()
        
    def clear_preview(self):
        """清空预览"""
        self.preview_text.clear()
        self.preview_text.setPlainText("这是样式预览文本。This is a style preview text.")
        self.details_text.clear()
        self.usage_list.clear()
        self.current_style = None
        self.apply_btn.setEnabled(False)


class StylePreviewWidget(QWidget):
    """样式预览组件（用于文档编辑器中的内联显示）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # 样式预览标签
        self.style_label = QLabel()
        self.style_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.style_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ddd;
                background-color: #f9f9f9;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        self.style_label.setMaximumHeight(60)
        layout.addWidget(self.style_label)
        
        # 样式名称
        self.name_label = QLabel()
        self.name_label.setStyleSheet("color: #666; font-size: 10px;")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)
        
    def load_style(self, style_name: str, style_info: StyleInfo):
        """加载样式预览"""
        try:
            # 设置预览文本
            preview_text = f"样式: {style_name}"
            self.style_label.setText(preview_text)
            
            # 应用样式
            font = QFont()
            if style_info.font_name:
                font.setFamily(style_info.font_name)
            if style_info.font_size and style_info.font_size > 0:
                font.setPointSize(min(style_info.font_size, 12))  # 限制字号
            if style_info.bold:
                font.setBold(True)
            if style_info.italic:
                font.setItalic(True)
            if style_info.underline:
                font.setUnderline(True)
                
            self.style_label.setFont(font)
            
            # 设置颜色
            style_sheet = self.style_label.styleSheet()
            if style_info.color:
                try:
                    color = QColor(style_info.color)
                    style_sheet += f"color: {color.name()};"
                except Exception:
                    pass
                    
            if style_info.background_color:
                try:
                    color = QColor(style_info.background_color)
                    style_sheet += f"background-color: {color.name()};"
                except Exception:
                    pass
                    
            self.style_label.setStyleSheet(style_sheet)
            
            # 设置名称
            self.name_label.setText(style_name)
            
        except Exception as e:
            print(f"加载样式预览失败: {e}")
            self.style_label.setText("样式预览失败")
            self.name_label.setText(style_name)
            
    def clear(self):
        """清空显示"""
        self.style_label.setText("无样式")
        self.name_label.clear()
        
        # 重置样式
        self.style_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ddd;
                background-color: #f9f9f9;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        self.style_label.setFont(QFont())
