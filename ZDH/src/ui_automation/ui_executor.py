"""
UI执行器
提供高级UI自动化操作接口
"""

import time
import pywinauto
from pywinauto import Application, WindowSpecification
from pywinauto.controls import ButtonWrapper, EditWrapper, ComboBoxWrapper
from typing import Optional, Tuple, Dict, Any, Union
from pathlib import Path
import win32api
import win32con
import win32gui
from src.utils.logger import get_logger
from src.utils.config_manager import config_manager
from src.ui_automation.beike_ui_locator import BeikeUILocator


class UIExecutor:
    """UI自动化执行器"""
    
    def __init__(self):
        """初始化执行器"""
        self.logger = get_logger("UIExecutor")
        self.config = config_manager.get_ui_config()
        self.locator = BeikeUILocator()
        
        # 操作配置
        self.click_delay = self.config.get('operations', {}).get('click_delay', 0.1)
        self.type_delay = self.config.get('operations', {}).get('type_delay', 0.05)
        self.wait_timeout = self.config.get('operations', {}).get('wait_timeout', 30)
        self.retry_count = self.config.get('operations', {}).get('retry_count', 3)
        
        # 当前应用和窗口
        self.current_app: Optional[Application] = None
        self.current_window: Optional[WindowSpecification] = None
    
    def connect_to_application(self, app_path: str, app_name: str = None) -> bool:
        """
        连接到应用程序
        
        Args:
            app_path: 应用程序路径
            app_name: 应用程序名称
            
        Returns:
            连接是否成功
        """
        try:
            self.logger.info(f"连接到应用程序: {app_path}")
            
            # 尝试连接到已运行的应用程序
            try:
                if app_name:
                    self.current_app = Application().connect(title_re=f".*{app_name}.*")
                else:
                    self.current_app = Application().connect(path=app_path)
                
                self.logger.info("连接到已运行的应用程序成功")
                
            except Exception:
                # 启动新应用程序
                self.logger.info("启动新应用程序")
                self.current_app = Application().start(app_path)
                time.sleep(2)  # 等待应用启动
            
            # 获取主窗口
            self.current_window = self.current_app.window()
            self.logger.info(f"主窗口标题: {self.current_window.window_text()}")
            
            return True
        
        except Exception as e:
            self.logger.error(f"连接应用程序失败: {e}")
            return False
    
    def click_element(self, target: str, method: str = "auto", 
                     click_type: str = "left", retry: bool = True) -> bool:
        """
        点击元素
        
        Args:
            target: 目标元素名称
            method: 定位方法
            click_type: 点击类型 ("left", "right", "double")
            retry: 是否重试
            
        Returns:
            点击是否成功
        """
        max_attempts = self.retry_count if retry else 1
        
        for attempt in range(max_attempts):
            try:
                self.logger.info(f"点击元素: {target}, 尝试 {attempt + 1}/{max_attempts}")
                
                # 定位元素
                coordinates = self.locator.locate_element(target, method)
                if coordinates is None:
                    if attempt < max_attempts - 1:
                        self.logger.warning(f"定位元素失败，等待后重试: {target}")
                        time.sleep(1)
                        continue
                    else:
                        self.logger.error(f"定位元素失败: {target}")
                        return False
                
                # 执行点击
                x, y = coordinates
                if click_type == "left":
                    win32api.SetCursorPos((x, y))
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
                    time.sleep(self.click_delay)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
                elif click_type == "right":
                    win32api.SetCursorPos((x, y))
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
                    time.sleep(self.click_delay)
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)
                elif click_type == "double":
                    win32api.SetCursorPos((x, y))
                    for _ in range(2):
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
                        time.sleep(self.click_delay)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
                        time.sleep(self.click_delay)
                
                self.logger.info(f"点击成功: {target} at ({x}, {y})")
                return True
                
            except Exception as e:
                self.logger.error(f"点击失败 {target}: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(1)
                    continue
                else:
                    return False
        
        return False
    
    def input_text(self, target: str, text: str, method: str = "auto", 
                   clear_first: bool = True) -> bool:
        """
        输入文本
        
        Args:
            target: 目标元素名称
            text: 要输入的文本
            method: 定位方法
            clear_first: 是否先清空
            
        Returns:
            输入是否成功
        """
        try:
            self.logger.info(f"输入文本: {target} -> {text}")
            
            # 定位元素
            coordinates = self.locator.locate_element(target, method)
            if coordinates is None:
                self.logger.error(f"定位元素失败: {target}")
                return False
            
            # 点击元素以获取焦点
            x, y = coordinates
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            time.sleep(self.click_delay)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            time.sleep(0.5)  # 等待焦点
            
            # 清空现有内容
            if clear_first:
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                win32api.keybd_event(ord('A'), 0, 0, 0)
                win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_DELETE, 0, 0, 0)
                win32api.keybd_event(win32con.VK_DELETE, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.1)
            
            # 输入文本
            for char in text:
                if char.isupper():
                    win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                    win32api.keybd_event(ord(char.upper()), 0, 0, 0)
                    win32api.keybd_event(ord(char.upper()), 0, win32con.KEYEVENTF_KEYUP, 0)
                    win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
                else:
                    win32api.keybd_event(ord(char.upper()), 0, 0, 0)
                    win32api.keybd_event(ord(char.upper()), 0, win32con.KEYEVENTF_KEYUP, 0)
                
                time.sleep(self.type_delay)
            
            self.logger.info(f"文本输入成功: {target} -> {text}")
            return True
            
        except Exception as e:
            self.logger.error(f"文本输入失败 {target}: {e}")
            return False
    
    def select_option(self, target: str, option: str, method: str = "auto") -> bool:
        """
        选择选项
        
        Args:
            target: 目标元素名称
            option: 要选择的选项
            method: 定位方法
            
        Returns:
            选择是否成功
        """
        try:
            self.logger.info(f"选择选项: {target} -> {option}")
            
            # 定位元素
            coordinates = self.locator.locate_element(target, method)
            if coordinates is None:
                self.logger.error(f"定位元素失败: {target}")
                return False
            
            # 点击元素
            if not self.click_element(target, method):
                return False
            
            time.sleep(0.5)  # 等待下拉菜单展开
            
            # 查找并选择选项
            # 这里可以使用OCR识别下拉选项，或者通过键盘导航
            # 简化实现：使用键盘导航
            option_lower = option.lower()
            
            # 模拟键盘输入选项名称
            for char in option:
                win32api.keybd_event(ord(char.upper()), 0, 0, 0)
                win32api.keybd_event(ord(char.upper()), 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(self.type_delay)
            
            # 按回车确认选择
            time.sleep(0.2)
            win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
            win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            self.logger.info(f"选项选择成功: {target} -> {option}")
            return True
            
        except Exception as e:
            self.logger.error(f"选项选择失败 {target}: {e}")
            return False
    
    def wait_for_element(self, target: str, method: str = "auto", 
                        timeout: int = None) -> bool:
        """
        等待元素出现
        
        Args:
            target: 目标元素名称
            method: 定位方法
            timeout: 超时时间（秒）
            
        Returns:
            元素是否出现
        """
        if timeout is None:
            timeout = self.wait_timeout
        
        start_time = time.time()
        self.logger.info(f"等待元素: {target}, 超时: {timeout}秒")
        
        while time.time() - start_time < timeout:
            try:
                coordinates = self.locator.locate_element(target, method)
                if coordinates is not None:
                    self.logger.info(f"元素出现: {target}")
                    return True
                
                time.sleep(0.5)  # 等待间隔
                
            except Exception as e:
                self.logger.debug(f"等待元素时出错: {e}")
                time.sleep(0.5)
        
        self.logger.warning(f"等待元素超时: {target}")
        return False
    
    def wait_for_element_disappear(self, target: str, method: str = "auto", 
                                 timeout: int = None) -> bool:
        """
        等待元素消失
        
        Args:
            target: 目标元素名称
            method: 定位方法
            timeout: 超时时间（秒）
            
        Returns:
            元素是否消失
        """
        if timeout is None:
            timeout = self.wait_timeout
        
        start_time = time.time()
        self.logger.info(f"等待元素消失: {target}, 超时: {timeout}秒")
        
        while time.time() - start_time < timeout:
            try:
                coordinates = self.locator.locate_element(target, method)
                if coordinates is None:
                    self.logger.info(f"元素消失: {target}")
                    return True
                
                time.sleep(0.5)  # 等待间隔
                
            except Exception as e:
                self.logger.debug(f"等待元素消失时出错: {e}")
                time.sleep(0.5)
        
        self.logger.warning(f"等待元素消失超时: {target}")
        return False
    
    def take_screenshot(self, save_path: str = None) -> Optional[str]:
        """
        截取屏幕截图
        
        Args:
            save_path: 保存路径
            
        Returns:
            截图文件路径
        """
        try:
            if save_path is None:
                # 生成默认路径
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                save_path = f"data/screenshots/screenshot_{timestamp}.png"
            
            # 确保目录存在
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 截取屏幕
            screenshot = self.locator._capture_screen()
            if screenshot is not None:
                # 保存截图
                cv2.imwrite(str(save_path), screenshot)
                self.logger.info(f"截图保存成功: {save_path}")
                return str(save_path)
            else:
                self.logger.error("截取屏幕失败")
                return None
                
        except Exception as e:
            self.logger.error(f"截图失败: {e}")
            return None
    
    def drag_and_drop(self, source: str, target: str, 
                     source_method: str = "auto", target_method: str = "auto") -> bool:
        """
        拖拽操作
        
        Args:
            source: 源元素名称
            target: 目标元素名称
            source_method: 源元素定位方法
            target_method: 目标元素定位方法
            
        Returns:
            拖拽是否成功
        """
        try:
            self.logger.info(f"拖拽操作: {source} -> {target}")
            
            # 定位源元素和目标元素
            source_coords = self.locator.locate_element(source, source_method)
            target_coords = self.locator.locate_element(target, target_method)
            
            if source_coords is None or target_coords is None:
                self.logger.error(f"定位元素失败: source={source}, target={target}")
                return False
            
            # 执行拖拽
            start_x, start_y = source_coords
            end_x, end_y = target_coords
            
            # 移动到源元素
            win32api.SetCursorPos((start_x, start_y))
            time.sleep(0.2)
            
            # 按下鼠标左键
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, start_x, start_y, 0, 0)
            time.sleep(0.2)
            
            # 移动到目标元素
            win32api.SetCursorPos((end_x, end_y))
            time.sleep(0.2)
            
            # 释放鼠标左键
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, end_x, end_y, 0, 0)
            
            self.logger.info(f"拖拽操作成功: {source} -> {target}")
            return True
            
        except Exception as e:
            self.logger.error(f"拖拽操作失败: {e}")
            return False
    
    def scroll(self, target: str, direction: str = "down", 
               amount: int = 100, method: str = "auto") -> bool:
        """
        滚动操作
        
        Args:
            target: 目标元素名称
            direction: 滚动方向 ("up", "down", "left", "right")
            amount: 滚动量
            method: 定位方法
            
        Returns:
            滚动是否成功
        """
        try:
            self.logger.info(f"滚动操作: {target} {direction} {amount}")
            
            # 定位元素
            coordinates = self.locator.locate_element(target, method)
            if coordinates is None:
                self.logger.error(f"定位元素失败: {target}")
                return False
            
            # 移动到目标元素
            x, y = coordinates
            win32api.SetCursorPos((x, y))
            time.sleep(0.2)
            
            # 执行滚动
            if direction == "down":
                win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, x, y, -amount, 0)
            elif direction == "up":
                win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, x, y, amount, 0)
            elif direction == "left":
                win32api.mouse_event(win32con.MOUSEEVENTF_HWHEEL, x, y, -amount, 0)
            elif direction == "right":
                win32api.mouse_event(win32con.MOUSEEVENTF_HWHEEL, x, y, amount, 0)
            
            self.logger.info(f"滚动操作成功: {target} {direction}")
            return True
            
        except Exception as e:
            self.logger.error(f"滚动操作失败: {e}")
            return False
    
    def get_element_text(self, target: str, method: str = "auto") -> Optional[str]:
        """
        获取元素文本
        
        Args:
            target: 目标元素名称
            method: 定位方法
            
        Returns:
            元素文本内容
        """
        try:
            self.logger.info(f"获取元素文本: {target}")
            
            # 使用OCR获取文本
            if self.locator.ocr_reader is not None:
                # 截取屏幕
                screenshot = self.locator._capture_screen()
                if screenshot is not None:
                    # OCR识别
                    results = self.locator.ocr_reader.readtext(screenshot)
                    confidence_threshold = self.config.get('ocr', {}).get('confidence_threshold', 0.7)
                    
                    # 查找目标元素附近的文本
                    target_coords = self.locator.locate_element(target, method)
                    if target_coords:
                        target_x, target_y = target_coords
                        
                        for (bbox, text, confidence) in results:
                            if confidence >= confidence_threshold:
                                # 检查文本是否在目标元素附近
                                bbox_center_x = (bbox[0][0] + bbox[2][0]) / 2
                                bbox_center_y = (bbox[0][1] + bbox[2][1]) / 2
                                
                                # 简单的距离检查（可以优化）
                                distance = ((bbox_center_x - target_x) ** 2 + 
                                          (bbox_center_y - target_y) ** 2) ** 0.5
                                
                                if distance < 100:  # 100像素内的文本
                                    self.logger.info(f"获取元素文本成功: {target} -> {text}")
                                    return text
            
            self.logger.warning(f"无法获取元素文本: {target}")
            return None
            
        except Exception as e:
            self.logger.error(f"获取元素文本失败: {e}")
            return None
    
    def is_element_visible(self, target: str, method: str = "auto") -> bool:
        """
        检查元素是否可见
        
        Args:
            target: 目标元素名称
            method: 定位方法
            
        Returns:
            元素是否可见
        """
        try:
            coordinates = self.locator.locate_element(target, method)
            return coordinates is not None
            
        except Exception as e:
            self.logger.error(f"检查元素可见性失败: {e}")
            return False
    
    def get_current_window_info(self) -> Dict[str, Any]:
        """获取当前窗口信息"""
        try:
            if self.current_window:
                return {
                    "title": self.current_window.window_text(),
                    "class_name": self.current_window.class_name(),
                    "handle": self.current_window.handle,
                    "is_visible": self.current_window.is_visible(),
                    "is_enabled": self.current_window.is_enabled()
                }
            else:
                return {}
        except Exception as e:
            self.logger.error(f"获取窗口信息失败: {e}")
            return {}
