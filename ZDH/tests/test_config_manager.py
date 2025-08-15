"""
配置管理器单元测试
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """配置管理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时配置文件
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.yaml"
        
        # 测试配置内容
        self.test_config = """
ai_interface:
  claude_api:
    base_url: "https://api.anthropic.com"
    api_key: "${CLAUDE_API_KEY}"
    model: "claude-3-opus-20240229"
    max_tokens: 4096
    temperature: 0.1
  
  request_timeout: 30
  max_retries: 3

ui_automation:
  image_recognition:
    confidence_threshold: 0.8
    template_cache_size: 100
    screenshot_quality: 0.9
  
  coordinate_positioning:
    cache_enabled: true
    cache_expiry: 3600
    fallback_enabled: true

database:
  sqlite:
    path: "data/test_system.db"
    timeout: 30
  
  file_storage:
    base_path: "data"
    screenshots: "screenshots"
    logs: "logs"
    templates: "templates"
    reports: "reports"

test_execution:
  parallel:
    max_workers: 4
    max_concurrent_tests: 2
  
  timeouts:
    test_case: 300
    test_step: 60
    system_recovery: 120
  
  retry:
    max_attempts: 3
    delay_between_attempts: 5
"""
        
        # 写入测试配置文件
        with open(self.config_file, 'w', encoding='utf-8') as f:
            f.write(self.test_config)
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_init_with_valid_config(self):
        """测试使用有效配置文件初始化"""
        config_manager = ConfigManager(str(self.config_file))
        
        # 验证基本配置加载
        self.assertIsNotNone(config_manager.config)
        self.assertIn('ai_interface', config_manager.config)
        self.assertIn('ui_automation', config_manager.config)
        self.assertIn('database', config_manager.config)
        self.assertIn('test_execution', config_manager.config)
    
    def test_init_with_invalid_path(self):
        """测试使用无效路径初始化"""
        with self.assertRaises(RuntimeError):
            ConfigManager("invalid/path/config.yaml")
    
    def test_get_config_sections(self):
        """测试获取配置节"""
        config_manager = ConfigManager(str(self.config_file))
        
        # 测试获取AI配置
        ai_config = config_manager.get_ai_config()
        self.assertIsInstance(ai_config, dict)
        self.assertIn('claude_api', ai_config)
        
        # 测试获取UI配置
        ui_config = config_manager.get_ui_config()
        self.assertIsInstance(ui_config, dict)
        self.assertIn('image_recognition', ui_config)
        
        # 测试获取数据库配置
        db_config = config_manager.get_db_config()
        self.assertIsInstance(db_config, dict)
        self.assertIn('sqlite', db_config)
        
        # 测试获取测试执行配置
        test_config = config_manager.get_test_config()
        self.assertIsInstance(test_config, dict)
        self.assertIn('parallel', test_config)
    
    def test_get_nested_config(self):
        """测试获取嵌套配置"""
        config_manager = ConfigManager(str(self.config_file))
        
        # 测试点号分隔的键
        api_key = config_manager.get('ai_interface.claude_api.api_key')
        self.assertEqual(api_key, "${CLAUDE_API_KEY}")
        
        confidence = config_manager.get('ui_automation.image_recognition.confidence_threshold')
        self.assertEqual(confidence, 0.8)
        
        # 测试不存在的键
        non_existent = config_manager.get('non.existent.key', 'default_value')
        self.assertEqual(non_existent, 'default_value')
    
    def test_environment_variable_substitution(self):
        """测试环境变量替换"""
        # 设置测试环境变量
        test_api_key = "test_api_key_12345"
        os.environ['CLAUDE_API_KEY'] = test_api_key
        
        config_manager = ConfigManager(str(self.config_file))
        
        # 验证环境变量被替换
        api_key = config_manager.get('ai_interface.claude_api.api_key')
        self.assertEqual(api_key, test_api_key)
        
        # 清理环境变量
        del os.environ['CLAUDE_API_KEY']
    
    def test_validate_config(self):
        """测试配置验证"""
        config_manager = ConfigManager(str(self.config_file))
        
        # 验证有效配置
        self.assertTrue(config_manager.validate())
    
    def test_validate_invalid_config(self):
        """测试无效配置验证"""
        # 创建缺少必要节的配置文件
        invalid_config = """
ai_interface:
  claude_api:
    base_url: "https://api.anthropic.com"
"""
        
        invalid_config_file = Path(self.temp_dir) / "invalid_config.yaml"
        with open(invalid_config_file, 'w', encoding='utf-8') as f:
            f.write(invalid_config)
        
        config_manager = ConfigManager(str(invalid_config_file))
        
        # 验证无效配置
        self.assertFalse(config_manager.validate())
    
    def test_reload_config(self):
        """测试重新加载配置"""
        config_manager = ConfigManager(str(self.config_file))
        
        # 修改配置文件
        modified_config = self.test_config.replace('max_tokens: 4096', 'max_tokens: 8192')
        with open(self.config_file, 'w', encoding='utf-8') as f:
            f.write(modified_config)
        
        # 重新加载配置
        config_manager.reload()
        
        # 验证配置已更新
        max_tokens = config_manager.get('ai_interface.claude_api.max_tokens')
        self.assertEqual(max_tokens, 8192)
    
    def test_directory_creation(self):
        """测试目录创建"""
        config_manager = ConfigManager(str(self.config_file))
        
        # 验证必要的目录被创建
        data_dirs = ['data', 'data/logs', 'data/screenshots', 'data/templates', 'data/reports']
        for dir_path in data_dirs:
            self.assertTrue(Path(dir_path).exists())


if __name__ == '__main__':
    unittest.main()
