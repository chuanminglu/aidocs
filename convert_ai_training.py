#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将AI培训三天课程脉络图转换为Word文档
"""

import logging
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def convert_ai_training_doc():
    """将AI培训课程文档转换为Word格式"""
    print("=== AI培训三天课程脉络图 MD转DOCX ===\n")
    
    try:
        from src.md2doc.core.format_converter import FormatConverter
        print("✅ 模块导入成功")
        
        # 读取markdown文件
        md_file = Path("AI培训三天课程脉络图.md")
        
        if not md_file.exists():
            print(f"❌ 文件不存在: {md_file}")
            return
            
        with open(md_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        print(f"📄 读取Markdown文件: {len(markdown_content)} 字符")
        print(f"📊 检测到 {markdown_content.count('```plantuml')} 个PlantUML图表")
        
        # 创建转换器
        converter = FormatConverter()
        print("✅ 转换器创建成功")
        
        # 执行转换
        print("🔄 开始转换...")
        converter.convert_markdown_to_word(markdown_content)
        print("✅ 内容转换完成")
        
        # 保存文档
        import time
        timestamp = int(time.time())
        output_file = f"AI培训三天课程脉络图_{timestamp}.docx"
        converter.save_document(output_file)
        print(f"✅ 文档保存完成: {output_file}")
        
        # 检查文件大小
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"📄 文件大小: {file_size:,} 字节 ({file_size/1024:.1f}KB)")
            
            if file_size > 100000:  # 100KB以上说明包含多个图表
                print("✅ 文件大小正常，包含多个渲染的图表")
            elif file_size > 50000:  # 50KB以上
                print("✅ 文件大小正常，包含渲染的图表")
            else:
                print("⚠️ 文件较小，部分图表可能未成功渲染")
        
        print("\n=== 转换完成 ===")
        print(f"📋 生成的文件: {output_file}")
        print("🔍 文档包含内容:")
        print("  1. 完整的课程概述")
        print("  2. 整体课程架构图")
        print("  3. 详细学习路径")
        print("  4. 三天课程流程图")
        print("  5. 技术栈掌握路径")
        print("  6. 课程特色和预期收获")
        print("\n📝 验证要点:")
        print("  ✓ 字体显示为微软雅黑")
        print("  ✓ 所有PlantUML图表正常显示")
        print("  ✓ 图表尺寸按1:1比例显示")
        print("  ✓ 表格格式美观规整")
        print("  ✓ 整体文档布局专业")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    convert_ai_training_doc()
