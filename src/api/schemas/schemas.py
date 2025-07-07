"""
Pydantic 数据模式定义
用于API请求和响应的数据验证
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    """文档类型枚举"""
    MARKDOWN = "markdown"
    TEXT = "text"
    HTML = "html"
    PDF = "pdf"
    WORD = "word"

class RelationType(str, Enum):
    """关系类型枚举"""
    REFERENCE = "reference"
    RELATED = "related"
    INHERIT = "inherit"
    DEPENDENCY = "dependency"

# 基础模式
class BaseSchema(BaseModel):
    """基础模式配置"""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )

# 文档模式
class DocumentBase(BaseSchema):
    """文档基础模式"""
    title: str = Field(..., min_length=1, max_length=255, description="文档标题")
    content: Optional[str] = Field(None, description="文档内容")
    file_path: str = Field(..., min_length=1, max_length=500, description="文件路径")
    file_type: DocumentType = Field(DocumentType.MARKDOWN, description="文件类型")
    year: int = Field(..., ge=1970, le=2100, description="年份")
    month: int = Field(..., ge=1, le=12, description="月份")
    day: int = Field(..., ge=1, le=31, description="日期")
    is_active: bool = Field(True, description="是否激活")
    is_favorite: bool = Field(False, description="是否收藏")
    category_id: Optional[int] = Field(None, description="分类ID")

class DocumentCreate(DocumentBase):
    """创建文档模式"""
    tag_ids: List[int] = Field([], description="标签ID列表")
    template_ids: List[int] = Field([], description="模板ID列表")

class DocumentUpdate(BaseSchema):
    """更新文档模式"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="文档标题")
    content: Optional[str] = Field(None, description="文档内容")
    file_path: Optional[str] = Field(None, min_length=1, max_length=500, description="文件路径")
    file_type: Optional[DocumentType] = Field(None, description="文件类型")
    year: Optional[int] = Field(None, ge=1970, le=2100, description="年份")
    month: Optional[int] = Field(None, ge=1, le=12, description="月份")
    day: Optional[int] = Field(None, ge=1, le=31, description="日期")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_favorite: Optional[bool] = Field(None, description="是否收藏")
    category_id: Optional[int] = Field(None, description="分类ID")
    tag_ids: Optional[List[int]] = Field(None, description="标签ID列表")
    template_ids: Optional[List[int]] = Field(None, description="模板ID列表")

class DocumentResponse(DocumentBase):
    """文档响应模式"""
    id: int
    created_at: datetime
    updated_at: datetime
    category: Optional["CategoryResponse"] = None
    tags: List["TagResponse"] = []
    templates: List["TemplateResponse"] = []

# 分类模式
class CategoryBase(BaseSchema):
    """分类基础模式"""
    name: str = Field(..., min_length=1, max_length=100, description="分类名称")
    description: Optional[str] = Field(None, max_length=255, description="分类描述")
    color: str = Field("#007bff", pattern=r"^#[0-9a-fA-F]{6}$", description="分类颜色")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    level: int = Field(0, ge=0, le=10, description="层级")
    sort_order: int = Field(0, description="排序")
    is_active: bool = Field(True, description="是否激活")

class CategoryCreate(CategoryBase):
    """创建分类模式"""
    pass

class CategoryUpdate(BaseSchema):
    """更新分类模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="分类名称")
    description: Optional[str] = Field(None, max_length=255, description="分类描述")
    color: Optional[str] = Field(None, pattern=r"^#[0-9a-fA-F]{6}$", description="分类颜色")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    level: Optional[int] = Field(None, ge=0, le=10, description="层级")
    sort_order: Optional[int] = Field(None, description="排序")
    is_active: Optional[bool] = Field(None, description="是否激活")

class CategoryResponse(CategoryBase):
    """分类响应模式"""
    id: int
    created_at: datetime
    children: List["CategoryResponse"] = []
    document_count: int = 0

# 标签模式
class TagBase(BaseSchema):
    """标签基础模式"""
    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    description: Optional[str] = Field(None, max_length=255, description="标签描述")
    color: str = Field("#28a745", pattern=r"^#[0-9a-fA-F]{6}$", description="标签颜色")
    is_active: bool = Field(True, description="是否激活")

class TagCreate(TagBase):
    """创建标签模式"""
    pass

class TagUpdate(BaseSchema):
    """更新标签模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="标签名称")
    description: Optional[str] = Field(None, max_length=255, description="标签描述")
    color: Optional[str] = Field(None, pattern=r"^#[0-9a-fA-F]{6}$", description="标签颜色")
    is_active: Optional[bool] = Field(None, description="是否激活")

class TagResponse(TagBase):
    """标签响应模式"""
    id: int
    usage_count: int = 0
    created_at: datetime
    document_count: int = 0

