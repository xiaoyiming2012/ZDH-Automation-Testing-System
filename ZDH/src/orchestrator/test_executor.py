"""
测试执行器
负责管理测试用例和测试套件的执行
"""

import time
import uuid
from typing import Dict, Any, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json
from src.utils.logger import get_logger
from src.utils.config_manager import config_manager
from src.ui_automation.ui_executor import UIExecutor
from src.ai_interface.claude_client import ClaudeClient


class TestExecutor:
    """测试用例执行器"""
    
    def __init__(self):
        """初始化执行器"""
        self.logger = get_logger("TestExecutor")
        self.config = config_manager.get_test_config()
        
        # 组件初始化
        self.ui_executor = UIExecutor()
        self.ai_client = ClaudeClient()
        
        # 执行配置
        self.max_workers = self.config.get('parallel', {}).get('max_workers', 4)
        self.max_concurrent_tests = self.config.get('parallel', {}).get('max_concurrent_tests', 2)
        self.test_timeout = self.config.get('timeouts', {}).get('test_case', 300)
        self.step_timeout = self.config.get('timeouts', {}).get('test_step', 60)
        self.max_retries = self.config.get('retry', {}).get('max_attempts', 3)
        self.retry_delay = self.config.get('retry', {}).get('delay_between_attempts', 5)
        
        # 执行状态
        self.executions: Dict[str, Dict[str, Any]] = {}
        self.execution_queue: List[Dict[str, Any]] = []
        self.running_executions: List[str] = []
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        self.logger.info("测试执行器初始化成功")
    
    def execute_test_case(self, test_case: Dict[str, Any], 
                         environment: str = "default",
                         data_overrides: Dict[str, Any] = None,
                         beike_ui_config: Dict[str, Any] = None) -> str:
        """
        执行单个测试用例
        
        Args:
            test_case: 测试用例
            environment: 测试环境
            data_overrides: 数据覆盖
            beike_ui_config: 贝壳库UI配置
            
        Returns:
            执行ID
        """
        execution_id = str(uuid.uuid4())
        
        # 创建执行记录
        execution_record = {
            "id": execution_id,
            "test_case": test_case,
            "environment": environment,
            "data_overrides": data_overrides or {},
            "beike_ui_config": beike_ui_config or {},
            "status": "pending",
            "start_time": None,
            "end_time": None,
            "duration": 0,
            "results": [],
            "screenshots": [],
            "logs": [],
            "errors": []
        }
        
        self.executions[execution_id] = execution_record
        self.execution_queue.append(execution_id)
        
        self.logger.log_test_start(test_case.get('name', 'Unknown'), execution_id)
        
        # 异步执行
        future = self.executor.submit(
            self._execute_test_case_worker, execution_id
        )
        
        return execution_id
    
    def execute_test_suite(self, test_cases: List[Dict[str, Any]], 
                          environment: str = "default",
                          data_overrides: Dict[str, Any] = None,
                          beike_ui_config: Dict[str, Any] = None,
                          parallel: bool = True) -> List[str]:
        """
        执行测试套件
        
        Args:
            test_cases: 测试用例列表
            environment: 测试环境
            data_overrides: 数据覆盖
            beike_ui_config: 贝壳库UI配置
            parallel: 是否并行执行
            
        Returns:
            执行ID列表
        """
        execution_ids = []
        
        if parallel:
            # 并行执行
            futures = []
            for test_case in test_cases:
                execution_id = self.execute_test_case(
                    test_case, environment, data_overrides, beike_ui_config
                )
                execution_ids.append(execution_id)
            
            # 等待所有执行完成
            self._wait_for_executions(execution_ids)
            
        else:
            # 串行执行
            for test_case in test_cases:
                execution_id = self.execute_test_case(
                    test_case, environment, data_overrides, beike_ui_config
                )
                execution_ids.append(execution_id)
                
                # 等待当前执行完成
                self._wait_for_executions([execution_id])
        
        return execution_ids
    
    def _execute_test_case_worker(self, execution_id: str):
        """测试用例执行工作线程"""
        execution = self.executions[execution_id]
        test_case = execution["test_case"]
        
        try:
            # 更新状态
            execution["status"] = "running"
            execution["start_time"] = time.time()
            self.running_executions.append(execution_id)
            
            self.logger.info(f"开始执行测试用例: {test_case.get('name', 'Unknown')}")
            
            # 执行前置条件
            if not self._execute_preconditions(test_case, execution):
                execution["status"] = "failed"
                execution["errors"].append("前置条件执行失败")
                return
            
            # 执行测试步骤
            test_steps = test_case.get('test_steps', [])
            for step in test_steps:
                step_result = self._execute_test_step(step, execution)
                execution["results"].append(step_result)
                
                if not step_result["success"]:
                    # 步骤失败，记录错误并继续
                    execution["errors"].append(step_result["error"])
                    if step.get("critical", False):
                        # 关键步骤失败，停止执行
                        execution["status"] = "failed"
                        break
            
            # 执行后置条件
            self._execute_postconditions(test_case, execution)
            
            # 确定最终状态
            if execution["status"] != "failed":
                if execution["errors"]:
                    execution["status"] = "partial_success"
                else:
                    execution["status"] = "passed"
            
            # 计算执行时间
            execution["end_time"] = time.time()
            execution["duration"] = execution["end_time"] - execution["start_time"]
            
            self.logger.log_test_end(
                test_case.get('name', 'Unknown'), 
                execution_id, 
                execution["status"], 
                execution["duration"]
            )
            
        except Exception as e:
            execution["status"] = "error"
            execution["errors"].append(f"执行异常: {str(e)}")
            self.logger.log_error(e, f"测试用例执行失败: {execution_id}")
        
        finally:
            # 清理状态
            if execution_id in self.running_executions:
                self.running_executions.remove(execution_id)
    
    def _execute_test_step(self, step: Dict[str, Any], 
                          execution: Dict[str, Any]) -> Dict[str, Any]:
        """执行测试步骤"""
        step_id = step.get('step_id', 'unknown')
        action = step.get('action', '')
        target = step.get('target', '')
        
        self.logger.log_test_step(
            execution["id"], 
            f"步骤{step_id}: {action}", 
            "开始"
        )
        
        step_result = {
            "step_id": step_id,
            "action": action,
            "target": target,
            "start_time": time.time(),
            "end_time": None,
            "duration": 0,
            "success": False,
            "error": None,
            "screenshot": None,
            "details": {}
        }
        
        try:
            # 执行操作
            if action == "click":
                success = self.ui_executor.click_element(target)
                step_result["success"] = success
                if not success:
                    step_result["error"] = "点击操作失败"
            
            elif action == "input":
                input_data = step.get('input_data', '')
                success = self.ui_executor.input_text(target, input_data)
                step_result["success"] = success
                if not success:
                    step_result["error"] = "文本输入失败"
            
            elif action == "select":
                option = step.get('input_data', '')
                success = self.ui_executor.select_option(target, option)
                step_result["success"] = success
                if not success:
                    step_result["error"] = "选项选择失败"
            
            elif action == "wait":
                timeout = step.get('timeout', self.step_timeout)
                success = self.ui_executor.wait_for_element(target, timeout=timeout)
                step_result["success"] = success
                if not success:
                    step_result["error"] = "等待元素超时"
            
            elif action == "screenshot":
                screenshot_path = self.ui_executor.take_screenshot()
                step_result["success"] = screenshot_path is not None
                step_result["screenshot"] = screenshot_path
                if screenshot_path:
                    execution["screenshots"].append(screenshot_path)
                else:
                    step_result["error"] = "截图失败"
            
            elif action == "verify":
                expected_result = step.get('expected_result', '')
                actual_result = self.ui_executor.get_element_text(target)
                success = actual_result == expected_result
                step_result["success"] = success
                step_result["details"]["expected"] = expected_result
                step_result["details"]["actual"] = actual_result
                if not success:
                    step_result["error"] = f"验证失败: 期望 '{expected_result}', 实际 '{actual_result}'"
            
            elif action == "scroll":
                direction = step.get('input_data', 'down')
                success = self.ui_executor.scroll(target, direction)
                step_result["success"] = success
                if not success:
                    step_result["error"] = "滚动操作失败"
            
            else:
                step_result["error"] = f"不支持的操作类型: {action}"
                step_result["success"] = False
            
            # 记录步骤完成
            step_result["end_time"] = time.time()
            step_result["duration"] = step_result["end_time"] - step_result["start_time"]
            
            status = "成功" if step_result["success"] else "失败"
            self.logger.log_test_step(
                execution["id"], 
                f"步骤{step_id}: {action}", 
                status,
                step_result.get("error", "")
            )
            
        except Exception as e:
            step_result["error"] = f"步骤执行异常: {str(e)}"
            step_result["success"] = False
            self.logger.log_error(e, f"测试步骤执行失败: {step_id}")
        
        return step_result
    
    def _execute_preconditions(self, test_case: Dict[str, Any], 
                             execution: Dict[str, Any]) -> bool:
        """执行前置条件"""
        preconditions = test_case.get('preconditions', [])
        
        for precondition in preconditions:
            try:
                # 这里可以执行各种前置条件，如启动应用、准备数据等
                self.logger.info(f"执行前置条件: {precondition}")
                
                # 示例：启动应用程序
                if precondition.startswith("启动应用:"):
                    app_path = precondition.split(":", 1)[1].strip()
                    if not self.ui_executor.connect_to_application(app_path):
                        self.logger.error(f"启动应用失败: {app_path}")
                        return False
                
                # 示例：等待元素出现
                elif precondition.startswith("等待元素:"):
                    element_name = precondition.split(":", 1)[1].strip()
                    if not self.ui_executor.wait_for_element(element_name):
                        self.logger.error(f"等待元素失败: {element_name}")
                        return False
                
            except Exception as e:
                self.logger.error(f"执行前置条件失败: {precondition}, 错误: {e}")
                return False
        
        return True
    
    def _execute_postconditions(self, test_case: Dict[str, Any], 
                              execution: Dict[str, Any]):
        """执行后置条件"""
        postconditions = test_case.get('postconditions', [])
        
        for postcondition in postconditions:
            try:
                self.logger.info(f"执行后置条件: {postcondition}")
                
                # 示例：清理数据
                if postcondition.startswith("清理数据:"):
                    # 实现数据清理逻辑
                    pass
                
                # 示例：关闭应用
                elif postcondition.startswith("关闭应用"):
                    # 实现应用关闭逻辑
                    pass
                
            except Exception as e:
                self.logger.error(f"执行后置条件失败: {postcondition}, 错误: {e}")
                # 后置条件失败不影响测试结果
    
    def _wait_for_executions(self, execution_ids: List[str]):
        """等待执行完成"""
        while True:
            completed = all(
                execution_id not in self.running_executions 
                for execution_id in execution_ids
            )
            
            if completed:
                break
            
            time.sleep(0.1)
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """获取执行状态"""
        return self.executions.get(execution_id)
    
    def get_all_executions(self) -> List[Dict[str, Any]]:
        """获取所有执行记录"""
        return list(self.executions.values())
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        total = len(self.executions)
        passed = sum(1 for e in self.executions.values() if e["status"] == "passed")
        failed = sum(1 for e in self.executions.values() if e["status"] == "failed")
        partial = sum(1 for e in self.executions.values() if e["status"] == "partial_success")
        error = sum(1 for e in self.executions.values() if e["status"] == "error")
        running = len(self.running_executions)
        pending = len(self.execution_queue) - running
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "partial_success": partial,
            "error": error,
            "running": running,
            "pending": pending,
            "success_rate": (passed + partial) / total if total > 0 else 0
        }
    
    def stop_execution(self, execution_id: str) -> bool:
        """停止执行"""
        if execution_id in self.running_executions:
            execution = self.executions[execution_id]
            execution["status"] = "stopped"
            execution["end_time"] = time.time()
            execution["duration"] = execution["end_time"] - execution["start_time"]
            
            self.running_executions.remove(execution_id)
            self.logger.info(f"停止执行: {execution_id}")
            return True
        
        return False
    
    def clear_executions(self, status_filter: str = None):
        """清理执行记录"""
        if status_filter:
            # 按状态过滤清理
            to_remove = [
                eid for eid, execution in self.executions.items()
                if execution["status"] == status_filter
            ]
        else:
            # 清理所有记录
            to_remove = list(self.executions.keys())
        
        for execution_id in to_remove:
            if execution_id in self.running_executions:
                self.stop_execution(execution_id)
            
            del self.executions[execution_id]
            if execution_id in self.execution_queue:
                self.execution_queue.remove(execution_id)
        
        self.logger.info(f"清理执行记录: {len(to_remove)} 条")
    
    def export_execution_report(self, execution_id: str, 
                               format: str = "json") -> Optional[str]:
        """导出执行报告"""
        execution = self.executions.get(execution_id)
        if not execution:
            return None
        
        try:
            if format == "json":
                report_path = f"data/reports/execution_{execution_id}.json"
                Path(report_path).parent.mkdir(parents=True, exist_ok=True)
                
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(execution, f, ensure_ascii=False, indent=2)
                
                return report_path
            
            elif format == "html":
                # 实现HTML报告生成
                pass
            
            else:
                self.logger.error(f"不支持的报告格式: {format}")
                return None
                
        except Exception as e:
            self.logger.error(f"导出执行报告失败: {e}")
            return None
    
    def shutdown(self):
        """关闭执行器"""
        self.logger.info("关闭测试执行器")
        
        # 停止所有运行中的执行
        for execution_id in list(self.running_executions):
            self.stop_execution(execution_id)
        
        # 关闭线程池
        self.executor.shutdown(wait=True)
        
        self.logger.info("测试执行器已关闭")
