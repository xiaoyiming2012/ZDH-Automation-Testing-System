#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选择性执行测试用例
"""

import json
import time
from datetime import datetime
from unified_automation_framework import UnifiedAutomationFramework, TestCase, AutomationStep, ActionType

def load_test_cases():
    """加载测试用例"""
    try:
        with open('converted_test_cases.json', 'r', encoding='utf-8') as f:
            test_cases = json.load(f)
        print(f"成功加载 {len(test_cases)} 个测试用例")
        return test_cases
    except Exception as e:
        print(f"加载测试用例失败: {e}")
        return []

def convert_json_to_test_case(json_case):
    """将JSON格式的测试用例转换为TestCase对象"""
    steps = []
    for step_data in json_case['steps']:
        step = AutomationStep(
            step_id=step_data['step_id'],
            description=step_data['description'],
            action_type=ActionType(step_data['action_type']),
            parameters=step_data['parameters'],
            expected_result=step_data['expected_result']
        )
        steps.append(step)
    
    test_case = TestCase(
        case_id=json_case['case_id'],
        name=json_case['name'],
        description=json_case['description'],
        steps=steps,
        preconditions=[],
        postconditions=[],
        tags=json_case['tags']
    )
    return test_case

def show_test_cases_menu(test_cases, start_index=0, count=10):
    """显示测试用例菜单"""
    print(f"\n测试用例列表 (第{start_index+1}-{min(start_index+count, len(test_cases))}个):")
    print("-" * 80)
    
    for i in range(start_index, min(start_index + count, len(test_cases))):
        case = test_cases[i]
        print(f"{i+1:3d}. [{case['case_id']}] {case['name']}")
        print(f"     步骤数: {len(case['steps'])} | 标签: {', '.join(case['tags'])}")
        print(f"     描述: {case['description'][:60]}...")
        print()

def execute_single_test_case(framework, test_case):
    """执行单个测试用例"""
    print(f"\n执行测试用例: {test_case.case_id} - {test_case.name}")
    print("=" * 60)
    
    try:
        # 检查前置条件
        if hasattr(framework, 'execute_preconditions'):
            print("检查前置条件...")
            if not framework.execute_preconditions(test_case):
                print("❌ 前置条件检查失败，跳过此测试用例")
                return {
                    'success': False, 
                    'error_message': '前置条件检查失败',
                    'step_results': []
                }
            print("✅ 前置条件检查通过")
        
        start_time = time.time()
        result = framework.execute_test_case(test_case)
        execution_time = time.time() - start_time
        
        print(f"执行结果: {'✓ 成功' if result.get('status') == 'passed' else '✗ 失败'}")
        print(f"执行时间: {execution_time:.2f}秒")
        
        if result.get('status') != 'passed':
            print(f"错误信息: {result.get('error_message', '未知错误')}")
        
        # 显示步骤结果
        for step_result in result.get('steps', []):
            step_status = "✓" if step_result.get('status') == 'passed' else "✗"
            print(f"  {step_status} {step_result.get('step_id', 'unknown')}: {step_result.get('description', 'unknown')}")
        
        return {
            'success': result.get('status') == 'passed',
            'error_message': result.get('error_message'),
            'step_results': result.get('steps', [])
        }
        
    except Exception as e:
        print(f"执行异常: {e}")
        return {'success': False, 'error_message': str(e), 'step_results': []}

def main():
    """主函数"""
    print("选择性执行测试用例")
    print("=" * 40)
    
    # 加载测试用例
    test_cases = load_test_cases()
    if not test_cases:
        return
    
    # 创建框架实例
    framework = UnifiedAutomationFramework()
    
    current_index = 0
    page_size = 10
    
    while True:
        # 显示当前页的测试用例
        show_test_cases_menu(test_cases, current_index, page_size)
        
        print("操作选项:")
        print("1-10: 选择执行对应的测试用例")
        print("n: 下一页")
        print("p: 上一页")
        print("s: 搜索测试用例")
        print("q: 退出")
        
        choice = input("\n请选择操作: ").strip().lower()
        
        if choice == 'q':
            print("退出程序")
            break
        elif choice == 'n':
            current_index = min(current_index + page_size, len(test_cases) - page_size)
            if current_index < 0:
                current_index = 0
        elif choice == 'p':
            current_index = max(current_index - page_size, 0)
        elif choice == 's':
            keyword = input("请输入搜索关键词: ").strip()
            if keyword:
                found_cases = []
                for i, case in enumerate(test_cases):
                    if (keyword.lower() in case['name'].lower() or 
                        keyword.lower() in case['case_id'].lower() or
                        keyword.lower() in case['description'].lower()):
                        found_cases.append((i, case))
                
                if found_cases:
                    print(f"\n找到 {len(found_cases)} 个匹配的测试用例:")
                    for i, (idx, case) in enumerate(found_cases[:10]):
                        print(f"{i+1}. [{case['case_id']}] {case['name']}")
                    
                    if len(found_cases) > 10:
                        print("... (仅显示前10个)")
                    
                    # 选择要执行的测试用例
                    try:
                        select = int(input("请选择要执行的测试用例编号 (1-10): ")) - 1
                        if 0 <= select < len(found_cases):
                            selected_idx, selected_case = found_cases[select]
                            test_case = convert_json_to_test_case(selected_case)
                            execute_single_test_case(framework, test_case)
                    except (ValueError, IndexError):
                        print("选择无效")
                else:
                    print("未找到匹配的测试用例")
        else:
            try:
                case_num = int(choice)
                if 1 <= case_num <= page_size:
                    actual_index = current_index + case_num - 1
                    if actual_index < len(test_cases):
                        selected_case = test_cases[actual_index]
                        test_case = convert_json_to_test_case(selected_case)
                        execute_single_test_case(framework, test_case)
                        
                        # 询问是否继续
                        continue_choice = input("\n是否继续执行其他测试用例? (y/n): ").strip().lower()
                        if continue_choice not in ['y', 'yes', '是']:
                            break
                    else:
                        print("测试用例编号超出范围")
                else:
                    print("无效的选择")
            except ValueError:
                print("无效的输入")

if __name__ == "__main__":
    main()


