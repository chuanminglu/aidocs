"""
主转换器

提供Markdown到Word的完整转换流程：
- 集成解析器和生成器
- 统一的转换接口
- 完整的错误处理
- 详细的转换日志
"""

from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from .parser import MarkdownParser, ParseResult
from .generator import WordDocumentGenerator
from .config import ConfigManager
from ..utils.logger import get_logger, ProgressLogger, log_execution_time


class ConversionError(Exception):
    """转换异常类"""
    pass


class MD2DocConverter:
    """Markdown到Word转换器"""
    
    def __init__(self, config: Optional[ConfigManager] = None):
        """初始化转换器
        
        Args:
            config: 配置管理器实例
        """
        self.config = config or ConfigManager()
        self.logger = get_logger("md2doc.converter")
        self.parser = MarkdownParser()
        self.generator = WordDocumentGenerator(self.config)
        self.conversion_stats = {}
        
    @log_execution_time
    def convert_file(self, input_path: Path, output_path: Optional[Path] = None) -> Path:
        """转换Markdown文件到Word文档
        
        Args:
            input_path: 输入Markdown文件路径
            output_path: 输出Word文档路径，如果为None则自动生成
            
        Returns:
            输出文件路径
            
        Raises:
            ConversionError: 转换失败时抛出
        """
        try:
            # 验证输入文件
            if not input_path.exists():
                raise ConversionError(f"输入文件不存在: {input_path}")
            
            if not input_path.is_file():
                raise ConversionError(f"输入路径不是文件: {input_path}")
            
            # 确定输出路径
            if output_path is None:
                output_path = input_path.with_suffix('.docx')
            
            self.logger.info(f"开始转换: {input_path} -> {output_path}")
            
            # 创建进度追踪器
            progress = ProgressLogger(self.logger)
            
            # 1. 读取文件
            progress.update(1, 4, "读取Markdown文件")
            content = self._read_markdown_file(input_path)
            
            # 2. 解析内容
            progress.update(2, 4, "解析Markdown内容")
            parse_result = self._parse_content(content)
            
            # 3. 生成Word文档
            progress.update(3, 4, "生成Word文档")
            document = self._generate_document(parse_result)
            
            # 4. 保存文档
            progress.update(4, 4, "保存文档")
            self._save_document(document, output_path)
            
            progress.complete("转换完成")
            
            # 记录转换统计信息
            self._record_conversion_stats(input_path, output_path, parse_result)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"转换失败: {e}")
            raise ConversionError(f"转换失败: {e}") from e
    
    def convert_string(self, content: str, output_path: Path) -> Path:
        """转换Markdown字符串到Word文档
        
        Args:
            content: Markdown内容字符串
            output_path: 输出Word文档路径
            
        Returns:
            输出文件路径
            
        Raises:
            ConversionError: 转换失败时抛出
        """
        try:
            self.logger.info(f"开始转换字符串内容到: {output_path}")
            
            # 创建进度追踪器
            progress = ProgressLogger(self.logger)
            
            # 1. 验证内容
            progress.update(1, 3, "验证内容")
            if not content or not content.strip():
                raise ConversionError("输入内容为空")
            
            # 2. 解析内容
            progress.update(2, 3, "解析Markdown内容")
            parse_result = self._parse_content(content)
            
            # 3. 生成并保存文档
            progress.update(3, 3, "生成并保存文档")
            document = self._generate_document(parse_result)
            self._save_document(document, output_path)
            
            progress.complete("转换完成")
            
            # 记录转换统计信息
            self._record_conversion_stats(None, output_path, parse_result)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"字符串转换失败: {e}")
            raise ConversionError(f"字符串转换失败: {e}") from e
    
    def batch_convert(self, input_dir: Path, output_dir: Optional[Path] = None, 
                     pattern: str = "*.md") -> Dict[Path, Path]:
        """批量转换目录中的Markdown文件
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录，如果为None则使用输入目录
            pattern: 文件匹配模式
            
        Returns:
            转换结果字典 {输入文件: 输出文件}
            
        Raises:
            ConversionError: 转换失败时抛出
        """
        try:
            if not input_dir.exists() or not input_dir.is_dir():
                raise ConversionError(f"输入目录无效: {input_dir}")
            
            if output_dir is None:
                output_dir = input_dir
            
            # 确保输出目录存在
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 查找所有匹配的文件
            markdown_files = list(input_dir.glob(pattern))
            if not markdown_files:
                self.logger.warning(f"在 {input_dir} 中未找到匹配 {pattern} 的文件")
                return {}
            
            self.logger.info(f"开始批量转换: {len(markdown_files)} 个文件")
            
            # 创建总体进度追踪器
            progress = ProgressLogger(self.logger)
            results = {}
            
            for i, input_file in enumerate(markdown_files):
                try:
                    # 生成输出文件路径
                    output_file = output_dir / input_file.with_suffix('.docx').name
                    
                    progress.update(i + 1, len(markdown_files), f"转换 {input_file.name}")
                    
                    # 转换单个文件
                    result_path = self.convert_file(input_file, output_file)
                    results[input_file] = result_path
                    
                except Exception as e:
                    self.logger.error(f"转换文件 {input_file} 失败: {e}")
                    results[input_file] = None
            
            progress.complete(f"批量转换完成: {len([r for r in results.values() if r])} 成功")
            
            return results
            
        except Exception as e:
            self.logger.error(f"批量转换失败: {e}")
            raise ConversionError(f"批量转换失败: {e}") from e
    
    def _read_markdown_file(self, file_path: Path) -> str:
        """读取Markdown文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容
        """
        try:
            # 尝试多种编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    self.logger.debug(f"成功读取文件 {file_path} (编码: {encoding})")
                    return content
                except UnicodeDecodeError:
                    continue
            
            raise ConversionError(f"无法读取文件 {file_path}：不支持的编码格式")
            
        except Exception as e:
            raise ConversionError(f"读取文件失败: {e}") from e
    
    def _parse_content(self, content: str) -> ParseResult:
        """解析Markdown内容
        
        Args:
            content: Markdown内容
            
        Returns:
            解析结果
        """
        try:
            parse_result = self.parser.parse(content)
            
            self.logger.info(f"解析完成: {parse_result.metadata['total_elements']} 个元素")
            self.logger.debug(f"解析详情: {parse_result.metadata}")
            
            return parse_result
            
        except Exception as e:
            raise ConversionError(f"解析内容失败: {e}") from e
    
    def _generate_document(self, parse_result: ParseResult):
        """生成Word文档
        
        Args:
            parse_result: 解析结果
            
        Returns:
            Word文档对象
        """
        try:
            document = self.generator.generate_from_parse_result(parse_result)
            
            # 获取生成统计信息
            stats = self.generator.get_document_stats()
            self.logger.info(f"文档生成完成: {stats}")
            
            return document
            
        except Exception as e:
            raise ConversionError(f"生成文档失败: {e}") from e
    
    def _save_document(self, document, output_path: Path):
        """保存Word文档
        
        Args:
            document: Word文档对象
            output_path: 输出路径
        """
        try:
            self.generator.save_document(document, output_path)
            
            # 验证输出文件
            if output_path.exists():
                file_size = output_path.stat().st_size
                self.logger.info(f"文档保存成功: {output_path} (大小: {file_size} 字节)")
            else:
                raise ConversionError("文档保存后文件不存在")
                
        except Exception as e:
            raise ConversionError(f"保存文档失败: {e}") from e
    
    def _record_conversion_stats(self, input_path: Optional[Path], 
                               output_path: Path, parse_result: ParseResult):
        """记录转换统计信息
        
        Args:
            input_path: 输入文件路径（可能为None）
            output_path: 输出文件路径
            parse_result: 解析结果
        """
        stats = {
            "timestamp": datetime.now().isoformat(),
            "input_path": str(input_path) if input_path else "string_input",
            "output_path": str(output_path),
            "input_size": input_path.stat().st_size if input_path and input_path.exists() else 0,
            "output_size": output_path.stat().st_size if output_path.exists() else 0,
            "elements_parsed": parse_result.metadata['total_elements'],
            "parse_details": parse_result.metadata,
            "document_stats": self.generator.get_document_stats()
        }
        
        self.conversion_stats = stats
        self.logger.debug(f"转换统计: {stats}")
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """获取最近一次转换的统计信息
        
        Returns:
            转换统计信息
        """
        return self.conversion_stats.copy()
    
    def validate_conversion(self, input_path: Path, output_path: Path) -> bool:
        """验证转换结果
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            
        Returns:
            是否验证通过
        """
        try:
            # 检查输出文件是否存在
            if not output_path.exists():
                self.logger.error("输出文件不存在")
                return False
            
            # 检查文件大小
            output_size = output_path.stat().st_size
            if output_size < 1000:  # Word文档至少应该有1KB
                self.logger.error(f"输出文件过小: {output_size} 字节")
                return False
            
            # 尝试重新读取解析输入文件
            content = self._read_markdown_file(input_path)
            parse_result = self._parse_content(content)
            
            # 检查是否有内容被解析
            if parse_result.metadata['total_elements'] == 0:
                self.logger.warning("输入文件没有解析到任何元素")
            
            self.logger.info("转换验证通过")
            return True
            
        except Exception as e:
            self.logger.error(f"转换验证失败: {e}")
            return False