# 模板模式
class TemplateBase(BaseSchema):
    """模板基础模式"""
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, max_length=255, description="模板描述")
    content: str = Field(..., min_length=1, description="模板内容")
    file_path: str = Field(..., min_length=1, max_length=500, description="文件路径")
    template_type: DocumentType = Field(DocumentType.MARKDOWN, description="模板类型")
    category: str = Field("general", max_length=100, description="模板分类")
    is_active: bool = Field(True, description="是否激活")
    is_system: bool = Field(False, description="是否系统模板")

class TemplateCreate(TemplateBase):
    """创建模板模式"""
    pass

class TemplateUpdate(BaseSchema):
    """更新模板模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, max_length=255, description="模板描述")
    content: Optional[str] = Field(None, min_length=1, description="模板内容")
    file_path: Optional[str] = Field(None, min_length=1, max_length=500, description="文件路径")
    template_type: Optional[DocumentType] = Field(None, description="模板类型")
    category: Optional[str] = Field(None, max_length=100, description="模板分类")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_system: Optional[bool] = Field(None, description="是否系统模板")

class TemplateResponse(TemplateBase):
    """模板响应模式"""
    id: int
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime
    document_count: int = 0

# 搜索索引模式
class SearchIndexBase(BaseSchema):
    """搜索索引基础模式"""
    document_id: int = Field(..., description="文档ID")
    title_index: str = Field(..., description="标题索引")
    content_index: str = Field(..., description="内容索引")
    keywords: Optional[str] = Field(None, max_length=1000, description="关键词")
    embedding: Optional[str] = Field(None, description="向量嵌入")
    is_indexed: bool = Field(False, description="是否已索引")

class SearchIndexCreate(SearchIndexBase):
    """创建搜索索引模式"""
    pass

class SearchIndexUpdate(BaseSchema):
    """更新搜索索引模式"""
    title_index: Optional[str] = Field(None, description="标题索引")
    content_index: Optional[str] = Field(None, description="内容索引")
    keywords: Optional[str] = Field(None, max_length=1000, description="关键词")
    embedding: Optional[str] = Field(None, description="向量嵌入")
    is_indexed: Optional[bool] = Field(None, description="是否已索引")

class SearchIndexResponse(SearchIndexBase):
    """搜索索引响应模式"""
    id: int
    indexed_at: Optional[datetime] = None

# 知识图谱模式
class KnowledgeGraphBase(BaseSchema):
    """知识图谱基础模式"""
    source_id: int = Field(..., description="源文档ID")
    target_id: int = Field(..., description="目标文档ID")
    relation_type: RelationType = Field(..., description="关系类型")
    relation_strength: float = Field(1.0, ge=0.0, le=1.0, description="关系强度")
    description: Optional[str] = Field(None, max_length=255, description="关系描述")
    is_active: bool = Field(True, description="是否激活")

class KnowledgeGraphCreate(KnowledgeGraphBase):
    """创建知识图谱模式"""
    pass

class KnowledgeGraphUpdate(BaseSchema):
    """更新知识图谱模式"""
    relation_type: Optional[RelationType] = Field(None, description="关系类型")
    relation_strength: Optional[float] = Field(None, ge=0.0, le=1.0, description="关系强度")
    description: Optional[str] = Field(None, max_length=255, description="关系描述")
    is_active: Optional[bool] = Field(None, description="是否激活")

class KnowledgeGraphResponse(KnowledgeGraphBase):
    """知识图谱响应模式"""
    id: int
    created_at: datetime

# 搜索模式
class SearchQuery(BaseSchema):
    """搜索查询模式"""
    query: str = Field(..., min_length=1, max_length=200, description="搜索关键词")
    category_id: Optional[int] = Field(None, description="分类ID")
    tag_ids: Optional[List[int]] = Field(None, description="标签ID列表")
    year: Optional[int] = Field(None, ge=1970, le=2100, description="年份")
    month: Optional[int] = Field(None, ge=1, le=12, description="月份")
    day: Optional[int] = Field(None, ge=1, le=31, description="日期")
    file_type: Optional[DocumentType] = Field(None, description="文件类型")
    is_favorite: Optional[bool] = Field(None, description="是否收藏")
    limit: int = Field(20, ge=1, le=100, description="返回结果数量")
    offset: int = Field(0, ge=0, description="偏移量")

class SearchResult(BaseSchema):
    """搜索结果模式"""
    total: int = Field(..., description="总结果数")
    results: List[DocumentResponse] = Field(..., description="搜索结果")
    facets: Dict[str, Any] = Field({}, description="搜索分面")

# 统计模式
class StatisticsResponse(BaseSchema):
    """统计响应模式"""
    total_documents: int = 0
    total_categories: int = 0
    total_tags: int = 0
    total_templates: int = 0
    documents_by_month: Dict[str, int] = {}
    documents_by_category: Dict[str, int] = {}
    popular_tags: List[Dict[str, Any]] = []

# 更新前向引用
CategoryResponse.model_rebuild()
DocumentResponse.model_rebuild()
TagResponse.model_rebuild()
TemplateResponse.model_rebuild()
