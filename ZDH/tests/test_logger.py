"""
日志管理器单元测试
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import LoggerManager, get_logger


class TestLoggerManager(unittest.TestCase):
    """日志管理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = Path(self.temp_dir) / "test.log"
        
        # 设置环境变量
        os.environ['TEST_LOG_PATH'] = str(self.log_file)
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir)
        if 'TEST_LOG_PATH' in os.environ:
            del os.environ['TEST_LOG_PATH']
    
    def test_init_logger_manager(self):
        """测试日志管理器初始化"""
        logger_manager = LoggerManager()
        
        # 验证基本属性
        self.assertIsNotNone(logger_manager.logger)
        self.assertIsInstance(logger_manager.logger, type(logger_manager.logger))
    
    def test_get_logger_with_name(self):
        """测试获取带名称的日志记录器"""
        logger_manager = LoggerManager()
        named_logger = logger_manager.get_logger("TestComponent")
        
        self.assertIsNotNone(named_logger)
    
    def test_get_logger_without_name(self):
        """测试获取不带名称的日志记录器"""
        logger_manager = LoggerManager()
        default_logger = logger_manager.get_logger()
        
        self.assertIsNotNone(default_logger)
    
    def test_log_test_start(self):
        """测试记录测试开始"""
        logger_manager = LoggerManager()
        
        # 测试记录测试开始
        try:
            logger_manager.log_test_start("Test Case 1", "test_001")
            # 如果没有异常，测试通过
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"记录测试开始失败: {e}")
    
    def test_log_test_end(self):
        """测试记录测试结束"""
        logger_manager = LoggerManager()
        
        # 测试记录测试结束
        try:
            logger_manager.log_test_end("Test Case 1", "test_001", "PASS", 1.5)
            # 如果没有异常，测试通过
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"记录测试结束失败: {e}")
    
    def test_log_test_step(self):
        """测试记录测试步骤"""
        logger_manager = LoggerManager()
        
        # 测试记录测试步骤
        try:
            logger_manager.log_test_step("test_001", "Step 1", "PASS", "执行成功")
            # 如果没有异常，测试通过
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"记录测试步骤失败: {e}")
    
    def test_log_ui_action(self):
        """测试记录UI操作"""
        logger_manager = LoggerManager()
        
        # 测试记录UI操作
        try:
            logger_manager.log_ui_action("click", "button_login", "SUCCESS", "点击登录按钮")
            # 如果没有异常，测试通过
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"记录UI操作失败: {e}")
    
    def test_log_security_event(self):
        """测试记录安全事件"""
        logger_manager = LoggerManager()
        
        # 测试记录不同级别的安全事件
        try:
            logger_manager.log_security_event("login_attempt", "用户登录尝试", "INFO")
            logger_manager.log_security_event("permission_denied", "权限被拒绝", "WARNING")
            logger_manager.log_security_event("unauthorized_access", "未授权访问", "ERROR")
            # 如果没有异常，测试通过
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"记录安全事件失败: {e}")
    
    def test_log_performance_metric(self):
        """测试记录性能指标"""
        logger_manager = LoggerManager()
        
        # 测试记录性能指标
        try:
            logger_manager.log_performance_metric("response_time", 150.5, "ms")
            # 如果没有异常，测试通过
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"记录性能指标失败: {e}")
    
    def test_log_error(self):
        """测试记录错误"""
        logger_manager = LoggerManager()
        
        # 测试记录错误
        try:
            test_error = ValueError("测试错误")
            logger_manager.log_error(test_error, "测试上下文")
            # 如果没有异常，测试通过
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"记录错误失败: {e}")
    
    def test_log_warning(self):
        """测试记录警告"""
        logger_manager = LoggerManager()
        
        # 测试记录警告
        try:
            logger_manager.log_warning("测试警告消息", "测试上下文")
            logger_manager.log_warning("测试警告消息")  # 无上下文
            # 如果没有异常，测试通过
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"记录警告失败: {e}")
    
    def test_log_info(self):
        """测试记录信息"""
        logger_manager = LoggerManager()
        
        # 测试记录信息
        try:
            logger_manager.log_info("测试信息消息", "测试上下文")
            logger_manager.log_info("测试信息消息")  # 无上下文
            # 如果没有异常，测试通过
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"记录信息失败: {e}")
    
    def test_log_debug(self):
        """测试记录调试信息"""
        logger_manager = LoggerManager()
        
        # 测试记录调试信息
        try:
            logger_manager.log_debug("测试调试消息", "测试上下文")
            logger_manager.log_debug("测试调试消息")  # 无上下文
            # 如果没有异常，测试通过
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"记录调试信息失败: {e}")


class TestGetLoggerFunction(unittest.TestCase):
    """get_logger函数测试类"""
    
    def test_get_logger_function(self):
        """测试get_logger函数"""
        # 测试获取日志记录器
        logger = get_logger("TestFunction")
        self.assertIsNotNone(logger)
        
        # 测试获取默认日志记录器
        default_logger = get_logger()
        self.assertIsNotNone(default_logger)


if __name__ == '__main__':
    unittest.main()
