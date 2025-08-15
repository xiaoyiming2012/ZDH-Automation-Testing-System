#!/usr/bin/env python3
"""
测试报告生成器
为自动化测试用例生成详细的测试报告
"""

import json
import time
from datetime import datetime
from pathlib import Path

class TestReportGenerator:
    """测试报告生成器"""
    
    def __init__(self):
        """初始化"""
        self.report_data = {
            "test_case_info": {},
            "execution_summary": {},
            "step_results": [],
            "performance_metrics": {},
            "screenshots": [],
            "logs": [],
            "recommendations": []
        }
        
        # 创建报告目录
        self.report_dir = Path("test_reports")
        self.report_dir.mkdir(exist_ok=True)
    
    def load_test_config(self, config_file="test_case_config.json"):
        """加载测试配置"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.report_data["test_case_info"] = config["test_case"]
            self.report_data["test_steps"] = config["test_steps"]
            
            return True
        except Exception as e:
            print(f"加载测试配置失败: {e}")
            return False
    
    def add_execution_result(self, step_id, step_name, status, details, execution_time):
        """添加执行结果"""
        step_result = {
            "step_id": step_id,
            "step_name": step_name,
            "status": status,  # PASS, FAIL, SKIP
            "details": details,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }
        
        self.report_data["step_results"].append(step_result)
    
    def add_performance_metrics(self, total_time, ocr_time, file_locate_time, open_time):
        """添加性能指标"""
        self.report_data["performance_metrics"] = {
            "total_execution_time": total_time,
            "ocr_processing_time": ocr_time,
            "file_locating_time": file_locate_time,
            "file_opening_time": open_time,
            "average_step_time": total_time / len(self.report_data["step_results"]) if self.report_data["step_results"] else 0
        }
    
    def add_screenshot(self, screenshot_path, description):
        """添加截图信息"""
        screenshot_info = {
            "path": str(screenshot_path),
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        
        self.report_data["screenshots"].append(screenshot_info)
    
    def add_log(self, log_level, message, timestamp=None):
        """添加日志信息"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        log_entry = {
            "level": log_level,
            "message": message,
            "timestamp": timestamp
        }
        
        self.report_data["logs"].append(log_entry)
    
    def add_recommendation(self, recommendation_type, description, priority):
        """添加建议"""
        recommendation = {
            "type": recommendation_type,  # IMPROVEMENT, BUG_FIX, OPTIMIZATION
            "description": description,
            "priority": priority,  # HIGH, MEDIUM, LOW
            "timestamp": datetime.now().isoformat()
        }
        
        self.report_data["recommendations"].append(recommendation)
    
    def generate_summary(self):
        """生成执行摘要"""
        total_steps = len(self.report_data["step_results"])
        passed_steps = len([s for s in self.report_data["step_results"] if s["status"] == "PASS"])
        failed_steps = len([s for s in self.report_data["step_results"] if s["status"] == "FAIL"])
        skipped_steps = len([s for s in self.report_data["step_results"] if s["status"] == "SKIP"])
        
        overall_status = "PASS" if failed_steps == 0 else "FAIL"
        
        self.report_data["execution_summary"] = {
            "overall_status": overall_status,
            "total_steps": total_steps,
            "passed_steps": passed_steps,
            "failed_steps": failed_steps,
            "skipped_steps": skipped_steps,
            "success_rate": (passed_steps / total_steps * 100) if total_steps > 0 else 0,
            "execution_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def generate_html_report(self):
        """生成HTML格式的测试报告"""
        html_content = self._get_html_template()
        
        # 生成报告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"test_report_{timestamp}.html"
        report_path = self.report_dir / report_filename
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ HTML测试报告已生成: {report_path}")
            return str(report_path)
            
        except Exception as e:
            print(f"❌ 生成HTML报告失败: {e}")
            return None
    
    def _get_html_template(self):
        """获取HTML模板"""
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>自动化测试报告 - {self.report_data.get('test_case_info', {}).get('name', '未知测试')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .summary {{
            padding: 30px;
            border-bottom: 1px solid #eee;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .status-pass {{
            color: #28a745;
        }}
        .status-fail {{
            color: #dc3545;
        }}
        .status-skip {{
            color: #ffc107;
        }}
        .steps {{
            padding: 30px;
        }}
        .step-item {{
            background: #f8f9fa;
            margin: 15px 0;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #ddd;
        }}
        .step-item.pass {{
            border-left-color: #28a745;
        }}
        .step-item.fail {{
            border-left-color: #dc3545;
        }}
        .step-item.skip {{
            border-left-color: #ffc107;
        }}
        .step-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .step-title {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        .step-status {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .step-status.pass {{
            background: #d4edda;
            color: #155724;
        }}
        .step-status.fail {{
            background: #f8d7da;
            color: #721c24;
        }}
        .step-status.skip {{
            background: #fff3cd;
            color: #856404;
        }}
        .step-details {{
            color: #666;
            margin-top: 10px;
        }}
        .performance {{
            padding: 30px;
            background: #f8f9fa;
        }}
        .performance h3 {{
            margin-top: 0;
            color: #333;
        }}
        .performance-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }}
        .performance-item {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .performance-item .label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }}
        .performance-item .value {{
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }}
        .recommendations {{
            padding: 30px;
        }}
        .recommendation-item {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            margin: 10px 0;
            border-radius: 6px;
        }}
        .recommendation-priority {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .priority-high {{
            background: #f8d7da;
            color: #721c24;
        }}
        .priority-medium {{
            background: #fff3cd;
            color: #856404;
        }}
        .priority-low {{
            background: #d1ecf1;
            color: #0c5460;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 自动化测试报告</h1>
            <p>{self.report_data.get('test_case_info', {}).get('description', '')}</p>
        </div>
        
        <div class="summary">
            <h2>📊 执行摘要</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>总体状态</h3>
                    <div class="value status-{self.report_data.get('execution_summary', {}).get('overall_status', 'UNKNOWN').lower()}">
                        {self.report_data.get('execution_summary', {}).get('overall_status', 'UNKNOWN')}
                    </div>
                </div>
                <div class="summary-card">
                    <h3>总步骤数</h3>
                    <div class="value">{self.report_data.get('execution_summary', {}).get('total_steps', 0)}</div>
                </div>
                <div class="summary-card">
                    <h3>通过步骤</h3>
                    <div class="value status-pass">{self.report_data.get('execution_summary', {}).get('passed_steps', 0)}</div>
                </div>
                <div class="summary-card">
                    <h3>失败步骤</h3>
                    <div class="value status-fail">{self.report_data.get('execution_summary', {}).get('failed_steps', 0)}</div>
                </div>
                <div class="summary-card">
                    <h3>跳过步骤</h3>
                    <div class="value status-skip">{self.report_data.get('execution_summary', {}).get('skipped_steps', 0)}</div>
                </div>
                <div class="summary-card">
                    <h3>成功率</h3>
                    <div class="value">{self.report_data.get('execution_summary', {}).get('success_rate', 0):.1f}%</div>
                </div>
            </div>
        </div>
        
        <div class="steps">
            <h2>📋 步骤详情</h2>
            {self._generate_steps_html()}
        </div>
        
        <div class="performance">
            <h3>⚡ 性能指标</h3>
            <div class="performance-grid">
                {self._generate_performance_html()}
            </div>
        </div>
        
        {self._generate_recommendations_html()}
        
        <div style="padding: 30px; text-align: center; color: #666; border-top: 1px solid #eee;">
            <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>自动化测试框架 v1.0</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _generate_steps_html(self):
        """生成步骤HTML"""
        html = ""
        for step in self.report_data.get("step_results", []):
            status_class = step.get("status", "UNKNOWN").lower()
            html += f"""
            <div class="step-item {status_class}">
                <div class="step-header">
                    <div class="step-title">步骤 {step.get('step_id')}: {step.get('step_name')}</div>
                    <div class="step-status {status_class}">{step.get('status')}</div>
                </div>
                <div class="step-details">
                    <p><strong>详情:</strong> {step.get('details')}</p>
                    <p><strong>执行时间:</strong> {step.get('execution_time', 0):.2f}秒</p>
                    <p><strong>时间戳:</strong> {step.get('timestamp')}</p>
                </div>
            </div>
            """
        return html
    
    def _generate_performance_html(self):
        """生成性能指标HTML"""
        metrics = self.report_data.get("performance_metrics", {})
        html = ""
        
        for key, value in metrics.items():
            if isinstance(value, float):
                display_value = f"{value:.2f}秒"
            else:
                display_value = str(value)
            
            label = key.replace("_", " ").title()
            html += f"""
            <div class="performance-item">
                <div class="label">{label}</div>
                <div class="value">{display_value}</div>
            </div>
            """
        
        return html
    
    def _generate_recommendations_html(self):
        """生成建议HTML"""
        if not self.report_data.get("recommendations"):
            return ""
        
        html = """
        <div class="recommendations">
            <h3>💡 改进建议</h3>
        """
        
        for rec in self.report_data.get("recommendations", []):
            priority_class = f"priority-{rec.get('priority', 'medium').lower()}"
            html += f"""
            <div class="recommendation-item">
                <div class="recommendation-priority {priority_class}">{rec.get('priority', 'MEDIUM')}</div>
                <p><strong>{rec.get('type', 'UNKNOWN')}:</strong> {rec.get('description', '')}</p>
            </div>
            """
        
        html += "</div>"
        return html
    
    def generate_json_report(self):
        """生成JSON格式的测试报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"test_report_{timestamp}.json"
        report_path = self.report_dir / report_filename
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.report_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ JSON测试报告已生成: {report_path}")
            return str(report_path)
            
        except Exception as e:
            print(f"❌ 生成JSON报告失败: {e}")
            return None

def main():
    """主函数 - 演示报告生成"""
    print("🧪 测试报告生成器演示")
    print("=" * 50)
    
    # 创建报告生成器
    generator = TestReportGenerator()
    
    # 加载测试配置
    if generator.load_test_config():
        print("✅ 测试配置加载成功")
    else:
        print("❌ 测试配置加载失败")
        return
    
    # 模拟测试结果
    generator.add_execution_result(1, "检查文件存在性", "PASS", "文件info.json存在于桌面", 0.5)
    generator.add_execution_result(2, "定位文件位置", "PASS", "通过OCR成功定位文件位置(400, 300)", 2.3)
    generator.add_execution_result(3, "打开文件", "PASS", "双击成功打开文件", 1.2)
    
    # 添加性能指标
    generator.add_performance_metrics(4.0, 2.3, 1.5, 1.2)
    
    # 添加建议
    generator.add_recommendation("OPTIMIZATION", "OCR处理时间可以进一步优化", "MEDIUM")
    generator.add_recommendation("IMPROVEMENT", "可以添加更多文件打开方式的回退策略", "LOW")
    
    # 生成摘要
    generator.generate_summary()
    
    # 生成报告
    html_report = generator.generate_html_report()
    json_report = generator.generate_json_report()
    
    if html_report and json_report:
        print("🎉 测试报告生成完成！")
        print(f"📄 HTML报告: {html_report}")
        print(f"📄 JSON报告: {json_report}")
    else:
        print("❌ 报告生成失败")

if __name__ == "__main__":
    main()





