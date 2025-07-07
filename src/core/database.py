"""
数据库初始化和配置
FastAPI + SQLAlchemy 2.0 版本
"""
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import os
from config.settings import Settings

# 获取配置
settings = Settings()

# 同步数据库引擎
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=3600
)

# 异步数据库引擎（用于FastAPI）
async_engine = create_async_engine(
    settings.async_database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=3600
)

# 会话工厂
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 数据模型基类
Base = declarative_base()

# 元数据
metadata = MetaData()

# 依赖注入：获取数据库会话
def get_db():
    """获取同步数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 数据库初始化
def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)

async def init_async_db():
    """异步初始化数据库表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 数据库连接测试
def test_db_connection():
    """测试数据库连接"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return result.fetchone() is not None
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False

async def test_async_db_connection():
    """异步测试数据库连接"""
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()
            return row is not None
    except Exception as e:
        print(f"异步数据库连接失败: {e}")
        return False
