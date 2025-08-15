"""
贝壳库UI定位器
实现多层级识别策略：图像识别 > 坐标定位 > 颜色匹配 > OCR文本
"""

import cv2
import numpy as np
import easyocr
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
from PIL import Image, ImageGrab
import time
from src.utils.logger import get_logger
from src.utils.config_manager import config_manager


class BeikeUILocator:
    """贝壳库UI定位器"""
    
    def __init__(self):
        """初始化定位器"""
        self.logger = get_logger("BeikeUILocator")
        self.config = config_manager.get_beike_ui_config()
        
        # 初始化组件
        self.template_images: Dict[str, np.ndarray] = {}
        self.coordinate_cache: Dict[str, Tuple[int, int]] = {}
        self.color_patterns: Dict[str, Dict[str, Any]] = {}
        
        # 初始化OCR
        self.ocr_reader = None
        if self.config.get('ocr', {}).get('enabled', True):
            self._init_ocr()
        
        # 加载配置
        self._load_config()
    
    def _init_ocr(self):
        """初始化OCR"""
        try:
            languages = self.config.get('ocr', {}).get('language', 'ch_sim+en')
            self.ocr_reader = easyocr.Reader(languages.split('+'))
            self.logger.info("OCR初始化成功")
        except Exception as e:
            self.logger.warning(f"OCR初始化失败: {e}")
            self.ocr_reader = None
    
    def _load_config(self):
        """加载配置"""
        # 加载坐标缓存
        self._load_coordinate_cache()
        
        # 加载图像模板
        self._load_image_templates()
        
        # 加载颜色模式
        self._load_color_patterns()
    
    def _load_coordinate_cache(self):
        """加载坐标缓存"""
        cache_config = self.config.get('coordinate_cache', {})
        if cache_config.get('enabled', True):
            cache_file = Path("data/coordinate_cache.json")
            if cache_file.exists():
                try:
                    import json
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        self.coordinate_cache = json.load(f)
                    self.logger.info(f"加载坐标缓存: {len(self.coordinate_cache)} 项")
                except Exception as e:
                    self.logger.warning(f"加载坐标缓存失败: {e}")
    
    def _load_image_templates(self):
        """加载图像模板"""
        template_config = self.config.get('image_templates', {})
        base_path = Path(template_config.get('base_path', 'data/templates'))
        
        if base_path.exists():
            for template_file in base_path.glob("*.png"):
                template_name = template_file.stem
                try:
                    template = cv2.imread(str(template_file))
                    if template is not None:
                        self.template_images[template_name] = template
                        self.logger.debug(f"加载图像模板: {template_name}")
                except Exception as e:
                    self.logger.warning(f"加载图像模板失败 {template_name}: {e}")
        
        self.logger.info(f"加载图像模板: {len(self.template_images)} 个")
    
    def _load_color_patterns(self):
        """加载颜色模式"""
        # 预定义的颜色模式
        self.color_patterns = {
            "button_normal": {
                "primary": (0, 120, 215),    # 蓝色按钮
                "tolerance": 20
            },
            "button_hover": {
                "primary": (0, 100, 180),    # 悬停状态
                "tolerance": 20
            },
            "button_pressed": {
                "primary": (0, 80, 150),     # 按下状态
                "tolerance": 20
            },
            "text_normal": {
                "primary": (0, 0, 0),        # 黑色文字
                "tolerance": 30
            },
            "text_disabled": {
                "primary": (128, 128, 128),  # 灰色文字
                "tolerance": 30
            }
        }
    
    def locate_element(self, target_name: str, method: str = "auto") -> Optional[Tuple[int, int]]:
        """
        定位UI元素
        
        Args:
            target_name: 目标元素名称
            method: 定位方法 ("auto", "image", "coordinate", "color", "ocr")
            
        Returns:
            元素坐标 (x, y)，未找到返回None
        """
        start_time = time.time()
        
        try:
            if method == "auto":
                # 按优先级尝试不同方法
                recognition_priority = self.config.get('recognition_priority', [
                    'image_recognition', 'coordinate_positioning', 
                    'color_matching', 'ocr_text'
                ])
                
                for method_name in recognition_priority:
                    if method_name == 'image_recognition':
                        result = self._locate_by_image(target_name)
                        if result:
                            self.logger.info(f"图像识别定位成功: {target_name}")
                            return result
                    
                    elif method_name == 'coordinate_positioning':
                        result = self._locate_by_coordinate(target_name)
                        if result:
                            self.logger.info(f"坐标定位成功: {target_name}")
                            return result
                    
                    elif method_name == 'color_matching':
                        result = self._locate_by_color(target_name)
                        if result:
                            self.logger.info(f"颜色匹配定位成功: {target_name}")
                            return result
                    
                    elif method_name == 'ocr_text':
                        result = self._locate_by_ocr(target_name)
                        if result:
                            self.logger.info(f"OCR定位成功: {target_name}")
                            return result
                
                self.logger.warning(f"所有定位方法都失败: {target_name}")
                return None
            
            else:
                # 使用指定方法
                if method == "image":
                    return self._locate_by_image(target_name)
                elif method == "coordinate":
                    return self._locate_by_coordinate(target_name)
                elif method == "color":
                    return self._locate_by_color(target_name)
                elif method == "ocr":
                    return self._locate_by_ocr(target_name)
                else:
                    self.logger.error(f"不支持的定位方法: {method}")
                    return None
        
        except Exception as e:
            self.logger.error(f"定位元素失败 {target_name}: {e}")
            return None
        
        finally:
            duration = time.time() - start_time
            self.logger.debug(f"定位耗时: {duration:.3f}秒")
    
    def _locate_by_image(self, target_name: str) -> Optional[Tuple[int, int]]:
        """通过图像模板匹配定位元素"""
        if target_name not in self.template_images:
            self.logger.warning(f"图像模板不存在: {target_name}")
            return None
        
        try:
            # 截取屏幕
            screenshot = self._capture_screen()
            if screenshot is None:
                return None
            
            # 获取模板
            template = self.template_images[target_name]
            
            # 模板匹配
            confidence_threshold = self.config.get('image_recognition', {}).get('confidence_threshold', 0.8)
            
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= confidence_threshold:
                # 计算中心点
                h, w = template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                
                self.logger.debug(f"图像匹配成功: {target_name}, 置信度: {max_val:.3f}")
                return (center_x, center_y)
            else:
                self.logger.debug(f"图像匹配失败: {target_name}, 置信度: {max_val:.3f}")
                return None
        
        except Exception as e:
            self.logger.error(f"图像定位失败 {target_name}: {e}")
            return None
    
    def _locate_by_coordinate(self, target_name: str) -> Optional[Tuple[int, int]]:
        """通过缓存坐标定位元素"""
        if target_name in self.coordinate_cache:
            coordinates = self.coordinate_cache[target_name]
            self.logger.debug(f"坐标缓存命中: {target_name}")
            return coordinates
        
        self.logger.debug(f"坐标缓存未命中: {target_name}")
        return None
    
    def _locate_by_color(self, target_name: str) -> Optional[Tuple[int, int]]:
        """通过颜色模式定位元素"""
        try:
            # 截取屏幕
            screenshot = self._capture_screen()
            if screenshot is None:
                return None
            
            # 查找匹配的颜色模式
            for pattern_name, pattern in self.color_patterns.items():
                if target_name.lower() in pattern_name.lower():
                    primary_color = pattern['primary']
                    tolerance = pattern['tolerance']
                    
                    # 颜色范围
                    lower = np.array([max(0, c - tolerance) for c in primary_color])
                    upper = np.array([min(255, c + tolerance) for c in primary_color])
                    
                    # 颜色掩码
                    mask = cv2.inRange(screenshot, lower, upper)
                    
                    # 查找轮廓
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    if contours:
                        # 选择最大的轮廓
                        largest_contour = max(contours, key=cv2.contourArea)
                        M = cv2.moments(largest_contour)
                        
                        if M["m00"] != 0:
                            center_x = int(M["m10"] / M["m00"])
                            center_y = int(M["m01"] / M["m00"])
                            
                            self.logger.debug(f"颜色匹配成功: {target_name}, 模式: {pattern_name}")
                            return (center_x, center_y)
            
            self.logger.debug(f"颜色匹配失败: {target_name}")
            return None
        
        except Exception as e:
            self.logger.error(f"颜色定位失败 {target_name}: {e}")
            return None
    
    def _locate_by_ocr(self, target_name: str) -> Optional[Tuple[int, int]]:
        """通过OCR文本识别定位元素"""
        if self.ocr_reader is None:
            self.logger.warning("OCR未初始化")
            return None
        
        try:
            # 截取屏幕
            screenshot = self._capture_screen()
            if screenshot is None:
                return None
            
            # OCR识别
            results = self.ocr_reader.readtext(screenshot)
            confidence_threshold = self.config.get('ocr', {}).get('confidence_threshold', 0.7)
            
            for (bbox, text, confidence) in results:
                if confidence >= confidence_threshold and target_name.lower() in text.lower():
                    # 计算文本中心点
                    top_left = bbox[0]
                    bottom_right = bbox[2]
                    
                    center_x = int((top_left[0] + bottom_right[0]) / 2)
                    center_y = int((top_left[1] + bottom_right[1]) / 2)
                    
                    self.logger.debug(f"OCR识别成功: {target_name}, 文本: {text}, 置信度: {confidence:.3f}")
                    return (center_x, center_y)
            
            self.logger.debug(f"OCR识别失败: {target_name}")
            return None
        
        except Exception as e:
            self.logger.error(f"OCR定位失败 {target_name}: {e}")
            return None
    
    def _capture_screen(self) -> Optional[np.ndarray]:
        """截取屏幕"""
        try:
            # 使用PIL截屏
            screenshot = ImageGrab.grab()
            screenshot_np = np.array(screenshot)
            
            # 转换为OpenCV格式 (BGR)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            return screenshot_cv
        
        except Exception as e:
            self.logger.error(f"截屏失败: {e}")
            return None
    
    def update_coordinate_cache(self, target_name: str, coordinates: Tuple[int, int]):
        """更新坐标缓存"""
        self.coordinate_cache[target_name] = coordinates
        
        # 保存到文件
        cache_file = Path("data/coordinate_cache.json")
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            import json
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.coordinate_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.warning(f"保存坐标缓存失败: {e}")
    
    def add_image_template(self, target_name: str, template_path: str):
        """添加图像模板"""
        try:
            template = cv2.imread(template_path)
            if template is not None:
                self.template_images[target_name] = template
                self.logger.info(f"添加图像模板: {target_name}")
                
                # 保存到模板目录
                template_dir = Path(self.config.get('image_templates', {}).get('base_path', 'data/templates'))
                template_dir.mkdir(parents=True, exist_ok=True)
                
                save_path = template_dir / f"{target_name}.png"
                cv2.imwrite(str(save_path), template)
            else:
                self.logger.error(f"加载图像模板失败: {template_path}")
        
        except Exception as e:
            self.logger.error(f"添加图像模板失败 {target_name}: {e}")
    
    def validate_coordinates(self, target_name: str, coordinates: Tuple[int, int]) -> bool:
        """验证坐标有效性"""
        try:
            # 检查坐标是否在屏幕范围内
            screen_width, screen_height = ImageGrab.grab().size
            
            x, y = coordinates
            if 0 <= x < screen_width and 0 <= y < screen_height:
                return True
            else:
                self.logger.warning(f"坐标超出屏幕范围: {target_name} ({x}, {y})")
                return False
        
        except Exception as e:
            self.logger.error(f"验证坐标失败 {target_name}: {e}")
            return False
    
    def get_element_info(self, target_name: str) -> Dict[str, Any]:
        """获取元素信息"""
        info = {
            "name": target_name,
            "has_template": target_name in self.template_images,
            "has_coordinates": target_name in self.coordinate_cache,
            "template_size": None,
            "cached_coordinates": None
        }
        
        if target_name in self.template_images:
            template = self.template_images[target_name]
            info["template_size"] = (template.shape[1], template.shape[0])
        
        if target_name in self.coordinate_cache:
            info["cached_coordinates"] = self.coordinate_cache[target_name]
        
        return info
