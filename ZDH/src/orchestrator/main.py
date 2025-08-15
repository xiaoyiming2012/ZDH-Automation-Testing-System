"""
Windows自动化测试系统 - 主要编排器服务
整合所有组件并提供HTTP API接口
"""

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import time
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.config_manager import config_manager
from src.ai_interface.claude_client import ClaudeClient
from src.orchestrator.test_executor import TestExecutor
from src.ui_automation.ui_executor import UIExecutor


# 数据模型
class BusinessFlowAnalysisRequest(BaseModel):
    input_type: str  # "natural_language", "flowchart", "table"
    content: str
    context: Optional[Dict[str, Any]] = None


class TestCaseGenerationRequest(BaseModel):
    business_model: Dict[str, Any]
    coverage_requirements: Optional[Dict[str, bool]] = None
    special_requirements: Optional[Dict[str, Any]] = None


class TestExecutionRequest(BaseModel):
    test_case_id: str
    environment: str = "default"
    data_overrides: Optional[Dict[str, Any]] = None
    beike_ui_config: Optional[Dict[str, Any]] = None


class TestSuiteExecutionRequest(BaseModel):
    test_cases: List[Dict[str, Any]]
    environment: str = "default"
    data_overrides: Optional[Dict[str, Any]] = None
    beike_ui_config: Optional[Dict[str, Any]] = None
    parallel: bool = True


