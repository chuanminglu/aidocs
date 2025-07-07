"""
文档编辑器 - 集成多文档标签页、AI功能、大纲导航等功能的完整文档编辑器
"""
import sys
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTextEdit,
    QSplitter, QPushButton, QLabel, QFileDialog, QMessageBox, QStatusBar,
    QToolBar, QProgressBar, QTextBrowser, QFrame, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QAction, QFont, QTextCursor, QKeySequence

from src.gui.find_replace_dialog import FindReplaceDialog
from src.gui.document_outline_navigator import DocumentOutlineNavigator
from src.core.ai_service import AIService
from src.core.word_parser import WordDocumentParser, check_word_support
from config.settings import Settings

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))



# 常量定义
AI_SERVICE_UNAVAILABLE_MSG = "AI服务不可用，请检查配置"


class DocumentTab:
    """文档标签页数据类"""
    
    def __init__(self, file_path: str = "", content: str = "", is_modified: bool = False):
        self.file_path = file_path
        self.content = content
        self.is_modified = is_modified
        self.created_at = datetime.now()
        self.last_saved = None
        self.encoding = "utf-8"
        self.language = "markdown"
        self.cursor_position = 0
        self.scroll_position = 0
        # Word文档相关属性
        self.is_word_document = False
        self.word_mode = "readonly"  # readonly, markdown_edit
        self.original_word_content = ""  # 原始Word内容，用于保存
        
    def get_display_name(self) -> str:
        """获取显示名称"""
        if self.file_path:
            name = Path(self.file_path).name
        else:
            name = "未命名文档"
        
        # 添加Word文档标识
        if self.is_word_document:
            name += " [Word]"
        
        if self.is_modified:
            name += " *"
        
        return name
    
    def get_file_type(self) -> str:
        """获取文件类型"""
        if self.file_path:
            suffix = Path(self.file_path).suffix.lower()
            return suffix[1:] if suffix else "txt"
        return "txt"
    
    def is_word_file(self) -> bool:
        """检查是否为Word文档"""
        if self.file_path:
            suffix = Path(self.file_path).suffix.lower()
            return suffix in ['.docx', '.doc']
        return False


class AIWorker(QThread):
    """AI处理工作线程"""
    
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, ai_service: AIService, task: str, content: str, **kwargs):
        super().__init__()
        self.ai_service = ai_service
        self.task = task
        self.content = content
        self.kwargs = kwargs
    
    def run(self):
        """执行AI任务"""
        try:
            response = None
            if self.task == "generate_outline":
                response = self.ai_service.generate_outline(
                    self.content, 
                    self.kwargs.get('doc_type', 'markdown')
                )
            elif self.task == "suggest_content":
                response = self.ai_service.suggest_content(
                    self.content,
                    self.kwargs.get('context', '')
                )
            elif self.task == "improve_writing":
                response = self.ai_service.improve_writing(
                    self.content
                )
            else:
                raise ValueError(f"Unknown task: {self.task}")
                
            self.finished.emit({
                'task': self.task,
                'response': response,
                'success': True
            })
            
        except Exception as e:
            self.error.emit(f"AI处理失败: {str(e)}")


