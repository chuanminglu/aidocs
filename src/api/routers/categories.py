"""
分类管理路由
处理分类的CRUD操作
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime, timezone

from src.core.database import get_async_db
from src.api.models.models import Category
from src.api.schemas.schemas import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=500, description="返回的记录数"),
    parent_id: Optional[int] = Query(None, description="父分类ID"),
    is_active: bool = Query(True, description="是否激活"),
    db: AsyncSession = Depends(get_async_db)
):
    """获取分类列表"""
    query = select(Category).where(Category.is_active == is_active)
    
    if parent_id is not None:
        query = query.where(Category.parent_id == parent_id)
    
    query = query.order_by(Category.sort_order, Category.name).offset(skip).limit(limit)
    
    result = await db.execute(query)
    categories = result.scalars().all()
    
    return [CategoryResponse.model_validate(cat) for cat in categories]

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """获取单个分类"""
    query = select(Category).where(Category.id == category_id)
    result = await db.execute(query)
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类ID {category_id} 不存在"
        )
    
    return CategoryResponse.model_validate(category)

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """创建新分类"""
    # 检查名称是否已存在
    query = select(Category).where(Category.name == category_data.name)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"分类名称 '{category_data.name}' 已存在"
        )
    
    # 创建分类
    category = Category(
        name=category_data.name,
        description=category_data.description,
        color=category_data.color,
        parent_id=category_data.parent_id,
        level=category_data.level,
        sort_order=category_data.sort_order,
        is_active=category_data.is_active,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    return CategoryResponse.model_validate(category)

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """更新分类"""
    query = select(Category).where(Category.id == category_id)
    result = await db.execute(query)
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类ID {category_id} 不存在"
        )
    
    # 更新字段
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    await db.commit()
    await db.refresh(category)
    
    return CategoryResponse.model_validate(category)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """删除分类"""
    query = select(Category).where(Category.id == category_id)
    result = await db.execute(query)
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类ID {category_id} 不存在"
        )
    
    # 软删除
    category.is_active = False
    await db.commit()

@router.get("/tree/all", response_model=List[CategoryResponse])
async def get_category_tree(
    db: AsyncSession = Depends(get_async_db)
):
    """获取分类树"""
    query = select(Category).where(Category.is_active.is_(True)).order_by(Category.level, Category.sort_order)
    result = await db.execute(query)
    categories = result.scalars().all()
    
    # 构建树结构
    category_dict = {cat.id: CategoryResponse.model_validate(cat) for cat in categories}
    tree = []
    
    for cat in categories:
        cat_response = category_dict[cat.id]
        if cat.parent_id is None:
            tree.append(cat_response)
        else:
            parent = category_dict.get(cat.parent_id)
            if parent:
                parent.children.append(cat_response)
    
    return tree
