#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mermaid代码清理和修复工具
"""

import re
from typing import List, Tuple

class MermaidCodeCleaner:
    """Mermaid代码清理器"""
    
    def __init__(self):
        self.logger = None
    
    def clean_and_fix(self, mermaid_code: str) -> str:
        """清理和修复Mermaid代码
        
        Args:
            mermaid_code: 原始Mermaid代码
            
        Returns:
            修复后的代码
        """
        # 1. 基本清理
        code = self._basic_cleanup(mermaid_code)
        
        # 2. 修复换行问题
        code = self._fix_line_breaks(code)
        
        # 3. 修复节点定义
        code = self._fix_node_definitions(code)
        
        # 4. 修复连接语法
        code = self._fix_connections(code)
        
        # 5. 修复样式定义
        code = self._fix_styles(code)
        
        # 6. 最终验证和清理
        code = self._final_cleanup(code)
        
        return code
    
    def _basic_cleanup(self, code: str) -> str:
        """基本清理"""
        # 移除多余的空白行
        lines = [line.rstrip() for line in code.split('\n')]
        
        # 移除空行
        non_empty_lines = [line for line in lines if line.strip()]
        
        return '\n'.join(non_empty_lines)
    
    def _fix_line_breaks(self, code: str) -> str:
        """修复不正确的换行"""
        lines = code.split('\n')
        fixed_lines = []
        current_line = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 如果当前行以 --> 结尾，下一行应该是目标节点
            if current_line.endswith('-->'):
                current_line += " " + line
            # 如果当前行是不完整的节点定义（中文字符结尾但没有']'）
            elif current_line and not current_line.endswith(']') and not current_line.startswith('style') and not 'fill:' in current_line:
                # 检查是否是被截断的中文节点名
                if self._is_incomplete_chinese_node(current_line):
                    current_line += line
                else:
                    # 保存当前行，开始新行
                    if current_line:
                        fixed_lines.append(current_line)
                    current_line = line
            else:
                # 保存当前行，开始新行
                if current_line:
                    fixed_lines.append(current_line)
                current_line = line
        
        # 添加最后一行
        if current_line:
            fixed_lines.append(current_line)
        
        return '\n'.join(fixed_lines)
    
    def _is_incomplete_chinese_node(self, line: str) -> bool:
        """检查是否是不完整的中文节点定义"""
        # 如果行中有'['但没有对应的']'，且以中文字符结尾
        if '[' in line and ']' not in line:
            return True
        
        # 如果行以中文字符结尾且不是完整的连接语句
        if re.search(r'[\u4e00-\u9fff]$', line) and '-->' not in line:
            return True
        
        return False
    
    def _fix_node_definitions(self, code: str) -> str:
        """修复节点定义"""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 确保每个连接语句在单独的行上
            if '-->' in line:
                # 分割多个连接语句
                connections = self._split_connections(line)
                fixed_lines.extend(connections)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _split_connections(self, line: str) -> List[str]:
        """分割连接语句"""
        # 使用正则表达式找到所有的连接模式
        # 模式：节点 --> 节点
        pattern = r'([A-Za-z0-9_]+(?:\[[^\]]+\])?)\s*-->\s*([A-Za-z0-9_]+(?:\[[^\]]+\])?)'
        
        connections = []
        remaining = line
        
        while True:
            match = re.search(pattern, remaining)
            if not match:
                break
            
            source = match.group(1).strip()
            target = match.group(2).strip()
            connections.append(f"    {source} --> {target}")
            
            # 移除已处理的部分，继续处理剩余部分
            remaining = remaining[match.end():].strip()
            
            # 如果剩余部分以源节点开始，说明有链式连接
            if remaining and not remaining.startswith(source.split('[')[0]):
                # 查找下一个源节点
                next_match = re.search(r'^([A-Za-z0-9_]+)', remaining)
                if next_match:
                    remaining = remaining
                else:
                    break
        
        return connections if connections else [f"    {line}"]
    
    def _fix_connections(self, code: str) -> str:
        """修复连接语法"""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 确保适当的缩进
            if line.startswith('graph') or line.startswith('flowchart'):
                fixed_lines.append(line)
            elif line.startswith('style'):
                fixed_lines.append(f"    {line}")
            elif '-->' in line and not line.startswith('    '):
                fixed_lines.append(f"    {line}")
            else:
                fixed_lines.append(line if line.startswith('    ') or not line.strip() else f"    {line}")
        
        return '\n'.join(fixed_lines)
    
    def _fix_styles(self, code: str) -> str:
        """修复样式定义"""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 修复样式语法
            if line.startswith('style'):
                # 确保样式语法正确
                if not re.match(r'style\s+\w+\s+fill:#[0-9a-fA-F]{6}$', line):
                    # 尝试修复常见的样式问题
                    style_match = re.match(r'style\s+(\w+)\s*fill:\s*#?([0-9a-fA-F]{6})', line)
                    if style_match:
                        node_id = style_match.group(1)
                        color = style_match.group(2)
                        line = f"style {node_id} fill:#{color}"
                
                fixed_lines.append(f"    {line}")
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _final_cleanup(self, code: str) -> str:
        """最终清理"""
        lines = code.split('\n')
        
        # 移除空行并确保格式一致
        cleaned_lines = []
        for line in lines:
            line = line.rstrip()
            if line.strip():
                cleaned_lines.append(line)
        
        # 确保图表类型声明在第一行
        if cleaned_lines and not cleaned_lines[0].startswith(('graph', 'flowchart')):
            cleaned_lines.insert(0, 'graph TB')
        
        return '\n'.join(cleaned_lines)

# 测试清理器
def test_cleaner():
    """测试清理器"""
    import sys
    import os
    
    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    sys.path.insert(0, project_root)
    
    from src.md2doc.engines.mermaid_engine import MermaidEngine
    from src.md2doc.engines.chart_detector import ChartInfo, ChartType
    
    # 原始问题代码
    problem_code = """graph TB
    A[3.3 专项服务] --> B[3.3.1 AI编程助手集成服务] A --> C[3.3.2 合规管控服
务] B --> B1[3.3.1.1 GitHub Copilot Enterprise部署] B --> B2[3.3.1.2 AI代码质量管
控] B --> B3[3.3.1.3 AI使用规范制定] B --> B4[3.3.1.4 AI安全和合规] B -->
B5[3.3.1.5 团队培训和推广] C --> C1[3.3.2.1 民航标准对接] C --> C2[3.3.2.2 审计体系
建设] C --> C3[3.3.2.3 持续合规监控] C --> C4[3.3.2.4 合规报告自动化] C -->
C5[3.3.2.5 合规风险管理] B1 --> B11[3.3.1.1.1 企业账户配置] B1 --> B12[3.3.1.1.2
IDE集成配置] B1 --> B13[3.3.1.1.3 团队权限管理] B1 --> B14[3.3.1.1.4 使用监控配置]
C1 --> C11[3.3.2.1.1 CCAR-396标准映射] C1 --> C12[3.3.2.1.2 ISO 27001对接] C1 -->
C13[3.3.2.1.3 行业最佳实践] style A fill:#ff9999 style B fill:#99ccff style C
fill:#99ff99"""
    
    cleaner = MermaidCodeCleaner()
    cleaned_code = cleaner.clean_and_fix(problem_code)
    
    print("清理后的Mermaid代码:")
    print("=" * 50)
    print(cleaned_code)
    print("=" * 50)
    
    # 测试渲染
    chart_info = ChartInfo(
        chart_type=ChartType.MERMAID,
        content=cleaned_code,
        language="mermaid"
    )
    
    engine = MermaidEngine()
    
    try:
        result = engine.render(chart_info)
        print(f"✅ 清理后渲染成功！结果类型: {type(result)}")
        if isinstance(result, bytes):
            print(f"图片大小: {len(result)} 字节")
        return True
    except Exception as e:
        print(f"❌ 清理后仍然失败: {e}")
        return False

if __name__ == "__main__":
    test_cleaner()
