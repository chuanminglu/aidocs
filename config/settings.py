"""
AI文档管理系统配置文件
基于 PyQt6 + FastAPI + SQLAlchemy + DeepSeek 架构
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """应用程序配置"""
    
    # 应用基础配置
    app_name: str = "AI文档管理系统"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # 项目路径
    project_root: Path = Path(__file__).parent.parent
    data_dir: Path = project_root / "data"
    documents_dir: Path = data_dir / "documents"
    templates_dir: Path = data_dir / "templates"
    database_dir: Path = data_dir / "database"
    cache_dir: Path = data_dir / "cache"
    
    # FastAPI 配置
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = ["*"]
    
    # 数据库配置
    database_url: str = ""
    async_database_url: str = ""
    database_echo: bool = False
    
    # DeepSeek AI 配置
    deepseek_api_key: Optional[str] = "sk-4b7b1f6ec79040ffa41768c3c267b6c9"
    deepseek_api_base: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"
    
    # 搜索配置
    search_index_dir: Path = cache_dir / "search_index"
    max_search_results: int = 100
    
    # 文档配置
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    supported_formats: List[str] = [".md", ".txt", ".docx", ".pdf", ".html"]
    
    # 缓存配置
    cache_ttl: int = 3600  # 1小时
    max_cache_size: int = 100 * 1024 * 1024  # 100MB
    cache_retention_days: int = 7
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Path = project_root / "logs" / "aidocs.log"
    
    # 模板配置
    default_template: str = "default.md"
    template_extensions: List[str] = [".md", ".txt", ".html"]
    
    # GUI配置
    window_width: int = 1200
    window_height: int = 800
    theme: str = "light"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化时设置数据库URL
        self.database_url = f"sqlite:///{self.database_dir}/aidocs.db"
        self.async_database_url = f"sqlite+aiosqlite:///{self.database_dir}/aidocs.db"
        
        # 创建必要的目录
        self.create_directories()
    
    def create_directories(self):
        """创建必要的目录"""
        directories = [
            self.data_dir,
            self.documents_dir,
            self.templates_dir,
            self.database_dir,
            self.cache_dir,
            self.search_index_dir,
            self.project_root / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_database_url(self, async_mode: bool = False) -> str:
        """获取数据库连接URL"""
        if async_mode:
            return self.async_database_url
        return self.database_url
    
    def get_documents_path(self) -> Path:
        """获取文档存储路径"""
        return self.documents_dir
    
    def get_templates_path(self) -> Path:
        """获取模板存储路径"""
        return self.templates_dir
    
    def is_supported_format(self, file_path: str) -> bool:
        """检查文件格式是否支持"""
        return Path(file_path).suffix.lower() in self.supported_formats
    
    def get_ai_config(self) -> dict:
        """获取AI配置"""
        return {
            "api_key": self.deepseek_api_key,
            "api_base": self.deepseek_api_base,
            "model": self.deepseek_model
        }
    
    class Config:
        """Pydantic配置"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 创建全局配置实例
settings = Settings()


# 时间维度配置
TIME_DIMENSIONS = {
    "year": {"format": "%Y", "display": "年度"},
    "month": {"format": "%Y-%m", "display": "月度"},
    "week": {"format": "%Y-W%W", "display": "周度"},
    "day": {"format": "%Y-%m-%d", "display": "日期"},
}

# 专业维度配置
PROFESSIONAL_DIMENSIONS = {
    "人工智能": {
        "subcategories": ["机器学习", "深度学习", "自然语言处理", "计算机视觉", "强化学习"],
        "color": "#FF6B6B",
        "icon": "🤖"
    },
    "项目管理": {
        "subcategories": ["敏捷开发", "需求管理", "风险管理", "团队协作", "项目复盘"],
        "color": "#4ECDC4",
        "icon": "📊"
    },
    "DevOps": {
        "subcategories": ["持续集成", "监控运维", "质量工程", "容器化", "自动化"],
        "color": "#45B7D1",
        "icon": "🔧"
    },
    "技术研究": {
        "subcategories": ["新技术调研", "技术选型", "最佳实践", "技术方案", "问题解决"],
        "color": "#96CEB4",
        "icon": "🔬"
    }
}

# 文档模板配置
DOCUMENT_TEMPLATES = {
    "技术研究笔记": {
        "file": "技术研究笔记模板.md",
        "category": "技术研究",
        "description": "用于记录技术研究过程和结果"
    },
    "项目复盘": {
        "file": "项目复盘模板.md",
        "category": "项目管理",
        "description": "项目结束后的复盘总结"
    },
    "日报": {
        "file": "日报模板.md",
        "category": "日常工作",
        "description": "每日工作记录和总结"
    }
}


# 导出配置
__all__ = ["Settings", "settings", "TIME_DIMENSIONS", "PROFESSIONAL_DIMENSIONS", "DOCUMENT_TEMPLATES"]