# 创建FastAPI应用
app = FastAPI(
    title="Windows自动化测试系统",
    description="基于AI的Windows平台自动化测试系统，专门用于测试贝壳库应用",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局组件实例
logger = get_logger("Orchestrator")
ai_client: Optional[ClaudeClient] = None
test_executor: Optional[TestExecutor] = None
ui_executor: Optional[UIExecutor] = None


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    global ai_client, test_executor, ui_executor
    
    try:
        logger.info("启动Windows自动化测试系统")
        
        # 初始化组件
        ai_client = ClaudeClient()
        test_executor = TestExecutor()
        ui_executor = UIExecutor()
        
        # 验证配置
        config_manager.validate()
        
        logger.info("系统启动成功")
        
    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    try:
        logger.info("关闭Windows自动化测试系统")
        
        if test_executor:
            test_executor.shutdown()
        
        logger.info("系统已关闭")
        
    except Exception as e:
        logger.error(f"系统关闭失败: {e}")


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查AI客户端状态
        ai_status = ai_client.get_api_status() if ai_client else {"status": "not_initialized"}
        
        # 检查测试执行器状态
        executor_summary = test_executor.get_execution_summary() if test_executor else {}
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "ai_client": ai_status,
            "test_executor": executor_summary,
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 业务流程分析
@app.post("/api/v1/analyze")
async def analyze_business_flow(request: BusinessFlowAnalysisRequest):
    """分析业务流程"""
    try:
        logger.info(f"业务流程分析请求: {request.input_type}")
        
        if not ai_client:
            raise HTTPException(status_code=500, detail="AI客户端未初始化")
        
        # 调用AI分析
        result = ai_client.analyze_business_flow(
            content=request.content,
            input_type=request.input_type,
            context=request.context
        )
        
        # 验证响应
        if not ai_client.validate_response(result):
            logger.warning("AI响应验证失败")
            result["warning"] = "响应格式可能不完整"
        
        return result
        
    except Exception as e:
        logger.error(f"业务流程分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 测试用例生成
@app.post("/api/v1/generate")
async def generate_test_cases(request: TestCaseGenerationRequest):
    """生成测试用例"""
    try:
        logger.info("测试用例生成请求")
        
        if not ai_client:
            raise HTTPException(status_code=500, detail="AI客户端未初始化")
        
        # 调用AI生成测试用例
        result = ai_client.generate_test_cases(
            business_model=request.business_model,
            coverage_requirements=request.coverage_requirements,
            special_requirements=request.special_requirements
        )
        
        # 验证响应
        if not ai_client.validate_response(result):
            logger.warning("AI响应验证失败")
            result["warning"] = "响应格式可能不完整"
        
        return result
        
    except Exception as e:
        logger.error(f"测试用例生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 测试用例执行
@app.post("/api/v1/execute")
async def execute_test_case(request: TestExecutionRequest):
    """执行单个测试用例"""
    try:
        logger.info(f"测试用例执行请求: {request.test_case_id}")
        
        if not test_executor:
            raise HTTPException(status_code=500, detail="测试执行器未初始化")
        
        # 查找测试用例（这里需要实现测试用例存储和检索）
        # 暂时使用模拟数据
        test_case = {
            "id": request.test_case_id,
            "name": f"测试用例 {request.test_case_id}",
            "description": "模拟测试用例",
            "test_steps": [
                {
                    "step_id": "1",
                    "action": "click",
                    "target": "start_button",
                    "expected_result": "应用启动"
                }
            ]
        }
        
        # 执行测试用例
        execution_id = test_executor.execute_test_case(
            test_case=test_case,
            environment=request.environment,
            data_overrides=request.data_overrides,
            beike_ui_config=request.beike_ui_config
        )
        
        return {
            "execution_id": execution_id,
            "status": "started",
            "message": "测试用例执行已启动"
        }
        
    except Exception as e:
        logger.error(f"测试用例执行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 测试套件执行
@app.post("/api/v1/execute/suite")
async def execute_test_suite(request: TestSuiteExecutionRequest):
    """执行测试套件"""
    try:
        logger.info(f"测试套件执行请求: {len(request.test_cases)} 个测试用例")
        
        if not test_executor:
            raise HTTPException(status_code=500, detail="测试执行器未初始化")
        
        # 执行测试套件
        execution_ids = test_executor.execute_test_suite(
            test_cases=request.test_cases,
            environment=request.environment,
            data_overrides=request.data_overrides,
            beike_ui_config=request.beike_ui_config,
            parallel=request.parallel
        )
        
        return {
            "execution_ids": execution_ids,
            "total_count": len(request.test_cases),
            "status": "started",
            "message": "测试套件执行已启动"
        }
        
    except Exception as e:
        logger.error(f"测试套件执行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 执行状态查询
@app.get("/api/v1/execute/{execution_id}/status")
async def get_execution_status(execution_id: str):
    """获取执行状态"""
    try:
        if not test_executor:
            raise HTTPException(status_code=500, detail="测试执行器未初始化")
        
        execution = test_executor.get_execution_status(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="执行记录不存在")
        
        return execution
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取执行状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 执行摘要
@app.get("/api/v1/execute/summary")
async def get_execution_summary():
    """获取执行摘要"""
    try:
        if not test_executor:
            raise HTTPException(status_code=500, detail="测试执行器未初始化")
        
        summary = test_executor.get_execution_summary()
        return summary
        
    except Exception as e:
        logger.error(f"获取执行摘要失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 所有执行记录
@app.get("/api/v1/execute/all")
async def get_all_executions():
    """获取所有执行记录"""
    try:
        if not test_executor:
            raise HTTPException(status_code=500, detail="测试执行器未初始化")
        
        executions = test_executor.get_all_executions()
        return {"executions": executions, "total": len(executions)}
        
    except Exception as e:
        logger.error(f"获取所有执行记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 停止执行
@app.post("/api/v1/execute/{execution_id}/stop")
async def stop_execution(execution_id: str):
    """停止执行"""
    try:
        if not test_executor:
            raise HTTPException(status_code=500, detail="测试执行器未初始化")
        
        success = test_executor.stop_execution(execution_id)
        if not success:
            raise HTTPException(status_code=404, detail="执行记录不存在或已停止")
        
        return {"message": "执行已停止", "execution_id": execution_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"停止执行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 清理执行记录
@app.delete("/api/v1/execute/clear")
async def clear_executions(status_filter: Optional[str] = None):
    """清理执行记录"""
    try:
        if not test_executor:
            raise HTTPException(status_code=500, detail="测试执行器未初始化")
        
        test_executor.clear_executions(status_filter)
        
        return {"message": "执行记录已清理", "filter": status_filter}
        
    except Exception as e:
        logger.error(f"清理执行记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 导出执行报告
@app.get("/api/v1/execute/{execution_id}/report")
async def export_execution_report(execution_id: str, format: str = "json"):
    """导出执行报告"""
    try:
        if not test_executor:
            raise HTTPException(status_code=500, detail="测试执行器未初始化")
        
        report_path = test_executor.export_execution_report(execution_id, format)
        if not report_path:
            raise HTTPException(status_code=404, detail="执行记录不存在")
        
        return {
            "execution_id": execution_id,
            "report_path": report_path,
            "format": format,
            "message": "报告导出成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出执行报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# UI操作接口
@app.post("/api/v1/ui/click")
async def ui_click(target: str, method: str = "auto", click_type: str = "left"):
    """UI点击操作"""
    try:
        if not ui_executor:
            raise HTTPException(status_code=500, detail="UI执行器未初始化")
        
        success = ui_executor.click_element(target, method, click_type)
        
        return {
            "action": "click",
            "target": target,
            "success": success,
            "message": "点击成功" if success else "点击失败"
        }
        
    except Exception as e:
        logger.error(f"UI点击操作失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ui/input")
async def ui_input(target: str, text: str, method: str = "auto"):
    """UI文本输入操作"""
    try:
        if not ui_executor:
            raise HTTPException(status_code=500, detail="UI执行器未初始化")
        
        success = ui_executor.input_text(target, text, method)
        
        return {
            "action": "input",
            "target": target,
            "text": text,
            "success": success,
            "message": "输入成功" if success else "输入失败"
        }
        
    except Exception as e:
        logger.error(f"UI文本输入操作失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ui/screenshot")
async def ui_screenshot(save_path: Optional[str] = None):
    """UI截图操作"""
    try:
        if not ui_executor:
            raise HTTPException(status_code=500, detail="UI执行器未初始化")
        
        screenshot_path = ui_executor.take_screenshot(save_path)
        
        return {
            "action": "screenshot",
            "success": screenshot_path is not None,
            "screenshot_path": screenshot_path,
            "message": "截图成功" if screenshot_path else "截图失败"
        }
        
    except Exception as e:
        logger.error(f"UI截图操作失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 配置管理接口
@app.get("/api/v1/config")
async def get_config():
    """获取系统配置"""
    try:
        return {
            "ai_interface": config_manager.get_ai_config(),
            "ui_automation": config_manager.get_ui_config(),
            "test_execution": config_manager.get_test_config(),
            "security": config_manager.get_security_config(),
            "beike_ui": config_manager.get_beike_ui_config()
        }
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/config/reload")
async def reload_config():
    """重新加载配置"""
    try:
        config_manager.reload()
        config_manager.validate()
        
        return {"message": "配置重新加载成功"}
        
    except Exception as e:
        logger.error(f"重新加载配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 系统信息接口
@app.get("/api/v1/system/info")
async def get_system_info():
    """获取系统信息"""
    try:
        import platform
        import psutil
        
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": psutil.disk_usage('/').percent
        }
        
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # 获取配置
    host = config_manager.get('communication.http.host', '127.0.0.1')
    port = config_manager.get('communication.http.port', 8089)
    debug = config_manager.get('logging.level', 'INFO') == 'DEBUG'
    
    # 启动服务
    uvicorn.run(
        "src.orchestrator.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level=config_manager.get('logging.level', 'INFO').lower()
    )