class DocumentEditor(QWidget):
    """文档编辑器主类"""
    
    # 信号定义
    documentChanged = pyqtSignal(str)  # 文档内容改变
    documentSaved = pyqtSignal(str)    # 文档保存
    documentOpened = pyqtSignal(str)   # 文档打开
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.ai_service = AIService(api_key=self.settings.deepseek_api_key)
        
        # Word文档解析器
        self.word_parser = WordDocumentParser()
        self.word_support_available, self.word_support_message = check_word_support()
        
        self.tabs: Dict[int, DocumentTab] = {}
        self.current_tab_id = 0
        self.find_dialog = None
        self.ai_worker = None
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(30000)  # 30秒自动保存
        
        # 用于管理标签页ID的映射
        self.tab_id_mapping = {}  # index -> tab_id
        
        self.setup_ui()
        self.setup_connections()
        self.load_settings()
        
        # 在UI完成后创建默认文档
        self.new_document()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建工具栏
        self.create_toolbar()
        layout.addWidget(self.toolbar)
        
        # 创建主分割器
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.main_splitter)
        
        # 创建左侧面板（大纲导航）
        self.create_left_panel()
        
        # 创建中央编辑区域
        self.create_central_area()
        
        # 创建右侧面板（AI助手）
        self.create_right_panel()
        
        # 设置分割器比例 - 增大大纲区域
        self.main_splitter.setSizes([250, 700, 200])
        
        # 创建状态栏（必须在中央区域之后）
        self.create_status_bar()
        layout.addWidget(self.status_bar)
        
    def create_toolbar(self):
        """创建工具栏"""
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        
        # 文件操作
        self.new_action = QAction("新建", self)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_action.triggered.connect(self.new_document)
        self.toolbar.addAction(self.new_action)
        
        self.open_action = QAction("打开", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.triggered.connect(self.open_document)
        self.toolbar.addAction(self.open_action)
        
        self.save_action = QAction("保存", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.triggered.connect(self.save_document)
        self.toolbar.addAction(self.save_action)
        
        self.save_as_action = QAction("另存为", self)
        self.save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.save_as_action.triggered.connect(self.save_as_document)
        self.toolbar.addAction(self.save_as_action)
        
        self.toolbar.addSeparator()
        
        # 编辑操作
        self.find_action = QAction("查找", self)
        self.find_action.setShortcut(QKeySequence.StandardKey.Find)
        self.find_action.triggered.connect(self.show_find_dialog)
        self.toolbar.addAction(self.find_action)
        
        self.toolbar.addSeparator()
        
        # Word文档功能（仅在Word支持可用时显示）
        if self.word_support_available:
            self.word_mode_action = QAction("切换编辑模式", self)
            self.word_mode_action.triggered.connect(self.toggle_word_mode)
            self.word_mode_action.setEnabled(False)  # 默认禁用，打开Word文档时启用
            self.toolbar.addAction(self.word_mode_action)
            
            self.save_as_word_action = QAction("保存为Word", self)
            self.save_as_word_action.triggered.connect(self.save_as_word)
            self.toolbar.addAction(self.save_as_word_action)
            
            self.toolbar.addSeparator()
        
        # AI功能
        self.ai_outline_action = QAction("生成大纲", self)
        self.ai_outline_action.triggered.connect(self.generate_ai_outline)
        self.toolbar.addAction(self.ai_outline_action)
        
        self.ai_suggest_action = QAction("内容建议", self)
        self.ai_suggest_action.triggered.connect(self.get_ai_suggestions)
        self.toolbar.addAction(self.ai_suggest_action)
        
    def create_left_panel(self):
        """创建左侧面板"""
        self.left_panel = QFrame()
        self.left_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        self.left_panel.setMinimumWidth(200)
        self.left_panel.setMaximumWidth(450)
        
        layout = QVBoxLayout(self.left_panel)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # 大纲导航标题
        title_label = QLabel("文档大纲")
        title_label.setFont(QFont("", 11, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 大纲导航器 - 扩大显示区域
        self.outline_navigator = DocumentOutlineNavigator()
        if hasattr(self.outline_navigator, 'jump_to_line'):
            self.outline_navigator.jump_to_line.connect(self.on_outline_jump_to_line)
        layout.addWidget(self.outline_navigator)
        
        # 移除最近文件区域，让大纲占用全部空间
        
        self.main_splitter.addWidget(self.left_panel)
        
    def create_central_area(self):
        """创建中央编辑区域"""
        self.central_widget = QWidget()
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标签页控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        layout.addWidget(self.tab_widget)
        
        self.main_splitter.addWidget(self.central_widget)
        
    def create_right_panel(self):
        """创建右侧面板（AI助手）"""
        self.right_panel = QFrame()
        self.right_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        self.right_panel.setMinimumWidth(180)
        self.right_panel.setMaximumWidth(350)
        
        layout = QVBoxLayout(self.right_panel)
        
        # AI助手标题
        ai_title = QLabel("AI助手")
        ai_title.setFont(QFont("", 10, QFont.Weight.Bold))
        layout.addWidget(ai_title)
        
        # AI功能按钮组
        ai_group = QGroupBox("AI功能")
        ai_group_layout = QVBoxLayout(ai_group)
        
        self.ai_outline_btn = QPushButton("生成大纲")
        self.ai_outline_btn.clicked.connect(self.generate_ai_outline)
        ai_group_layout.addWidget(self.ai_outline_btn)
        
        self.ai_suggest_btn = QPushButton("内容建议")
        self.ai_suggest_btn.clicked.connect(self.get_ai_suggestions)
        ai_group_layout.addWidget(self.ai_suggest_btn)
        
        self.ai_improve_btn = QPushButton("改进文本")
        self.ai_improve_btn.clicked.connect(self.improve_writing)
        ai_group_layout.addWidget(self.ai_improve_btn)
        
        layout.addWidget(ai_group)
        
        # AI结果显示
        self.ai_result_label = QLabel("AI结果")
        self.ai_result_label.setFont(QFont("", 10, QFont.Weight.Bold))
        layout.addWidget(self.ai_result_label)
        
        self.ai_result_text = QTextBrowser()
        self.ai_result_text.setMaximumHeight(200)
        layout.addWidget(self.ai_result_text)
        
        # 进度条
        self.ai_progress = QProgressBar()
        self.ai_progress.setVisible(False)
        layout.addWidget(self.ai_progress)
        
        # 弹性空间
        layout.addStretch()
        
        self.main_splitter.addWidget(self.right_panel)
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.status_bar.setFixedHeight(25)  # 固定状态栏高度
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 文档信息
        self.doc_info_label = QLabel("")
        self.status_bar.addPermanentWidget(self.doc_info_label)
        
        # 光标位置
        self.cursor_info_label = QLabel("行: 1, 列: 1")
        self.status_bar.addPermanentWidget(self.cursor_info_label)
        
    def setup_connections(self):
        """设置信号连接"""
        # 文档变化信号
        self.documentChanged.connect(self.update_outline)
        self.documentChanged.connect(self.update_status)
        
        # 窗口调整大小时的延迟调整布局
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.adjust_layout)
        
    def resizeEvent(self, event):
        """窗口大小变化事件"""
        super().resizeEvent(event)
        # 延迟调整布局，避免频繁调整
        self.resize_timer.start(100)  # 100ms延迟
        
    def adjust_layout(self):
        """调整布局以适应窗口大小"""
        # 获取窗口大小
        window_width = self.width()
        window_height = self.height()
        
        # 计算各区域的合适大小
        outline_width = max(200, min(350, window_width * 0.2))  # 大纲区域占20%，最小200，最大350
        ai_width = max(180, min(300, window_width * 0.18))      # AI区域占18%，最小180，最大300
        editor_width = window_width - outline_width - ai_width - 20  # 剩余给编辑区域
        
        # 设置分割器大小
        self.main_splitter.setSizes([int(outline_width), int(editor_width), int(ai_width)])
        
        # 调整AI结果显示区域的高度
        available_height = window_height - 150  # 减去工具栏、状态栏等固定高度
        ai_result_height = min(250, max(150, available_height * 0.3))  # AI结果区域占30%
        self.ai_result_text.setMaximumHeight(int(ai_result_height))
        
    def new_document(self):
        """新建文档"""
        self.current_tab_id += 1
        tab_id = self.current_tab_id
        
        # 创建文档标签页数据
        doc_tab = DocumentTab()
        self.tabs[tab_id] = doc_tab
        
        # 创建文本编辑器
        text_edit = QTextEdit()
        text_edit.setFont(QFont("Consolas", 12))
        text_edit.textChanged.connect(lambda: self.on_text_changed(tab_id))
        text_edit.cursorPositionChanged.connect(self.update_cursor_position)
        
        # 添加到标签页
        index = self.tab_widget.addTab(text_edit, doc_tab.get_display_name())
        self.tab_widget.setCurrentIndex(index)
        
        # 建立标签页索引和ID的映射关系
        self.tab_id_mapping[index] = tab_id
        
        self.update_status()
        
    def open_document(self):
        """打开文档"""
        # 构建文件过滤器，包含Word文档支持
        file_filters = []
        
        if self.word_support_available:
            file_filters.append("所有支持的文件 (*.md *.txt *.html *.py *.js *.css *.json *.docx *.doc)")
            file_filters.append("Word文档 (*.docx *.doc)")
        else:
            file_filters.append("所有支持的文件 (*.md *.txt *.html *.py *.js *.css *.json)")
        
        file_filters.extend([
            "Markdown文件 (*.md)",
            "文本文件 (*.txt)",
            "所有文件 (*.*)"
        ])
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "打开文档",
            "",
            ";;".join(file_filters)
        )
        
        if file_path:
            self.open_file(file_path)
            
    def open_file(self, file_path: str):
        """打开指定文件"""
        try:
            # 检查文件是否已经打开
            for tab_id, doc_tab in self.tabs.items():
                if doc_tab.file_path == file_path:
                    # 切换到已打开的标签页
                    for i in range(self.tab_widget.count()):
                        if self.tab_id_mapping.get(i) == tab_id:
                            self.tab_widget.setCurrentIndex(i)
                            return
            
            # 检查是否为Word文档
            is_word_file = self.word_parser.is_word_file(file_path)
            content = ""
            
            if is_word_file and self.word_support_available:
                # 处理Word文档
                result = self.word_parser.extract_structured_content(file_path)
                if result.success:
                    content = result.content
                    QMessageBox.information(
                        self, 
                        "Word文档", 
                        f"已将Word文档转换为Markdown格式进行编辑。\n原始Word文档: {Path(file_path).name}\n\n提示: 可以使用'保存为Word'功能保存修改。"
                    )
                else:
                    QMessageBox.warning(self, "错误", f"无法读取Word文档: {result.error_message}")
                    return
            else:
                # 处理普通文本文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                            
            # 创建新标签页
            self.current_tab_id += 1
            tab_id = self.current_tab_id
            
            doc_tab = DocumentTab(file_path, content, False)
            
            # 设置Word文档属性
            if is_word_file and self.word_support_available:
                doc_tab.is_word_document = True
                doc_tab.word_mode = "markdown_edit"
                doc_tab.original_word_content = file_path  # 保存原始文件路径
            
            self.tabs[tab_id] = doc_tab
            
            # 创建文本编辑器
            text_edit = QTextEdit()
            text_edit.setFont(QFont("Consolas", 12))
            text_edit.setPlainText(content)
            text_edit.textChanged.connect(lambda: self.on_text_changed(tab_id))
            text_edit.cursorPositionChanged.connect(self.update_cursor_position)
            
            # 添加到标签页
            index = self.tab_widget.addTab(text_edit, doc_tab.get_display_name())
            self.tab_widget.setCurrentIndex(index)
            
            # 建立标签页索引和ID的映射关系
            self.tab_id_mapping[index] = tab_id
            
            self.documentOpened.emit(file_path)
            self.update_status()
            # 立即更新大纲导航
            self.update_outline()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件: {str(e)}")
            
    def save_document(self):
        """保存当前文档"""
        current_tab_id = self.get_current_tab_id()
        if current_tab_id is None:
            return
            
        doc_tab = self.tabs[current_tab_id]
        
        if not doc_tab.file_path:
            self.save_as_document()
            return
            
        try:
            current_text_edit = self.tab_widget.currentWidget()
            if current_text_edit:
                content = current_text_edit.toPlainText()
                
                with open(doc_tab.file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                doc_tab.content = content
                doc_tab.is_modified = False
                doc_tab.last_saved = datetime.now()
                
                # 更新标签页标题
                current_index = self.tab_widget.currentIndex()
                self.tab_widget.setTabText(current_index, doc_tab.get_display_name())
                
                self.documentSaved.emit(doc_tab.file_path)
                self.status_label.setText("文档已保存")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法保存文件: {str(e)}")
            
    def save_as_document(self):
        """另存为文档"""
        current_tab_id = self.get_current_tab_id()
        if current_tab_id is None:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "另存为",
            "",
            "Markdown文件 (*.md);;文本文件 (*.txt);;HTML文件 (*.html);;所有文件 (*.*)"
        )
        
        if file_path:
            doc_tab = self.tabs[current_tab_id]
            doc_tab.file_path = file_path
            self.save_document()
            
    def close_tab(self, index: int):
        """关闭标签页"""
        tab_id = self.tab_id_mapping.get(index)
        if tab_id is None:
            return
            
        doc_tab = self.tabs.get(tab_id)
        if doc_tab and doc_tab.is_modified:
            reply = QMessageBox.question(
                self,
                "确认",
                f"文档 '{doc_tab.get_display_name()}' 已修改，是否保存？",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_document()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
                
        # 删除标签页和数据
        self.tab_widget.removeTab(index)
        if tab_id in self.tabs:
            del self.tabs[tab_id]
        
        # 更新映射关系
        if index in self.tab_id_mapping:
            del self.tab_id_mapping[index]
        
        # 重新建立后续标签页的映射关系
        new_mapping = {}
        for old_index, mapped_tab_id in self.tab_id_mapping.items():
            if old_index > index:
                new_mapping[old_index - 1] = mapped_tab_id
            else:
                new_mapping[old_index] = mapped_tab_id
        self.tab_id_mapping = new_mapping
            
        # 如果没有标签页了，创建新文档
        if self.tab_widget.count() == 0:
            self.new_document()
            
    def on_tab_changed(self, index: int):
        """标签页切换事件"""
        if index >= 0:
            self.update_outline()
            self.update_status()
            self.update_word_mode_ui()  # 更新Word模式UI
            
    def on_text_changed(self, tab_id: int):
        """文本内容改变事件"""
        if tab_id in self.tabs:
            doc_tab = self.tabs[tab_id]
            doc_tab.is_modified = True
            
            # 更新标签页标题
            for index, mapped_tab_id in self.tab_id_mapping.items():
                if mapped_tab_id == tab_id:
                    self.tab_widget.setTabText(index, doc_tab.get_display_name())
                    break
                    
            current_text_edit = self.tab_widget.currentWidget()
            if current_text_edit:
                content = current_text_edit.toPlainText()
                doc_tab.content = content
                self.documentChanged.emit(content)
                
    def get_current_tab_id(self) -> Optional[int]:
        """获取当前标签页ID"""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            return self.tab_id_mapping.get(current_index)
        return None
        
    def get_current_text_edit(self) -> Optional[QTextEdit]:
        """获取当前文本编辑器"""
        widget = self.tab_widget.currentWidget()
        if isinstance(widget, QTextEdit):
            return widget
        return None
        
    def show_find_dialog(self):
        """显示查找对话框"""
        current_text_edit = self.get_current_text_edit()
        if current_text_edit:
            if not self.find_dialog:
                self.find_dialog = FindReplaceDialog(current_text_edit, self)
            else:
                self.find_dialog.text_edit = current_text_edit
            self.find_dialog.show()
            
    def update_outline(self):
        """更新大纲导航"""
        current_text_edit = self.get_current_text_edit()
        if current_text_edit and hasattr(self.outline_navigator, 'update_content'):
            content = current_text_edit.toPlainText()
            current_tab_id = self.get_current_tab_id()
            if current_tab_id:
                doc_tab = self.tabs[current_tab_id]
                
                # 确定文档类型和文件路径
                if doc_tab.is_word_document:
                    doc_type = "word"
                    file_path = doc_tab.file_path
                else:
                    doc_type = doc_tab.get_file_type()
                    file_path = doc_tab.file_path if doc_tab.file_path else None
                
                # 更新大纲内容
                self.outline_navigator.update_content(content, doc_type, file_path)
                
                # 提示信息
                if doc_tab.is_word_document:
                    self.status_label.setText("Word文档大纲已加载")
                elif content.strip() and doc_type == 'md' and '##' not in content and '#' not in content:
                    self.status_label.setText("提示：添加标题(#)可生成大纲导航")
                        
    def highlight_current_section(self):
        """高亮当前编辑位置对应的大纲项"""
        pass  # 暂未实现
                
    def update_status(self):
        """更新状态栏"""
        current_tab_id = self.get_current_tab_id()
        if current_tab_id:
            doc_tab = self.tabs[current_tab_id]
            
            # 更新文档信息
            if doc_tab.file_path:
                file_name = Path(doc_tab.file_path).name
                file_type = doc_tab.get_file_type().upper()
                
                # 添加Word文档状态显示
                if doc_tab.is_word_document:
                    mode_text = "只读" if doc_tab.word_mode == "readonly" else "编辑"
                    self.doc_info_label.setText(f"{file_name} (Word - {mode_text})")
                else:
                    self.doc_info_label.setText(f"{file_name} ({file_type})")
            else:
                self.doc_info_label.setText("未命名文档")
                
            # 更新状态
            if doc_tab.is_modified:
                self.status_label.setText("文档已修改")
            elif doc_tab.is_word_document:
                self.status_label.setText(f"Word文档 - {doc_tab.word_mode}")
            else:
                self.status_label.setText("就绪")
                
    def update_cursor_position(self):
        """更新光标位置"""
        current_text_edit = self.get_current_text_edit()
        if current_text_edit:
            cursor = current_text_edit.textCursor()
            line = cursor.blockNumber() + 1
            column = cursor.columnNumber() + 1
            self.cursor_info_label.setText(f"行: {line}, 列: {column}")
            
            # 高亮当前章节
            self.highlight_current_section()
            
    def on_outline_jump_to_line(self, line_number):
        """大纲跳转到行号事件"""
        current_text_edit = self.get_current_text_edit()
        if current_text_edit and line_number > 0:
            # 跳转到对应行
            cursor = current_text_edit.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            
            # 移动到目标行
            for _ in range(line_number - 1):
                cursor.movePosition(QTextCursor.MoveOperation.Down)
            
            # 设置光标位置并聚焦
            current_text_edit.setTextCursor(cursor)
            current_text_edit.setFocus()
            
            # 确保目标行可见
            current_text_edit.ensureCursorVisible()
            
            # 更新状态栏显示
            self.status_label.setText(f"已跳转到第 {line_number} 行")
            
    def load_settings(self):
        """加载设置"""
        try:
            # 加载字体设置
            font_family = "Consolas"
            font_size = 12
            
            if hasattr(self.settings, 'get'):
                font_family = self.settings.get('editor.font_family', 'Consolas') or 'Consolas'
                font_size = self.settings.get('editor.font_size', 12) or 12
            
            # 确保字体大小是整数
            if not isinstance(font_size, int):
                font_size = 12
            
            for i in range(self.tab_widget.count()):
                text_edit = self.tab_widget.widget(i)
                if isinstance(text_edit, QTextEdit):
                    text_edit.setFont(QFont(font_family, font_size))
        except Exception as e:
            print(f"加载设置失败: {e}")
                
    def auto_save(self):
        """自动保存"""
        for tab_id, doc_tab in self.tabs.items():
            if doc_tab.is_modified and doc_tab.file_path:
                self._save_tab_backup(tab_id, doc_tab)
    
    def _save_tab_backup(self, tab_id: int, doc_tab: DocumentTab):
        """保存单个标签页的备份"""
        # 找到对应的文本编辑器
        for index, mapped_tab_id in self.tab_id_mapping.items():
            if mapped_tab_id == tab_id:
                text_edit = self.tab_widget.widget(index)
                if isinstance(text_edit, QTextEdit):
                    try:
                        content = text_edit.toPlainText()
                        backup_path = doc_tab.file_path + ".backup"
                        with open(backup_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                    except Exception as e:
                        print(f"自动保存失败: {e}")
                break
                        
    def generate_ai_outline(self):
        """生成AI大纲"""
        current_text_edit = self.get_current_text_edit()
        if not current_text_edit:
            return
            
        content = current_text_edit.toPlainText()
        if not content.strip():
            QMessageBox.information(self, "提示", "请先输入一些内容")
            return
            
        if not self.ai_service.is_available():
            QMessageBox.warning(self, "警告", AI_SERVICE_UNAVAILABLE_MSG)
            return
            
        # 禁用按钮，显示进度
        self.ai_outline_btn.setEnabled(False)
        self.ai_progress.setVisible(True)
        self.ai_progress.setRange(0, 0)  # 不确定进度
        
        current_tab_id = self.get_current_tab_id()
        doc_type = "markdown"
        if current_tab_id:
            doc_tab = self.tabs[current_tab_id]
            doc_type = doc_tab.get_file_type()
            
        # 启动AI工作线程
        self.ai_worker = AIWorker(self.ai_service, "generate_outline", content, doc_type=doc_type)
        self.ai_worker.finished.connect(self.on_ai_finished)
        self.ai_worker.error.connect(self.on_ai_error)
        self.ai_worker.start()
        
    def get_ai_suggestions(self):
        """获取AI内容建议"""
        current_text_edit = self.get_current_text_edit()
        if not current_text_edit:
            return
            
        cursor = current_text_edit.textCursor()
        if cursor.hasSelection():
            content = cursor.selectedText()
        else:
            content = current_text_edit.toPlainText()
            
        if not content.strip():
            QMessageBox.information(self, "提示", "请先选择或输入一些内容")
            return
            
        if not self.ai_service.is_available():
            QMessageBox.warning(self, "警告", AI_SERVICE_UNAVAILABLE_MSG)
            return
            
        # 禁用按钮，显示进度
        self.ai_suggest_btn.setEnabled(False)
        self.ai_progress.setVisible(True)
        self.ai_progress.setRange(0, 0)
        
        # 启动AI工作线程
        self.ai_worker = AIWorker(self.ai_service, "suggest_content", content)
        self.ai_worker.finished.connect(self.on_ai_finished)
        self.ai_worker.error.connect(self.on_ai_error)
        self.ai_worker.start()
        
    def improve_writing(self):
        """改进写作"""
        current_text_edit = self.get_current_text_edit()
        if not current_text_edit:
            return
            
        cursor = current_text_edit.textCursor()
        if cursor.hasSelection():
            content = cursor.selectedText()
        else:
            content = current_text_edit.toPlainText()
            
        if not content.strip():
            QMessageBox.information(self, "提示", "请先选择或输入一些内容")
            return
            
        if not self.ai_service.is_available():
            QMessageBox.warning(self, "警告", AI_SERVICE_UNAVAILABLE_MSG)
            return
            
        # 禁用按钮，显示进度
        self.ai_improve_btn.setEnabled(False)
        self.ai_progress.setVisible(True)
        self.ai_progress.setRange(0, 0)
        
        # 启动AI工作线程
        self.ai_worker = AIWorker(self.ai_service, "improve_writing", content)
        self.ai_worker.finished.connect(self.on_ai_finished)
        self.ai_worker.error.connect(self.on_ai_error)
        self.ai_worker.start()
        
    @pyqtSlot(dict)
    def on_ai_finished(self, result: dict):
        """AI处理完成"""
        # 恢复按钮状态
        self.ai_outline_btn.setEnabled(True)
        self.ai_suggest_btn.setEnabled(True)
        self.ai_improve_btn.setEnabled(True)
        self.ai_progress.setVisible(False)
        
        if result.get('success'):
            task = result['task']
            response = result['response']
            
            # 显示结果
            if hasattr(response, 'content'):
                self.ai_result_text.setPlainText(response.content)
            else:
                self.ai_result_text.setPlainText(str(response))
                
            self.status_label.setText(f"AI {task} 完成")
        else:
            QMessageBox.warning(self, "警告", "AI处理失败")
            
    @pyqtSlot(str)
    def on_ai_error(self, error_msg: str):
        """AI处理错误"""
        # 恢复按钮状态
        self.ai_outline_btn.setEnabled(True)
        self.ai_suggest_btn.setEnabled(True)
        self.ai_improve_btn.setEnabled(True)
        self.ai_progress.setVisible(False)
        
        QMessageBox.critical(self, "错误", error_msg)
        
    def closeEvent(self, event):
        """关闭事件"""
        # 检查是否有未保存的文档
        modified_docs = []
        for tab_id, doc_tab in self.tabs.items():
            if doc_tab.is_modified:
                modified_docs.append(doc_tab)
                
        if modified_docs:
            reply = QMessageBox.question(
                self,
                "确认",
                f"有 {len(modified_docs)} 个文档未保存，是否确认退出？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
                
        event.accept()

    # Word文档相关方法
    def toggle_word_mode(self):
        """切换Word文档编辑模式"""
        current_tab_id = self.get_current_tab_id()
        if current_tab_id is None:
            return
            
        doc_tab = self.tabs[current_tab_id]
        if not doc_tab.is_word_document:
            QMessageBox.information(self, "提示", "当前文档不是Word文档")
            return
        
        if doc_tab.word_mode == "readonly":
            doc_tab.word_mode = "markdown_edit"
            QMessageBox.information(
                self, 
                "模式切换", 
                "已切换到Markdown编辑模式\n可以编辑文档内容，使用'保存为Word'保存修改"
            )
        else:
            doc_tab.word_mode = "readonly"
            QMessageBox.information(
                self, 
                "模式切换", 
                "已切换到只读模式"
            )
        
        self.update_word_mode_ui()
    
    def save_as_word(self):
        """保存为Word文档"""
        current_tab_id = self.get_current_tab_id()
        if current_tab_id is None:
            return
            
        doc_tab = self.tabs[current_tab_id]
        current_editor = self.get_current_text_edit()
        if current_editor is None:
            return
        
        # 获取当前内容
        content = current_editor.toPlainText()
        
        # 选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存为Word文档",
            "",
            "Word文档 (*.docx);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                # 确保文件扩展名正确
                if not file_path.lower().endswith('.docx'):
                    file_path += '.docx'
                
                # 使用Word解析器保存
                title = Path(file_path).stem
                success = self.word_parser.save_as_word(content, file_path, title)
                
                if success:
                    QMessageBox.information(
                        self, 
                        "保存成功", 
                        f"文档已成功保存为Word格式:\n{file_path}"
                    )
                    
                    # 如果当前是Word文档，更新文件路径
                    if doc_tab.is_word_document:
                        doc_tab.file_path = file_path
                        doc_tab.is_modified = False
                        self.update_tab_title(current_tab_id)
                        
                else:
                    QMessageBox.warning(self, "保存失败", "无法保存为Word格式，请检查文件路径和权限")
                    
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存Word文档时出错: {str(e)}")
    
    def update_word_mode_ui(self):
        """更新Word模式相关的UI状态"""
        current_tab_id = self.get_current_tab_id()
        if current_tab_id is None:
            return
            
        doc_tab = self.tabs[current_tab_id]
        
        # 更新工具栏按钮状态
        if hasattr(self, 'word_mode_action'):
            if doc_tab.is_word_document:
                self.word_mode_action.setEnabled(True)
                if doc_tab.word_mode == "readonly":
                    self.word_mode_action.setText("切换到编辑模式")
                else:
                    self.word_mode_action.setText("切换到只读模式")
            else:
                self.word_mode_action.setEnabled(False)
                self.word_mode_action.setText("切换编辑模式")
        
        # 更新编辑器状态
        current_editor = self.get_current_text_edit()
        if current_editor and doc_tab.is_word_document:
            if doc_tab.word_mode == "readonly":
                current_editor.setReadOnly(True)
                current_editor.setStyleSheet("background-color: #f0f0f0;")
            else:
                current_editor.setReadOnly(False)
                current_editor.setStyleSheet("")
    
    def update_tab_title(self, tab_id: int):
        """更新标签页标题"""
        if tab_id not in self.tabs:
            return
            
        doc_tab = self.tabs[tab_id]
        
        # 找到对应的标签页索引
        for i in range(self.tab_widget.count()):
            if self.tab_id_mapping.get(i) == tab_id:
                self.tab_widget.setTabText(i, doc_tab.get_display_name())
                break
