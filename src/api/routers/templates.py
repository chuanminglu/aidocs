"""
模板管理路由
处理模板的CRUD操作
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timezone

from src.core.database import get_async_db
from src.api.models.models import Template
from src.api.schemas.schemas import TemplateCreate, TemplateUpdate, TemplateResponse

router = APIRouter()

@router.get("/", response_model=List[TemplateResponse])
async def list_templates(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(50, ge=1, le=200, description="返回的记录数"),
    category: str = Query(None, description="模板分类"),
    is_active: bool = Query(True, description="是否激活"),
    is_system: bool = Query(None, description="是否系统模板"),
    db: AsyncSession = Depends(get_async_db)
):
    """获取模板列表"""
    query = select(Template).where(Template.is_active == is_active)
    
    if category:
        query = query.where(Template.category == category)
    if is_system is not None:
        query = query.where(Template.is_system == is_system)
    
    query = query.order_by(Template.usage_count.desc(), Template.name).offset(skip).limit(limit)
    
    result = await db.execute(query)
    templates = result.scalars().all()
    
    return [TemplateResponse.model_validate(template) for template in templates]

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """获取单个模板"""
    query = select(Template).where(Template.id == template_id)
    result = await db.execute(query)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"模板ID {template_id} 不存在"
        )
    
    return TemplateResponse.model_validate(template)

@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """创建新模板"""
    # 检查名称是否已存在
    query = select(Template).where(Template.name == template_data.name)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"模板名称 '{template_data.name}' 已存在"
        )
    
    # 创建模板
    template = Template(
        name=template_data.name,
        description=template_data.description,
        content=template_data.content,
        file_path=template_data.file_path,
        template_type=template_data.template_type,
        category=template_data.category,
        is_active=template_data.is_active,
        is_system=template_data.is_system,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    return TemplateResponse.model_validate(template)

@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """更新模板"""
    query = select(Template).where(Template.id == template_id)
    result = await db.execute(query)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"模板ID {template_id} 不存在"
        )
    
    # 更新字段
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    template.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(template)
    
    return TemplateResponse.model_validate(template)

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """删除模板"""
    query = select(Template).where(Template.id == template_id)
    result = await db.execute(query)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"模板ID {template_id} 不存在"
        )
    
    # 软删除
    template.is_active = False
    template.updated_at = datetime.now(timezone.utc)
    await db.commit()

@router.post("/{template_id}/use")
async def use_template(
    template_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """使用模板（增加使用次数）"""
    query = select(Template).where(Template.id == template_id)
    result = await db.execute(query)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"模板ID {template_id} 不存在"
        )
    
    template.usage_count += 1
    template.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(template)
    
    return {
        "template_id": template_id,
        "usage_count": template.usage_count,
        "message": "模板使用次数已更新"
    }
