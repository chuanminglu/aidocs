"""
日志系统配置

提供md2doc的日志功能：
- 多级别日志记录
- 文件和控制台输出
- 进度显示功能
- 自定义格式化
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class ColorFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }
    
    def format(self, record):
        # 获取原始格式化的消息
        formatted = super().format(record)
        
        # 如果支持颜色（通常是控制台），添加颜色
        if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            color = self.COLORS.get(record.levelname, '')
            reset = self.COLORS['RESET']
            return f"{color}{formatted}{reset}"
        
        return formatted


class ProgressLogger:
    """进度显示日志器"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._last_progress = -1
    
    def update(self, current: int, total: int, message: str = ""):
        """更新进度
        
        Args:
            current: 当前进度
            total: 总进度
            message: 额外消息
        """
        if total <= 0:
            return
            
        progress = int((current / total) * 100)
        
        # 只在进度变化时更新（避免过多输出）
        if progress != self._last_progress:
            bar_length = 30
            filled_length = int(bar_length * current // total)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            progress_msg = f"[{bar}] {progress}% ({current}/{total})"
            if message:
                progress_msg += f" - {message}"
            
            self.logger.info(progress_msg)
            self._last_progress = progress
    
    def complete(self, message: str = "完成"):
        """标记为完成"""
        self.logger.info(f"✅ {message}")


def setup_logger(name: str = "md2doc", config: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """设置日志器
    
    Args:
        name: 日志器名称
        config: 配置字典
        
    Returns:
        配置好的日志器
    """
    # 默认配置
    default_config = {
        "level": "INFO",
        "file": "logs/md2doc.log",
        "console": True,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "date_format": "%Y-%m-%d %H:%M:%S"
    }
    
    if config:
        default_config.update(config)
    
    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, default_config["level"].upper()))
    
    # 清除现有的处理器（避免重复）
    logger.handlers.clear()
    
    # 创建格式化器
    formatter = logging.Formatter(
        default_config["format"],
        datefmt=default_config["date_format"]
    )
    
    # 控制台处理器
    if default_config["console"]:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # 使用彩色格式化器
        color_formatter = ColorFormatter(
            default_config["format"],
            datefmt=default_config["date_format"]
        )
        console_handler.setFormatter(color_formatter)
        logger.addHandler(console_handler)
    
    # 文件处理器
    if default_config["file"]:
        log_file = Path(default_config["file"])
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "md2doc") -> logging.Logger:
    """获取日志器实例
    
    Args:
        name: 日志器名称
        
    Returns:
        日志器实例
    """
    return logging.getLogger(name)


def log_function_call(func):
    """函数调用日志装饰器"""
    def wrapper(*args, **kwargs):
        logger = get_logger()
        logger.debug(f"调用函数: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"函数 {func.__name__} 执行成功")
            return result
        except Exception as e:
            logger.error(f"函数 {func.__name__} 执行失败: {e}")
            raise
    return wrapper


def log_execution_time(func):
    """执行时间日志装饰器"""
    def wrapper(*args, **kwargs):
        logger = get_logger()
        start_time = datetime.now()
        logger.debug(f"开始执行: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"函数 {func.__name__} 执行完成，耗时: {duration:.2f}秒")
            return result
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.error(f"函数 {func.__name__} 执行失败，耗时: {duration:.2f}秒，错误: {e}")
            raise
    return wrapper


# 默认日志器实例
_default_logger = None


def get_default_logger() -> logging.Logger:
    """获取默认日志器"""
    global _default_logger
    if _default_logger is None:
        _default_logger = setup_logger()
    return _default_logger


# 便捷函数
def debug(message: str):
    """记录调试信息"""
    get_default_logger().debug(message)


def info(message: str):
    """记录信息"""
    get_default_logger().info(message)


def warning(message: str):
    """记录警告"""
    get_default_logger().warning(message)


def error(message: str):
    """记录错误"""
    get_default_logger().error(message)


def critical(message: str):
    """记录严重错误"""
    get_default_logger().critical(message)
