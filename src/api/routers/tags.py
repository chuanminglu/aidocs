"""
标签管理路由
处理标签的CRUD操作
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timezone

from src.core.database import get_async_db
from src.api.models.models import Tag
from src.api.schemas.schemas import TagCreate, TagUpdate, TagResponse

router = APIRouter()

@router.get("/", response_model=List[TagResponse])
async def list_tags(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=500, description="返回的记录数"),
    is_active: bool = Query(True, description="是否激活"),
    db: AsyncSession = Depends(get_async_db)
):
    """获取标签列表"""
    query = select(Tag).where(Tag.is_active == is_active)
    query = query.order_by(Tag.usage_count.desc(), Tag.name).offset(skip).limit(limit)
    
    result = await db.execute(query)
    tags = result.scalars().all()
    
    return [TagResponse.model_validate(tag) for tag in tags]

@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """获取单个标签"""
    query = select(Tag).where(Tag.id == tag_id)
    result = await db.execute(query)
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标签ID {tag_id} 不存在"
        )
    
    return TagResponse.model_validate(tag)

@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """创建新标签"""
    # 检查名称是否已存在
    query = select(Tag).where(Tag.name == tag_data.name)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"标签名称 '{tag_data.name}' 已存在"
        )
    
    # 创建标签
    tag = Tag(
        name=tag_data.name,
        description=tag_data.description,
        color=tag_data.color,
        is_active=tag_data.is_active,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    
    return TagResponse.model_validate(tag)

@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """更新标签"""
    query = select(Tag).where(Tag.id == tag_id)
    result = await db.execute(query)
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标签ID {tag_id} 不存在"
        )
    
    # 更新字段
    update_data = tag_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)
    
    await db.commit()
    await db.refresh(tag)
    
    return TagResponse.model_validate(tag)

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """删除标签"""
    query = select(Tag).where(Tag.id == tag_id)
    result = await db.execute(query)
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标签ID {tag_id} 不存在"
        )
    
    # 软删除
    tag.is_active = False
    await db.commit()

@router.get("/popular/top", response_model=List[TagResponse])
async def get_popular_tags(
    limit: int = Query(10, ge=1, le=50, description="返回的标签数量"),
    db: AsyncSession = Depends(get_async_db)
):
    """获取热门标签"""
    query = select(Tag).where(Tag.is_active.is_(True)).order_by(Tag.usage_count.desc()).limit(limit)
    result = await db.execute(query)
    tags = result.scalars().all()
    
    return [TagResponse.model_validate(tag) for tag in tags]
