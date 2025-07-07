"""
AI服务模块
提供文档分析、大纲生成、内容建议等AI功能
"""
import re
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from openai import OpenAI


class AIServiceError(Exception):
    """AI服务异常"""
    pass


class APICallError(AIServiceError):
    """API调用异常"""
    pass


@dataclass
class AIResponse:
    """AI响应数据类"""
    content: str
    confidence: float
    suggestions: List[str]
    metadata: Dict[str, Any]


class AIService:
    """AI服务类"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"
        self.max_tokens = 4000
        self.temperature = 0.7
        
        # 初始化OpenAI客户端（兼容DeepSeek API）
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            self.client = None
        
    def is_available(self) -> bool:
        """检查AI服务是否可用"""
        return bool(self.api_key and self.client)
    
    def _call_api(self, messages: List[Dict[str, str]], max_tokens: Optional[int] = None) -> str:
        """调用DeepSeek API"""
        if not self.is_available():
            raise AIServiceError("AI服务不可用，请检查API配置")
        
        try:
            # 转换消息格式以符合OpenAI API要求
            formatted_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,  # type: ignore
                max_tokens=max_tokens or self.max_tokens,
                temperature=self.temperature
            )
            content = response.choices[0].message.content
            return content or ""
        except Exception as e:
            print(f"API调用失败: {e}")
            # 如果API调用失败，降级到fallback方法
            raise APICallError(f"API调用失败: {str(e)}")
    
    def generate_outline(self, content: str, doc_type: str = "markdown") -> AIResponse:
        """生成文档大纲"""
        if not self.is_available():
            return self._fallback_generate_outline(content, doc_type)
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"你是一个专业的文档分析师。请为以下{doc_type}文档生成一个详细的大纲结构。大纲应该包含主要章节和子章节，使用Markdown格式。"
                },
                {
                    "role": "user",
                    "content": f"请为以下内容生成大纲：\n\n{content}"
                }
            ]
            
            ai_content = self._call_api(messages, max_tokens=2000)
            
            return AIResponse(
                content=ai_content,
                confidence=0.9,
                suggestions=[
                    "AI生成的大纲，建议根据需要调整",
                    "可以进一步完善章节内容",
                    "考虑添加更多细节和例子"
                ],
                metadata={
                    "method": "api",
                    "timestamp": datetime.now().isoformat(),
                    "doc_type": doc_type,
                    "model": self.model
                }
            )
            
        except Exception as e:
            print(f"AI大纲生成失败，使用fallback方法: {e}")
            return self._fallback_generate_outline(content, doc_type)
    
    def _fallback_generate_outline(self, content: str, doc_type: str = "markdown") -> AIResponse:
        """大纲生成的后备方法"""
        lines = content.split('\n')
        outline_parts = []
        
        # 提取现有标题
        existing_headers = self._extract_headers(lines)
        
        if existing_headers:
            outline_parts = self._generate_toc_from_headers(existing_headers)
        else:
            outline_parts = self._generate_outline_from_content(content)
        
        outline_content = "\n".join(outline_parts)
        
        return AIResponse(
            content=outline_content,
            confidence=0.8,
            suggestions=[
                "建议根据实际内容调整大纲结构",
                "可以添加更多细节和子章节",
                "考虑增加图表和示例说明"
            ],
            metadata={
                "method": "fallback",
                "timestamp": datetime.now().isoformat(),
                "doc_type": doc_type
            }
        )
    
    def _extract_headers(self, lines: List[str]) -> List[str]:
        """提取现有标题"""
        headers = []
        for line in lines:
            line = line.strip()
            if line.startswith('#') and len(line) > 1:
                headers.append(line)
        return headers
    
    def _generate_toc_from_headers(self, headers: List[str]) -> List[str]:
        """从标题生成目录"""
        outline_parts = ["# 目录", ""]
        
        for header in headers:
            level = self._get_header_level(header)
            title = header.strip('#').strip()
            if title:
                indent = "  " * (level - 1)
                outline_parts.append(f"{indent}- {title}")
        
        return outline_parts
    
    def _get_header_level(self, header: str) -> int:
        """获取标题级别"""
        level = 0
        for char in header:
            if char == '#':
                level += 1
            else:
                break
        return level
    
    def _generate_outline_from_content(self, content: str) -> List[str]:
        """从内容生成大纲"""
        outline_parts = ["# 文档大纲", ""]
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if len(paragraphs) > 0:
            key_points = self._extract_key_points(paragraphs)
            
            if key_points:
                outline_parts.extend(self._format_key_points(key_points))
            else:
                outline_parts.extend(self._get_default_outline())
        
        return outline_parts
    
    def _extract_key_points(self, paragraphs: List[str]) -> List[str]:
        """提取关键要点"""
        key_points = []
        for para in paragraphs[:10]:  # 限制分析前10段
            if len(para) > 50:  # 过滤短段落
                sentences = re.split(r'[。！？.!?]', para)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if 20 < len(sentence) < 100:
                        key_points.append(sentence)
        return key_points
    
    def _format_key_points(self, key_points: List[str]) -> List[str]:
        """格式化关键要点"""
        outline_parts = ["## 主要内容", ""]
        for point in key_points[:5]:  # 最多5个要点
            outline_parts.append(f"### {point[:30]}...")
            outline_parts.append("")
        return outline_parts
    
    def _get_default_outline(self) -> List[str]:
        """获取默认大纲"""
        return [
            "## 概述",
            "## 主要内容", 
            "## 详细说明",
            "## 总结"
        ]
    
    def get_content_suggestions(self, content: str, context: str = "") -> AIResponse:
        """获取内容改进建议"""
        if not self.is_available():
            return self._fallback_content_suggestions(content, context)
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的文档写作助手。请分析用户提供的文档内容，并提供具体的改进建议。建议应该包括结构优化、内容完善、表达改进等方面。"
                },
                {
                    "role": "user",
                    "content": f"请为以下内容提供改进建议：\n\n{content}\n\n上下文：{context}"
                }
            ]
            
            ai_content = self._call_api(messages, max_tokens=1500)
            
            # 解析AI返回的建议
            suggestions = []
            for line in ai_content.split('\n'):
                line = line.strip()
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    suggestions.append(line[1:].strip())
                elif line and not line.startswith('#'):
                    suggestions.append(line)
            
            return AIResponse(
                content=ai_content,
                confidence=0.85,
                suggestions=suggestions[:10],  # 最多10个建议
                metadata={
                    "method": "api",
                    "timestamp": datetime.now().isoformat(),
                    "content_length": len(content),
                    "model": self.model
                }
            )
            
        except Exception as e:
            print(f"AI内容建议失败，使用fallback方法: {e}")
            return self._fallback_content_suggestions(content, context)
    
    def _fallback_content_suggestions(self, content: str, context: str = "") -> AIResponse:
        """内容建议的后备方法"""
        suggestions = []
        
        # 执行各种检查
        suggestions.extend(self._check_content_length(content))
        suggestions.extend(self._check_punctuation(content))
        suggestions.extend(self._check_sentence_length(content))
        suggestions.extend(self._check_word_frequency(content))
        suggestions.extend(self._check_structure(content))
        suggestions.extend(self._check_formatting(content))
        
        # 如果没有发现问题，给出积极建议
        if not suggestions:
            suggestions = self._get_positive_suggestions()
        
        return AIResponse(
            content="\n".join(f"• {suggestion}" for suggestion in suggestions),
            confidence=0.7,
            suggestions=suggestions,
            metadata={
                "method": "fallback",
                "timestamp": datetime.now().isoformat(),
                "content_length": len(content),
                "word_count": len(content.split())
            }
        )
    
    def _check_content_length(self, content: str) -> List[str]:
        """检查内容长度"""
        if len(content) < 20:
            return ["内容较短，建议扩展更多细节和例子"]
        return []
    
    def _check_punctuation(self, content: str) -> List[str]:
        """检查标点符号"""
        if not any(punct in content for punct in ['。', '.', '!', '?', '！', '？']):
            return ["建议添加适当的标点符号以提高可读性"]
        return []
    
    def _check_sentence_length(self, content: str) -> List[str]:
        """检查句子长度"""
        sentences = re.split(r'[。！？.!?]', content)
        long_sentences = [s for s in sentences if len(s) > 50]
        if long_sentences:
            return [f"发现{len(long_sentences)}个长句子，建议分解为更短的句子"]
        return []
    
    def _check_word_frequency(self, content: str) -> List[str]:
        """检查词频"""
        words = re.findall(r'\b\w+\b', content.lower())
        if not words:
            return []
        
        word_count = {}
        for word in words:
            if len(word) > 1:  # 忽略单字符
                word_count[word] = word_count.get(word, 0) + 1
        
        frequent_words = [(word, count) for word, count in word_count.items() 
                         if count > 3 and len(word) > 2]
        
        if frequent_words:
            word_list = ', '.join([f'{w}({c}次)' for w, c in frequent_words[:3]])
            return [f"检测到高频词汇：{word_list}，建议使用同义词"]
        return []
    
    def _check_structure(self, content: str) -> List[str]:
        """检查结构"""
        if '\n' not in content:
            return ["建议将内容分段，使用段落结构提高可读性"]
        return []
    
    def _check_formatting(self, content: str) -> List[str]:
        """检查格式"""
        if not re.search(r'[*_#]', content):
            return ["建议使用Markdown格式突出重点内容"]
        return []
    
    def _get_positive_suggestions(self) -> List[str]:
        """获取积极建议"""
        return [
            "内容结构良好，可以考虑添加更多具体例子",
            "建议增加图表或数据支持论点",
            "可以添加相关链接或参考资料"
        ]
    
    def analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """分析文档结构"""
        lines = content.split('\n')
        
        # 统计信息
        stats = {
            "total_lines": len(lines),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "total_characters": len(content),
            "total_words": len(content.split()),
            "paragraphs": len([p for p in content.split('\n\n') if p.strip()]),
            "headers": [],
            "lists": [],
            "code_blocks": 0,
            "links": 0,
            "images": 0
        }
        
        # 分析标题
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                stats["headers"].append({
                    "level": level,
                    "title": title,
                    "line_number": i + 1
                })
        
        # 分析列表
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith(('-', '*', '+')):
                stats["lists"].append({
                    "type": "unordered",
                    "content": line[1:].strip(),
                    "line_number": i + 1
                })
            elif re.match(r'^\d+\.', line):
                stats["lists"].append({
                    "type": "ordered",
                    "content": line.split('.', 1)[1].strip(),
                    "line_number": i + 1
                })
        
        # 分析代码块
        stats["code_blocks"] = len(re.findall(r'```', content)) // 2
        
        # 分析链接
        stats["links"] = len(re.findall(r'\[.*?\]\([^\)]*\)', content))
        
        # 分析图片
        stats["images"] = len(re.findall(r'!\[.*?\]\([^\)]*\)', content))
        
        return stats
    
    def suggest_improvements(self, content: str) -> List[str]:
        """建议改进方案"""
        structure = self.analyze_document_structure(content)
        suggestions = []
        
        # 结构建议
        if not structure["headers"]:
            suggestions.append("建议添加标题来组织内容结构")
        
        if structure["paragraphs"] < 3 and structure["total_words"] > 100:
            suggestions.append("建议将内容分解为更多段落")
        
        # 内容建议
        if structure["total_words"] < 50:
            suggestions.append("内容较少，建议扩展更多细节")
        
        if structure["lists"] == 0 and structure["total_words"] > 200:
            suggestions.append("建议使用列表来组织要点")
        
        # 格式建议
        if structure["code_blocks"] == 0 and "代码" in content:
            suggestions.append("建议使用代码块格式化代码内容")
        
        if structure["links"] == 0 and structure["total_words"] > 300:
            suggestions.append("建议添加相关链接或参考资料")
        
        return suggestions
    
    def suggest_content(self, content: str, context: str = "") -> AIResponse:
        """内容建议 - 兼容性方法"""
        return self.get_content_suggestions(content, context)
    
    def improve_writing(self, content: str) -> AIResponse:
        """改进写作"""
        if not self.is_available():
            return self._fallback_improve_writing(content)
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的文档编辑助手。请帮助改进用户提供的文档内容，包括：1) 修正语法和拼写错误；2) 优化表达和措辞；3) 改善句子结构和流畅性；4) 保持原意的基础上提升文档质量。请直接提供改进后的文档内容。"
                },
                {
                    "role": "user",
                    "content": f"请改进以下文档内容：\n\n{content}"
                }
            ]
            
            ai_content = self._call_api(messages, max_tokens=3000)
            
            return AIResponse(
                content=ai_content,
                confidence=0.88,
                suggestions=[
                    "AI已优化文档的语法和表达",
                    "改进了句子结构和流畅性",
                    "保持了原文的主要含义",
                    "建议人工审核并根据需要调整"
                ],
                metadata={
                    "method": "api",
                    "timestamp": datetime.now().isoformat(),
                    "original_length": len(content),
                    "improved_length": len(ai_content),
                    "model": self.model
                }
            )
            
        except Exception as e:
            print(f"AI写作改进失败，使用fallback方法: {e}")
            return self._fallback_improve_writing(content)
    
    def _fallback_improve_writing(self, content: str) -> AIResponse:
        """写作改进的后备方法"""
        suggestions = []
        improved_content = content
        
        # 基本改进
        if content:
            # 修复常见格式问题
            improved_content = re.sub(r'\s+', ' ', content.strip())
            improved_content = re.sub(r'([。！？])([A-Za-z])', r'\1 \2', improved_content)
            improved_content = re.sub(r'([a-z])([A-Z])', r'\1 \2', improved_content)
            
            suggestions.extend([
                "已优化空格和标点符号格式",
                "建议检查语法和拼写错误",
                "可以使用更丰富的词汇表达"
            ])
        
        return AIResponse(
            content=improved_content,
            confidence=0.75,
            suggestions=suggestions,
            metadata={
                "method": "fallback",
                "timestamp": datetime.now().isoformat(),
                "original_length": len(content),
                "improved_length": len(improved_content)
            }
        )
