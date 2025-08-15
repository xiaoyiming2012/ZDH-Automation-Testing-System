#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行转换后的自动化测试用例
"""

import json
import time
from datetime import datetime
from unified_automation_framework import UnifiedAutomationFramework, TestCase, AutomationStep, ActionType

def load_converted_test_cases(file_path: str = "converted_test_cases.json"):
    """加载转换后的测试用例"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"成功加载 {len(data)} 个测试用例")
        return data
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

def execute_test_cases(test_cases, max_cases=10, start_index=0):
    """执行测试用例"""
    if not test_cases:
        print("没有可执行的测试用例")
        return
    
    # 创建框架实例
    framework = UnifiedAutomationFramework()
    
    # 选择要执行的测试用例
    end_index = min(start_index + max_cases, len(test_cases))
    selected_cases = test_cases[start_index:end_index]
    
    print(f"\n开始执行测试用例 (第{start_index+1}-{end_index}个，共{len(selected_cases)}个)")
    print("=" * 60)
    
    # 执行统计
    total_cases = len(selected_cases)
    passed_cases = 0
    failed_cases = 0
    execution_results = []
    
    for i, json_case in enumerate(selected_cases, 1):
        print(f"\n执行测试用例 {i}/{total_cases}: {json_case['case_id']} - {json_case['name']}")
        print("-" * 50)
        
        try:
            # 转换为TestCase对象
            test_case = convert_json_to_test_case(json_case)
            
            # 执行测试用例
            start_time = time.time()
            result = framework.execute_test_case(test_case)
            execution_time = time.time() - start_time
            
            # 记录结果
            case_result = {
                'case_id': json_case['case_id'],
                'name': json_case['name'],
                'success': result['success'],
                'execution_time': execution_time,
                'step_results': result.get('step_results', []),
                'error_message': result.get('error_message', '')
            }
            execution_results.append(case_result)
            
            # 显示结果
            status = "✓ 成功" if result['success'] else "✗ 失败"
            print(f"执行结果: {status}")
            print(f"执行时间: {execution_time:.2f}秒")
            
            if result['success']:
                passed_cases += 1
            else:
                failed_cases += 1
                print(f"错误信息: {result.get('error_message', '未知错误')}")
            
            # 显示步骤结果
            for step_result in result.get('step_results', []):
                step_status = "✓" if step_result['success'] else "✗"
                print(f"  {step_status} {step_result['step_id']}: {step_result['description']}")
            
        except Exception as e:
            print(f"执行异常: {e}")
            failed_cases += 1
            execution_results.append({
                'case_id': json_case['case_id'],
                'name': json_case['name'],
                'success': False,
                'execution_time': 0,
                'step_results': [],
                'error_message': str(e)
            })
        
        print("-" * 30)
    
    # 生成执行报告
    generate_execution_report(execution_results, passed_cases, failed_cases, total_cases)
    
    return execution_results

def generate_execution_report(results, passed, failed, total):
    """生成执行报告"""
    print("\n" + "=" * 60)
    print("测试执行报告")
    print("=" * 60)
    
    print(f"总测试用例数: {total}")
    print(f"成功: {passed} 个 ({passed/total*100:.1f}%)")
    print(f"失败: {failed} 个 ({failed/total*100:.1f}%)")
    
    # 统计操作类型
    action_type_stats = {}
    for result in results:
        for step_result in result['step_results']:
            action_type = step_result.get('action_type', 'unknown')
            action_type_stats[action_type] = action_type_stats.get(action_type, 0) + 1
    
    print(f"\n操作类型统计:")
    for action_type, count in action_type_stats.items():
        print(f"  {action_type}: {count} 个")
    
    # 保存详细报告
    report_file = f"test_execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_cases': total,
                    'passed_cases': passed,
                    'failed_cases': failed,
                    'pass_rate': passed/total*100 if total > 0 else 0,
                    'execution_time': datetime.now().isoformat()
                },
                'action_type_stats': action_type_stats,
                'detailed_results': results
            }, f, ensure_ascii=False, indent=2)
        print(f"\n详细报告已保存到: {report_file}")
    except Exception as e:
        print(f"保存报告失败: {e}")

def main():
    """主函数"""
    print("执行转换后的自动化测试用例")
    print("=" * 40)
    
    # 加载测试用例
    test_cases = load_converted_test_cases()
    if not test_cases:
        return
    
    # 询问执行参数
    try:
        max_cases = int(input(f"请输入要执行的测试用例数量 (1-{len(test_cases)}, 默认10): ") or "10")
        max_cases = min(max_cases, len(test_cases))
        
        start_index = int(input(f"请输入起始索引 (0-{len(test_cases)-1}, 默认0): ") or "0")
        start_index = max(0, min(start_index, len(test_cases)-1))
        
    except ValueError:
        print("输入无效，使用默认值")
        max_cases = 10
        start_index = 0
    
    # 执行测试用例
    results = execute_test_cases(test_cases, max_cases, start_index)
    
    print(f"\n执行完成！共执行了 {len(results)} 个测试用例")

if __name__ == "__main__":
    main()
