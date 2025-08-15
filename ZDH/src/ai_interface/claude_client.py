"""
Claude AI客户端
负责与Claude AI API的交互
"""

import json
import time
import requests
from typing import Dict, Any, Optional, List
from src.utils.logger import get_logger
from src.utils.config_manager import config_manager


class ClaudeClient:
    """Claude API客户端"""
    
    def __init__(self):
        """初始化客户端"""
        self.logger = get_logger("ClaudeClient")
        self.config = config_manager.get_ai_config()
        
        # API配置
        self.base_url = self.config.get('claude_api', {}).get('base_url', 'https://api.anthropic.com')
        self.api_key = self.config.get('claude_api', {}).get('api_key')
        self.model = self.config.get('claude_api', {}).get('model', 'claude-3-opus-20240229')
        self.max_tokens = self.config.get('claude_api', {}).get('max_tokens', 4096)
        self.temperature = self.config.get('claude_api', {}).get('temperature', 0.1)
        
        # 请求配置
        self.timeout = self.config.get('request_timeout', 30)
        self.max_retries = self.config.get('max_retries', 3)
        
        # 验证配置
        if not self.api_key:
            raise ValueError("Claude API密钥未配置")
        
        self.logger.info("Claude客户端初始化成功")
    
    def analyze_business_flow(self, content: str, input_type: str = "natural_language", 
                            context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        分析业务流程
        
        Args:
            content: 输入内容（自然语言描述或流程图）
            input_type: 输入类型 ("natural_language", "flowchart", "table")
            context: 上下文信息
            
        Returns:
            分析结果
        """
        try:
            self.logger.info(f"分析业务流程: {input_type}")
            
            # 构建提示词
            prompt = self._build_business_analysis_prompt(content, input_type, context)
            
            # 发送请求
            response = self._send_request(prompt, "business_analysis")
            
            # 解析响应
            result = self._parse_business_analysis_response(response)
            
            self.logger.info("业务流程分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"业务流程分析失败: {e}")
            return {"error": str(e)}
    
    def generate_test_cases(self, business_model: Dict[str, Any], 
                           coverage_requirements: Dict[str, bool] = None,
                           special_requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成测试用例
        
        Args:
            business_model: 业务模型
            coverage_requirements: 覆盖率要求
            special_requirements: 特殊要求
            
        Returns:
            生成的测试用例
        """
        try:
            self.logger.info("生成测试用例")
            
            # 构建提示词
            prompt = self._build_test_case_generation_prompt(
                business_model, coverage_requirements, special_requirements
            )
            
            # 发送请求
            response = self._send_request(prompt, "test_case_generation")
            
            # 解析响应
            result = self._parse_test_case_response(response)
            
            self.logger.info("测试用例生成完成")
            return result
            
        except Exception as e:
            self.logger.error(f"测试用例生成失败: {e}")
            return {"error": str(e)}
    
    def optimize_test_strategy(self, test_cases: List[Dict[str, Any]], 
                             execution_results: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        优化测试策略
        
        Args:
            test_cases: 测试用例列表
            execution_results: 执行结果列表
            
        Returns:
            优化建议
        """
        try:
            self.logger.info("优化测试策略")
            
            # 构建提示词
            prompt = self._build_optimization_prompt(test_cases, execution_results)
            
            # 发送请求
            response = self._send_request(prompt, "strategy_optimization")
            
            # 解析响应
            result = self._parse_optimization_response(response)
            
            self.logger.info("测试策略优化完成")
            return result
            
        except Exception as e:
            self.logger.error(f"测试策略优化失败: {e}")
            return {"error": str(e)}
    
    def _build_business_analysis_prompt(self, content: str, input_type: str, 
                                      context: Dict[str, Any]) -> str:
        """构建业务流程分析提示词"""
        prompt = f"""
你是一个专业的软件测试分析师，专门负责分析业务流程并生成测试策略。

输入类型: {input_type}
输入内容: {content}

上下文信息: {json.dumps(context, ensure_ascii=False) if context else '无'}

请分析上述内容并返回以下JSON格式的结果：

{{
    "business_model": {{
        "name": "业务流程名称",
        "description": "业务流程描述",
        "nodes": [
            {{
                "id": "节点ID",
                "name": "节点名称",
                "type": "节点类型",
                "description": "节点描述",
                "actions": ["动作1", "动作2"],
                "expected_results": ["预期结果1", "预期结果2"]
            }}
        ],
        "flows": [
            {{
                "from": "起始节点ID",
                "to": "目标节点ID",
                "condition": "流转条件",
                "description": "流转描述"
            }}
        ],
        "entry_points": ["入口节点ID列表"],
        "exit_points": ["出口节点ID列表"]
    }},
    "test_strategy": {{
        "main_flows": ["主要流程测试策略"],
        "branch_flows": ["分支流程测试策略"],
        "exception_flows": ["异常流程测试策略"],
        "boundary_conditions": ["边界条件测试策略"]
    }},
    "complexity_analysis": {{
        "overall_complexity": "整体复杂度评估",
        "risk_areas": ["风险区域"],
        "testing_effort": "测试工作量评估"
    }}
}}

请确保返回的是有效的JSON格式，不要包含其他文本。
"""
        return prompt
    
    def _build_test_case_generation_prompt(self, business_model: Dict[str, Any],
                                          coverage_requirements: Dict[str, bool],
                                          special_requirements: Dict[str, Any]) -> str:
        """构建测试用例生成提示词"""
        prompt = f"""
你是一个专业的软件测试工程师，负责基于业务模型生成完整的测试用例。

业务模型: {json.dumps(business_model, ensure_ascii=False)}

覆盖率要求: {json.dumps(coverage_requirements, ensure_ascii=False) if coverage_requirements else '{}'}

特殊要求: {json.dumps(special_requirements, ensure_ascii=False) if special_requirements else '{}'}

请生成完整的测试用例集，确保覆盖所有业务场景。返回以下JSON格式：

{{
    "test_cases": [
        {{
            "id": "测试用例ID",
            "name": "测试用例名称",
            "description": "测试用例描述",
            "priority": "优先级",
            "category": "测试类别",
            "preconditions": ["前置条件"],
            "test_steps": [
                {{
                    "step_id": "步骤ID",
                    "action": "操作动作",
                    "target": "操作目标",
                    "input_data": "输入数据",
                    "expected_result": "预期结果",
                    "timeout": "超时时间"
                }}
            ],
            "postconditions": ["后置条件"],
            "test_data": {{
                "input_data": "输入数据",
                "expected_output": "预期输出"
            }}
        }}
    ],
    "coverage_analysis": {{
        "main_flow_coverage": "主流程覆盖率",
        "branch_coverage": "分支覆盖率",
        "exception_coverage": "异常场景覆盖率",
        "boundary_coverage": "边界条件覆盖率"
    }},
    "execution_plan": {{
        "estimated_duration": "预估执行时间",
        "parallel_execution": "是否支持并行执行",
        "resource_requirements": "资源需求"
    }}
}}

请确保返回的是有效的JSON格式，不要包含其他文本。
"""
        return prompt
    
    def _build_optimization_prompt(self, test_cases: List[Dict[str, Any]],
                                 execution_results: List[Dict[str, Any]]) -> str:
        """构建优化提示词"""
        prompt = f"""
你是一个专业的测试策略优化专家，负责分析测试用例和执行结果，提供优化建议。

测试用例: {json.dumps(test_cases, ensure_ascii=False)}

执行结果: {json.dumps(execution_results, ensure_ascii=False) if execution_results else '[]'}

请分析上述信息并提供优化建议，返回以下JSON格式：

{{
    "optimization_suggestions": [
        {{
            "area": "优化领域",
            "suggestion": "优化建议",
            "priority": "优先级",
            "expected_impact": "预期影响",
            "implementation_effort": "实施难度"
        }}
    ],
    "performance_improvements": [
        {{
            "aspect": "性能方面",
            "current_status": "当前状态",
            "target_status": "目标状态",
            "improvement_method": "改进方法"
        }}
    ],
    "risk_mitigation": [
        {{
            "risk": "风险描述",
            "probability": "发生概率",
            "impact": "影响程度",
            "mitigation_strategy": "缓解策略"
        }}
    ]
}}

请确保返回的是有效的JSON格式，不要包含其他文本。
"""
        return prompt
    
    def _send_request(self, prompt: str, request_type: str) -> Dict[str, Any]:
        """发送API请求"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"发送API请求: {request_type}, 尝试 {attempt + 1}/{self.max_retries}")
                
                response = requests.post(
                    f"{self.base_url}/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                result = response.json()
                
                # 记录响应时间
                response_time = time.time() - start_time
                self.logger.log_ai_request(request_type, prompt[:100], response_time)
                
                return result
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"API请求失败 (尝试 {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    raise RuntimeError(f"API请求失败，已重试 {self.max_retries} 次: {e}")
        
        raise RuntimeError("API请求失败")
    
    def _parse_business_analysis_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """解析业务流程分析响应"""
        try:
            content = response.get('content', [])
            if content and len(content) > 0:
                text_content = content[0].get('text', '')
                
                # 尝试解析JSON
                try:
                    result = json.loads(text_content)
                    return result
                except json.JSONDecodeError:
                    self.logger.warning("响应不是有效的JSON格式，尝试提取JSON部分")
                    
                    # 尝试提取JSON部分
                    import re
                    json_match = re.search(r'\{.*\}', text_content, re.DOTALL)
                    if json_match:
                        try:
                            result = json.loads(json_match.group())
                            return result
                        except json.JSONDecodeError:
                            pass
                    
                    # 如果无法解析，返回原始文本
                    return {
                        "raw_response": text_content,
                        "error": "无法解析JSON响应"
                    }
            else:
                return {"error": "响应内容为空"}
                
        except Exception as e:
            self.logger.error(f"解析业务流程分析响应失败: {e}")
            return {"error": str(e)}
    
    def _parse_test_case_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """解析测试用例响应"""
        return self._parse_business_analysis_response(response)
    
    def _parse_optimization_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """解析优化响应"""
        return self._parse_business_analysis_response(response)
    
    def validate_response(self, response: Dict[str, Any]) -> bool:
        """验证响应有效性"""
        try:
            # 检查是否有错误
            if "error" in response:
                return False
            
            # 检查必需字段
            if "business_model" in response:
                required_fields = ["name", "nodes", "flows"]
                for field in required_fields:
                    if field not in response["business_model"]:
                        return False
            
            elif "test_cases" in response:
                if not isinstance(response["test_cases"], list):
                    return False
                for test_case in response["test_cases"]:
                    required_fields = ["id", "name", "test_steps"]
                    for field in required_fields:
                        if field not in test_case:
                            return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"验证响应失败: {e}")
            return False
    
    def get_api_status(self) -> Dict[str, Any]:
        """获取API状态"""
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            response = requests.get(
                f"{self.base_url}/v1/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "available_models": response.json().get("data", [])
                }
            else:
                return {
                    "status": "unhealthy",
                    "status_code": response.status_code,
                    "error": response.text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
