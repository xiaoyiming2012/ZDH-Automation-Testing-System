#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV to Automation Test Case Converter
读取read.csv文件，将测试用例转换为自动化测试用例
"""

import csv
import json
import os
import re
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from unified_automation_framework import UnifiedAutomationFramework, ActionType, AutomationStep, TestCase

@dataclass
class CSVTestCase:
    """CSV测试用例数据结构"""
    case_id: str
    product: str
    module: str
    requirements: str
    title: str
    preconditions: str
    steps: str
    expected_results: str
    actual_results: str
    keywords: str
    priority: str
    test_type: str
    applicable_stage: str
    status: str
    created_by: str
    created_date: str

class CSVToAutomationConverter:
    """CSV到自动化测试用例转换器"""
    
    def __init__(self, csv_file_path: str = "read.csv"):
        self.csv_file_path = csv_file_path
        self.framework = UnifiedAutomationFramework()
        self.converted_cases = []
        
    def read_csv_file(self) -> List[CSVTestCase]:
        """读取CSV文件"""
        test_cases = []
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    test_case = CSVTestCase(
                        case_id=row.get('用例编号', ''),
                        product=row.get('所属产品', ''),
                        module=row.get('所属模块', ''),
                        requirements=row.get('相关研发需求', ''),
                        title=row.get('用例标题', ''),
                        preconditions=row.get('前置条件', ''),
                        steps=row.get('步骤', ''),
                        expected_results=row.get('预期', ''),
                        actual_results=row.get('实际情况', ''),
                        keywords=row.get('关键词', ''),
                        priority=row.get('优先级', ''),
                        test_type=row.get('用例类型', ''),
                        applicable_stage=row.get('适用阶段', ''),
                        status=row.get('用例状态', ''),
                        created_by=row.get('由谁创建', ''),
                        created_date=row.get('创建日期', '')
                    )
                    test_cases.append(test_case)
                    
            print(f"成功读取 {len(test_cases)} 个测试用例")
            return test_cases
            
        except Exception as e:
            print(f"读取CSV文件失败: {e}")
            return []
    
    def parse_steps(self, steps_text: str) -> List[str]:
        """解析步骤文本"""
        if not steps_text:
            return []
        
        # 按数字编号分割步骤
        steps = re.split(r'\d+\.\s*', steps_text)
        # 过滤空字符串并清理
        steps = [step.strip() for step in steps if step.strip()]
        return steps
    
    def parse_expected_results(self, expected_text: str) -> List[str]:
        """解析预期结果文本"""
        if not expected_text:
            return []
        
        # 按数字编号分割预期结果
        results = re.split(r'\d+\.\s*', expected_text)
        # 过滤空字符串并清理
        results = [result.strip() for result in results if result.strip()]
        return results
    
    def convert_step_to_automation(self, step: str, expected_result: str = "") -> List[AutomationStep]:
        """将单个步骤转换为自动化步骤"""
        automation_steps = []
        
        # 清理步骤文本
        step = step.strip()
        if not step:
            return automation_steps
        
        # 根据步骤内容判断自动化类型
        step_lower = step.lower()
        
        # 打开文件相关
        if any(keyword in step_lower for keyword in ['打开', 'open', '点击打开']):
            if 'pdf' in step_lower or '文件' in step_lower:
                automation_steps.append(AutomationStep(
                    step_id=f"step_{len(automation_steps)+1}",
                    description=f"打开PDF文件: {step}",
                    action_type=ActionType.OPEN_FILE,
                    parameters={"file_path": "sample.pdf", "timeout": 30},
                    expected_result=expected_result
                ))
        
        # 点击操作
        elif any(keyword in step_lower for keyword in ['点击', 'click', '选中']):
            automation_steps.append(AutomationStep(
                step_id=f"step_{len(automation_steps)+1}",
                description=f"点击操作: {step}",
                action_type=ActionType.CLICK,
                parameters={"element": "button", "timeout": 10},
                expected_result=expected_result
            ))
        
        # 输入文本
        elif any(keyword in step_lower for keyword in ['输入', 'input', '输入框', '输入内容']):
            automation_steps.append(AutomationStep(
                step_id=f"step_{len(automation_steps)+1}",
                description=f"输入文本: {step}",
                action_type=ActionType.TYPE,
                parameters={"text": "test_text", "timeout": 10},
                expected_result=expected_result
            ))
        
        # 等待操作
        elif any(keyword in step_lower for keyword in ['等待', 'wait', '等待加载']):
            automation_steps.append(AutomationStep(
                step_id=f"step_{len(automation_steps)+1}",
                description=f"等待操作: {step}",
                action_type=ActionType.WAIT,
                parameters={"duration": 5},
                expected_result=expected_result
            ))
        
        # 截图操作
        elif any(keyword in step_lower for keyword in ['截图', 'screenshot', '保存']):
            automation_steps.append(AutomationStep(
                step_id=f"step_{len(automation_steps)+1}",
                description=f"截图操作: {step}",
                action_type=ActionType.SCREENSHOT,
                parameters={"filename": f"screenshot_{len(automation_steps)+1}"},
                expected_result=expected_result
            ))
        
        # 默认操作 - 点击
        else:
            automation_steps.append(AutomationStep(
                step_id=f"step_{len(automation_steps)+1}",
                description=f"执行操作: {step}",
                action_type=ActionType.CLICK,
                parameters={"element": "ui_element", "timeout": 10},
                expected_result=expected_result
            ))
        
        return automation_steps
    
    def convert_test_case(self, csv_case: CSVTestCase) -> TestCase:
        """转换单个测试用例"""
        # 解析步骤和预期结果
        steps = self.parse_steps(csv_case.steps)
        expected_results = self.parse_expected_results(csv_case.expected_results)
        
        # 转换自动化步骤
        automation_steps = []
        for i, step in enumerate(steps):
            expected_result = expected_results[i] if i < len(expected_results) else ""
            step_automation = self.convert_step_to_automation(step, expected_result)
            automation_steps.extend(step_automation)
        
        # 创建测试用例
        test_case = TestCase(
            case_id=csv_case.case_id,
            name=csv_case.title,
            description=f"产品: {csv_case.product}\n模块: {csv_case.module}\n前置条件: {csv_case.preconditions}",
            preconditions=[],
            steps=automation_steps,
            postconditions=[],
            tags=[csv_case.test_type, csv_case.module, csv_case.keywords] if csv_case.keywords else [csv_case.test_type, csv_case.module]
        )
        
        return test_case
    
    def convert_all_cases(self) -> List[TestCase]:
        """转换所有测试用例"""
        csv_cases = self.read_csv_file()
        converted_cases = []
        
        for csv_case in csv_cases:
            try:
                converted_case = self.convert_test_case(csv_case)
                converted_cases.append(converted_case)
                print(f"转换测试用例: {csv_case.case_id} - {csv_case.title}")
            except Exception as e:
                print(f"转换测试用例失败 {csv_case.case_id}: {e}")
        
        self.converted_cases = converted_cases
        return converted_cases
    
    def save_converted_cases(self, output_file: str = "converted_test_cases.json"):
        """保存转换后的测试用例"""
        if not self.converted_cases:
            print("没有可保存的测试用例")
            return
        
        # 转换为字典格式
        cases_dict = []
        for case in self.converted_cases:
            case_dict = {
                "case_id": case.case_id,
                "name": case.name,
                "description": case.description,
                "tags": case.tags,
                "steps": []
            }
            
            for step in case.steps:
                step_dict = {
                    "step_id": step.step_id,
                    "description": step.description,
                    "action_type": step.action_type.value,
                    "parameters": step.parameters,
                    "expected_result": step.expected_result
                }
                case_dict["steps"].append(step_dict)
            
            cases_dict.append(case_dict)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(cases_dict, f, ensure_ascii=False, indent=2)
            print(f"成功保存 {len(cases_dict)} 个转换后的测试用例到 {output_file}")
        except Exception as e:
            print(f"保存文件失败: {e}")
    
    def execute_sample_cases(self, max_cases: int = 5):
        """执行示例测试用例"""
        if not self.converted_cases:
            print("没有可执行的测试用例")
            return
        
        # 选择前几个测试用例执行
        sample_cases = self.converted_cases[:max_cases]
        
        print(f"\n开始执行 {len(sample_cases)} 个示例测试用例:")
        print("=" * 50)
        
        for i, test_case in enumerate(sample_cases, 1):
            print(f"\n执行测试用例 {i}: {test_case.name}")
            print(f"原始用例ID: {test_case.case_id}")
            print(f"描述: {test_case.description[:100]}...")
            
            try:
                # 执行测试用例
                result = self.framework.execute_test_case(test_case)
                
                print(f"执行结果: {'成功' if result['success'] else '失败'}")
                print(f"执行时间: {result['execution_time']:.2f}秒")
                
                # 显示步骤结果
                for step_result in result['step_results']:
                    status = "✓" if step_result['success'] else "✗"
                    print(f"  {status} {step_result['step_id']}: {step_result['description']}")
                
            except Exception as e:
                print(f"执行失败: {e}")
            
            print("-" * 30)
    
    def generate_summary_report(self):
        """生成转换摘要报告"""
        if not self.converted_cases:
            print("没有转换的测试用例")
            return
        
        print("\n" + "=" * 60)
        print("CSV到自动化测试用例转换摘要报告")
        print("=" * 60)
        
        # 统计信息
        total_cases = len(self.converted_cases)
        priority_stats = {}
        module_stats = {}
        action_type_stats = {}
        
        for case in self.converted_cases:
            # 优先级统计 - 从case_id中提取优先级信息
            priority = case.case_id[:2] if case.case_id else '未知'
            priority_stats[priority] = priority_stats.get(priority, 0) + 1
            
            # 模块统计 - 从tags中提取模块信息
            module = case.tags[1] if len(case.tags) > 1 else '未知'
            module_stats[module] = module_stats.get(module, 0) + 1
            
            # 操作类型统计
            for step in case.steps:
                action_type = step.action_type.value
                action_type_stats[action_type] = action_type_stats.get(action_type, 0) + 1
        
        print(f"总测试用例数: {total_cases}")
        
        print(f"\n优先级分布:")
        for priority, count in sorted(priority_stats.items()):
            print(f"  {priority}: {count} 个")
        
        print(f"\n模块分布:")
        for module, count in sorted(module_stats.items()):
            print(f"  {module}: {count} 个")
        
        print(f"\n操作类型分布:")
        for action_type, count in sorted(action_type_stats.items()):
            print(f"  {action_type}: {count} 个")
        
        print("=" * 60)

def main():
    """主函数"""
    print("CSV到自动化测试用例转换器")
    print("=" * 40)
    
    # 创建转换器
    converter = CSVToAutomationConverter("read.csv")
    
    # 转换所有测试用例
    print("开始转换测试用例...")
    converted_cases = converter.convert_all_cases()
    
    if not converted_cases:
        print("没有成功转换的测试用例")
        return
    
    # 保存转换结果
    converter.save_converted_cases()
    
    # 生成摘要报告
    converter.generate_summary_report()
    
    # 询问是否执行示例
    try:
        user_input = input("\n是否执行示例测试用例? (y/n): ").lower().strip()
        if user_input in ['y', 'yes', '是']:
            converter.execute_sample_cases(3)
    except KeyboardInterrupt:
        print("\n用户取消执行")
    
    print("\n转换完成!")

if __name__ == "__main__":
    main()
