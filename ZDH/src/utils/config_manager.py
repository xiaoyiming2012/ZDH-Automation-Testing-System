"""
配置管理器
负责加载和管理系统配置
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load_config()
        self._ensure_directories()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            # 加载环境变量
            load_dotenv()
            
            # 加载YAML配置
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
            else:
                raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
            
            # 替换环境变量
            self._replace_env_vars()
            
        except Exception as e:
            raise RuntimeError(f"加载配置失败: {e}")
    
    def _ensure_directories(self):
        """确保必要的目录结构存在"""
        try:
            # 获取数据库配置
            db_config = self.get_db_config()
            
            # 创建数据目录
            data_paths = [
                "data",
                "data/logs",
                "data/screenshots", 
                "data/templates",
                "data/reports",
                "data/coordinate_cache"
            ]
            
            for path in data_paths:
                Path(path).mkdir(parents=True, exist_ok=True)
                
            # 创建配置文件指定的目录
            if db_config:
                sqlite_path = db_config.get('sqlite', {}).get('path', 'data/test_system.db')
                Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
                
                file_storage = db_config.get('file_storage', {})
                for key, path in file_storage.items():
                    if isinstance(path, str):
                        Path(path).mkdir(parents=True, exist_ok=True)
                        
        except Exception as e:
            print(f"警告: 创建目录结构失败: {e}")
    
    def _replace_env_vars(self):
        """替换配置中的环境变量"""
        def replace_in_dict(data: Any) -> Any:
            if isinstance(data, dict):
                return {k: replace_in_dict(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [replace_in_dict(item) for item in data]
            elif isinstance(data, str) and data.startswith("${") and data.endswith("}"):
                env_var = data[2:-1]
                return os.getenv(env_var, data)
            else:
                return data
        
        self.config = replace_in_dict(self.config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_ai_config(self) -> Dict[str, Any]:
        """获取AI接口配置"""
        return self.config.get('ai_interface', {})
    
    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI自动化配置"""
        return self.config.get('ui_automation', {})
    
    def get_db_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return self.config.get('database', {})
    
    def get_test_config(self) -> Dict[str, Any]:
        """获取测试执行配置"""
        return self.config.get('test_execution', {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """获取安全配置"""
        return self.config.get('security', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.config.get('logging', {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """获取监控配置"""
        return self.config.get('monitoring', {})
    
    def get_communication_config(self) -> Dict[str, Any]:
        """获取通信配置"""
        return self.config.get('communication', {})
    
    def get_beike_ui_config(self) -> Dict[str, Any]:
        """获取贝壳库UI配置"""
        return self.config.get('beike_ui', {})
    
    def reload(self):
        """重新加载配置"""
        self._load_config()
        self._ensure_directories()
    
    def validate(self) -> bool:
        """验证配置有效性"""
        try:
            # 检查必要的配置项
            required_sections = ['ai_interface', 'ui_automation', 'database', 'test_execution']
            for section in required_sections:
                if section not in self.config:
                    raise ValueError(f"缺少必要的配置节: {section}")
            
            # 检查AI配置
            ai_config = self.get_ai_config()
            if not ai_config.get('claude_api', {}).get('api_key'):
                print("警告: Claude API密钥未配置")
            
            # 检查数据库配置
            db_config = self.get_db_config()
            if not db_config.get('sqlite', {}).get('path'):
                print("警告: 数据库路径未配置")
            
            return True
            
        except Exception as e:
            print(f"配置验证失败: {e}")
            return False


# 创建全局实例
config_manager = ConfigManager()
