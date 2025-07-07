"""
Word文档增强查看器
集成图片、表格、样式查看功能的综合组件
"""
from typing import List, Dict, Any
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QTextEdit, QSplitter, QPushButton, QGroupBox,
    QFrame, QMessageBox, QProgressBar, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread

from src.gui.widgets.image_viewer import ImageViewer
from src.gui.widgets.table_viewer import TableViewer
from src.gui.widgets.style_viewer import StyleViewer
from src.core.enhanced_word_parser import EnhancedWordParser, ImageInfo, TableInfo, StyleInfo, ParagraphInfo


class ParseWorker(QThread):
    """解析工作线程"""
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, file_path: str, extract_images: bool = True, 
                 extract_tables: bool = True, extract_styles: bool = True):
        super().__init__()
        self.file_path = file_path
        self.extract_images = extract_images
        self.extract_tables = extract_tables
        self.extract_styles = extract_styles
        
    def run(self):
        """执行解析任务"""
        try:
            self.status_updated.emit("开始解析Word文档...")
            self.progress_updated.emit(10)
            
            # 创建解析器
            with EnhancedWordParser(
                extract_images=self.extract_images,
                preserve_styles=self.extract_styles
            ) as parser:
                
                self.progress_updated.emit(30)
                self.status_updated.emit("解析文档结构...")
                
                # 解析文档
                result = parser.parse_document(self.file_path)
                
                if not result.success:
                    self.error.emit(result.error_message)
                    return
                
                self.progress_updated.emit(100)
                self.status_updated.emit("解析完成")
                
                # 发送结果
                self.finished.emit({
                    'success': True,
                    'content': result.content,
                    'markdown_content': result.markdown_content,
                    'images': result.images,
                    'tables': result.tables,
                    'styles': result.styles,
                    'paragraphs': result.paragraphs,
                    'metadata': result.metadata
                })
                
        except Exception as e:
            self.error.emit(f"解析失败: {str(e)}")


