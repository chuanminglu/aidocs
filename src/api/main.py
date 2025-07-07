"""
FastAPI 主应用入口
AI文档管理系统后端API
"""
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from config.settings import Settings
from src.core.database import init_async_db, test_async_db_connection
from src.api.routers import documents, categories, tags, templates, search


# 获取配置
settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("正在启动AI文档管理系统...")
    
    # 测试数据库连接
    if await test_async_db_connection():
        print("数据库连接成功")
    else:
        print("数据库连接失败")
        raise Exception("数据库连接失败")
    
    # 初始化数据库
    try:
        await init_async_db()
        print("数据库初始化成功")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        raise
    
    print("API服务器启动完成")
    yield
    
    # 关闭时执行
    print("正在关闭AI文档管理系统...")

# 创建FastAPI应用
app = FastAPI(
    title="AI文档管理系统",
    description="智能化个人文档管理平台 - 支持双维度索引、全文检索、标签管理、知识图谱等功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.debug else "服务器内部错误",
            "detail": None
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "message": exc.detail,
            "detail": None
        }
    )

# 根路由
@app.get("/", tags=["根路由"])
async def root():
    """API根路由"""
    return {
        "message": "AI文档管理系统API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# 健康检查
@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    db_status = await test_async_db_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "version": "1.0.0"
    }

# 注册路由
app.include_router(documents.router, prefix="/api/v1/documents", tags=["文档管理"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["分类管理"])
app.include_router(tags.router, prefix="/api/v1/tags", tags=["标签管理"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["模板管理"])
app.include_router(search.router, prefix="/api/v1/search", tags=["搜索功能"])

# 开发服务器
if __name__ == "__main__":
    print("启动开发服务器...")
    print(f"API文档地址: http://localhost:{settings.api_port}/docs")
    print(f"数据库: {settings.database_url}")
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )
