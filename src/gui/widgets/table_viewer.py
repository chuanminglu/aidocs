"""
表格查看器组件
支持Word文档中的复杂表格显示，包括合并单元格、样式等
"""
from typing import List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QFrame, QScrollArea, QSplitter,
    QGroupBox, QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QBrush

from src.core.enhanced_word_parser import TableInfo, TableCellInfo


class TableViewer(QWidget):
    """表格查看器组件"""
    
    # 信号
    cell_clicked = pyqtSignal(int, int)  # 单元格被点击 (row, col)
    table_exported = pyqtSignal(str)     # 表格被导出
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table_info = None
        self.current_table_index = 0
        self.tables_data = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 表格控制栏
        self.create_control_bar()
        layout.addWidget(self.control_frame)
        
        # 主分割器
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(self.main_splitter)
        
        # 表格显示区域
        self.create_table_area()
        self.main_splitter.addWidget(self.table_scroll)
        
        # 表格信息区域
        self.create_info_area()
        self.main_splitter.addWidget(self.info_frame)
        
        # 设置分割器比例
        self.main_splitter.setSizes([400, 100])
        
    def create_control_bar(self):
        """创建控制栏"""
        self.control_frame = QFrame()
        self.control_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.control_frame.setMaximumHeight(50)
        
        layout = QHBoxLayout(self.control_frame)
        
        # 表格选择
        self.table_label = QLabel("表格:")
        layout.addWidget(self.table_label)
        
        self.table_combo = QComboBox()
        self.table_combo.currentIndexChanged.connect(self.on_table_changed)
        layout.addWidget(self.table_combo)
        
        layout.addStretch()
        
        # 显示选项
        self.show_headers_cb = QCheckBox("显示表头")
        self.show_headers_cb.setChecked(True)
        self.show_headers_cb.toggled.connect(self.update_table_display)
        layout.addWidget(self.show_headers_cb)
        
        self.show_grid_cb = QCheckBox("显示网格")
        self.show_grid_cb.setChecked(True)
        self.show_grid_cb.toggled.connect(self.update_table_display)
        layout.addWidget(self.show_grid_cb)
        
        layout.addStretch()
        
        # 导出按钮
        self.export_btn = QPushButton("导出表格")
        self.export_btn.clicked.connect(self.export_table)
        layout.addWidget(self.export_btn)
        
        # 初始状态禁用控件
        self.set_controls_enabled(False)
        
    def create_table_area(self):
        """创建表格显示区域"""
        self.table_scroll = QScrollArea()
        self.table_scroll.setWidgetResizable(True)
        
        self.table_widget = QTableWidget()
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.cellClicked.connect(self.on_cell_clicked)
        
        # 设置表头
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        self.table_scroll.setWidget(self.table_widget)
        
    def create_info_area(self):
        """创建信息区域"""
        self.info_frame = QGroupBox("表格信息")
        layout = QVBoxLayout(self.info_frame)
        
        # 基本信息
        self.basic_info_label = QLabel()
        self.basic_info_label.setWordWrap(True)
        layout.addWidget(self.basic_info_label)
        
        # 单元格详情
        self.cell_info_label = QLabel()
        self.cell_info_label.setWordWrap(True)
        self.cell_info_label.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        layout.addWidget(self.cell_info_label)
        
    def load_tables(self, tables_data: List[TableInfo]):
        """加载表格数据"""
        self.tables_data = tables_data
        self.current_table_index = 0
        
        # 更新表格选择下拉框
        self.table_combo.clear()
        for i, table_info in enumerate(tables_data):
            caption = table_info.caption or f"表格 {i+1}"
            rows = len(table_info.rows)
            cols = len(table_info.rows[0]) if table_info.rows else 0
            self.table_combo.addItem(f"{caption} ({rows}×{cols})")
            
        if tables_data:
            self.set_controls_enabled(True)
            self.display_table(0)
        else:
            self.set_controls_enabled(False)
            self.clear_display()
            
    def display_table(self, index: int):
        """显示指定索引的表格"""
        if index < 0 or index >= len(self.tables_data):
            return
            
        self.current_table_index = index
        self.table_info = self.tables_data[index]
        
        # 设置表格尺寸
        rows = len(self.table_info.rows)
        cols = len(self.table_info.rows[0]) if self.table_info.rows else 0
        
        self.table_widget.setRowCount(rows)
        self.table_widget.setColumnCount(cols)
        
        # 填充表格数据
        for row_idx, row_data in enumerate(self.table_info.rows):
            for col_idx, cell_info in enumerate(row_data):
                item = QTableWidgetItem(cell_info.text)
                
                # 设置单元格样式
                self.apply_cell_style(item, cell_info)
                
                # 设置单元格数据
                item.setData(Qt.ItemDataRole.UserRole, cell_info)
                
                self.table_widget.setItem(row_idx, col_idx, item)
                
                # 处理合并单元格
                if cell_info.row_span > 1 or cell_info.col_span > 1:
                    self.table_widget.setSpan(row_idx, col_idx, 
                                            cell_info.row_span, cell_info.col_span)
        
        # 设置表头
        if self.table_info.has_header and self.show_headers_cb.isChecked():
            self.setup_table_headers()
        
        # 更新显示选项
        self.update_table_display()
        
        # 更新信息
        self.update_table_info()
        
    def apply_cell_style(self, item: QTableWidgetItem, cell_info: TableCellInfo):
        """应用单元格样式"""
        # 设置字体
        font = item.font()
        font.setBold(cell_info.bold)
        font.setItalic(cell_info.italic)
        item.setFont(font)
        
        # 设置文本颜色
        if cell_info.text_color:
            try:
                color = QColor(cell_info.text_color)
                item.setForeground(QBrush(color))
            except Exception:
                pass
        
        # 设置背景色
        if cell_info.background_color:
            try:
                color = QColor(cell_info.background_color)
                item.setBackground(QBrush(color))
            except Exception:
                pass
        
        # 设置对齐方式
        alignment = Qt.AlignmentFlag.AlignLeft
        if cell_info.alignment == "center":
            alignment = Qt.AlignmentFlag.AlignCenter
        elif cell_info.alignment == "right":
            alignment = Qt.AlignmentFlag.AlignRight
        elif cell_info.alignment == "justify":
            alignment = Qt.AlignmentFlag.AlignJustify
            
        item.setTextAlignment(alignment | Qt.AlignmentFlag.AlignVCenter)
        
        # 标记表头
        if cell_info.is_header:
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            
    def setup_table_headers(self):
        """设置表格表头"""
        if not self.table_info.rows:
            return
            
        # 使用第一行作为表头
        header_row = self.table_info.rows[0]
        horizontal_headers = []
        
        for col_idx, cell_info in enumerate(header_row):
            if col_idx < len(header_row):
                horizontal_headers.append(cell_info.text)
                
        if horizontal_headers:
            self.table_widget.setHorizontalHeaderLabels(horizontal_headers)
            
    def update_table_display(self):
        """更新表格显示"""
        if not self.table_info:
            return
            
        # 显示/隐藏表头
        if self.show_headers_cb.isChecked():
            self.table_widget.horizontalHeader().setVisible(True)
            self.table_widget.verticalHeader().setVisible(True)
        else:
            self.table_widget.horizontalHeader().setVisible(False)
            self.table_widget.verticalHeader().setVisible(False)
            
        # 显示/隐藏网格
        self.table_widget.setShowGrid(self.show_grid_cb.isChecked())
        
    def update_table_info(self):
        """更新表格信息"""
        if not self.table_info:
            self.basic_info_label.setText("无表格数据")
            return
            
        # 基本信息
        rows = len(self.table_info.rows)
        cols = len(self.table_info.rows[0]) if self.table_info.rows else 0
        
        info_parts = [
            f"尺寸: {rows}×{cols}",
            f"对齐: {self.table_info.alignment}",
            f"表头: {'是' if self.table_info.has_header else '否'}"
        ]
        
        if self.table_info.caption:
            info_parts.insert(0, f"标题: {self.table_info.caption}")
            
        self.basic_info_label.setText(" | ".join(info_parts))
        
    def on_table_changed(self, index: int):
        """表格选择改变"""
        if index >= 0:
            self.display_table(index)
            
    def on_cell_clicked(self, row: int, col: int):
        """单元格被点击"""
        item = self.table_widget.item(row, col)
        if item:
            cell_info = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(cell_info, TableCellInfo):
                self.show_cell_info(cell_info, row, col)
                
        self.cell_clicked.emit(row, col)
        
    def show_cell_info(self, cell_info: TableCellInfo, row: int, col: int):
        """显示单元格信息"""
        info_parts = [
            f"位置: ({row+1}, {col+1})",
            f"内容: {cell_info.text[:50]}{'...' if len(cell_info.text) > 50 else ''}",
            f"跨行: {cell_info.row_span}",
            f"跨列: {cell_info.col_span}",
            f"对齐: {cell_info.alignment}",
            f"表头: {'是' if cell_info.is_header else '否'}"
        ]
        
        if cell_info.bold or cell_info.italic:
            styles = []
            if cell_info.bold:
                styles.append("加粗")
            if cell_info.italic:
                styles.append("斜体")
            info_parts.append(f"样式: {', '.join(styles)}")
            
        if cell_info.text_color:
            info_parts.append(f"文本颜色: {cell_info.text_color}")
            
        if cell_info.background_color:
            info_parts.append(f"背景色: {cell_info.background_color}")
            
        self.cell_info_label.setText("\n".join(info_parts))
        
    def export_table(self):
        """导出表格"""
        if not self.table_info:
            return
            
        # 这里可以实现导出功能，例如导出为CSV、Excel等
        # 暂时只发送信号
        self.table_exported.emit(f"table_{self.current_table_index}")
        
    def set_controls_enabled(self, enabled: bool):
        """设置控制按钮状态"""
        self.table_combo.setEnabled(enabled)
        self.show_headers_cb.setEnabled(enabled)
        self.show_grid_cb.setEnabled(enabled)
        self.export_btn.setEnabled(enabled)
        
    def clear_display(self):
        """清空显示"""
        self.table_widget.clear()
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(0)
        self.basic_info_label.setText("无表格数据")
        self.cell_info_label.clear()
        self.table_info = None


