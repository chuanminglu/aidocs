"""
文档模板管理系统核心模块
实现模板的创建、编辑、管理功能
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class TemplateMetadata:
    """模板元数据"""
    id: str
    name: str
    description: str
    category: str
    subcategory: str
    tags: List[str]
    author: str
    version: str
    created_at: str
    updated_at: str
    usage_count: int
    rating: float
    file_path: str
    variables: List[Dict[str, str]]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateMetadata':
        """从字典创建"""
        return cls(**data)


class TemplateVariable:
    """模板变量基类"""
    
    def __init__(self, name: str, var_type: str, default: str = "", description: str = ""):
        self.name = name
        self.type = var_type
        self.default = default
        self.description = description
    
    def render(self, context: Dict[str, Any]) -> str:
        """渲染变量"""
        return context.get(self.name, self.default)


class DateVariable(TemplateVariable):
    """日期变量"""
    FORMATS = {
        'date': '%Y-%m-%d',
        'datetime': '%Y-%m-%d %H:%M:%S',
        'time': '%H:%M:%S',
        'chinese_date': '%Y年%m月%d日',
        'week': '第%W周',
        'month': '%Y年%m月'
    }
    
    def render(self, context: Dict[str, Any]) -> str:
        """渲染日期变量"""
        if self.default == 'today':
            return datetime.now().strftime(self.FORMATS.get('date', '%Y-%m-%d'))
        elif self.default == 'now':
            return datetime.now().strftime(self.FORMATS.get('datetime', '%Y-%m-%d %H:%M:%S'))
        elif self.default == 'date':
            return datetime.now().strftime('%Y-%m-%d')
        return context.get(self.name, self.default)


class StringVariable(TemplateVariable):
    """文本变量"""
    
    def render(self, context: Dict[str, Any]) -> str:
        """渲染文本变量"""
        if self.default == 'current_user':
            return context.get('user_name', '未知用户')
        return context.get(self.name, self.default)


class SelectVariable(TemplateVariable):
    """选择变量"""
    
    def __init__(self, name: str, options: List[str], default: str = "", description: str = ""):
        super().__init__(name, 'select', default, description)
        self.options = options
    
    def render(self, context: Dict[str, Any]) -> str:
        """渲染选择变量"""
        value = context.get(self.name, self.default)
        return value if value in self.options else self.default


class TemplateEngine:
    """模板渲染引擎"""
    
    def __init__(self):
        self.variables = {}
        self.functions = {}
    
    def register_variable(self, variable: TemplateVariable):
        """注册模板变量"""
        self.variables[variable.name] = variable
    
    def register_function(self, name: str, func: Callable):
        """注册模板函数"""
        self.functions[name] = func
    
    def render(self, template_content: str, context: Dict[str, Any]) -> str:
        """渲染模板"""
        import re
        
        # 处理变量替换 {variable}
        def replace_variable(match):
            var_name = match.group(1)
            if var_name in self.variables:
                return self.variables[var_name].render(context)
            return context.get(var_name, match.group(0))
        
        # 替换 {variable} 格式的变量
        result = re.sub(r'\{(\w+)\}', replace_variable, template_content)
        
        # 处理函数调用 {{function(args)}}
        def replace_function(match):
            func_call = match.group(1)
            if '(' in func_call:
                func_name = func_call.split('(')[0]
                if func_name in self.functions:
                    try:
                        return str(self.functions[func_name]())
                    except:
                        return match.group(0)
            return match.group(0)
        
        result = re.sub(r'\{\{([^}]+)\}\}', replace_function, result)
        
        return result
    
    def extract_variables(self, template_content: str) -> List[str]:
        """提取模板中的变量"""
        import re
        variables = set()
        
        # 查找 {variable} 格式的变量
        matches = re.findall(r'\{(\w+)\}', template_content)
        variables.update(matches)
        
        # 查找 {{function()}} 格式的函数调用
        func_matches = re.findall(r'\{\{(\w+)\(\)\}\}', template_content)
        variables.update(func_matches)
        
        return list(variables)


class TemplateManager:
    """模板管理器"""
    
    def __init__(self, templates_dir: Union[str, Path]):
        self.templates_dir = Path(templates_dir)
        self.metadata_file = self.templates_dir / "metadata.json"
        self.engine = TemplateEngine()
        self.templates = {}
        self.load_templates()
    
    def load_templates(self):
        """加载模板"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
            except Exception as e:
                print(f"加载模板元数据失败: {e}")
                self.templates = {}
        else:
            self.templates = {}
    
    def save_templates(self):
        """保存模板元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存模板元数据失败: {e}")
            return False
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """列出所有模板"""
        return list(self.templates.values())
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """获取模板"""
        if template_id not in self.templates:
            return None
        
        metadata = self.templates[template_id]
        template_file = self.templates_dir / metadata['file_path']
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'metadata': metadata,
                'content': content
            }
        except Exception as e:
            print(f"读取模板文件失败: {e}")
            return None
    
    def create_template(self, name: str, content: str, category: str = "自定义", 
                       description: str = "", tags: Optional[List[str]] = None) -> Optional[str]:
        """创建新模板"""
        if tags is None:
            tags = []
        
        # 生成模板ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        template_id = f"template_{name.replace(' ', '_').lower()}_{timestamp}"
        
        # 创建目录
        category_dir = self.templates_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # 文件路径
        template_file = category_dir / f"{name}.md"
        
        try:
            # 保存模板内容
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 提取变量
            variables = self.extract_template_variables(content)
            
            # 创建元数据
            metadata = {
                'id': template_id,
                'name': name,
                'description': description,
                'category': category,
                'subcategory': category,
                'tags': tags,
                'author': 'user',
                'version': '1.0.0',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'usage_count': 0,
                'rating': 0.0,
                'file_path': str(template_file.relative_to(self.templates_dir)),
                'variables': variables
            }
            
            # 保存元数据
            self.templates[template_id] = metadata
            if self.save_templates():
                return template_id
            return None
            
        except Exception as e:
            print(f"创建模板失败: {e}")
            return None
    
    def update_template(self, template_id: str, content: Optional[str] = None, 
                       metadata_updates: Optional[Dict[str, Any]] = None) -> bool:
        """更新模板"""
        if template_id not in self.templates:
            return False
        
        metadata = self.templates[template_id]
        
        try:
            # 更新内容
            if content is not None:
                template_file = self.templates_dir / metadata['file_path']
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # 更新变量
                variables = self.extract_template_variables(content)
                metadata['variables'] = variables
            
            # 更新元数据
            if metadata_updates:
                metadata.update(metadata_updates)
                metadata['updated_at'] = datetime.now().isoformat()
            
            return self.save_templates()
            
        except Exception as e:
            print(f"更新模板失败: {e}")
            return False
    
    def delete_template(self, template_id: str) -> bool:
        """删除模板"""
        if template_id not in self.templates:
            return False
        
        try:
            # 删除模板文件
            metadata = self.templates[template_id]
            template_file = self.templates_dir / metadata['file_path']
            if template_file.exists():
                template_file.unlink()
            
            # 删除元数据
            del self.templates[template_id]
            return self.save_templates()
            
        except Exception as e:
            print(f"删除模板失败: {e}")
            return False
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        categories = set()
        for template in self.templates.values():
            categories.add(template['category'])
        return sorted(list(categories))
    
    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """搜索模板"""
        results = []
        query_lower = query.lower()
        
        for template in self.templates.values():
            if (query_lower in template['name'].lower() or
                query_lower in template['description'].lower() or
                any(query_lower in tag.lower() for tag in template['tags'])):
                results.append(template)
        
        return results
    
    def render_template(self, template_id: str, context: Dict[str, Any]) -> Optional[str]:
        """渲染模板"""
        template_data = self.get_template(template_id)
        if not template_data:
            return None
        
        try:
            # 增加使用次数
            self.templates[template_id]['usage_count'] += 1
            self.save_templates()
            
            # 渲染模板
            return self.engine.render(template_data['content'], context)
        except Exception as e:
            print(f"渲染模板失败: {e}")
            return None
    
    def import_template(self, file_path: Path) -> Optional[str]:
        """导入模板"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            name = file_path.stem
            return self.create_template(name, content, "导入", f"从 {file_path.name} 导入")
            
        except Exception as e:
            print(f"导入模板失败: {e}")
            return None
    
    def export_template(self, template_id: str, export_path: Path) -> bool:
        """导出模板"""
        template_data = self.get_template(template_id)
        if not template_data:
            return False
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(template_data['content'])
            return True
        except Exception as e:
            print(f"导出模板失败: {e}")
            return False
    
    def extract_template_variables(self, content: str) -> List[Dict[str, str]]:
        """提取模板变量"""
        import re
        variables = []
        
        # 查找 {variable} 格式的变量
        matches = re.findall(r'\{(\w+)\}', content)
        
        for var_name in set(matches):
            # 尝试推断变量类型
            var_type = 'text'
            if 'date' in var_name.lower():
                var_type = 'date'
            elif any(keyword in var_name.lower() for keyword in ['status', 'priority', 'mood']):
                var_type = 'select'
            
            variables.append({
                'name': var_name,
                'type': var_type,
                'default': '',
                'description': f'变量 {var_name}'
            })
        
        return variables
    
    def get_template_statistics(self) -> Dict[str, Any]:
        """获取模板统计信息"""
        total_templates = len(self.templates)
        categories = self.get_categories()
        
        category_counts = {}
        for category in categories:
            category_counts[category] = sum(1 for t in self.templates.values() 
                                          if t['category'] == category)
        
        return {
            'total_templates': total_templates,
            'categories': categories,
            'category_counts': category_counts,
            'most_used': sorted(self.templates.values(), 
                              key=lambda x: x['usage_count'], reverse=True)[:5]
        }
