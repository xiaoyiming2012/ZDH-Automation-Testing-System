#!/usr/bin/env python3
"""
简化的测试报告生成器
"""

import json
import time
from datetime import datetime
from pathlib import Path

class SimpleTestReport:
    """简化的测试报告生成器"""
    
    def __init__(self):
        """初始化"""
        self.report_data = {
            "test_case": "打开桌面上的info.json",
            "execution_time": "",
            "status": "",
            "steps": [],
            "performance": {},
            "summary": ""
        }
        
        # 创建报告目录
        self.report_dir = Path("test_reports")
        self.report_dir.mkdir(exist_ok=True)
    
    def add_step(self, step_name, status, details, time_taken):
        """添加测试步骤"""
        step = {
            "name": step_name,
            "status": status,
            "details": details,
            "time": time_taken
        }
        self.report_data["steps"].append(step)
    
    def set_performance(self, total_time, ocr_time, locate_time, open_time):
        """设置性能指标"""
        self.report_data["performance"] = {
            "total_time": total_time,
            "ocr_time": ocr_time,
            "locate_time": locate_time,
            "open_time": open_time
        }
    
    def set_status(self, status):
        """设置测试状态"""
        self.report_data["status"] = status
    
    def set_execution_time(self, execution_time):
        """设置执行时间"""
        self.report_data["execution_time"] = execution_time
    
    def generate_report(self):
        """生成测试报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 生成JSON报告
        json_filename = f"test_report_{timestamp}.json"
        json_path = self.report_dir / json_filename
        
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.report_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 测试报告已生成: {json_path}")
            
            # 显示报告摘要
            self._display_summary()
            
            return str(json_path)
            
        except Exception as e:
            print(f"❌ 生成报告失败: {e}")
            return None
    
    def _display_summary(self):
        """显示报告摘要"""
        print("\n" + "=" * 60)
        print("📊 测试报告摘要")
        print("=" * 60)
        print(f"测试用例: {self.report_data['test_case']}")
        print(f"执行状态: {self.report_data['status']}")
        print(f"执行时间: {self.report_data['execution_time']}")
        
        print(f"\n步骤详情:")
        for i, step in enumerate(self.report_data['steps'], 1):
            status_icon = "✅" if step['status'] == "PASS" else "❌"
            print(f"  {i}. {step['name']}: {status_icon} ({step['time']:.2f}秒)")
            print(f"     详情: {step['details']}")
        
        if self.report_data['performance']:
            perf = self.report_data['performance']
            print(f"\n性能指标:")
            print(f"  总时间: {perf['total_time']:.2f}秒")
            print(f"  OCR处理: {perf['ocr_time']:.2f}秒")
            print(f"  文件定位: {perf['locate_time']:.2f}秒")
            print(f"  文件打开: {perf['open_time']:.2f}秒")
        
        print("=" * 60)

def main():
    """演示报告生成"""
    print("🧪 简化测试报告生成器演示")
    
    # 创建报告
    report = SimpleTestReport()
    
    # 添加测试步骤
    report.add_step("检查文件存在性", "PASS", "文件info.json存在于桌面", 0.5)
    report.add_step("定位文件位置", "PASS", "通过OCR成功定位文件位置(400, 300)", 2.3)
    report.add_step("打开文件", "PASS", "双击成功打开文件", 1.2)
    
    # 设置性能指标
    report.set_performance(4.0, 2.3, 1.5, 1.2)
    
    # 设置状态和时间
    report.set_status("PASSED")
    report.set_execution_time("2025-01-13 10:30:00")
    
    # 生成报告
    report.generate_report()

if __name__ == "__main__":
    main()



