#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前置条件检查功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from unified_automation_framework import UnifiedAutomationFramework, TestCase, AutomationStep, ActionType

def test_precondition_parsing():
    """测试前置条件解析功能"""
    print("测试前置条件解析功能")
    print("=" * 50)
    
    # 创建框架实例
    framework = UnifiedAutomationFramework()
    
    # 测试用例1：极光PDF相关
    test_case_1 = TestCase(
        case_id="test_001",
        name="极光PDF右键菜单测试",
        description="产品: 极光PDF阅读器\n模块: 核心用例\n前置条件: 1.打开PDF阅读器界面\n2.打开文件选取一段文字\n3.右键点击选取文字区域",
        steps=[
            AutomationStep(
                step_id="step_1",
                description="点击转换为可编辑文档",
                action_type=ActionType.CLICK,
                parameters={"element": "button", "timeout": 10},
                expected_result="点击转换菜单调起转换器成功"
            )
        ],
        preconditions=[],  # 空的前置条件，测试自动解析
        tags=["功能测试", "极光PDF"]
    )
    
    print(f"测试用例1: {test_case_1.name}")
    print(f"原始前置条件: {test_case_1.preconditions}")
    
    # 执行前置条件解析
    framework._parse_preconditions_from_description(test_case_1)
    print(f"解析后前置条件: {test_case_1.preconditions}")
    print()
    
    # 测试用例2：Adobe Reader相关
    test_case_2 = TestCase(
        case_id="test_002",
        name="Adobe Reader文件操作测试",
        description="产品: Adobe Reader\n模块: 文件操作\n功能: 打开PDF文件并验证",
        steps=[
            AutomationStep(
                step_id="step_1",
                description="打开PDF文件",
                action_type=ActionType.OPEN_FILE,
                parameters={"filename": "test.pdf", "timeout": 30},
                expected_result="文件成功打开"
            )
        ],
        preconditions=[],
        tags=["功能测试", "Adobe"]
    )
    
    print(f"测试用例2: {test_case_2.name}")
    print(f"原始前置条件: {test_case_2.preconditions}")
    
    # 执行前置条件解析
    framework._parse_preconditions_from_description(test_case_2)
    print(f"解析后前置条件: {test_case_2.preconditions}")
    print()
    
    # 测试用例3：WPS相关
    test_case_3 = TestCase(
        case_id="test_003",
        name="WPS文档编辑测试",
        description="产品: WPS Office\n模块: 文档编辑\n功能: 创建和编辑文档",
        steps=[
            AutomationStep(
                step_id="step_1",
                description="创建新文档",
                action_type=ActionType.CLICK,
                parameters={"element": "button", "timeout": 10},
                expected_result="新文档创建成功"
            )
        ],
        preconditions=[],
        tags=["功能测试", "WPS"]
    )
    
    print(f"测试用例3: {test_case_3.name}")
    print(f"原始前置条件: {test_case_3.preconditions}")
    
    # 执行前置条件解析
    framework._parse_preconditions_from_description(test_case_3)
    print(f"解析后前置条件: {test_case_3.preconditions}")
    print()

def test_software_check():
    """测试软件检查功能"""
    print("测试软件检查功能")
    print("=" * 50)
    
    # 创建框架实例
    framework = UnifiedAutomationFramework()
    
    # 检查极光PDF
    print("检查极光PDF:")
    print(f"  已安装: {framework.check_software_installed('极光PDF')}")
    print(f"  正在运行: {framework.check_software_running('极光PDF')}")
    print(f"  窗口存在: {framework.check_window_exists('极光PDF')}")
    print()
    
    # 检查Adobe Reader
    print("检查Adobe Reader:")
    print(f"  已安装: {framework.check_software_installed('Adobe Reader')}")
    print(f"  正在运行: {framework.check_software_running('Adobe Reader')}")
    print(f"  窗口存在: {framework.check_window_exists('Adobe Reader')}")
    print()
    
    # 检查WPS
    print("检查WPS:")
    print(f"  已安装: {framework.check_software_installed('WPS')}")
    print(f"  正在运行: {framework.check_software_running('WPS')}")
    print(f"  窗口存在: {framework.check_window_exists('WPS')}")
    print()

def main():
    """主函数"""
    print("前置条件检查功能测试")
    print("=" * 60)
    
    try:
        # 测试前置条件解析
        test_precondition_parsing()
        
        # 测试软件检查
        test_software_check()
        
        print("测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