class WordEnhancedViewer(QWidget):
    """Word文档增强查看器"""
    
    # 信号
    content_changed = pyqtSignal(str)
    image_extracted = pyqtSignal(str)
    table_exported = pyqtSignal(str)
    style_applied = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = None
        self.parse_worker = None
        self.parsed_data = {}
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 顶部控制栏
        self.create_control_bar()
        layout.addWidget(self.control_frame)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # 主分割器
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.main_splitter)
        
        # 左侧：文档内容
        self.create_content_area()
        self.main_splitter.addWidget(self.content_frame)
        
        # 右侧：增强功能标签页
        self.create_enhanced_tabs()
        self.main_splitter.addWidget(self.enhanced_tabs)
        
        # 设置分割器比例
        self.main_splitter.setSizes([500, 400])
        
    def create_control_bar(self):
        """创建控制栏"""
        self.control_frame = QFrame()
        self.control_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.control_frame.setMaximumHeight(60)
        
        layout = QHBoxLayout(self.control_frame)
        
        # 文件信息
        self.file_info_label = QLabel("未打开文档")
        self.file_info_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.file_info_label)
        
        layout.addStretch()
        
        # 提取选项
        self.extract_images_cb = QCheckBox("提取图片")
        self.extract_images_cb.setChecked(True)
        layout.addWidget(self.extract_images_cb)
        
        self.extract_tables_cb = QCheckBox("提取表格")
        self.extract_tables_cb.setChecked(True)
        layout.addWidget(self.extract_tables_cb)
        
        self.extract_styles_cb = QCheckBox("提取样式")
        self.extract_styles_cb.setChecked(True)
        layout.addWidget(self.extract_styles_cb)
        
        # 重新解析按钮
        self.reparse_btn = QPushButton("重新解析")
        self.reparse_btn.clicked.connect(self.reparse_document)
        self.reparse_btn.setEnabled(False)
        layout.addWidget(self.reparse_btn)
        
        # 导出按钮
        self.export_btn = QPushButton("导出内容")
        self.export_btn.clicked.connect(self.export_content)
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)
        
    def create_content_area(self):
        """创建内容区域"""
        self.content_frame = QGroupBox("文档内容")
        layout = QVBoxLayout(self.content_frame)
        
        # 内容显示
        self.content_edit = QTextEdit()
        self.content_edit.setReadOnly(True)
        layout.addWidget(self.content_edit)
        
        # 内容统计
        self.content_stats_label = QLabel()
        self.content_stats_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.content_stats_label)
        
    def create_enhanced_tabs(self):
        """创建增强功能标签页"""
        self.enhanced_tabs = QTabWidget()
        
        # 图片标签页
        self.image_viewer = ImageViewer()
        self.enhanced_tabs.addTab(self.image_viewer, "图片")
        
        # 表格标签页
        self.table_viewer = TableViewer()
        self.enhanced_tabs.addTab(self.table_viewer, "表格")
        
        # 样式标签页
        self.style_viewer = StyleViewer()
        self.enhanced_tabs.addTab(self.style_viewer, "样式")
        
        # 概览标签页
        self.create_overview_tab()
        self.enhanced_tabs.addTab(self.overview_widget, "概览")
        
    def create_overview_tab(self):
        """创建概览标签页"""
        self.overview_widget = QWidget()
        layout = QVBoxLayout(self.overview_widget)
        
        # 文档统计
        self.stats_group = QGroupBox("文档统计")
        stats_layout = QVBoxLayout(self.stats_group)
        
        self.stats_label = QLabel()
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        
        layout.addWidget(self.stats_group)
        
        # 功能状态
        self.features_group = QGroupBox("功能状态")
        features_layout = QVBoxLayout(self.features_group)
        
        self.features_label = QLabel()
        self.features_label.setWordWrap(True)
        features_layout.addWidget(self.features_label)
        
        layout.addWidget(self.features_group)
        
        # 快速操作
        self.quick_actions_group = QGroupBox("快速操作")
        actions_layout = QVBoxLayout(self.quick_actions_group)
        
        self.view_all_images_btn = QPushButton("查看所有图片")
        self.view_all_images_btn.clicked.connect(lambda: self.enhanced_tabs.setCurrentIndex(0))
        actions_layout.addWidget(self.view_all_images_btn)
        
        self.view_all_tables_btn = QPushButton("查看所有表格")
        self.view_all_tables_btn.clicked.connect(lambda: self.enhanced_tabs.setCurrentIndex(1))
        actions_layout.addWidget(self.view_all_tables_btn)
        
        self.view_all_styles_btn = QPushButton("查看所有样式")
        self.view_all_styles_btn.clicked.connect(lambda: self.enhanced_tabs.setCurrentIndex(2))
        actions_layout.addWidget(self.view_all_styles_btn)
        
        layout.addWidget(self.quick_actions_group)
        
        layout.addStretch()
        
    def setup_connections(self):
        """设置信号连接"""
        # 图片查看器
        self.image_viewer.image_saved.connect(self.on_image_saved)
        
        # 表格查看器
        self.table_viewer.table_exported.connect(self.on_table_exported)
        
        # 样式查看器
        self.style_viewer.style_applied.connect(self.on_style_applied)
        
    def load_document(self, file_path: str):
        """加载Word文档"""
        self.file_path = file_path
        
        # 更新文件信息
        file_name = Path(file_path).name
        self.file_info_label.setText(f"文档: {file_name}")
        
        # 开始解析
        self.start_parsing()
        
    def start_parsing(self):
        """开始解析文档"""
        if not self.file_path:
            return
            
        # 创建工作线程
        self.parse_worker = ParseWorker(
            self.file_path,
            extract_images=self.extract_images_cb.isChecked(),
            extract_tables=self.extract_tables_cb.isChecked(),
            extract_styles=self.extract_styles_cb.isChecked()
        )
        
        # 连接信号
        self.parse_worker.progress_updated.connect(self.progress_bar.setValue)
        self.parse_worker.status_updated.connect(self.status_label.setText)
        self.parse_worker.finished.connect(self.on_parse_finished)
        self.parse_worker.error.connect(self.on_parse_error)
        
        # 显示进度
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 启动解析
        self.parse_worker.start()
        
    def on_parse_finished(self, result: Dict[str, Any]):
        """解析完成"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("解析完成")
        
        # 保存结果
        self.parsed_data = result
        
        # 显示内容
        if result.get('content'):
            self.content_edit.setPlainText(result['content'])
            
        # 加载各类内容
        if result.get('images'):
            self.load_images(result['images'])
            
        if result.get('tables'):
            self.load_tables(result['tables'])
            
        if result.get('styles') and result.get('paragraphs'):
            self.load_styles(result['styles'], result['paragraphs'])
            
        # 更新概览
        self.update_overview()
        
        # 启用按钮
        self.reparse_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        
    def on_parse_error(self, error_msg: str):
        """解析错误"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"解析失败: {error_msg}")
        
        QMessageBox.warning(self, "解析错误", error_msg)
        
    def load_images(self, images: List[ImageInfo]):
        """加载图片"""
        if images:
            # 加载第一张图片
            first_image = images[0]
            if first_image.base64_data:
                self.image_viewer.load_image_from_base64(
                    first_image.base64_data,
                    first_image.filename,
                    first_image.width,
                    first_image.height,
                    first_image.format,
                    first_image.description
                )
            elif first_image.local_path:
                self.image_viewer.load_image_from_file(
                    first_image.local_path,
                    first_image.description
                )
                
    def load_tables(self, tables: List[TableInfo]):
        """加载表格"""
        if tables:
            self.table_viewer.load_tables(tables)
            
    def load_styles(self, styles: Dict[str, StyleInfo], paragraphs: List[ParagraphInfo]):
        """加载样式"""
        if styles:
            self.style_viewer.load_styles(styles, paragraphs)
            
    def update_overview(self):
        """更新概览信息"""
        if not self.parsed_data:
            return
            
        # 统计信息
        stats = []
        
        if self.parsed_data.get('content'):
            content = self.parsed_data['content']
            stats.append(f"字符数: {len(content)}")
            stats.append(f"段落数: {content.count('\\n\\n') + 1}")
            stats.append(f"行数: {content.count('\\n') + 1}")
            
        if self.parsed_data.get('images'):
            stats.append(f"图片数: {len(self.parsed_data['images'])}")
            
        if self.parsed_data.get('tables'):
            stats.append(f"表格数: {len(self.parsed_data['tables'])}")
            
        if self.parsed_data.get('styles'):
            stats.append(f"样式数: {len(self.parsed_data['styles'])}")
            
        self.stats_label.setText('\\n'.join(stats))
        
        # 功能状态
        features = []
        
        if self.parsed_data.get('images'):
            features.append("✓ 图片提取已启用")
        else:
            features.append("✗ 图片提取未启用")
            
        if self.parsed_data.get('tables'):
            features.append("✓ 表格提取已启用")
        else:
            features.append("✗ 表格提取未启用")
            
        if self.parsed_data.get('styles'):
            features.append("✓ 样式提取已启用")
        else:
            features.append("✗ 样式提取未启用")
            
        self.features_label.setText('\\n'.join(features))
        
    def reparse_document(self):
        """重新解析文档"""
        if self.file_path:
            self.start_parsing()
            
    def export_content(self):
        """导出内容"""
        if not self.parsed_data:
            return
            
        # 这里可以实现导出功能
        # 暂时只发送信号
        self.content_changed.emit(self.parsed_data.get('content', ''))
        
    def on_image_saved(self, file_path: str):
        """图片保存完成"""
        self.image_extracted.emit(file_path)
        
    def on_table_exported(self, table_name: str):
        """表格导出完成"""
        self.table_exported.emit(table_name)
        
    def on_style_applied(self, style_name: str):
        """样式应用完成"""
        self.style_applied.emit(style_name)
        
    def clear(self):
        """清空查看器"""
        self.file_path = None
        self.parsed_data = {}
        
        self.file_info_label.setText("未打开文档")
        self.content_edit.clear()
        self.content_stats_label.clear()
        self.status_label.clear()
        self.stats_label.clear()
        self.features_label.clear()
        
        self.image_viewer.clear()
        self.table_viewer.clear_display()
        self.style_viewer.clear_preview()
        
        self.reparse_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        
        if self.parse_worker and self.parse_worker.isRunning():
            self.parse_worker.quit()
            self.parse_worker.wait()
