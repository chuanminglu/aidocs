"""
数据模型定义
FastAPI + SQLAlchemy 2.0 版本
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional
from src.core.database import Base

# 多对多关系表：文档-标签
document_tags = Table(
    'document_tags',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

# 多对多关系表：文档-模板
document_templates = Table(
    'document_templates',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id'), primary_key=True),
    Column('template_id', Integer, ForeignKey('templates.id'), primary_key=True)
)

class Document(Base):
    """文档模型"""
    __tablename__ = 'documents'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), default='markdown')
    
    # 时间字段
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # 时间维度索引
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # 状态字段
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 外键关系
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('categories.id'), nullable=True)
    
    # 关系映射
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="documents")
    tags: Mapped[List["Tag"]] = relationship("Tag", secondary=document_tags, back_populates="documents")
    templates: Mapped[List["Template"]] = relationship("Template", secondary=document_templates, back_populates="documents")
    search_indices: Mapped[List["SearchIndex"]] = relationship("SearchIndex", back_populates="document")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'year': self.year,
            'month': self.month,
            'day': self.day,
            'is_active': self.is_active,
            'is_favorite': self.is_favorite,
            'category': self.category.to_dict() if self.category else None,
            'tags': [tag.to_dict() for tag in self.tags],
            'templates': [template.to_dict() for template in self.templates]
        }

class Category(Base):
    """分类模型"""
    __tablename__ = 'categories'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    color: Mapped[str] = mapped_column(String(7), default='#007bff')  # 十六进制颜色
    
    # 层级关系
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('categories.id'), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # 状态字段
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # 关系映射
    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side=[id], back_populates="children")
    children: Mapped[List["Category"]] = relationship("Category", back_populates="parent")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'parent_id': self.parent_id,
            'level': self.level,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'children': [child.to_dict() for child in self.children] if self.children else [],
            'document_count': len(self.documents) if self.documents else 0
        }

class Tag(Base):
    """标签模型"""
    __tablename__ = 'tags'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    color: Mapped[str] = mapped_column(String(7), default='#28a745')  # 十六进制颜色
    
    # 统计字段
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # 状态字段
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # 关系映射
    documents: Mapped[List["Document"]] = relationship("Document", secondary=document_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'usage_count': self.usage_count,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'document_count': len(self.documents) if self.documents else 0
        }

class Template(Base):
    """模板模型"""
    __tablename__ = 'templates'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # 模板类型和分类
    template_type: Mapped[str] = mapped_column(String(50), default='markdown')
    category: Mapped[str] = mapped_column(String(100), default='general')
    
    # 使用统计
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # 状态字段
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)  # 系统模板
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关系映射
    documents: Mapped[List["Document"]] = relationship("Document", secondary=document_templates, back_populates="templates")
    
    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'content': self.content,
            'file_path': self.file_path,
            'template_type': self.template_type,
            'category': self.category,
            'usage_count': self.usage_count,
            'is_active': self.is_active,
            'is_system': self.is_system,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'document_count': len(self.documents) if self.documents else 0
        }

class SearchIndex(Base):
    """搜索索引模型"""
    __tablename__ = 'search_indices'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey('documents.id'), nullable=False)
    
    # 索引内容
    title_index: Mapped[str] = mapped_column(Text, nullable=False)
    content_index: Mapped[str] = mapped_column(Text, nullable=False)
    keywords: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    # 向量索引（为AI功能预留）
    embedding: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 索引状态
    is_indexed: Mapped[bool] = mapped_column(Boolean, default=False)
    indexed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 关系映射
    document: Mapped["Document"] = relationship("Document", back_populates="search_indices")
    
    def __repr__(self):
        return f"<SearchIndex(id={self.id}, document_id={self.document_id})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'title_index': self.title_index,
            'content_index': self.content_index,
            'keywords': self.keywords,
            'embedding': self.embedding,
            'is_indexed': self.is_indexed,
            'indexed_at': self.indexed_at.isoformat() if self.indexed_at else None
        }

class KnowledgeGraph(Base):
    """知识图谱模型"""
    __tablename__ = 'knowledge_graphs'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 节点信息
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey('documents.id'), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, ForeignKey('documents.id'), nullable=False)
    
    # 关系类型
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 引用、相关、继承等
    relation_strength: Mapped[float] = mapped_column(default=1.0)  # 关系强度
    
    # 关系描述
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # 状态字段
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<KnowledgeGraph(id={self.id}, {self.source_id}->{self.target_id})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_id': self.source_id,
            'target_id': self.target_id,
            'relation_type': self.relation_type,
            'relation_strength': self.relation_strength,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
