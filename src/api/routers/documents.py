"""
文档管理路由
处理文档的CRUD操作
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import os
from datetime import datetime

from src.core.database import get_async_db
from src.api.models.models import Document, Category, Tag
from src.api.schemas.schemas import (
    DocumentCreate, DocumentUpdate, DocumentResponse, SearchQuery, SearchResult
)

router = APIRouter()

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    tag_id: Optional[int] = Query(None, description="标签ID"),
    year: Optional[int] = Query(None, ge=1970, le=2100, description="年份"),
    month: Optional[int] = Query(None, ge=1, le=12, description="月份"),
    is_favorite: Optional[bool] = Query(None, description="是否收藏"),
    db: AsyncSession = Depends(get_async_db)
):
    """获取文档列表"""
    query = select(Document).where(Document.is_active == True)
    
    # 应用过滤条件
    if category_id:
        query = query.where(Document.category_id == category_id)
    if tag_id:
        query = query.join(Document.tags).where(Tag.id == tag_id)
    if year:
        query = query.where(Document.year == year)
    if month:
        query = query.where(Document.month == month)
    if is_favorite is not None:
        query = query.where(Document.is_favorite == is_favorite)
    
    # 排序和分页
    query = query.order_by(Document.updated_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return [DocumentResponse.model_validate(doc) for doc in documents]

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """获取单个文档"""
    query = select(Document).where(
        and_(Document.id == document_id, Document.is_active == True)
    )
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文档ID {document_id} 不存在"
        )
    
    return DocumentResponse.model_validate(document)

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """创建新文档"""
    # 检查文件路径是否已存在
    query = select(Document).where(Document.file_path == document_data.file_path)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件路径 {document_data.file_path} 已存在"
        )
    
    # 创建文档
    document = Document(
        title=document_data.title,
        content=document_data.content,
        file_path=document_data.file_path,
        file_type=document_data.file_type,
        year=document_data.year,
        month=document_data.month,
        day=document_data.day,
        is_active=document_data.is_active,
        is_favorite=document_data.is_favorite,
        category_id=document_data.category_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # 处理标签关联
    if document_data.tag_ids:
        tag_query = select(Tag).where(Tag.id.in_(document_data.tag_ids))
        tag_result = await db.execute(tag_query)
        tags = tag_result.scalars().all()
        document.tags.extend(tags)
    
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    return DocumentResponse.model_validate(document)

@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """更新文档"""
    # 获取文档
    query = select(Document).where(
        and_(Document.id == document_id, Document.is_active == True)
    )
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文档ID {document_id} 不存在"
        )
    
    # 更新字段
    update_data = document_data.model_dump(exclude_unset=True)
    tag_ids = update_data.pop('tag_ids', None)
    template_ids = update_data.pop('template_ids', None)
    
    for field, value in update_data.items():
        setattr(document, field, value)
    
    document.updated_at = datetime.utcnow()
    
    # 处理标签关联
    if tag_ids is not None:
        tag_query = select(Tag).where(Tag.id.in_(tag_ids))
        tag_result = await db.execute(tag_query)
        tags = tag_result.scalars().all()
        document.tags.clear()
        document.tags.extend(tags)
    
    await db.commit()
    await db.refresh(document)
    
    return DocumentResponse.model_validate(document)

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    permanent: bool = Query(False, description="是否永久删除"),
    db: AsyncSession = Depends(get_async_db)
):
    """删除文档"""
    query = select(Document).where(Document.id == document_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文档ID {document_id} 不存在"
        )
    
    if permanent:
        # 永久删除
        await db.delete(document)
    else:
        # 软删除
        document.is_active = False
        document.updated_at = datetime.utcnow()
    
    await db.commit()

@router.get("/{document_id}/content")
async def get_document_content(
    document_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """获取文档内容"""
    query = select(Document).where(
        and_(Document.id == document_id, Document.is_active == True)
    )
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文档ID {document_id} 不存在"
        )
    
    # 尝试读取文件内容
    try:
        if os.path.exists(document.file_path):
            with open(document.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"content": content, "from_file": True}
        else:
            return {"content": document.content or "", "from_file": False}
    except Exception as e:
        return {"content": document.content or "", "from_file": False, "error": str(e)}

@router.post("/{document_id}/favorite")
async def toggle_favorite(
    document_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """切换文档收藏状态"""
    query = select(Document).where(
        and_(Document.id == document_id, Document.is_active == True)
    )
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文档ID {document_id} 不存在"
        )
    
    document.is_favorite = not document.is_favorite
    document.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(document)
    
    return {
        "document_id": document_id,
        "is_favorite": document.is_favorite,
        "message": "已收藏" if document.is_favorite else "已取消收藏"
    }

@router.get("/statistics/summary")
async def get_document_statistics(
    db: AsyncSession = Depends(get_async_db)
):
    """获取文档统计信息"""
    # 总文档数
    total_query = select(func.count(Document.id)).where(Document.is_active == True)
    total_result = await db.execute(total_query)
    total_documents = total_result.scalar()
    
    # 收藏文档数
    favorite_query = select(func.count(Document.id)).where(
        and_(Document.is_active == True, Document.is_favorite == True)
    )
    favorite_result = await db.execute(favorite_query)
    favorite_documents = favorite_result.scalar()
    
    # 按月份统计
    monthly_query = select(
        Document.year,
        Document.month,
        func.count(Document.id).label('count')
    ).where(Document.is_active == True).group_by(Document.year, Document.month)
    monthly_result = await db.execute(monthly_query)
    monthly_stats = monthly_result.all()
    
    # 按分类统计
    category_query = select(
        Category.name,
        func.count(Document.id).label('count')
    ).join(Document.category).where(Document.is_active == True).group_by(Category.name)
    category_result = await db.execute(category_query)
    category_stats = category_result.all()
    
    return {
        "total_documents": total_documents,
        "favorite_documents": favorite_documents,
        "monthly_stats": [
            {"year": row.year, "month": row.month, "count": row.count}
            for row in monthly_stats
        ],
        "category_stats": [
            {"category": row.name, "count": row.count}
            for row in category_stats
        ]
    }
