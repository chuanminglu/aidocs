# -*- coding: utf-8 -*-
"""图片处理和缓存模块

提供图片处理、缓存和优化功能：
- 图片尺寸调整和优化
- 智能缓存机制
- 多格式转换支持
- 缓存清理和管理
"""

import hashlib
import json
import shutil
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL/Pillow not available. Image processing will be limited.")


class ImageFormat(Enum):
    """支持的图片格式"""
    PNG = "png"
    JPEG = "jpeg"
    JPG = "jpg"
    BMP = "bmp"
    TIFF = "tiff"
    WEBP = "webp"


class ImageQuality(Enum):
    """图片质量级别"""
    LOW = 60
    MEDIUM = 80
    HIGH = 95
    LOSSLESS = 100


@dataclass
class ImageProcessConfig:
    """图片处理配置"""
    max_width: int = 800  # 最大宽度（像素）
    max_height: int = 600  # 最大高度（像素）
    output_format: ImageFormat = ImageFormat.PNG
    quality: ImageQuality = ImageQuality.HIGH
    dpi: int = 96  # DPI设置
    optimize: bool = True  # 是否优化文件大小
    preserve_aspect_ratio: bool = True  # 保持宽高比
    
    # Word文档专用设置
    word_max_width_inches: float = 6.0  # Word文档最大宽度（英寸）
    word_dpi: int = 96  # Word文档DPI
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为可序列化的字典"""
        return {
            'max_width': self.max_width,
            'max_height': self.max_height,
            'output_format': self.output_format.value,  # 转换枚举为字符串
            'quality': self.quality.value,  # 转换枚举为数值
            'dpi': self.dpi,
            'optimize': self.optimize,
            'preserve_aspect_ratio': self.preserve_aspect_ratio,
            'word_max_width_inches': self.word_max_width_inches,
            'word_dpi': self.word_dpi
        }


@dataclass
class CacheEntry:
    """缓存条目"""
    source_hash: str  # 源内容哈希
    file_path: str  # 缓存文件路径
    created_at: datetime  # 创建时间
    accessed_at: datetime  # 最后访问时间
    config_hash: str  # 配置哈希
    file_size: int  # 文件大小（字节）
    original_format: str  # 原始格式
    processed_format: str  # 处理后格式


class ImageProcessor:
    """图片处理器"""
    
    def __init__(self, cache_dir: Optional[Path] = None, config: Optional[ImageProcessConfig] = None):
        """
        初始化图片处理器
        
        Args:
            cache_dir: 缓存目录，默认为系统临时目录下的md2doc_image_cache
            config: 图片处理配置
        """
        self.logger = logging.getLogger(__name__)
        
        # 设置缓存目录
        if cache_dir is None:
            cache_dir = Path(tempfile.gettempdir()) / "md2doc_image_cache"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置配置
        self.config = config or ImageProcessConfig()
        
        # 缓存索引文件
        self.cache_index_file = self.cache_dir / "cache_index.json"
        self.cache_index: Dict[str, CacheEntry] = self._load_cache_index()
        
        self.logger.info(f"ImageProcessor initialized with cache dir: {self.cache_dir}")
    
    def _load_cache_index(self) -> Dict[str, CacheEntry]:
        """加载缓存索引"""
        if not self.cache_index_file.exists():
            return {}
        
        try:
            with open(self.cache_index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cache_index = {}
                for key, entry_data in data.items():
                    entry_data['created_at'] = datetime.fromisoformat(entry_data['created_at'])
                    entry_data['accessed_at'] = datetime.fromisoformat(entry_data['accessed_at'])
                    cache_index[key] = CacheEntry(**entry_data)
                return cache_index
        except Exception as e:
            self.logger.warning(f"Failed to load cache index: {e}")
            return {}
    
    def _save_cache_index(self):
        """保存缓存索引"""
        try:
            data = {}
            for key, entry in self.cache_index.items():
                entry_dict = asdict(entry)
                entry_dict['created_at'] = entry.created_at.isoformat()
                entry_dict['accessed_at'] = entry.accessed_at.isoformat()
                data[key] = entry_dict
            
            with open(self.cache_index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save cache index: {e}")
    
    def _generate_cache_key(self, source_content: Union[str, bytes], config: ImageProcessConfig) -> str:
        """生成缓存键"""
        if isinstance(source_content, str):
            source_content = source_content.encode('utf-8')
        
        source_hash = hashlib.md5(source_content).hexdigest()
        config_hash = hashlib.md5(json.dumps(config.to_dict(), sort_keys=True).encode('utf-8')).hexdigest()
        
        return f"{source_hash}_{config_hash}"
    
    def _get_cached_image(self, cache_key: str) -> Optional[Path]:
        """获取缓存的图片"""
        if cache_key not in self.cache_index:
            return None
        
        entry = self.cache_index[cache_key]
        cached_file = Path(entry.file_path)
        
        # 检查文件是否存在
        if not cached_file.exists():
            self.logger.warning(f"Cached file not found: {cached_file}")
            del self.cache_index[cache_key]
            return None
        
        # 更新访问时间
        entry.accessed_at = datetime.now()
        self._save_cache_index()
        
        self.logger.debug(f"Cache hit for key: {cache_key}")
        return cached_file
    
    def _cache_image(self, cache_key: str, image_path: Path, source_format: str) -> None:
        """缓存图片"""
        try:
            # 生成缓存文件名
            cache_filename = f"{cache_key}.{self.config.output_format.value}"
            cache_file_path = self.cache_dir / cache_filename
            
            # 复制文件到缓存目录
            shutil.copy2(image_path, cache_file_path)
            
            # 创建缓存条目
            file_size = cache_file_path.stat().st_size
            now = datetime.now()
            
            config_hash = hashlib.md5(json.dumps(self.config.to_dict(), sort_keys=True).encode('utf-8')).hexdigest()
            
            entry = CacheEntry(
                source_hash=cache_key.split('_')[0],
                file_path=str(cache_file_path),
                created_at=now,
                accessed_at=now,
                config_hash=config_hash,
                file_size=file_size,
                original_format=source_format,
                processed_format=self.config.output_format.value
            )
            
            self.cache_index[cache_key] = entry
            self._save_cache_index()
            
            self.logger.debug(f"Cached image: {cache_file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to cache image: {e}")
    
    def process_image(self, 
                     source_path: Union[str, Path], 
                     output_path: Optional[Union[str, Path]] = None,
                     config: Optional[ImageProcessConfig] = None) -> Path:
        """
        处理图片
        
        Args:
            source_path: 源图片路径
            output_path: 输出路径，如果不提供则生成临时文件
            config: 处理配置，如果不提供则使用默认配置
            
        Returns:
            处理后的图片路径
        """
        source_path = Path(source_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source image not found: {source_path}")
        
        # 使用提供的配置或默认配置
        process_config = config or self.config
        
        # 生成缓存键
        with open(source_path, 'rb') as f:
            source_content = f.read()
        cache_key = self._generate_cache_key(source_content, process_config)
        
        # 检查缓存
        cached_image = self._get_cached_image(cache_key)
        if cached_image and not output_path:
            return cached_image
        
        # 处理图片
        try:
            # 确保 output_path 是 Path 类型或 None
            output_path_typed = Path(output_path) if output_path is not None else None
            processed_path = self._process_image_with_pil(source_path, output_path_typed, process_config)
            
            # 如果没有指定输出路径，则缓存处理后的图片
            if not output_path:
                self._cache_image(cache_key, processed_path, source_path.suffix.lower())

            return processed_path
            
        except Exception as e:
            self.logger.error(f"Failed to process image {source_path}: {e}")
            # 如果处理失败，返回原图片
            if output_path:
                shutil.copy2(source_path, output_path)
                return Path(output_path)
            else:
                return source_path
    
    def _process_image_with_pil(self, 
                               source_path: Path, 
                               output_path: Optional[Path],
                               config: ImageProcessConfig) -> Path:
        """使用PIL处理图片"""
        if not PIL_AVAILABLE:
            # 如果PIL不可用，直接复制文件
            if output_path:
                shutil.copy2(source_path, output_path)
                return Path(output_path)
            else:
                return source_path
        
        # 打开并处理图片
        return self._pil_process_core(source_path, output_path, config)
    
    def _pil_process_core(self, source_path: Path, output_path: Optional[Path], config: ImageProcessConfig) -> Path:
        """PIL处理核心逻辑"""
        with Image.open(source_path) as img:
            # 转换颜色模式
            img = self._convert_color_mode(img, config)
            
            # 调整尺寸
            img = self._resize_image(img, config)
            
            # 设置输出路径
            if output_path is None:
                output_path = self.cache_dir / f"processed_{int(time.time())}_{source_path.stem}.{config.output_format.value}"
            else:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存图片
            self._save_image(img, output_path, config)
            
            self.logger.debug(f"Processed image saved to: {output_path}")
            return output_path
    
    def _convert_color_mode(self, img: Image.Image, config: ImageProcessConfig) -> Image.Image:
        """转换图片颜色模式"""
        if img.mode in ('RGBA', 'LA', 'P') and config.output_format in (ImageFormat.JPEG, ImageFormat.JPG):
            # 创建白色背景
            rgb_img = Image.new('RGB', img.size, color=(255, 255, 255))  # type: ignore
            if img.mode == 'P':
                img = img.convert('RGBA')
            rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            return rgb_img
        elif img.mode != 'RGB' and config.output_format not in (ImageFormat.PNG,):
            return img.convert('RGB')
        return img
    
    def _resize_image(self, img: Image.Image, config: ImageProcessConfig) -> Image.Image:
        """调整图片尺寸"""
        if config.preserve_aspect_ratio:
            img.thumbnail((config.max_width, config.max_height), Image.Resampling.LANCZOS)
        else:
            img = img.resize((config.max_width, config.max_height), Image.Resampling.LANCZOS)
        return img
    
    def _save_image(self, img: Image.Image, output_path: Path, config: ImageProcessConfig) -> None:
        """保存图片"""
        save_kwargs = {
            'format': config.output_format.value.upper(),
            'optimize': config.optimize,
            'dpi': (config.dpi, config.dpi)
        }
        
        if config.output_format in (ImageFormat.JPEG, ImageFormat.JPG):
            save_kwargs['quality'] = config.quality.value
        
        img.save(output_path, **save_kwargs)
    
    def optimize_for_word(self, source_path: Union[str, Path]) -> Path:
        """
        针对Word文档优化图片
        
        Args:
            source_path: 源图片路径
            
        Returns:
            优化后的图片路径
        """
        word_config = ImageProcessConfig(
            max_width=int(self.config.word_max_width_inches * self.config.word_dpi),
            max_height=int(self.config.word_max_width_inches * self.config.word_dpi * 0.75),  # 4:3比例
            output_format=ImageFormat.PNG,
            quality=ImageQuality.HIGH,
            dpi=self.config.word_dpi,
            optimize=True,
            preserve_aspect_ratio=True
        )
        
        return self.process_image(source_path, config=word_config)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_files = len(self.cache_index)
        total_size = sum(entry.file_size for entry in self.cache_index.values())
        
        now = datetime.now()
        recent_files = sum(1 for entry in self.cache_index.values() 
                          if (now - entry.accessed_at).days < 7)
        
        return {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'recent_files': recent_files,
            'cache_dir': str(self.cache_dir),
            'oldest_file': min((entry.created_at for entry in self.cache_index.values()), default=None),
            'newest_file': max((entry.created_at for entry in self.cache_index.values()), default=None)
        }
    
    def cleanup_cache(self, max_age_days: int = 30, max_size_mb: int = 500) -> Dict[str, Union[int, float]]:
        """
        清理缓存
        
        Args:
            max_age_days: 最大保留天数
            max_size_mb: 最大缓存大小（MB）
            
        Returns:
            清理统计信息
        """
        removed_files = 0
        removed_size = 0
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        # 按访问时间排序，最旧的先删除
        entries_by_access = sorted(self.cache_index.items(), 
                                 key=lambda x: x[1].accessed_at)
        
        current_size = sum(entry.file_size for entry in self.cache_index.values())
        max_size_bytes = max_size_mb * 1024 * 1024
        
        keys_to_remove = []
        
        for cache_key, entry in entries_by_access:
            should_remove = False
            
            # 检查年龄
            if entry.accessed_at < cutoff_date:
                should_remove = True
                self.logger.debug(f"Removing old cache entry: {cache_key}")
            
            # 检查大小
            elif current_size > max_size_bytes:
                should_remove = True
                self.logger.debug(f"Removing cache entry for size limit: {cache_key}")
            
            if should_remove:
                cache_file = Path(entry.file_path)
                if cache_file.exists():
                    try:
                        cache_file.unlink()
                        removed_files += 1
                        removed_size += entry.file_size
                        current_size -= entry.file_size
                    except Exception as e:
                        self.logger.error(f"Failed to remove cache file {cache_file}: {e}")
                
                keys_to_remove.append(cache_key)
        
        # 从索引中移除
        for key in keys_to_remove:
            del self.cache_index[key]
        
        self._save_cache_index()
        
        return {
            'removed_files': removed_files,
            'removed_size_mb': round(removed_size / (1024 * 1024), 2)
        }
    
    def clear_cache(self) -> bool:
        """清空所有缓存"""
        try:
            # 删除所有缓存文件
            for entry in self.cache_index.values():
                cache_file = Path(entry.file_path)
                if cache_file.exists():
                    cache_file.unlink()
            
            # 清空索引
            self.cache_index.clear()
            self._save_cache_index()
            
            self.logger.info("Cache cleared successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
            return False


def create_default_processor(cache_dir: Optional[Path] = None) -> ImageProcessor:
    """创建默认配置的图片处理器"""
    return ImageProcessor(cache_dir=cache_dir)


def optimize_chart_image(image_path: Union[str, Path]) -> Path:
    """
    快速优化图表图片的便利函数
    
    Args:
        image_path: 源图片路径
        
    Returns:
        优化后的图片路径
    """
    processor = create_default_processor()
    return processor.optimize_for_word(image_path)
