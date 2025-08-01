"""
测试运行器

提供便捷的测试运行和覆盖率检查功能
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """运行所有测试"""
    project_root = Path(__file__).parent.parent
    
    # 切换到项目根目录
    import os
    os.chdir(project_root)
    
    # 运行pytest
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/md2doc/",
        "-v",
        "--cov=src/md2doc",
        "--cov-report=term-missing",
        "--cov-report=html:tests/coverage_html",
        "--cov-fail-under=80"
    ]
    
    print("运行MD2DOC测试...")
    print(f"命令: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    return result.returncode == 0


def run_specific_test(test_file):
    """运行特定测试文件"""
    project_root = Path(__file__).parent.parent
    
    import os
    os.chdir(project_root)
    
    cmd = [
        sys.executable, "-m", "pytest",
        f"tests/md2doc/{test_file}",
        "-v"
    ]
    
    print(f"运行测试文件: {test_file}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    return result.returncode == 0


def check_coverage():
    """检查测试覆盖率"""
    project_root = Path(__file__).parent.parent
    
    import os
    os.chdir(project_root)
    
    cmd = [
        sys.executable, "-m", "coverage",
        "report",
        "--include=src/md2doc/*"
    ]
    
    print("检查测试覆盖率...")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("覆盖率报告:")
    print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MD2DOC测试运行器")
    parser.add_argument("--file", help="运行特定测试文件")
    parser.add_argument("--coverage", action="store_true", help="只检查覆盖率")
    
    args = parser.parse_args()
    
    if args.coverage:
        success = check_coverage()
    elif args.file:
        success = run_specific_test(args.file)
    else:
        success = run_tests()
    
    if success:
        print("\n✅ 测试运行成功!")
    else:
        print("\n❌ 测试运行失败!")
        sys.exit(1)
