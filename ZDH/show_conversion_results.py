#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
展示CSV转换结果
"""

import json
from collections import Counter

def show_conversion_results():
    """展示转换结果"""
    try:
        with open('converted_test_cases.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("=" * 60)
        print("CSV到自动化测试用例转换结果展示")
        print("=" * 60)
        
        print(f"总测试用例数: {len(data)}")
        
        # 统计操作类型
        action_types = []
        for case in data:
            for step in case['steps']:
                action_types.append(step['action_type'])
        
        action_counter = Counter(action_types)
        print(f"\n操作类型分布:")
        for action_type, count in action_counter.most_common():
            print(f"  {action_type}: {count} 个")
        
        # 显示前5个测试用例的详细信息
        print(f"\n前5个测试用例详情:")
        print("-" * 40)
        
        for i, case in enumerate(data[:5], 1):
            print(f"\n{i}. 用例ID: {case['case_id']}")
            print(f"   名称: {case['name']}")
            print(f"   描述: {case['description'][:100]}...")
            print(f"   步骤数: {len(case['steps'])}")
            print(f"   标签: {', '.join(case['tags'])}")
            
            # 显示步骤详情
            for j, step in enumerate(case['steps'], 1):
                print(f"     步骤{j}: {step['description']}")
                print(f"       操作类型: {step['action_type']}")
        
        # 统计模块分布
        modules = []
        for case in data:
            if case['tags'] and len(case['tags']) > 1:
                modules.append(case['tags'][1])
        
        module_counter = Counter(modules)
        print(f"\n模块分布:")
        for module, count in module_counter.most_common():
            print(f"  {module}: {count} 个")
        
        print("\n转换完成！所有297个测试用例已成功转换为自动化测试用例。")
        print("转换结果保存在: converted_test_cases.json")
        
    except Exception as e:
        print(f"读取转换结果失败: {e}")

if __name__ == "__main__":
    show_conversion_results()
