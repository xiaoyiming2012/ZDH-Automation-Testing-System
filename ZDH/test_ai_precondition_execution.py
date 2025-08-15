#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AI主动执行前置条件功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from unified_automation_framework import UnifiedAutomationFramework, TestCase, AutomationStep, ActionType

def test_ai_precondition_execution():
    """测试AI主动执行前置条件功能"""
    print("测试AI主动执行前置条件功能")
    print("=" * 60)
    
    # 创建框架实例
    framework = UnifiedAutomationFramework()
    
    # 测试用例：极光PDF右键菜单测试
    test_case = TestCase(
        case_id="test_ai_001",
        name="AI主动执行前置条件测试",
        description="产品: 极光PDF阅读器\n模块: 核心用例\n功能: 测试AI主动执行前置条件",
        steps=[
            AutomationStep(
                step_id="step_1",
                description="点击转换为可编辑文档",
                action_type=ActionType.CLICK,
                parameters={"element": "button", "timeout": 10},
                expected_result="点击转换菜单调起转换器成功"
            )
        ],
        preconditions=[
            "极光PDF已安装",
            "打开PDF阅读器界面",
            "打开文件",
            "选取一段文字",
            "右键点击选取文字区域"
        ],
        tags=["功能测试", "AI前置条件", "极光PDF"]
    )
    
    print(f"测试用例: {test_case.name}")
    print(f"前置条件: {test_case.preconditions}")
    print()
    
    print("开始执行前置条件...")
    print("-" * 40)
    
    # 执行前置条件
    success = framework.execute_preconditions(test_case)
    
    if success:
        print("✅ 所有前置条件执行成功！")
        print("现在可以执行测试步骤了")
        
        # 执行测试步骤
        print("\n开始执行测试步骤...")
        print("-" * 40)
        
        result = framework.execute_test_case(test_case)
        
        print(f"\n测试执行结果: {result.get('status', 'unknown')}")
        if result.get('error_message'):
            print(f"错误信息: {result['error_message']}")
        
    else:
        print("❌ 前置条件执行失败")
        print("无法继续执行测试用例")

def test_ai_software_launch():
    """测试AI启动软件功能"""
    print("\n测试AI启动软件功能")
    print("=" * 40)
    
    framework = UnifiedAutomationFramework()
    
    # 测试启动极光PDF
    print("测试启动极光PDF...")
    if framework._ai_open_pdf_reader():
        print("✅ AI成功启动PDF阅读器")
    else:
        print("❌ AI启动PDF阅读器失败")
    
    print()

def test_ai_file_operations():
    """测试AI文件操作功能"""
    print("\n测试AI文件操作功能")
    print("=" * 40)
    
    framework = UnifiedAutomationFramework()
    
    # 测试查找PDF文件
    print("测试查找PDF文件...")
    pdf_files = framework._find_pdf_files_on_desktop()
    if pdf_files:
        print(f"✅ AI找到 {len(pdf_files)} 个PDF文件:")
        for pdf in pdf_files[:3]:  # 只显示前3个
            print(f"  - {os.path.basename(pdf)}")
    else:
        print("❌ AI未找到PDF文件")
    
    print()

def test_ai_text_selection():
    """测试AI文字选择功能"""
    print("\n测试AI文字选择功能")
    print("=" * 40)
    
    framework = UnifiedAutomationFramework()
    
    # 测试查找可选择的文字区域
    print("测试查找可选择的文字区域...")
    text_regions = framework._find_selectable_text_regions()
    if text_regions:
        print(f"✅ AI找到 {len(text_regions)} 个可选择的文字区域")
        for i, region in enumerate(text_regions[:3]):  # 只显示前3个
            print(f"  区域 {i+1}: {region}")
    else:
        print("❌ AI未找到可选择的文字区域")
    
    print()

def main():
    """主函数"""
    print("AI主动执行前置条件功能测试")
    print("=" * 80)
    
    try:
        # 测试AI前置条件执行
        test_ai_precondition_execution()
        
        # 测试AI软件启动
        test_ai_software_launch()
        
        # 测试AI文件操作
        test_ai_file_operations()
        
        # 测试AI文字选择
        test_ai_text_selection()
        
        print("\n" + "=" * 80)
        print("测试完成！")
        print("\n说明：")
        print("1. AI会主动执行所有前置条件")
        print("2. 如果软件未安装，会提示安装")
        print("3. 如果软件未运行，AI会自动启动")
        print("4. 如果文件未打开，AI会自动查找并打开")
        print("5. 如果文字未选择，AI会自动选择")
        print("6. 如果右键菜单未出现，AI会自动右键点击")
        
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