class TablePreviewWidget(QWidget):
    """表格预览组件（用于文档编辑器中的内联显示）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # 表格预览
        self.preview_table = QTableWidget()
        self.preview_table.setMaximumHeight(150)
        self.preview_table.setMaximumWidth(300)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setShowGrid(True)
        self.preview_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        
        # 隐藏表头
        self.preview_table.horizontalHeader().setVisible(False)
        self.preview_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.preview_table)
        
        # 信息标签
        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: #666; font-size: 10px;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        
    def load_table(self, table_info: TableInfo):
        """加载表格预览"""
        try:
            if not table_info.rows:
                self.preview_table.setRowCount(1)
                self.preview_table.setColumnCount(1)
                item = QTableWidgetItem("空表格")
                self.preview_table.setItem(0, 0, item)
                self.info_label.setText("空表格")
                return
                
            # 限制预览大小
            max_rows = min(len(table_info.rows), 5)
            max_cols = min(len(table_info.rows[0]) if table_info.rows else 0, 5)
            
            self.preview_table.setRowCount(max_rows)
            self.preview_table.setColumnCount(max_cols)
            
            # 填充预览数据
            for row_idx in range(max_rows):
                for col_idx in range(max_cols):
                    if row_idx < len(table_info.rows) and col_idx < len(table_info.rows[row_idx]):
                        cell_info = table_info.rows[row_idx][col_idx]
                        text = cell_info.text
                        
                        # 截断长文本
                        if len(text) > 20:
                            text = text[:20] + "..."
                            
                        item = QTableWidgetItem(text)
                        
                        # 简化的样式应用
                        if cell_info.bold:
                            font = item.font()
                            font.setBold(True)
                            item.setFont(font)
                            
                        if cell_info.is_header:
                            item.setBackground(QBrush(QColor("#e0e0e0")))
                            
                        self.preview_table.setItem(row_idx, col_idx, item)
                        
            # 自动调整列宽
            self.preview_table.resizeColumnsToContents()
            self.preview_table.resizeRowsToContents()
            
            # 更新信息
            total_rows = len(table_info.rows)
            total_cols = len(table_info.rows[0]) if table_info.rows else 0
            caption = table_info.caption or "表格"
            
            info_text = f"{caption} ({total_rows}×{total_cols})"
            if max_rows < total_rows or max_cols < total_cols:
                info_text += " (预览)"
                
            self.info_label.setText(info_text)
            
        except Exception as e:
            print(f"加载表格预览失败: {e}")
            self.preview_table.setRowCount(1)
            self.preview_table.setColumnCount(1)
            item = QTableWidgetItem("加载失败")
            self.preview_table.setItem(0, 0, item)
            self.info_label.setText("加载失败")
            
    def clear(self):
        """清空显示"""
        self.preview_table.clear()
        self.preview_table.setRowCount(0)
        self.preview_table.setColumnCount(0)
        self.info_label.clear()
