#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单框架测试脚本
验证统一自动化测试框架的基本功能
"""

import os
import sys
import time
import json

def test_framework_basic():
    """测试框架基本功能"""
    print("=== 测试框架基本功能 ===")
    
    try:
        from unified_automation_framework import UnifiedAutomationFramework
        
        # 创建框架实例
        framework = UnifiedAutomationFramework()
        
        print("✅ 框架实例创建成功")
        
        # 检查配置
        print(f"配置键: {list(framework.config.keys())}")
        
        # 检查目录创建
        for directory in ["screenshots", "reports", "logs", "data"]:
            if os.path.exists(directory):
                print(f"✅ 目录存在: {directory}")
            else:
                print(f"❌ 目录不存在: {directory}")
        
        # 测试截图功能
        try:
            screenshot_path = framework._capture_screenshot("test_screenshot.png")
            if os.path.exists(screenshot_path):
                print(f"✅ 截图功能正常: {screenshot_path}")
            else:
                print(f"❌ 截图功能异常: {screenshot_path}")
        except Exception as e:
            print(f"❌ 截图功能失败: {e}")
        
        # 测试文件查找功能
        try:
            # 创建一个测试文件
            test_file = os.path.join(os.path.expanduser("~"), "Desktop", "test_framework.txt")
            with open(test_file, 'w') as f:
                f.write("测试文件")
            
            found_file = framework._find_file_on_desktop("test_framework.txt")
            if found_file:
                print(f"✅ 文件查找功能正常: {found_file}")
            else:
                print(f"❌ 文件查找功能异常")
            
            # 清理测试文件
            if os.path.exists(test_file):
                os.remove(test_file)
                
        except Exception as e:
            print(f"❌ 文件查找功能失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 框架基本功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_loading():
    """测试配置加载功能"""
    print("\n=== 测试配置加载功能 ===")
    
    try:
        from unified_automation_framework import UnifiedAutomationFramework
        
        # 测试默认配置
        framework = UnifiedAutomationFramework()
        default_config = framework._get_default_config()
        
        print("✅ 默认配置生成成功")
        print(f"默认配置键: {list(default_config.keys())}")
        
        # 检查必要的配置项
        required_keys = ["ocr", "image_recognition", "ui_automation", "file_operations", "applications"]
        for key in required_keys:
            if key in default_config:
                print(f"✅ 配置项存在: {key}")
            else:
                print(f"❌ 配置项缺失: {key}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置加载测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_test_case_creation():
    """测试测试用例创建功能"""
    print("\n=== 测试测试用例创建功能 ===")
    
    try:
        from unified_automation_framework import UnifiedAutomationFramework
        
        framework = UnifiedAutomationFramework()
        
        # 测试文件打开测试用例创建
        file_test = framework.create_file_opening_test("test.txt")
        print(f"✅ 文件打开测试用例创建成功: {file_test.name}")
        print(f"   步骤数: {len(file_test.steps)}")
        
        # 测试应用程序打开测试用例创建
        app_test = framework.create_application_opening_test("notepad")
        print(f"✅ 应用程序打开测试用例创建成功: {app_test.name}")
        print(f"   步骤数: {len(app_test.steps)}")
        
        # 测试网页导航测试用例创建
        web_test = framework.create_web_navigation_test("www.example.com")
        print(f"✅ 网页导航测试用例创建成功: {web_test.name}")
        print(f"   步骤数: {len(web_test.steps)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试用例创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 统一自动化测试框架基本功能测试")
    print("=" * 50)
    
    results = []
    
    # 测试1: 基本功能
    results.append(test_framework_basic())
    
    # 测试2: 配置加载
    results.append(test_config_loading())
    
    # 测试3: 测试用例创建
    results.append(test_test_case_creation())
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"总测试数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    
    if passed == total:
        print("🎉 所有测试通过！框架基本功能正常")
    else:
        print("⚠️  部分测试失败，需要进一步检查")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
