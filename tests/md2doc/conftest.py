"""
测试配置文件

提供测试所需的配置和工具函数
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

# 测试配置
TEST_CONFIG = {
    "document": {
        "font_name": "微软雅黑",
        "font_size": 12,
        "line_spacing": 1.15,
        "margin": {
            "top": 1.0,
            "bottom": 1.0, 
            "left": 1.0,
            "right": 1.0
        }
    },
    "debug": {
        "show_chart_code": True
    }
}

@pytest.fixture(scope="session")
def test_data_dir():
    """测试数据目录"""
    return Path(__file__).parent / "data"

@pytest.fixture(scope="session") 
def temp_dir():
    """临时目录"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def sample_markdown():
    """示例Markdown内容"""
    return """# 测试文档

这是一个测试文档。

## 二级标题

测试段落内容，包含**粗体**和*斜体*文本。

### 列表测试

- 项目1
- 项目2
  - 子项目1
  - 子项目2

### 代码测试

```python
def hello():
    print("Hello, World!")
```

### 表格测试

| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 数据1 | 数据2 | 数据3 |
| A | B | C |
"""

@pytest.fixture
def complex_markdown():
    """复杂Markdown内容"""
    return """# 复杂测试文档

## 1. 文本格式

支持**粗体**、*斜体*、`行内代码`和~~删除线~~。

## 2. 多级标题

### 2.1 三级标题
#### 2.1.1 四级标题
##### 2.1.1.1 五级标题
###### 2.1.1.1.1 六级标题

## 3. 列表功能

### 3.1 有序列表
1. 第一项
   1. 子项目
   2. 另一个子项目
2. 第二项

### 3.2 无序列表
- 项目A
  - 子项目1
    - 深层项目
- 项目B

## 4. 代码块

```python
# Python代码示例
class TestClass:
    def __init__(self):
        self.value = "test"
    
    def method(self):
        return self.value
```

```javascript
// JavaScript代码示例
function test() {
    console.log("测试");
}
```

## 5. 表格

| 功能 | 状态 | 备注 |
|------|------|------|
| 解析 | ✅ | 完成 |
| 生成 | ✅ | 完成 |
| 测试 | 🚧 | 进行中 |

## 6. 图表占位符

```mermaid
graph TD
    A[开始] --> B[处理]
    B --> C[结束]
```

```plantuml
@startuml
class Test {
    +method()
}
@enduml
```
"""

@pytest.fixture
def test_config():
    """测试用配置"""
    return TEST_CONFIG.copy()
