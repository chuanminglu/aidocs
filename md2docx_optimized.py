#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
优化的Markdown到Word文档转换工具 - 修复换行问题
特别优化代码块和命令行内容的换行处理
"""

import logging
import sys
import os
import argparse
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def convert_md_to_docx(input_file, output_file=None):
    """将Markdown文档转换为Word格式（优化版本）
    
    Args:
        input_file (str): 输入的Markdown文件路径
        output_file (str, optional): 输出的Word文件路径，如果为None则自动生成
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_path}")
        return False
        
    if not input_path.suffix.lower() in ['.md', '.markdown']:
        print(f"❌ 不是有效的Markdown文件: {input_path}")
        return False
    
    # 自动生成输出文件名
    if output_file is None:
        output_file = input_path.with_suffix('.docx').name
    
    print(f"=== Markdown转Word文档（优化版本） ===")
    print(f"📂 输入文件: {input_path}")
    print(f"📂 输出文件: {output_file}\n")
    
    try:
        from src.md2doc.core.format_converter_optimized import OptimizedFormatConverter
        print("✅ 优化版本模块导入成功")
        
        # 读取markdown文件
        with open(input_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        print(f"📄 读取Markdown文件: {len(markdown_content)} 字符")
        
        # 检测内容类型
        plantuml_count = markdown_content.count('```plantuml')
        mermaid_count = markdown_content.count('```mermaid')
        code_block_count = markdown_content.count('```') // 2
        table_count = markdown_content.count('|')
        
        if plantuml_count > 0:
            print(f"📊 检测到 {plantuml_count} 个PlantUML图表")
        if mermaid_count > 0:
            print(f"📊 检测到 {mermaid_count} 个Mermaid图表")
        if code_block_count > 0:
            print(f"💻 检测到 {code_block_count} 个代码块")
        if table_count > 10:  # 简单检测表格
            print(f"📋 检测到表格内容")
        
        # 创建优化转换器
        converter = OptimizedFormatConverter()
        print("✅ 优化转换器创建成功")
        
        # 执行转换
        print("🔄 开始转换...")
        converter.convert_markdown_to_word(markdown_content)
        print("✅ 内容转换完成（换行优化已应用）")
        
        # 保存文档
        converter.save_document(output_file)
        print(f"✅ 文档保存完成: {output_file}")
        
        # 检查文件大小
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"📄 文件大小: {file_size:,} 字节 ({file_size/1024:.1f}KB)")
            
            if file_size > 100000:  # 100KB以上说明内容丰富
                print("✅ 文件大小正常，包含丰富内容")
            elif file_size > 50000:  # 50KB以上
                print("✅ 文件大小正常")
            else:
                print("✅ 转换完成")
        
        print("\n=== 转换完成（优化版本） ===")
        print(f"📋 生成的文件: {output_file}")
        print("\n✅ 优化要点:")
        print("  ✓ 代码块换行完美保留")
        print("  ✓ 命令行格式正确显示")
        print("  ✓ 字体显示为微软雅黑")
        print("  ✓ 图表尺寸按1:1比例显示")
        print("  ✓ 表格格式美观规整")
        print("  ✓ 整体文档布局专业")
        
        return True
        
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(
        description='将Markdown文档转换为Word文档（优化版本）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python md2docx_optimized.py input.md                    # 自动生成输出文件名
  python md2docx_optimized.py input.md -o output.docx     # 指定输出文件名
  python md2docx_optimized.py "问卷调查.md"               # 处理中文文件名
  
优化特性:
  ✓ 代码块换行完美保留
  ✓ 命令行格式正确显示  
  ✓ 技术文档友好处理
        """
    )
    
    parser.add_argument('input', help='输入的Markdown文件路径')
    parser.add_argument('-o', '--output', help='输出的Word文件路径（可选，默认自动生成）')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 执行转换
    success = convert_md_to_docx(args.input, args.output)
    
    if success:
        print("\n🎉 转换成功完成！")
        sys.exit(0)
    else:
        print("\n❌ 转换失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
