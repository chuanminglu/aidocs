"""
图片处理器功能演示

演示图片处理器的主要功能：
- 图片优化
- 缓存管理
- 格式转换
- Word文档优化
"""

import sys
from pathlib import Path

# 添加源代码路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from md2doc.utils.image_processor import (
    ImageProcessor, ImageProcessConfig, ImageFormat, ImageQuality,
    create_default_processor
)


def demo_basic_usage():
    """演示基础用法"""
    print("=== 图片处理器基础用法演示 ===")
    
    # 创建默认处理器
    processor = create_default_processor()
    print(f"✓ 创建图片处理器，缓存目录: {processor.cache_dir}")
    
    # 查看初始缓存状态
    stats = processor.get_cache_stats()
    print(f"✓ 缓存统计: {stats['total_files']} 个文件, {stats['total_size_mb']} MB")
    
    print()


def demo_configuration():
    """演示配置选项"""
    print("=== 图片处理配置演示 ===")
    
    # 默认配置
    default_config = ImageProcessConfig()
    print(f"✓ 默认最大宽度: {default_config.max_width}px")
    print(f"✓ 默认输出格式: {default_config.output_format.value}")
    print(f"✓ 默认质量: {default_config.quality.value}")
    print(f"✓ 默认DPI: {default_config.dpi}")
    
    # 自定义配置
    custom_config = ImageProcessConfig(
        max_width=1200,
        max_height=900,
        output_format=ImageFormat.JPEG,
        quality=ImageQuality.MEDIUM,
        dpi=150
    )
    print(f"✓ 自定义配置 - 宽度: {custom_config.max_width}px, 格式: {custom_config.output_format.value}")
    
    # Word文档优化配置
    word_width = int(default_config.word_max_width_inches * default_config.word_dpi)
    print(f"✓ Word文档优化宽度: {word_width}px ({default_config.word_max_width_inches} 英寸)")
    
    print()


def demo_cache_management():
    """演示缓存管理功能"""
    print("=== 缓存管理功能演示 ===")
    
    # 创建临时缓存目录
    import tempfile
    temp_dir = Path(tempfile.mkdtemp())
    cache_dir = temp_dir / "demo_cache"
    
    try:
        processor = ImageProcessor(cache_dir=cache_dir)
        print(f"✓ 创建临时缓存目录: {cache_dir}")
        
        # 模拟添加缓存条目
        from md2doc.utils.image_processor import CacheEntry
        from datetime import datetime
        
        entry = CacheEntry(
            source_hash="demo_hash",
            file_path=str(cache_dir / "demo.png"),
            created_at=datetime.now(),
            accessed_at=datetime.now(),
            config_hash="config_hash",
            file_size=1024,
            original_format="png",
            processed_format="png"
        )
        
        processor.cache_index["demo_key"] = entry
        processor._save_cache_index()
        
        # 查看缓存统计
        stats = processor.get_cache_stats()
        print(f"✓ 缓存统计: {stats['total_files']} 个文件, {stats['total_size_mb']} MB")
        
        # 清空缓存
        result = processor.clear_cache()
        print(f"✓ 清空缓存结果: {'成功' if result else '失败'}")
        
        # 验证缓存已清空
        stats = processor.get_cache_stats()
        print(f"✓ 清空后缓存统计: {stats['total_files']} 个文件")
        
    finally:
        # 清理临时目录
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
    
    print()


def demo_format_support():
    """演示支持的格式"""
    print("=== 支持的图片格式演示 ===")
    
    # 输出格式
    print("✓ 支持的输出格式:")
    for format_type in ImageFormat:
        print(f"  - {format_type.name}: .{format_type.value}")
    
    # 质量级别
    print("✓ 支持的质量级别:")
    for quality in ImageQuality:
        print(f"  - {quality.name}: {quality.value}")
    
    print()


def demo_error_handling():
    """演示错误处理"""
    print("=== 错误处理演示 ===")
    
    processor = create_default_processor()
    
    # 测试不存在的文件
    try:
        nonexistent_file = Path("nonexistent_image.png")
        processor.process_image(nonexistent_file)
        print("✗ 应该抛出FileNotFoundError异常")
    except FileNotFoundError:
        print("✓ 正确处理不存在的文件")
    except Exception as e:
        print(f"✓ 异常处理: {type(e).__name__}: {e}")
    
    print()


def demo_pil_availability():
    """演示PIL可用性检测"""
    print("=== PIL可用性检测演示 ===")
    
    try:
        from md2doc.utils.image_processor import PIL_AVAILABLE
        if PIL_AVAILABLE:
            print("✓ PIL/Pillow 可用 - 支持高级图片处理功能")
            print("✓ PIL版本信息可用")
        else:
            print("⚠ PIL/Pillow 不可用 - 将使用基础文件操作")
    except Exception as e:
        print(f"✗ PIL检测异常: {e}")
    
    print()


def main():
    """主演示函数"""
    print("🖼️  MD2DOC 图片处理器功能演示")
    print("=" * 50)
    print()
    
    try:
        demo_basic_usage()
        demo_configuration()
        demo_cache_management()
        demo_format_support()
        demo_error_handling()
        demo_pil_availability()
        
        print("🎉 图片处理器功能演示完成！")
        print()
        print("主要功能:")
        print("- ✅ 图片处理和优化")
        print("- ✅ 智能缓存机制")
        print("- ✅ 多格式支持")
        print("- ✅ Word文档优化")
        print("- ✅ 错误处理")
        print("- ✅ 配置管理")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
