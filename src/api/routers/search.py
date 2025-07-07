"""
搜索功能路由
处理文档搜索和索引
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from typing import List
from datetime import datetime, timezone

from src.core.database import get_async_db
from src.api.models.models import Document, Tag, Category
from src.api.schemas.schemas import SearchQuery, SearchResult, DocumentResponse

router = APIRouter()

@router.post("/", response_model=SearchResult)
async def search_documents(
    search_query: SearchQuery,
    db: AsyncSession = Depends(get_async_db)
):
    """搜索文档"""
    query = select(Document).where(Document.is_active.is_(True))
    
    # 添加搜索条件
    if search_query.query:
        search_term = f"%{search_query.query}%"
        query = query.where(
            or_(
                Document.title.ilike(search_term),
                Document.content.ilike(search_term)
            )
        )
    
    # 添加过滤条件
    if search_query.category_id:
        query = query.where(Document.category_id == search_query.category_id)
    
    if search_query.tag_ids:
        query = query.join(Document.tags).where(Tag.id.in_(search_query.tag_ids))
    
    if search_query.year:
        query = query.where(Document.year == search_query.year)
    
    if search_query.month:
        query = query.where(Document.month == search_query.month)
    
    if search_query.day:
        query = query.where(Document.day == search_query.day)
    
    if search_query.file_type:
        query = query.where(Document.file_type == search_query.file_type)
    
    if search_query.is_favorite is not None:
        query = query.where(Document.is_favorite == search_query.is_favorite)
    
    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页和排序
    query = query.order_by(Document.updated_at.desc())
    query = query.offset(search_query.offset).limit(search_query.limit)
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return SearchResult(
        total=total,
        results=[DocumentResponse.model_validate(doc) for doc in documents],
        facets={}
    )

@router.get("/quick")
async def quick_search(
    q: str = Query(..., min_length=1, max_length=100, description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50, description="返回结果数量"),
    db: AsyncSession = Depends(get_async_db)
):
    """快速搜索"""
    search_term = f"%{q}%"
    query = select(Document).where(
        and_(
            Document.is_active.is_(True),
            or_(
                Document.title.ilike(search_term),
                Document.content.ilike(search_term)
            )
        )
    ).order_by(Document.updated_at.desc()).limit(limit)
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return {
        "query": q,
        "results": [
            {
                "id": doc.id,
                "title": doc.title,
                "file_path": doc.file_path,
                "updated_at": doc.updated_at.isoformat() if doc.updated_at else None
            }
            for doc in documents
        ]
    }

@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, max_length=50, description="搜索前缀"),
    limit: int = Query(5, ge=1, le=20, description="建议数量"),
    db: AsyncSession = Depends(get_async_db)
):
    """获取搜索建议"""
    search_term = f"{q}%"
    
    # 从文档标题中获取建议
    title_query = select(Document.title).where(
        and_(
            Document.is_active.is_(True),
            Document.title.ilike(search_term)
        )
    ).limit(limit)
    
    title_result = await db.execute(title_query)
    titles = title_result.scalars().all()
    
    # 从标签中获取建议
    tag_query = select(Tag.name).where(
        and_(
            Tag.is_active.is_(True),
            Tag.name.ilike(search_term)
        )
    ).limit(limit)
    
    tag_result = await db.execute(tag_query)
    tags = tag_result.scalars().all()
    
    # 从分类中获取建议
    category_query = select(Category.name).where(
        and_(
            Category.is_active.is_(True),
            Category.name.ilike(search_term)
        )
    ).limit(limit)
    
    category_result = await db.execute(category_query)
    categories = category_result.scalars().all()
    
    return {
        "query": q,
        "suggestions": {
            "titles": list(titles),
            "tags": list(tags),
            "categories": list(categories)
        }
    }
