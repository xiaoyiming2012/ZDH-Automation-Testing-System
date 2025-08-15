"""
贝壳库UI定位器单元测试
"""

import unittest
import tempfile
import os
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock

# 添加项目根目录到Python路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui_automation.beike_ui_locator import BeikeUILocator


class TestBeikeUILocator(unittest.TestCase):
    """贝壳库UI定位器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试目录结构
        self.data_dir = Path(self.temp_dir) / "data"
        self.templates_dir = self.data_dir / "templates"
        self.coordinate_cache_dir = self.data_dir / "coordinate_cache"
        
        for dir_path in [self.data_dir, self.templates_dir, self.coordinate_cache_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 创建测试图像模板
        self._create_test_templates()
        
        # 创建测试坐标缓存文件
        self._create_test_coordinate_cache()
        
        # Mock配置管理器
        self.mock_config = {
            'ocr': {'enabled': True, 'language': 'ch_sim+en'},
            'coordinate_cache': {'enabled': True},
            'image_templates': {'base_path': str(self.templates_dir)},
            'recognition_priority': ['image_recognition', 'coordinate_positioning', 'color_matching', 'ocr_text']
        }
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_test_templates(self):
        """创建测试图像模板"""
        # 创建简单的测试图像
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[40:60, 40:60] = [255, 0, 0]  # 红色方块
        
        # 保存测试模板
        import cv2
        template_path = self.templates_dir / "test_button.png"
        cv2.imwrite(str(template_path), test_image)
    
    def _create_test_coordinate_cache(self):
        """创建测试坐标缓存"""
        import json
        cache_data = {
            "test_button": [100, 200],
            "test_input": [300, 400]
        }
        
        cache_file = self.coordinate_cache_dir / "coordinate_cache.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f)
    
    @patch('src.ui_automation.beike_ui_locator.config_manager')
    @patch('src.ui_automation.beike_ui_locator.easyocr')
    def test_init_with_ocr_enabled(self, mock_easyocr, mock_config_manager):
        """测试启用OCR的初始化"""
        # Mock配置
        mock_config_manager.get_beike_ui_config.return_value = self.mock_config
        
        # Mock OCR
        mock_reader = Mock()
        mock_easyocr.Reader.return_value = mock_reader
        
        # 创建定位器实例
        locator = BeikeUILocator()
        
        # 验证OCR被初始化
        mock_easyocr.Reader.assert_called_once_with(['ch_sim', 'en'])
        self.assertIsNotNone(locator.ocr_reader)
    
    @patch('src.ui_automation.beike_ui_locator.config_manager')
    @patch('src.ui_automation.beike_ui_locator.easyocr')
    def test_init_with_ocr_disabled(self, mock_easyocr, mock_config_manager):
        """测试禁用OCR的初始化"""
        # Mock配置
        mock_config = self.mock_config.copy()
        mock_config['ocr']['enabled'] = False
        mock_config_manager.get_beike_ui_config.return_value = mock_config
        
        # 创建定位器实例
        locator = BeikeUILocator()
        
        # 验证OCR未被初始化
        mock_easyocr.Reader.assert_not_called()
        self.assertIsNone(locator.ocr_reader)
    
    @patch('src.ui_automation.beike_ui_locator.config_manager')
    @patch('src.ui_automation.beike_ui_locator.easyocr')
    def test_init_ocr_failure(self, mock_easyocr, mock_config_manager):
        """测试OCR初始化失败"""
        # Mock配置
        mock_config_manager.get_beike_ui_config.return_value = self.mock_config
        
        # Mock OCR初始化失败
        mock_easyocr.Reader.side_effect = Exception("OCR初始化失败")
        
        # 创建定位器实例（应该不会崩溃）
        locator = BeikeUILocator()
        
        # 验证OCR为None
        self.assertIsNone(locator.ocr_reader)
    
    @patch('src.ui_automation.beike_ui_locator.config_manager')
    @patch('src.ui_automation.beike_ui_locator.easyocr')
    def test_locate_element_auto_method(self, mock_easyocr, mock_config_manager):
        """测试自动定位元素"""
        # Mock配置
        mock_config_manager.get_beike_ui_config.return_value = self.mock_config
        
        # Mock OCR
        mock_reader = Mock()
        mock_easyocr.Reader.return_value = mock_reader
        
        # 创建定位器实例
        locator = BeikeUILocator()
        
        # Mock图像识别成功
        with patch.object(locator, '_locate_by_image') as mock_image:
            mock_image.return_value = (100, 200)
            
            # 测试自动定位
            result = locator.locate_element("test_button", "auto")
            
            # 验证结果
            self.assertEqual(result, (100, 200))
            mock_image.assert_called_once_with("test_button")
    
    @patch('src.ui_automation.beike_ui_locator.config_manager')
    @patch('src.ui_automation.beike_ui_locator.easyocr')
    def test_locate_element_image_method(self, mock_easyocr, mock_config_manager):
        """测试图像识别定位"""
        # Mock配置
        mock_config_manager.get_beike_ui_config.return_value = self.mock_config
        
        # Mock OCR
        mock_reader = Mock()
        mock_easyocr.Reader.return_value = mock_reader
        
        # 创建定位器实例
        locator = BeikeUILocator()
        
        # Mock图像识别
        with patch.object(locator, '_locate_by_image') as mock_image:
            mock_image.return_value = (150, 250)
            
            # 测试图像定位
            result = locator.locate_element("test_button", "image_recognition")
            
            # 验证结果
            self.assertEqual(result, (150, 250))
            mock_image.assert_called_once_with("test_button")
    
    @patch('src.ui_automation.beike_ui_locator.config_manager')
    @patch('src.ui_automation.beike_ui_locator.easyocr')
    def test_locate_element_coordinate_method(self, mock_easyocr, mock_config_manager):
        """测试坐标定位"""
        # Mock配置
        mock_config_manager.get_beike_ui_config.return_value = self.mock_config
        
        # Mock OCR
        mock_reader = Mock()
        mock_easyocr.Reader.return_value = mock_reader
        
        # 创建定位器实例
        locator = BeikeUILocator()
        
        # Mock坐标定位
        with patch.object(locator, '_locate_by_coordinate') as mock_coordinate:
            mock_coordinate.return_value = (300, 400)
            
            # 测试坐标定位
            result = locator.locate_element("test_input", "coordinate_positioning")
            
            # 验证结果
            self.assertEqual(result, (300, 400))
            mock_coordinate.assert_called_once_with("test_input")
    
    @patch('src.ui_automation.beike_ui_locator.config_manager')
    @patch('src.ui_automation.beike_ui_locator.easyocr')
    def test_locate_element_not_found(self, mock_easyocr, mock_config_manager):
        """测试元素未找到"""
        # Mock配置
        mock_config_manager.get_beike_ui_config.return_value = self.mock_config
        
        # Mock OCR
        mock_reader = Mock()
        mock_easyocr.Reader.return_value = mock_reader
        
        # 创建定位器实例
        locator = BeikeUILocator()
        
        # Mock所有定位方法都失败
        with patch.object(locator, '_locate_by_image') as mock_image:
            with patch.object(locator, '_locate_by_coordinate') as mock_coordinate:
                with patch.object(locator, '_locate_by_color') as mock_color:
                    with patch.object(locator, '_locate_by_ocr') as mock_ocr:
                        mock_image.return_value = None
                        mock_coordinate.return_value = None
                        mock_color.return_value = None
                        mock_ocr.return_value = None
                        
                        # 测试定位失败
                        result = locator.locate_element("non_existent_element", "auto")
                        
                        # 验证结果为None
                        self.assertIsNone(result)
    
    @patch('src.ui_automation.beike_ui_locator.config_manager')
    @patch('src.ui_automation.beike_ui_locator.easyocr')
    def test_update_coordinate_cache(self, mock_easyocr, mock_config_manager):
        """测试更新坐标缓存"""
        # Mock配置
        mock_config_manager.get_beike_ui_config.return_value = self.mock_config
        
        # Mock OCR
        mock_reader = Mock()
        mock_easyocr.Reader.return_value = mock_reader
        
        # 创建定位器实例
        locator = BeikeUILocator()
        
        # 测试更新缓存
        locator.update_coordinate_cache("new_button", (500, 600))
        
        # 验证缓存被更新
        self.assertIn("new_button", locator.coordinate_cache)
        self.assertEqual(locator.coordinate_cache["new_button"], (500, 600))
    
    @patch('src.ui_automation.beike_ui_locator.config_manager')
    @patch('src.ui_automation.beike_ui_locator.easyocr')
    def test_add_image_template(self, mock_easyocr, mock_config_manager):
        """测试添加图像模板"""
        # Mock配置
        mock_config_manager.get_beike_ui_config.return_value = self.mock_config
        
        # Mock OCR
        mock_reader = Mock()
        mock_easyocr.Reader.return_value = mock_reader
        
        # 创建定位器实例
        locator = BeikeUILocator()
        
        # 创建测试图像文件
        test_image_path = self.templates_dir / "new_template.png"
        import cv2
        test_image = np.zeros((50, 50, 3), dtype=np.uint8)
        test_image[20:30, 20:30] = [0, 255, 0]  # 绿色方块
        cv2.imwrite(str(test_image_path), test_image)
        
        # 测试添加模板
        locator.add_image_template("new_button", str(test_image_path))
        
        # 验证模板被添加
        self.assertIn("new_button", locator.template_images)
        self.assertIsInstance(locator.template_images["new_button"], np.ndarray)
    
    @patch('src.ui_automation.beike_ui_locator.config_manager')
    @patch('src.ui_automation.beike_ui_locator.easyocr')
    def test_validate_coordinates(self, mock_easyocr, mock_config_manager):
        """测试坐标验证"""
        # Mock配置
        mock_config_manager.get_beike_ui_config.return_value = self.mock_config
        
        # Mock OCR
        mock_reader = Mock()
        mock_easyocr.Reader.return_value = mock_reader
        
        # 创建定位器实例
        locator = BeikeUILocator()
        
        # 测试有效坐标
        valid_coords = (100, 200)
        result = locator.validate_coordinates("test_button", valid_coords)
        self.assertTrue(result)
        
        # 测试无效坐标
        invalid_coords = (-100, -200)
        result = locator.validate_coordinates("test_button", invalid_coords)
        self.assertFalse(result)
    
    @patch('src.ui_automation.beike_ui_locator.config_manager')
    @patch('src.ui_automation.beike_ui_locator.easyocr')
    def test_get_element_info(self, mock_easyocr, mock_config_manager):
        """测试获取元素信息"""
        # Mock配置
        mock_config_manager.get_beike_ui_config.return_value = self.mock_config
        
        # Mock OCR
        mock_reader = Mock()
        mock_easyocr.Reader.return_value = mock_reader
        
        # 创建定位器实例
        locator = BeikeUILocator()
        
        # 添加一些测试数据
        locator.coordinate_cache["test_button"] = (100, 200)
        locator.template_images["test_button"] = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # 测试获取元素信息
        info = locator.get_element_info("test_button")
        
        # 验证信息结构
        self.assertIsInstance(info, dict)
        self.assertIn("coordinates", info)
        self.assertIn("template_loaded", info)
        self.assertIn("cache_status", info)
        
        # 验证具体值
        self.assertEqual(info["coordinates"], (100, 200))
        self.assertTrue(info["template_loaded"])
        self.assertTrue(info["cache_status"])


if __name__ == '__main__':
    unittest.main()
