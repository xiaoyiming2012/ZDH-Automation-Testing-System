#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一自动化测试框架演示脚本
展示如何使用框架执行各种自动化测试
"""

from unified_automation_framework import UnifiedAutomationFramework, TestCase, AutomationStep, ActionType
import time

def demo_file_opening():
    """演示文件打开功能"""
    print("\n=== 演示：文件打开功能 ===")
    
    framework = UnifiedAutomationFramework()
    
    # 创建文件打开测试用例
    test_case = framework.create_file_opening_test("info.json")
    
    print(f"测试用例: {test_case.name}")
    print(f"描述: {test_case.description}")
    print(f"步骤数: {len(test_case.steps)}")
    
    # 执行测试
    result = framework.execute_test_case(test_case)
    
    print(f"执行结果: {result['status']}")
    if result['status'] == 'passed':
        print("✅ 文件打开测试成功")
    else:
        print("❌ 文件打开测试失败")
        if 'error_message' in result:
            print(f"错误信息: {result['error_message']}")
    
    return result

def demo_application_opening():
    """演示应用程序打开功能"""
    print("\n=== 演示：应用程序打开功能 ===")
    
    framework = UnifiedAutomationFramework()
    
    # 创建应用程序打开测试用例
    test_case = framework.create_application_opening_test("github_desktop")
    
    print(f"测试用例: {test_case.name}")
    print(f"描述: {test_case.description}")
    print(f"步骤数: {len(test_case.steps)}")
    
    # 执行测试
    result = framework.execute_test_case(test_case)
    
    print(f"执行结果: {result['status']}")
    if result['status'] == 'passed':
        print("✅ 应用程序打开测试成功")
    else:
        print("❌ 应用程序打开测试失败")
        if 'error_message' in result:
            print(f"错误信息: {result['error_message']}")
    
    return result

def demo_web_navigation():
    """演示网页导航功能"""
    print("\n=== 演示：网页导航功能 ===")
    
    framework = UnifiedAutomationFramework()
    
    # 创建网页导航测试用例
    test_case = framework.create_web_navigation_test("www.baidu.com", "打开Edge浏览器，访问百度网站")
    
    print(f"测试用例: {test_case.name}")
    print(f"描述: {test_case.description}")
    print(f"步骤数: {len(test_case.steps)}")
    
    # 执行测试
    result = framework.execute_test_case(test_case)
    
    print(f"执行结果: {result['status']}")
    if result['status'] == 'passed':
        print("✅ 网页导航测试成功")
    else:
        print("❌ 网页导航测试失败")
        if 'error_message' in result:
            print(f"错误信息: {result['error_message']}")
    
    return result

def demo_custom_test_case():
    """演示自定义测试用例"""
    print("\n=== 演示：自定义测试用例 ===")
    
    framework = UnifiedAutomationFramework()
    
    # 创建自定义测试用例：打开文件，然后截图
    steps = [
        AutomationStep(
            step_id="step_001",
            action_type=ActionType.OPEN_FILE,
            description="打开桌面上的info.json文件",
            parameters={"filename": "info.json"},
            expected_result="文件成功打开",
            critical=True
        ),
        AutomationStep(
            step_id="step_002",
            action_type=ActionType.WAIT,
            description="等待文件打开",
            parameters={"time": 3},
            expected_result="等待完成",
            critical=False
        ),
        AutomationStep(
            step_id="step_003",
            action_type=ActionType.SCREENSHOT,
            description="截图验证文件打开状态",
            parameters={"filename": "custom_test_screenshot.png"},
            expected_result="成功截图",
            critical=False
        )
    ]
    
    test_case = TestCase(
        case_id="custom_file_test",
        name="自定义文件打开测试",
        description="演示如何创建自定义测试用例",
        steps=steps,
        tags=["custom", "file_operation"]
    )
    
    print(f"测试用例: {test_case.name}")
    print(f"描述: {test_case.description}")
    print(f"步骤数: {len(test_case.steps)}")
    
    # 执行测试
    result = framework.execute_test_case(test_case)
    
    print(f"执行结果: {result['status']}")
    if result['status'] == 'passed':
        print("✅ 自定义测试用例成功")
    else:
        print("❌ 自定义测试用例失败")
        if 'error_message' in result:
            print(f"错误信息: {result['error_message']}")
    
    return result

def demo_batch_execution():
    """演示批量执行测试用例"""
    print("\n=== 演示：批量执行测试用例 ===")
    
    framework = UnifiedAutomationFramework()
    
    # 创建多个测试用例
    test_cases = [
        framework.create_file_opening_test("info.json"),
        framework.create_application_opening_test("github_desktop"),
        framework.create_web_navigation_test("www.baidu.com", "访问百度网站")
    ]
    
    print(f"准备执行 {len(test_cases)} 个测试用例...")
    
    # 批量执行
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n执行测试用例 {i}/{len(test_cases)}: {test_case.name}")
        result = framework.execute_test_case(test_case)
        results.append(result)
        
        # 在测试用例之间稍作等待
        if i < len(test_cases):
            time.sleep(2)
    
    # 生成批量测试报告
    report_path = framework.generate_report(results, "batch_test_report.json")
    
    print(f"\n批量测试完成！报告已保存到: {report_path}")
    
    return results

def main():
    """主函数"""
    print("🚀 统一自动化测试框架演示")
    print("=" * 50)
    
    try:
        # 演示1: 文件打开功能
        demo_file_opening()
        
        # 等待一下
        time.sleep(2)
        
        # 演示2: 应用程序打开功能
        demo_application_opening()
        
        # 等待一下
        time.sleep(2)
        
        # 演示3: 网页导航功能
        demo_web_navigation()
        
        # 等待一下
        time.sleep(2)
        
        # 演示4: 自定义测试用例
        demo_custom_test_case()
        
        # 等待一下
        time.sleep(2)
        
        # 演示5: 批量执行
        demo_batch_execution()
        
        print("\n🎉 所有演示完成！")
        print("\n框架特点总结:")
        print("✅ 统一的测试用例管理")
        print("✅ 多种操作类型支持（文件、应用、网页）")
        print("✅ 自动截图和日志记录")
        print("✅ 详细的测试报告生成")
        print("✅ 灵活的配置管理")
        print("✅ 错误处理和重试机制")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
