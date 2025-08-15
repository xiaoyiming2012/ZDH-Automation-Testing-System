"""
日志管理器
提供统一的日志记录功能
"""

import os
import sys
from pathlib import Path
from typing import Optional
from loguru import logger


class LoggerManager:
    """日志管理器"""
    
    def __init__(self):
        """初始化日志管理器"""
        self.logger = logger
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志配置"""
        # 移除默认的日志处理器
        self.logger.remove()
        
        # 延迟导入config_manager避免循环依赖
        try:
            from .config_manager import config_manager
            log_config = config_manager.get_logging_config()
        except Exception:
            # 如果配置管理器不可用，使用默认配置
            log_config = {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'console': {'enabled': True},
                'file': {'enabled': True}
            }
        
        log_level = log_config.get('level', 'INFO')
        log_format = log_config.get('format', 
                                  '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # 控制台日志处理器
        if log_config.get('console', {}).get('enabled', True):
            self.logger.add(
                sys.stdout,
                format=log_format,
                level=log_level,
                colorize=True
            )
        
        # 文件日志处理器
        if log_config.get('file', {}).get('enabled', True):
            self._setup_file_logging(log_config, log_format, log_level)
    
    def _setup_file_logging(self, log_config: dict, log_format: str, log_level: str):
        """设置文件日志"""
        file_config = log_config.get('file', {})
        log_file = file_config.get('path', 'data/logs/test_system.log')
        max_size = file_config.get('max_size', '10MB')
        backup_count = file_config.get('backup_count', 5)
        
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 添加文件日志处理器
        self.logger.add(
            log_file,
            format=log_format,
            level=log_level,
            rotation=max_size,
            retention=backup_count,
            compression="zip",
            encoding="utf-8"
        )
    
    def get_logger(self, name: str = None):
        """
        获取日志记录器
        
        Args:
            name: 日志记录器名称
            
        Returns:
            日志记录器实例
        """
        if name:
            return self.logger.bind(name=name)
        return self.logger
    
    def log_test_start(self, test_name: str, test_id: str):
        """记录测试开始"""
        self.logger.info(f"测试开始 - 名称: {test_name}, ID: {test_id}")
    
    def log_test_end(self, test_name: str, test_id: str, result: str, duration: float):
        """记录测试结束"""
        self.logger.info(f"测试结束 - 名称: {test_name}, ID: {test_id}, "
                        f"结果: {result}, 耗时: {duration:.2f}秒")
    
    def log_test_step(self, test_id: str, step_name: str, status: str, details: str = ""):
        """记录测试步骤"""
        self.logger.info(f"测试步骤 - ID: {test_id}, 步骤: {step_name}, "
                        f"状态: {status}, 详情: {details}")
    
    def log_ui_action(self, action: str, target: str, result: str, details: str = ""):
        """记录UI操作"""
        self.logger.info(f"UI操作 - 动作: {action}, 目标: {target}, "
                        f"结果: {result}, 详情: {details}")
    
    def log_security_event(self, event_type: str, details: str, severity: str = "INFO"):
        """记录安全事件"""
        if severity.upper() == "ERROR":
            self.logger.error(f"安全事件 - 类型: {event_type}, 详情: {details}")
        elif severity.upper() == "WARNING":
            self.logger.warning(f"安全事件 - 类型: {event_type}, 详情: {details}")
        else:
            self.logger.info(f"安全事件 - 类型: {event_type}, 详情: {details}")
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = ""):
        """记录性能指标"""
        self.logger.info(f"性能指标 - {metric_name}: {value}{unit}")
    
    def log_error(self, error: Exception, context: str = ""):
        """记录错误"""
        error_msg = f"错误 - 类型: {type(error).__name__}, 消息: {str(error)}"
        if context:
            error_msg += f", 上下文: {context}"
        self.logger.error(error_msg)
    
    def log_warning(self, message: str, context: str = ""):
        """记录警告"""
        if context:
            self.logger.warning(f"警告 - {message}, 上下文: {context}")
        else:
            self.logger.warning(f"警告 - {message}")
    
    def log_info(self, message: str, context: str = ""):
        """记录信息"""
        if context:
            self.logger.info(f"信息 - {message}, 上下文: {context}")
        else:
            self.logger.info(f"信息 - {message}")
    
    def log_debug(self, message: str, context: str = ""):
        """记录调试信息"""
        if context:
            self.logger.debug(f"调试 - {message}, 上下文: {context}")
        else:
            self.logger.debug(f"调试 - {message}")


# 创建全局实例
logger_manager = LoggerManager()


def get_logger(name: str = None):
    """获取日志记录器的便捷函数"""
    return logger_manager.get_logger(name)
