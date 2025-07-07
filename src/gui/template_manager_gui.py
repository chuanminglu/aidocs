"""
模板管理器GUI界面
提供模板的可视化管理功能
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QLabel, QLineEdit,
    QPushButton, QSplitter, QGroupBox, QComboBox, QSpinBox,
    QTabWidget, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox,
    QFormLayout, QMessageBox, QFileDialog, QToolBar, QMenuBar,
    QStatusBar, QProgressBar, QCheckBox, QSlider, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon, QFont, QPixmap, QTextCursor

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.settings import Settings
from src.core.template_manager import TemplateManager, TemplateMetadata

class TemplateManagerGUI(QMainWindow):
    """模板管理器主界面"""
    
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.template_manager = TemplateManager(self.settings.templates_dir)
        self.current_template_id = None
        self.init_ui()
        self.load_templates()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("模板管理器")
        self.setGeometry(100, 100, 1400, 900)
        
        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧面板：模板列表
        self.create_template_list_panel(splitter)
        
        # 右侧面板：模板编辑器
        self.create_template_editor_panel(splitter)
        
        # 设置分割器比例
        splitter.setSizes([400, 1000])
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建状态栏
        self.create_status_bar()
    
    def create_template_list_panel(self, parent):
        """创建模板列表面板"""
        # 左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 搜索栏
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索模板...")
        self.search_input.textChanged.connect(self.filter_templates)
        search_layout.addWidget(QLabel("搜索:"))
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)
        
        # 分类过滤
        category_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.addItem("全部分类")
        self.category_combo.currentTextChanged.connect(self.filter_by_category)
        category_layout.addWidget(QLabel("分类:"))
        category_layout.addWidget(self.category_combo)
        left_layout.addLayout(category_layout)
        
        # 模板列表
        self.template_list = QTreeWidget()
        self.template_list.setHeaderLabels(["模板", "信息"])
        self.template_list.itemClicked.connect(self.on_template_selected)
        self.template_list.setAlternatingRowColors(True)
        left_layout.addWidget(self.template_list)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        self.new_btn = QPushButton("新建")
        self.new_btn.clicked.connect(self.new_template)
        self.delete_btn = QPushButton("删除")
        self.delete_btn.clicked.connect(self.delete_template)
        self.import_btn = QPushButton("导入")
        self.import_btn.clicked.connect(self.import_template)
        self.export_btn = QPushButton("导出")
        self.export_btn.clicked.connect(self.export_template)
        
        button_layout.addWidget(self.new_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.export_btn)
        left_layout.addLayout(button_layout)
        
        parent.addWidget(left_panel)
    
    def create_template_editor_panel(self, parent):
        """创建模板编辑器面板"""
        # 右侧面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 模板信息区域
        info_group = QGroupBox("模板信息")
        info_layout = QFormLayout(info_group)
        
        self.name_input = QLineEdit()
        self.name_input.textChanged.connect(self.on_template_info_changed)
        info_layout.addRow("名称:", self.name_input)
        
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.currentTextChanged.connect(self.on_template_info_changed)
        info_layout.addRow("分类:", self.category_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.textChanged.connect(self.on_template_info_changed)
        info_layout.addRow("描述:", self.description_input)
        
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("标签用逗号分隔")
        self.tags_input.textChanged.connect(self.on_template_info_changed)
        info_layout.addRow("标签:", self.tags_input)
        
        right_layout.addWidget(info_group)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 内容编辑标签页
        self.content_tab = QWidget()
        content_layout = QVBoxLayout(self.content_tab)
        
        self.content_editor = QTextEdit()
        self.content_editor.setFont(QFont("Consolas", 10))
        self.content_editor.textChanged.connect(self.on_content_changed)
        content_layout.addWidget(self.content_editor)
        
        self.tab_widget.addTab(self.content_tab, "内容编辑")
        
        # 变量管理标签页
        self.variables_tab = QWidget()
        variables_layout = QVBoxLayout(self.variables_tab)
        
        # 变量检测区域
        var_detect_layout = QHBoxLayout()
        self.detect_vars_btn = QPushButton("检测变量")
        self.detect_vars_btn.clicked.connect(self.detect_variables)
        var_detect_layout.addWidget(self.detect_vars_btn)
        var_detect_layout.addStretch()
        variables_layout.addLayout(var_detect_layout)
        
        # 变量列表
        self.variables_list = QListWidget()
        variables_layout.addWidget(self.variables_list)
        
        self.tab_widget.addTab(self.variables_tab, "变量管理")
        
        # 预览标签页
        self.preview_tab = QWidget()
        preview_layout = QVBoxLayout(self.preview_tab)
        
        # 预览控制
        preview_control_layout = QHBoxLayout()
        self.preview_btn = QPushButton("生成预览")
        self.preview_btn.clicked.connect(self.generate_preview)
        preview_control_layout.addWidget(self.preview_btn)
        preview_control_layout.addStretch()
        preview_layout.addLayout(preview_control_layout)
        
        # 预览显示
        self.preview_display = QTextEdit()
        self.preview_display.setReadOnly(True)
        preview_layout.addWidget(self.preview_display)
        
        self.tab_widget.addTab(self.preview_tab, "预览")
        
        right_layout.addWidget(self.tab_widget)
        
        # 保存按钮
        save_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存模板")
        self.save_btn.clicked.connect(self.save_template)
        save_layout.addWidget(self.save_btn)
        save_layout.addStretch()
        right_layout.addLayout(save_layout)
        
        parent.addWidget(right_panel)
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        new_action = QAction('新建模板', self)
        new_action.triggered.connect(self.new_template)
        file_menu.addAction(new_action)
        
        open_action = QAction('打开模板', self)
        open_action.triggered.connect(self.open_template)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        import_action = QAction('导入模板', self)
        import_action.triggered.connect(self.import_template)
        file_menu.addAction(import_action)
        
        export_action = QAction('导出模板', self)
        export_action.triggered.connect(self.export_template)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑')
        
        detect_vars_action = QAction('检测变量', self)
        detect_vars_action.triggered.connect(self.detect_variables)
        edit_menu.addAction(detect_vars_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图')
        
        refresh_action = QAction('刷新', self)
        refresh_action.triggered.connect(self.load_templates)
        view_menu.addAction(refresh_action)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 新建按钮
        new_action = QAction('新建', self)
        new_action.triggered.connect(self.new_template)
        toolbar.addAction(new_action)
        
        # 保存按钮
        save_action = QAction('保存', self)
        save_action.triggered.connect(self.save_template)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # 导入按钮
        import_action = QAction('导入', self)
        import_action.triggered.connect(self.import_template)
        toolbar.addAction(import_action)
        
        # 导出按钮
        export_action = QAction('导出', self)
        export_action.triggered.connect(self.export_template)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # 预览按钮
        preview_action = QAction('预览', self)
        preview_action.triggered.connect(self.generate_preview)
        toolbar.addAction(preview_action)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def load_templates(self):
        """加载模板列表"""
        self.template_list.clear()
        
        # 加载分类
        categories = self.template_manager.get_categories()
        self.category_combo.clear()
        self.category_combo.addItem("全部分类")
        self.category_combo.addItems(categories)
        
        # 按分类组织模板
        templates = self.template_manager.list_templates()
        category_items = {}
        
        for template in templates:
            category = template.get('category', '其他')
            
            # 创建分类项
            if category not in category_items:
                category_item = QTreeWidgetItem(self.template_list)
                category_item.setText(0, category)
                category_item.setExpanded(True)
                category_items[category] = category_item
            
            # 创建模板项
            template_item = QTreeWidgetItem(category_items[category])
            template_item.setText(0, template['name'])
            template_item.setText(1, f"v{template['version']}")
            template_item.setData(0, Qt.ItemDataRole.UserRole, template['id'])
        
        self.status_bar.showMessage(f"已加载 {len(templates)} 个模板")
    
    def filter_templates(self, text):
        """过滤模板"""
        for i in range(self.template_list.topLevelItemCount()):
            category_item = self.template_list.topLevelItem(i)
            category_visible = False
            
            for j in range(category_item.childCount()):
                template_item = category_item.child(j)
                template_name = template_item.text(0).lower()
                visible = text.lower() in template_name
                template_item.setHidden(not visible)
                if visible:
                    category_visible = True
            
            category_item.setHidden(not category_visible)
    
    def filter_by_category(self, category):
        """按分类过滤"""
        for i in range(self.template_list.topLevelItemCount()):
            category_item = self.template_list.topLevelItem(i)
            if category == "全部分类":
                category_item.setHidden(False)
            else:
                category_item.setHidden(category_item.text(0) != category)
    
    def on_template_selected(self, item):
        """模板选择事件"""
        if item.parent():  # 是模板项，不是分类项
            template_id = item.data(0, Qt.ItemDataRole.UserRole)
            self.load_template(template_id)
    
    def load_template(self, template_id):
        """加载模板内容"""
        template_data = self.template_manager.get_template(template_id)
        if not template_data:
            return
        
        self.current_template_id = template_id
        metadata = template_data['metadata']
        content = template_data['content']
        
        # 填充模板信息
        self.name_input.setText(metadata['name'])
        self.category_input.setCurrentText(metadata['category'])
        self.description_input.setPlainText(metadata['description'])
        self.tags_input.setText(', '.join(metadata['tags']))
        
        # 填充内容
        self.content_editor.setPlainText(content)
        
        # 更新变量列表
        self.update_variables_list(metadata['variables'])
        
        self.status_bar.showMessage(f"已加载模板: {metadata['name']}")
    
    def update_variables_list(self, variables):
        """更新变量列表"""
        self.variables_list.clear()
        for var in variables:
            item = QListWidgetItem(f"{var['name']} ({var['type']})")
            item.setData(Qt.ItemDataRole.UserRole, var)
            self.variables_list.addItem(item)
    
    def new_template(self):
        """新建模板"""
        self.current_template_id = None
        self.name_input.clear()
        self.category_input.setCurrentText("")
        self.description_input.clear()
        self.tags_input.clear()
        self.content_editor.clear()
        self.variables_list.clear()
        self.preview_display.clear()
        self.status_bar.showMessage("新建模板")
    
    def save_template(self):
        """保存模板"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入模板名称")
            return
        
        category = self.category_input.currentText().strip()
        if not category:
            category = "自定义"
        
        description = self.description_input.toPlainText().strip()
        tags = [tag.strip() for tag in self.tags_input.text().split(',') if tag.strip()]
        content = self.content_editor.toPlainText()
        
        try:
            if self.current_template_id:
                # 更新现有模板
                metadata_updates = {
                    'name': name,
                    'category': category,
                    'description': description,
                    'tags': tags
                }
                success = self.template_manager.update_template(
                    self.current_template_id, content, metadata_updates
                )
                if success:
                    QMessageBox.information(self, "成功", "模板已更新")
                    self.load_templates()
                else:
                    QMessageBox.warning(self, "错误", "模板更新失败")
            else:
                # 创建新模板
                template_id = self.template_manager.create_template(
                    name, content, category, description, tags
                )
                if template_id:
                    self.current_template_id = template_id
                    QMessageBox.information(self, "成功", "模板已创建")
                    self.load_templates()
                else:
                    QMessageBox.warning(self, "错误", "模板创建失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
    
    def delete_template(self):
        """删除模板"""
        current_item = self.template_list.currentItem()
        if not current_item or not current_item.parent():
            QMessageBox.warning(self, "警告", "请选择要删除的模板")
            return
        
        template_id = current_item.data(0, Qt.ItemDataRole.UserRole)
        template_name = current_item.text(0)
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除模板 '{template_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.template_manager.delete_template(template_id):
                QMessageBox.information(self, "成功", "模板已删除")
                self.load_templates()
                self.new_template()  # 清空编辑器
            else:
                QMessageBox.warning(self, "错误", "删除失败")
    
    def import_template(self):
        """导入模板"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择模板文件", "", "Markdown文件 (*.md);;文本文件 (*.txt);;所有文件 (*)"
        )
        
        if file_path:
            try:
                template_id = self.template_manager.import_template(Path(file_path))
                if template_id:
                    QMessageBox.information(self, "成功", "模板导入成功")
                    self.load_templates()
                else:
                    QMessageBox.warning(self, "错误", "模板导入失败")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入失败: {str(e)}")
    
    def export_template(self):
        """导出模板"""
        current_item = self.template_list.currentItem()
        if not current_item or not current_item.parent():
            QMessageBox.warning(self, "警告", "请选择要导出的模板")
            return
        
        template_id = current_item.data(0, Qt.ItemDataRole.UserRole)
        template_name = current_item.text(0)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存模板", f"{template_name}.md", "Markdown文件 (*.md);;文本文件 (*.txt)"
        )
        
        if file_path:
            try:
                if self.template_manager.export_template(template_id, Path(file_path)):
                    QMessageBox.information(self, "成功", "模板导出成功")
                else:
                    QMessageBox.warning(self, "错误", "模板导出失败")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
    
    def detect_variables(self):
        """检测模板变量"""
        content = self.content_editor.toPlainText()
        variables = self.template_manager.engine.extract_variables(content)
        
        # 更新变量列表
        self.variables_list.clear()
        for var_name in variables:
            var_data = {
                'name': var_name,
                'type': 'text',
                'default': '',
                'description': f'变量 {var_name}'
            }
            item = QListWidgetItem(f"{var_name} (text)")
            item.setData(Qt.ItemDataRole.UserRole, var_data)
            self.variables_list.addItem(item)
        
        self.status_bar.showMessage(f"检测到 {len(variables)} 个变量")
    
    def generate_preview(self):
        """生成预览"""
        if not self.current_template_id:
            QMessageBox.warning(self, "警告", "请先保存模板")
            return
        
        # 创建示例上下文
        context = {
            'date': '2025-07-04',
            'author': '示例作者',
            'topic': '示例主题',
            'weather': '晴朗',
            'mood': '开心',
            'project_name': '示例项目',
            'researcher': '示例研究者',
            'priority': '高',
            'project_manager': '示例项目经理',
            'status': '进行中'
        }
        
        rendered = self.template_manager.render_template(self.current_template_id, context)
        if rendered:
            self.preview_display.setPlainText(rendered)
            self.status_bar.showMessage("预览已生成")
        else:
            QMessageBox.warning(self, "错误", "预览生成失败")
    
    def open_template(self):
        """打开模板文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开模板文件", "", "Markdown文件 (*.md);;文本文件 (*.txt);;所有文件 (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 在编辑器中显示
                self.content_editor.setPlainText(content)
                self.name_input.setText(Path(file_path).stem)
                self.status_bar.showMessage(f"已打开: {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"打开失败: {str(e)}")
    
    def on_template_info_changed(self):
        """模板信息改变"""
        if hasattr(self, 'current_template_id'):
            self.status_bar.showMessage("模板信息已修改")
    
    def on_content_changed(self):
        """内容改变"""
        if hasattr(self, 'current_template_id'):
            self.status_bar.showMessage("模板内容已修改")


def main():
    """主函数"""
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = TemplateManagerGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
