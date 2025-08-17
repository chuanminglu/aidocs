"""
通用工具函数

提供md2doc的工具函数：
- 文件操作
- 格式检测
- 路径处理
"""

from pathlib import Path
from typing import Optional, List


def detect_markdown_format(content: str) -> List[str]:
    """检测Markdown内容中的特殊格式
    
    Args:
        content: Markdown内容
        
    Returns:
        检测到的格式列表
    """
    formats = []
    
    # 检测Mermaid图表
    if "```mermaid" in content:
        formats.append("mermaid")
    
    # 检测代码块
    if "```" in content:
        formats.append("code_block")
    
    # 检测表格
    if "|" in content and "\n" in content:
        lines = content.split("\n")
        for line in lines:
            if line.count("|") >= 2:
                formats.append("table")
                break
    
    return formats


def validate_file_path(file_path: Path) -> bool:
    """验证文件路径
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否有效
    """
    return file_path.exists() and file_path.is_file()


def ensure_output_dir(output_path: Path) -> bool:
    """确保输出目录存在
    
    Args:
        output_path: 输出路径
        
    Returns:
        是否成功创建
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def ensure_directory(directory: Path) -> bool:
    """确保目录存在
    
    Args:
        directory: 目录路径
        
    Returns:
        是否成功创建
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def get_file_extension(file_path: Path) -> str:
    """获取文件扩展名
    
    Args:
        file_path: 文件路径
        
    Returns:
        扩展名
    """
    return file_path.suffix.lower()
