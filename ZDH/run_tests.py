#!/usr/bin/env python3
"""
测试运行器
执行所有单元测试并生成报告
"""

import sys
import unittest
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Windows自动化测试系统 - 单元测试")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 发现并运行测试
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # 创建测试运行器
    test_runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    # 运行测试
    print("发现测试用例:")
    for test in test_suite:
        print(f"  - {test}")
    print()
    
    result = test_runner.run(test_suite)
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # 返回退出码
    return 0 if result.wasSuccessful() else 1


def run_specific_test(test_name):
    """运行特定的测试"""
    print(f"运行特定测试: {test_name}")
    
    test_loader = unittest.TestLoader()
    test_suite = test_loader.loadTestsFromName(test_name)
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    return 0 if result.wasSuccessful() else 1


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 运行特定测试
        test_name = sys.argv[1]
        return run_specific_test(test_name)
    else:
        # 运行所有测试
        return run_all_tests()


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
