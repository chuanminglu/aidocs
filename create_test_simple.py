"""
生成完整的转换测试文档

创建一个包含所有支持元素的综合测试文档，
验证转换器的完整功能。
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

try:
    from md2doc import MD2DocConverter, ConfigManager
    print("✓ 模块导入成功")
except ImportError as e:
    print(f"✗ 模块导入失败: {e}")
    sys.exit(1)


def create_comprehensive_test():
    """创建全面的测试文档"""
    
    print("=== 创建综合测试文档 ===\n")
    
    # 从文件读取测试内容，避免复杂的字符串转义
    test_content_file = project_root / "comprehensive_test_content.md"
    
    # 如果文件不存在，创建一个基本的测试内容
    if not test_content_file.exists():
        with open(test_content_file, 'w', encoding='utf-8') as f:
            f.write("""# MD2DOC 功能验证测试文档

这是一个综合性的测试文档，用于验证MD2DocConverter的所有转换功能。

## 1. 基本文本格式

### 1.1 字体样式
- **粗体文本** - 重要内容强调
- *斜体文本* - 一般强调
- `行内代码` - 代码片段

### 1.2 段落测试
这是第一个段落。包含普通文本内容，用于测试基本的段落渲染。

这是第二个段落，测试段落间距。

## 2. 标题层级测试

### 2.1 三级标题
#### 2.1.1 四级标题
##### 2.1.1.1 五级标题
###### 2.1.1.1.1 六级标题

## 3. 列表功能

### 3.1 无序列表
- 第一级项目
  - 第二级项目
    - 第三级项目
- 另一个第一级项目
- 最后一个项目

### 3.2 有序列表
1. 第一项
   1. 子项目1
   2. 子项目2
2. 第二项
3. 第三项

## 4. 代码块测试

```python
def hello_world():
    print("Hello, MD2DOC!")
    return "完成"

result = hello_world()
```

```javascript
function calculateSum(a, b) {
    return a + b;
}

const result = calculateSum(10, 20);
console.log(result);
```

## 5. 表格功能

### 5.1 基本表格
| 功能 | 状态 | 备注 |
|------|------|------|
| 文本解析 | 完成 | 支持所有基本格式 |
| 表格转换 | 完成 | 支持复杂表格 |
| 代码块 | 完成 | 支持语法高亮 |

### 5.2 对齐表格
| 左对齐 | 居中 | 右对齐 |
|:-------|:----:|-------:|
| 数据1 | 数据2 | 数据3 |
| 长文本数据 | 短文本 | 999 |

## 6. 链接测试

- [文本链接](https://www.example.com)
- [带标题的链接](https://www.example.com "这是链接标题")

## 7. 图表代码块占位符

```mermaid
graph TD
    A[开始] --> B{是否成功?}
    B -->|是| C[继续处理]
    B -->|否| D[错误处理]
```

## 8. 转换统计信息

本文档包含了MD2DOC支持的主要Markdown元素：
- 标题 (1-6级)
- 段落和文本格式
- 列表 (有序/无序/嵌套)
- 代码块 (带语法标识)
- 表格 (基本/对齐)
- 链接

---

**测试完成** - MD2DOC v1.0.0
""")
    
    # 读取测试内容
    with open(test_content_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 创建转换器
    config = ConfigManager()
    converter = MD2DocConverter(config)
    
    # 执行转换
    try:
        output_path = project_root / "comprehensive_test_document.docx"
        result_path = converter.convert_string(content, output_path)
        
        print(f"✅ 综合测试文档生成成功!")
        print(f"📄 输出文件: {result_path}")
        print(f"📊 文件大小: {result_path.stat().st_size:,} 字节")
        
        # 获取转换统计
        stats = converter.get_conversion_stats()
        print(f"🔍 解析元素数: {stats['elements_parsed']}")
        print(f"📈 文档统计: {stats['document_stats']}")
        
        # 显示详细解析信息
        parse_details = stats['parse_details']
        print(f"\n📋 详细解析统计:")
        for element_type, count in parse_details.items():
            if element_type != 'total_elements' and count > 0:
                print(f"   {element_type}: {count}")
        
        print(f"\n🎯 测试结果: 转换成功，包含 {stats['elements_parsed']} 个元素")
        return True
        
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        return False


if __name__ == "__main__":
    try:
        success = create_comprehensive_test()
        if success:
            print("\n🎉 综合测试文档创建成功!")
            print("📖 请打开生成的Word文档查看转换效果。")
        else:
            print("\n💥 综合测试失败!")
            sys.exit(1)
    except Exception as e:
        print(f"\n🚨 程序执行错误: {e}")
        sys.exit(1)
