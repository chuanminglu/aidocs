"""
查找替换对话框
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QTextEdit, QMessageBox
)
from PyQt6.QtGui import QTextCursor


class FindReplaceDialog(QDialog):
    """查找替换对话框"""
    
    def __init__(self, text_edit: QTextEdit, parent=None):
        super().__init__(parent)
        self.text_edit = text_edit
        self.last_found_pos = 0
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("查找和替换")
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # 查找框
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("查找:"))
        self.find_edit = QLineEdit()
        self.find_edit.textChanged.connect(self.on_find_text_changed)
        find_layout.addWidget(self.find_edit)
        layout.addLayout(find_layout)
        
        # 替换框
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("替换:"))
        self.replace_edit = QLineEdit()
        replace_layout.addWidget(self.replace_edit)
        layout.addLayout(replace_layout)
        
        # 选项
        options_layout = QHBoxLayout()
        self.case_sensitive_cb = QCheckBox("区分大小写")
        self.whole_word_cb = QCheckBox("全词匹配")
        options_layout.addWidget(self.case_sensitive_cb)
        options_layout.addWidget(self.whole_word_cb)
        layout.addLayout(options_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.find_next_btn = QPushButton("查找下一个")
        self.find_next_btn.clicked.connect(self.find_next)
        self.find_next_btn.setEnabled(False)
        button_layout.addWidget(self.find_next_btn)
        
        self.replace_btn = QPushButton("替换")
        self.replace_btn.clicked.connect(self.replace_current)
        self.replace_btn.setEnabled(False)
        button_layout.addWidget(self.replace_btn)
        
        self.replace_all_btn = QPushButton("全部替换")
        self.replace_all_btn.clicked.connect(self.replace_all)
        self.replace_all_btn.setEnabled(False)
        button_layout.addWidget(self.replace_all_btn)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # 设置焦点
        self.find_edit.setFocus()
    
    def on_find_text_changed(self, text: str):
        """查找文本变化"""
        has_text = bool(text.strip())
        self.find_next_btn.setEnabled(has_text)
        self.replace_btn.setEnabled(has_text)
        self.replace_all_btn.setEnabled(has_text)
        self.last_found_pos = 0
    
    def find_next(self):
        """查找下一个"""
        find_text = self.find_edit.text()
        if not find_text:
            return
        
        content = self.text_edit.toPlainText()
        
        if not self.case_sensitive_cb.isChecked():
            content = content.lower()
            find_text = find_text.lower()
        
        # 从当前位置开始查找
        pos = content.find(find_text, self.last_found_pos)
        
        if pos == -1:
            # 从头开始查找
            pos = content.find(find_text, 0)
            if pos == -1:
                QMessageBox.information(self, "查找", "未找到指定文本")
                return
        
        # 选中找到的文本
        cursor = self.text_edit.textCursor()
        cursor.setPosition(pos)
        cursor.setPosition(pos + len(self.find_edit.text()), QTextCursor.MoveMode.KeepAnchor)
        self.text_edit.setTextCursor(cursor)
        
        # 更新查找位置
        self.last_found_pos = pos + 1
        
        # 滚动到可见位置
        self.text_edit.ensureCursorVisible()
    
    def replace_current(self):
        """替换当前选中的文本"""
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_edit.text())
            self.find_next()
    
    def replace_all(self):
        """替换全部"""
        find_text = self.find_edit.text()
        replace_text = self.replace_edit.text()
        
        if not find_text:
            return
        
        content = self.text_edit.toPlainText()
        
        # 根据选项处理
        if self.case_sensitive_cb.isChecked():
            new_content = content.replace(find_text, replace_text)
        else:
            # 不区分大小写的替换
            import re
            pattern = re.compile(re.escape(find_text), re.IGNORECASE)
            new_content = pattern.sub(replace_text, content)
        
        # 计算替换次数
        if self.case_sensitive_cb.isChecked():
            count = content.count(find_text)
        else:
            count = len(re.findall(re.escape(find_text), content, re.IGNORECASE))
        
        if count > 0:
            self.text_edit.setPlainText(new_content)
            QMessageBox.information(self, "替换", f"已替换 {count} 个匹配项")
        else:
            QMessageBox.information(self, "替换", "没有找到匹配项")
    
    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        # 如果文本编辑器有选中文本，自动填入查找框
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            if selected_text and len(selected_text) < 100:  # 限制长度
                self.find_edit.setText(selected_text)
                self.find_edit.selectAll()
