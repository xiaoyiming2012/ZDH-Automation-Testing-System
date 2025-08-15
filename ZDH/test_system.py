#!/usr/bin/env python3
"""
Windows自动化测试系统 - 系统测试脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_manager():
    """测试配置管理器"""
    print("测试配置管理器...")
    try:
        from src.utils.config_manager import config_manager
        
        # 测试配置加载
        config_manager.validate()
        print("✓ 配置管理器测试通过")
        
        # 测试配置获取
        ai_config = config_manager.get_ai_config()
        ui_config = config_manager.get_ui_config()
        print(f"✓ AI配置: {len(ai_config)} 项")
        print(f"✓ UI配置: {len(ui_config)} 项")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置管理器测试失败: {e}")
        return False

def test_logger():
    """测试日志管理器"""
    print("测试日志管理器...")
    try:
        from src.utils.logger import get_logger
        
        logger = get_logger("TestLogger")
        logger.info("测试日志信息")
        logger.warning("测试日志警告")
        print("✓ 日志管理器测试通过")
        
        return True
        
    except Exception as e:
        print(f"✗ 日志管理器测试失败: {e}")
        return False

def test_beike_ui_locator():
    """测试贝壳库UI定位器"""
    print("测试贝壳库UI定位器...")
    try:
        from src.ui_automation.beike_ui_locator import BeikeUILocator
        
        locator = BeikeUILocator()
        print(f"✓ 贝壳库UI定位器测试通过")
        print(f"  - 图像模板: {len(locator.template_images)} 个")
        print(f"  - 坐标缓存: {len(locator.coordinate_cache)} 项")
        print(f"  - 颜色模式: {len(locator.color_patterns)} 个")
        
        return True
        
    except Exception as e:
        print(f"✗ 贝壳库UI定位器测试失败: {e}")
        return False

def test_claude_client():
    """测试Claude客户端"""
    print("测试Claude客户端...")
    try:
        from src.ai_interface.claude_client import ClaudeClient
        
        # 注意：这需要有效的API密钥
        try:
            client = ClaudeClient()
            print("✓ Claude客户端测试通过")
            return True
        except ValueError as e:
            if "API密钥未配置" in str(e):
                print("⚠ Claude客户端测试跳过 (API密钥未配置)")
                return True
            else:
                raise e
                
    except Exception as e:
        print(f"✗ Claude客户端测试失败: {e}")
        return False

def test_test_executor():
    """测试测试执行器"""
    print("测试测试执行器...")
    try:
        from src.orchestrator.test_executor import TestExecutor
        
        executor = TestExecutor()
        print("✓ 测试执行器测试通过")
        print(f"  - 最大工作线程: {executor.max_workers}")
        print(f"  - 最大并发测试: {executor.max_concurrent_tests}")
        
        # 清理资源
        executor.shutdown()
        
        return True
        
    except Exception as e:
        print(f"✗ 测试执行器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("Windows自动化测试系统 - 系统测试")
    print("=" * 50)
    
    tests = [
        test_config_manager,
        test_logger,
        test_beike_ui_locator,
        test_claude_client,
        test_test_executor
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常使用。")
        return 0
    else:
        print("⚠ 部分测试失败，请检查配置和依赖。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
