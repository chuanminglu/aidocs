"""
主命令行入口

提供md2doc的命令行接口
"""

import argparse
from pathlib import Path
from typing import Optional


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Markdown to Word document converter",
        prog="md2doc"
    )
    
    parser.add_argument(
        "input",
        type=str,
        help="Input Markdown file path"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output Word document path"
    )
    
    parser.add_argument(
        "-t", "--template",
        type=str,
        default="standard",
        help="Document template name (default: standard)"
    )
    
    parser.add_argument(
        "-c", "--config",
        type=str,
        help="Configuration file path"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser


def main(args: Optional[list] = None) -> int:
    """主入口函数
    
    Args:
        args: 命令行参数
        
    Returns:
        退出码
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # 验证输入文件
    input_path = Path(parsed_args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1
    
    # 确定输出路径
    if parsed_args.output:
        output_path = Path(parsed_args.output)
    else:
        output_path = input_path.with_suffix('.docx')
    
    print(f"Converting {input_path} to {output_path}")
    print(f"Template: {parsed_args.template}")
    
    # TODO: 实现实际转换逻辑
    print("Conversion logic will be implemented in next phase")
    
    return 0


if __name__ == "__main__":
    exit(main())
