"""
图片查看器组件
支持Word文档中的图片预览和显示
"""
import base64
import tempfile
import shutil
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap

try:
    import importlib.util
    PILLOW_AVAILABLE = importlib.util.find_spec("PIL") is not None
except ImportError:
    PILLOW_AVAILABLE = False


class ImageViewer(QWidget):
    """图片查看器组件"""
    
    # 信号
    image_clicked = pyqtSignal(str)  # 图片被点击
    image_saved = pyqtSignal(str)    # 图片被保存
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_path = None
        self.image_data = None
        self.scale_factor = 1.0
        self.max_display_size = QSize(400, 300)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 图片显示区域
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        self.image_scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                background-color: #f9f9f9;
                padding: 5px;
            }
        """)
        self.image_label.setMinimumSize(200, 150)
        self.image_label.mousePressEvent = self.on_image_clicked
        
        self.image_scroll.setWidget(self.image_label)
        layout.addWidget(self.image_scroll)
        
        # 控制按钮
        self.create_control_buttons()
        layout.addLayout(self.button_layout)
        
        # 图片信息
        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.info_label)
        
    def create_control_buttons(self):
        """创建控制按钮"""
        self.button_layout = QHBoxLayout()
        
        # 缩放按钮
        self.zoom_in_btn = QPushButton("放大")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.button_layout.addWidget(self.zoom_in_btn)
        
        self.zoom_out_btn = QPushButton("缩小")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.button_layout.addWidget(self.zoom_out_btn)
        
        self.fit_to_window_btn = QPushButton("适应窗口")
        self.fit_to_window_btn.clicked.connect(self.fit_to_window)
        self.button_layout.addWidget(self.fit_to_window_btn)
        
        self.button_layout.addStretch()
        
        # 保存按钮
        self.save_btn = QPushButton("保存图片")
        self.save_btn.clicked.connect(self.save_image)
        self.button_layout.addWidget(self.save_btn)
        
        # 初始状态禁用按钮
        self.set_controls_enabled(False)
        
    def load_image_from_base64(self, base64_data: str, filename: str = "image", 
                              width: Optional[int] = None, height: Optional[int] = None, 
                              format: Optional[str] = None, description: Optional[str] = None):
        """从base64数据加载图片"""
        try:
            # 解码base64数据
            image_bytes = base64.b64decode(base64_data)
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(image_bytes)
                temp_path = temp_file.name
            
            # 加载图片
            pixmap = QPixmap(temp_path)
            if not pixmap.isNull():
                self.image_path = temp_path
                self.image_data = base64_data
                self.display_image(pixmap, filename, width, height, format, description)
                return True
            else:
                print(f"无法加载图片: {filename}")
                return False
                
        except Exception as e:
            print(f"加载base64图片失败: {e}")
            return False
            
    def load_image_from_file(self, file_path: str, description: Optional[str] = None):
        """从文件加载图片"""
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.image_path = file_path
                self.image_data = None
                
                # 获取图片信息
                filename = Path(file_path).name
                width = pixmap.width()
                height = pixmap.height()
                
                self.display_image(pixmap, filename, width, height, 
                                 Path(file_path).suffix.upper(), description)
                return True
            else:
                print(f"无法加载图片文件: {file_path}")
                return False
                
        except Exception as e:
            print(f"加载图片文件失败: {e}")
            return False
            
    def display_image(self, pixmap: QPixmap, filename: str, 
                     width: Optional[int] = None, height: Optional[int] = None, 
                     format: Optional[str] = None, description: Optional[str] = None):
        """显示图片"""
        # 计算缩放尺寸
        if width and height:
            # 原始尺寸信息用于显示
            pass
        else:
            # 使用pixmap的实际尺寸
            pass
            
        # 缩放图片以适应显示区域
        scaled_pixmap = self.scale_pixmap(pixmap, self.max_display_size)
        self.image_label.setPixmap(scaled_pixmap)
        
        # 更新信息
        info_parts = [f"文件: {filename}"]
        if width and height:
            info_parts.append(f"尺寸: {width}×{height}")
        if format:
            info_parts.append(f"格式: {format}")
        if description:
            info_parts.append(f"描述: {description}")
            
        self.info_label.setText(" | ".join(info_parts))
        
        # 启用控制按钮
        self.set_controls_enabled(True)
        
    def scale_pixmap(self, pixmap: QPixmap, max_size: QSize) -> QPixmap:
        """缩放图片以适应指定尺寸"""
        if pixmap.size().width() <= max_size.width() and pixmap.size().height() <= max_size.height():
            return pixmap
            
        return pixmap.scaled(max_size, Qt.AspectRatioMode.KeepAspectRatio, 
                           Qt.TransformationMode.SmoothTransformation)
        
    def zoom_in(self):
        """放大图片"""
        self.scale_factor *= 1.25
        self.update_image_display()
        
    def zoom_out(self):
        """缩小图片"""
        self.scale_factor /= 1.25
        self.update_image_display()
        
    def fit_to_window(self):
        """适应窗口大小"""
        self.scale_factor = 1.0
        self.update_image_display()
        
    def update_image_display(self):
        """更新图片显示"""
        if not self.image_path:
            return
            
        # 重新加载并缩放图片
        original_pixmap = QPixmap(self.image_path)
        if not original_pixmap.isNull():
            # 计算新尺寸
            new_size = QSize(
                int(self.max_display_size.width() * self.scale_factor),
                int(self.max_display_size.height() * self.scale_factor)
            )
            
            scaled_pixmap = self.scale_pixmap(original_pixmap, new_size)
            self.image_label.setPixmap(scaled_pixmap)
            
    def save_image(self):
        """保存图片"""
        if not self.image_path and not self.image_data:
            QMessageBox.warning(self, "警告", "没有图片可以保存")
            return
            
        # 选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存图片", "", 
            "PNG Files (*.png);;JPG Files (*.jpg);;All Files (*)"
        )
        
        if file_path:
            try:
                if self.image_data:
                    # 从base64数据保存
                    image_bytes = base64.b64decode(self.image_data)
                    with open(file_path, 'wb') as f:
                        f.write(image_bytes)
                else:
                    # 从文件复制
                    if self.image_path:
                        shutil.copy2(self.image_path, file_path)
                    else:
                        raise ValueError("没有有效的图片路径")
                    
                QMessageBox.information(self, "成功", f"图片已保存到: {file_path}")
                self.image_saved.emit(file_path)
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存图片失败: {str(e)}")
                
    def set_controls_enabled(self, enabled: bool):
        """设置控制按钮状态"""
        self.zoom_in_btn.setEnabled(enabled)
        self.zoom_out_btn.setEnabled(enabled)
        self.fit_to_window_btn.setEnabled(enabled)
        self.save_btn.setEnabled(enabled)
        
    def on_image_clicked(self, event):
        """图片被点击"""
        if self.image_path:
            self.image_clicked.emit(self.image_path)
            
    def clear(self):
        """清空显示"""
        self.image_label.clear()
        self.image_label.setText("无图片")
        self.info_label.clear()
        self.image_path = None
        self.image_data = None
        self.scale_factor = 1.0
        self.set_controls_enabled(False)


class ImagePreviewWidget(QWidget):
    """图片预览组件（用于文档编辑器中的内联显示）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # 图片标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ddd;
                background-color: #f5f5f5;
                padding: 2px;
                border-radius: 3px;
            }
        """)
        self.image_label.setMaximumSize(150, 100)
        self.image_label.setScaledContents(True)
        layout.addWidget(self.image_label)
        
        # 文件名标签
        self.filename_label = QLabel()
        self.filename_label.setStyleSheet("color: #666; font-size: 10px;")
        self.filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.filename_label)
        
    def load_image(self, base64_data: Optional[str] = None, file_path: Optional[str] = None,
                  filename: str = "image"):
        """加载图片"""
        try:
            pixmap = None
            
            if base64_data:
                # 从base64加载
                image_bytes = base64.b64decode(base64_data)
                pixmap = QPixmap()
                pixmap.loadFromData(image_bytes)
                
            elif file_path:
                # 从文件加载
                pixmap = QPixmap(file_path)
                
            if pixmap and not pixmap.isNull():
                # 缩放图片
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.filename_label.setText(filename)
                return True
                
        except Exception as e:
            print(f"加载图片预览失败: {e}")
            
        # 显示错误状态
        self.image_label.setText("无法显示")
        self.filename_label.setText(filename)
        return False
        
    def clear(self):
        """清空显示"""
        self.image_label.clear()
        self.image_label.setText("无图片")
        self.filename_label.clear()
