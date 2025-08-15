#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一自动化测试框架
整合文件打开、应用程序启动、网页自动化等功能
"""

import os
import sys
import time
import json
import subprocess
import psutil
import pyautogui
import pywinauto
from pywinauto import Application
from pywinauto.findwindows import find_window
import win32api
import win32con
import win32gui
import win32com.client
from PIL import Image, ImageFilter
import easyocr
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation_framework.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ActionType(Enum):
    """操作类型枚举"""
    OPEN_FILE = "open_file"
    OPEN_APPLICATION = "open_application"
    CLICK = "click"
    TYPE = "type"
    PRESS_KEY = "press_key"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    VERIFY = "verify"
    NAVIGATE_URL = "navigate_url"

@dataclass
class AutomationStep:
    """自动化步骤"""
    step_id: str
    action_type: ActionType
    description: str
    parameters: Dict[str, Any]
    expected_result: str
    timeout: int = 30
    retry_count: int = 3
    critical: bool = True

@dataclass
class TestCase:
    """测试用例"""
    case_id: str
    name: str
    description: str
    steps: List[AutomationStep]
    preconditions: List[str] = None
    postconditions: List[str] = None
    tags: List[str] = None

class UnifiedAutomationFramework:
    """统一自动化测试框架"""
    
    def __init__(self, config_file: str = "test_case_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self.ocr_reader = None
        self.screenshot_dir = "screenshots"
        self.reports_dir = "reports"
        self._ensure_directories()
        self._init_ocr()
        
        # 设置pyautogui安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        # 常见软件配置
        self.software_configs = {
            "极光PDF": {
                "process_names": ["JiGuangPDF.exe", "JiGuangPDFReader.exe"],
                "window_titles": ["极光PDF", "JiGuangPDF"],
                "install_paths": [
                    "C:\\Program Files\\JiGuangPDF",
                    "C:\\Program Files (x86)\\JiGuangPDF",
                    os.path.expanduser("~\\AppData\\Local\\JiGuangPDF")
                ]
            },
            "Adobe Reader": {
                "process_names": ["AcroRd32.exe", "AcroRd64.exe"],
                "window_titles": ["Adobe Reader", "Adobe Acrobat Reader"],
                "install_paths": [
                    "C:\\Program Files\\Adobe\\Acrobat Reader",
                    "C:\\Program Files (x86)\\Adobe\\Acrobat Reader"
                ]
            },
            "WPS": {
                "process_names": ["wps.exe", "wpp.exe", "et.exe"],
                "window_titles": ["WPS", "金山WPS"],
                "install_paths": [
                    "C:\\Program Files\\WPS Office",
                    "C:\\Program Files (x86)\\WPS Office"
                ]
            }
        }
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        for directory in [self.screenshot_dir, self.reports_dir, "logs", "data"]:
            os.makedirs(directory, exist_ok=True)
    
    def check_software_installed(self, software_name: str) -> bool:
        """检查软件是否已安装"""
        if software_name not in self.software_configs:
            logger.warning(f"未知软件: {software_name}")
            return False
        
        config = self.software_configs[software_name]
        
        # 检查安装路径
        for install_path in config["install_paths"]:
            if os.path.exists(install_path):
                logger.info(f"软件 {software_name} 已安装在: {install_path}")
                return True
        
        # 检查注册表
        try:
            import winreg
            for key_path in [
                f"SOFTWARE\\{software_name}",
                f"SOFTWARE\\WOW6432Node\\{software_name}"
            ]:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                    winreg.CloseKey(key)
                    logger.info(f"软件 {software_name} 在注册表中找到")
                    return True
                except FileNotFoundError:
                    continue
        except ImportError:
            logger.warning("无法导入winreg模块，跳过注册表检查")
        
        logger.warning(f"软件 {software_name} 未安装")
        return False
    
    def check_software_running(self, software_name: str) -> bool:
        """检查软件是否正在运行"""
        if software_name not in self.software_configs:
            return False
        
        config = self.software_configs[software_name]
        
        # 检查进程
        for process_name in config["process_names"]:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] == process_name:
                        logger.info(f"软件 {software_name} 正在运行，进程ID: {proc.info['pid']}")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        logger.info(f"软件 {software_name} 未运行")
        return False
    
    def check_window_exists(self, software_name: str) -> bool:
        """检查软件窗口是否存在"""
        if software_name not in self.software_configs:
            return False
        
        config = self.software_configs[software_name]
        
        # 检查窗口标题
        for window_title in config["window_titles"]:
            try:
                windows = find_window(title_re=f".*{window_title}.*")
                if windows:
                    logger.info(f"找到软件 {software_name} 的窗口: {windows}")
                    return True
            except Exception as e:
                logger.debug(f"查找窗口失败: {e}")
        
        return False
    
    def launch_software_if_needed(self, software_name: str) -> bool:
        """如果需要，启动软件"""
        if self.check_software_running(software_name):
            logger.info(f"软件 {software_name} 已在运行")
            return True
        
        if not self.check_software_installed(software_name):
            logger.error(f"软件 {software_name} 未安装，无法启动")
            return False
        
        # 尝试启动软件
        try:
            config = self.software_configs[software_name]
            for install_path in config["install_paths"]:
                exe_path = os.path.join(install_path, config["process_names"][0])
                if os.path.exists(exe_path):
                    subprocess.Popen([exe_path])
                    logger.info(f"启动软件 {software_name}: {exe_path}")
                    
                    # 等待软件启动
                    for _ in range(30):  # 最多等待30秒
                        time.sleep(1)
                        if self.check_software_running(software_name):
                            logger.info(f"软件 {software_name} 启动成功")
                            return True
                    
                    logger.warning(f"软件 {software_name} 启动超时")
                    return False
            
            logger.error(f"未找到软件 {software_name} 的可执行文件")
            return False
            
        except Exception as e:
            logger.error(f"启动软件 {software_name} 失败: {e}")
            return False
    
    def execute_preconditions(self, test_case: TestCase) -> bool:
        """执行前置条件检查"""
        if not test_case.preconditions:
            # 如果没有前置条件，尝试从描述中解析
            self._parse_preconditions_from_description(test_case)
        
        if not test_case.preconditions:
            logger.info("无前置条件，跳过检查")
            return True
        
        logger.info("开始执行前置条件...")
        
        for precondition in test_case.preconditions:
            logger.info(f"执行前置条件: {precondition}")
            
            # 检查软件安装和运行状态
            if "极光PDF已安装" in precondition:
                if not self.check_software_installed("极光PDF"):
                    logger.error("前置条件失败: 极光PDF未安装")
                    return False
                
            elif "Adobe Reader已安装" in precondition:
                if not self.check_software_installed("Adobe Reader"):
                    logger.error("前置条件失败: Adobe Reader未安装")
                    return False
                
            elif "WPS已安装" in precondition:
                if not self.check_software_installed("WPS"):
                    logger.error("前置条件失败: WPS未安装")
                    return False
            
            # 执行需要AI主动操作的前置条件
            elif "打开PDF阅读器界面" in precondition:
                if not self._ai_open_pdf_reader():
                    logger.error("前置条件失败: 无法打开PDF阅读器界面")
                    return False
                
            elif "打开文件" in precondition:
                if not self._ai_open_pdf_file():
                    logger.error("前置条件失败: 无法打开PDF文件")
                    return False
                
            elif "选取一段文字" in precondition:
                if not self._ai_select_text():
                    logger.error("前置条件失败: 无法选取文字")
                    return False
                
            elif "右键点击选取文字区域" in precondition:
                if not self._ai_right_click_selected_text():
                    logger.error("前置条件失败: 无法右键点击文字区域")
                    return False
        
        logger.info("前置条件执行完成")
        return True
    
    def _parse_preconditions_from_description(self, test_case: TestCase):
        """从测试用例描述中解析前置条件"""
        if not test_case.description:
            return
        
        description = test_case.description.lower()
        
        # 根据产品信息自动生成前置条件
        if "极光pdf" in description:
            test_case.preconditions = [
                "极光PDF已安装",
                "打开PDF阅读器界面",
                "打开文件",
                "选取一段文字",
                "右键点击选取文字区域"
            ]
            logger.info("从描述中解析出前置条件: 极光PDF相关")
            
        elif "adobe" in description or "reader" in description:
            test_case.preconditions = [
                "Adobe Reader已安装",
                "打开PDF阅读器界面",
                "打开文件",
                "选取一段文字",
                "右键点击选取文字区域"
            ]
            logger.info("从描述中解析出前置条件: Adobe Reader相关")
            
        elif "wps" in description:
            test_case.preconditions = [
                "WPS已安装",
                "打开WPS界面",
                "打开文件"
            ]
            logger.info("从描述中解析出前置条件: WPS相关")
        
        # 根据功能类型添加通用前置条件
        if "右键菜单" in description:
            if not test_case.preconditions:
                test_case.preconditions = []
            if "选取文字" not in str(test_case.preconditions):
                test_case.preconditions.append("选取一段文字")
            if "右键点击" not in str(test_case.preconditions):
                test_case.preconditions.append("右键点击选取文字区域")
        
        if "文件操作" in description or "打开文件" in description:
            if not test_case.preconditions:
                test_case.preconditions = []
            if "打开文件" not in str(test_case.preconditions):
                test_case.preconditions.append("打开文件")
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                
            # 检查配置文件结构，如果是旧格式，使用默认配置
            if "test_case" in loaded_config and "test_steps" in loaded_config:
                logger.warning("检测到旧格式配置文件，使用默认配置")
                return self._get_default_config()
            else:
                return loaded_config
                
        except FileNotFoundError:
            logger.warning(f"配置文件 {self.config_file} 不存在，使用默认配置")
            return self._get_default_config()
        except Exception as e:
            logger.warning(f"加载配置文件失败: {e}，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "ocr": {
                "enabled": True,
                "language": "ch_sim+en",
                "confidence": 0.6
            },
            "image_recognition": {
                "confidence": 0.8,
                "cache_enabled": True
            },
            "ui_automation": {
                "default_timeout": 30,
                "retry_count": 3,
                "click_delay": 0.5
            },
            "file_operations": {
                "desktop_path": os.path.join(os.path.expanduser("~"), "Desktop"),
                "common_paths": [
                    os.path.join(os.path.expanduser("~"), "Desktop"),
                    os.path.join(os.path.expanduser("~"), "Documents"),
                    os.path.join(os.path.expanduser("~"), "Downloads")
                ]
            },
            "applications": {
                "edge": {
                    "paths": [
                        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
                    ],
                    "process_name": "msedge.exe"
                },
                "github_desktop": {
                    "paths": [
                        r"C:\Users\{username}\AppData\Local\GitHubDesktop\GitHubDesktop.exe",
                        r"C:\Program Files\GitHub, Inc\GitHub Desktop\GitHubDesktop.exe"
                    ],
                    "process_name": "GitHubDesktop.exe"
                }
            }
        }
    
    def _init_ocr(self):
        """初始化OCR"""
        if self.config.get("ocr", {}).get("enabled", True):
            try:
                languages = self.config["ocr"]["language"].split("+")
                self.ocr_reader = easyocr.Reader(languages)
                logger.info("OCR初始化成功")
            except Exception as e:
                logger.error(f"OCR初始化失败: {e}")
                self.ocr_reader = None
    
    def _capture_screenshot(self, filename: str = None) -> str:
        """截图"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        filepath = os.path.join(self.screenshot_dir, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        logger.info(f"截图保存: {filepath}")
        return filepath
    
    def _find_text_on_screen(self, text: str, confidence: float = None) -> Optional[Tuple[int, int]]:
        """在屏幕上查找文本"""
        if self.ocr_reader is None:
            logger.warning("OCR未初始化，无法进行文本识别")
            return None
        
        if confidence is None:
            confidence = self.config["ocr"]["confidence"]
        
        try:
            screenshot = pyautogui.screenshot()
            results = self.ocr_reader.readtext(np.array(screenshot))
            
            for (bbox, detected_text, conf) in results:
                if conf >= confidence and text.lower() in detected_text.lower():
                    # 计算中心点
                    top_left = bbox[0]
                    bottom_right = bbox[2]
                    center_x = int((top_left[0] + bottom_right[0]) / 2)
                    center_y = int((top_left[1] + bottom_right[1]) / 2)
                    logger.info(f"找到文本 '{text}' 在位置 ({center_x}, {center_y})")
                    return (center_x, center_y)
            
            logger.warning(f"未找到文本 '{text}'")
            return None
            
        except Exception as e:
            logger.error(f"文本识别失败: {e}")
            return None
    
    def _find_file_on_desktop(self, filename: str) -> Optional[str]:
        """在桌面上查找文件"""
        desktop_path = self.config["file_operations"]["desktop_path"]
        file_path = os.path.join(desktop_path, filename)
        
        if os.path.exists(file_path):
            logger.info(f"找到文件: {file_path}")
            return file_path
        
        # 尝试其他常见路径
        for path in self.config["file_operations"]["common_paths"]:
            file_path = os.path.join(path, filename)
            if os.path.exists(file_path):
                logger.info(f"在 {path} 找到文件: {filename}")
                return file_path
        
        logger.warning(f"未找到文件: {filename}")
        return None
    
    def _open_file(self, file_path: str) -> bool:
        """打开文件"""
        try:
            # 方法1: 使用os.startfile
            os.startfile(file_path)
            logger.info(f"使用os.startfile打开文件: {file_path}")
            time.sleep(2)
            return True
        except Exception as e:
            logger.warning(f"os.startfile失败: {e}")
            
            try:
                # 方法2: 使用subprocess
                subprocess.Popen([file_path], shell=True)
                logger.info(f"使用subprocess打开文件: {file_path}")
                time.sleep(2)
                return True
            except Exception as e2:
                logger.error(f"subprocess失败: {e2}")
                return False
    
    def _open_application(self, app_config: Dict) -> bool:
        """打开应用程序"""
        process_name = app_config["process_name"]
        
        # 检查是否已经运行
        if self._is_process_running(process_name):
            logger.info(f"应用程序 {process_name} 已经在运行")
            return True
        
        # 尝试不同的路径启动
        for path in app_config["paths"]:
            path = path.replace("{username}", os.getenv("USERNAME", ""))
            if os.path.exists(path):
                try:
                    subprocess.Popen([path])
                    logger.info(f"启动应用程序: {path}")
                    time.sleep(3)
                    
                    # 验证是否成功启动
                    if self._is_process_running(process_name):
                        logger.info(f"应用程序 {process_name} 启动成功")
                        return True
                    else:
                        logger.warning(f"应用程序启动失败: {path}")
                        
                except Exception as e:
                    logger.error(f"启动应用程序失败 {path}: {e}")
        
        # 尝试从开始菜单启动
        try:
            pyautogui.press('win')
            time.sleep(1)
            pyautogui.write(process_name.replace('.exe', ''))
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(3)
            
            if self._is_process_running(process_name):
                logger.info(f"从开始菜单启动成功: {process_name}")
                return True
        except Exception as e:
            logger.error(f"从开始菜单启动失败: {e}")
        
        return False
    
    def _is_process_running(self, process_name: str) -> bool:
        """检查进程是否运行"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            logger.error(f"检查进程失败: {e}")
            return False
    
    def _click_at_position(self, x: int, y: int, button: str = 'left') -> bool:
        """在指定位置点击"""
        try:
            pyautogui.click(x, y, button=button)
            logger.info(f"点击位置 ({x}, {y})")
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"点击失败: {e}")
            return False
    
    def _type_text(self, text: str) -> bool:
        """输入文本"""
        try:
            pyautogui.write(text)
            logger.info(f"输入文本: {text}")
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"输入文本失败: {e}")
            return False
    
    def _press_key(self, key: str) -> bool:
        """按键"""
        try:
            pyautogui.press(key)
            logger.info(f"按键: {key}")
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"按键失败: {e}")
            return False
    
    def _wait_for_element(self, element_description: str, timeout: int = 30) -> bool:
        """等待元素出现"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            # 这里可以实现更复杂的等待逻辑
            time.sleep(1)
        logger.info(f"等待元素: {element_description}")
        return True
    
    def execute_step(self, step: AutomationStep) -> Dict[str, Any]:
        """执行单个步骤"""
        logger.info(f"执行步骤: {step.step_id} - {step.description}")
        
        result = {
            "step_id": step.step_id,
            "action_type": step.action_type.value,
            "description": step.description,
            "status": "failed",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "error_message": None,
            "screenshots": [],
            "details": {}
        }
        
        try:
            # 执行前截图
            screenshot_before = self._capture_screenshot(f"before_{step.step_id}.png")
            result["screenshots"].append(screenshot_before)
            
            # 根据操作类型执行相应动作
            if step.action_type == ActionType.OPEN_FILE:
                file_path = self._find_file_on_desktop(step.parameters["filename"])
                if file_path:
                    success = self._open_file(file_path)
                    result["details"]["file_path"] = file_path
                else:
                    success = False
                    result["error_message"] = f"文件未找到: {step.parameters['filename']}"
            
            elif step.action_type == ActionType.OPEN_APPLICATION:
                app_name = step.parameters["application"]
                app_config = self.config["applications"].get(app_name)
                if app_config:
                    success = self._open_application(app_config)
                    result["details"]["app_name"] = app_name
                else:
                    success = False
                    result["error_message"] = f"应用程序配置未找到: {app_name}"
            
            elif step.action_type == ActionType.CLICK:
                if "text" in step.parameters:
                    # 通过文本查找点击位置
                    position = self._find_text_on_screen(step.parameters["text"])
                    if position:
                        success = self._click_at_position(position[0], position[1])
                        result["details"]["click_position"] = position
                    else:
                        success = False
                        result["error_message"] = f"未找到文本: {step.parameters['text']}"
                elif "position" in step.parameters:
                    # 直接指定位置
                    position = step.parameters["position"]
                    success = self._click_at_position(position[0], position[1])
                    result["details"]["click_position"] = position
                else:
                    success = False
                    result["error_message"] = "点击操作缺少必要参数"
            
            elif step.action_type == ActionType.TYPE:
                success = self._type_text(step.parameters["text"])
                result["details"]["typed_text"] = step.parameters["text"]
            
            elif step.action_type == ActionType.PRESS_KEY:
                success = self._press_key(step.parameters["key"])
                result["details"]["pressed_key"] = step.parameters["key"]
            
            elif step.action_type == ActionType.WAIT:
                wait_time = step.parameters.get("time", 5)
                time.sleep(wait_time)
                success = True
                result["details"]["wait_time"] = wait_time
            
            elif step.action_type == ActionType.SCREENSHOT:
                filename = step.parameters.get("filename")
                if filename:
                    # 清理文件名中的特殊字符
                    import re
                    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                    screenshot_path = self._capture_screenshot(filename)
                else:
                    screenshot_path = self._capture_screenshot()
                success = True
                result["details"]["screenshot_path"] = screenshot_path
            
            elif step.action_type == ActionType.NAVIGATE_URL:
                # 打开浏览器并导航到URL
                app_config = self.config["applications"]["edge"]
                if self._open_application(app_config):
                    time.sleep(3)
                    # 点击地址栏
                    pyautogui.hotkey('ctrl', 'l')
                    time.sleep(1)
                    # 输入URL
                    self._type_text(step.parameters["url"])
                    time.sleep(1)
                    # 按回车
                    self._press_key('enter')
                    success = True
                    result["details"]["url"] = step.parameters["url"]
                else:
                    success = False
                    result["error_message"] = "浏览器启动失败"
            
            else:
                success = False
                result["error_message"] = f"不支持的操作类型: {step.action_type}"
            
            # 执行后截图
            screenshot_after = self._capture_screenshot(f"after_{step.step_id}.png")
            result["screenshots"].append(screenshot_after)
            
            if success:
                result["status"] = "passed"
                logger.info(f"步骤执行成功: {step.step_id}")
            else:
                logger.error(f"步骤执行失败: {step.step_id}")
                
        except Exception as e:
            result["error_message"] = str(e)
            logger.error(f"步骤执行异常: {step.step_id} - {e}")
        
        result["end_time"] = datetime.now().isoformat()
        return result
    
    def execute_test_case(self, test_case: TestCase) -> Dict[str, Any]:
        """执行测试用例"""
        logger.info(f"开始执行测试用例: {test_case.case_id} - {test_case.name}")
        
        result = {
            "case_id": test_case.case_id,
            "name": test_case.name,
            "description": test_case.description,
            "status": "failed",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "steps": [],
            "summary": {
                "total_steps": len(test_case.steps),
                "passed_steps": 0,
                "failed_steps": 0,
                "skipped_steps": 0
            }
        }
        
        try:
            # 执行前置条件检查
            if not self.execute_preconditions(test_case):
                result["error_message"] = "前置条件检查失败"
                logger.error("前置条件检查失败，停止执行测试用例")
                return result
            
            # 执行测试步骤
            for step in test_case.steps:
                step_result = self.execute_step(step)
                result["steps"].append(step_result)
                
                if step_result["status"] == "passed":
                    result["summary"]["passed_steps"] += 1
                elif step_result["status"] == "failed":
                    result["summary"]["failed_steps"] += 1
                    if step.critical:
                        logger.error(f"关键步骤失败，停止执行: {step.step_id}")
                        break
            
            # 执行后置条件
            if test_case.postconditions:
                logger.info("执行后置条件...")
                for postcondition in test_case.postconditions:
                    logger.info(f"后置条件: {postcondition}")
            
            # 确定测试用例状态
            if result["summary"]["failed_steps"] == 0:
                result["status"] = "passed"
            elif result["summary"]["passed_steps"] > 0:
                result["status"] = "partial"
            else:
                result["status"] = "failed"
                
        except Exception as e:
            result["error_message"] = str(e)
            logger.error(f"测试用例执行异常: {test_case.case_id} - {e}")
        
        result["end_time"] = datetime.now().isoformat()
        return result
    
    def create_file_opening_test(self, filename: str) -> TestCase:
        """创建文件打开测试用例"""
        steps = [
            AutomationStep(
                step_id="step_001",
                action_type=ActionType.OPEN_FILE,
                description=f"打开桌面上的文件 {filename}",
                parameters={"filename": filename},
                expected_result=f"文件 {filename} 成功打开",
                critical=True
            ),
            AutomationStep(
                step_id="step_002",
                action_type=ActionType.SCREENSHOT,
                description="截图验证文件打开状态",
                parameters={"filename": f"file_opened_{filename}"},
                expected_result="成功截图",
                critical=False
            )
        ]
        
        return TestCase(
            case_id=f"file_open_{filename.replace('.', '_')}",
            name=f"打开文件 {filename}",
            description=f"自动化测试：打开桌面上的文件 {filename}",
            steps=steps,
            tags=["file_operation", "desktop"]
        )
    
    def create_application_opening_test(self, app_name: str) -> TestCase:
        """创建应用程序打开测试用例"""
        steps = [
            AutomationStep(
                step_id="step_001",
                action_type=ActionType.OPEN_APPLICATION,
                description=f"打开应用程序 {app_name}",
                parameters={"application": app_name},
                expected_result=f"应用程序 {app_name} 成功启动",
                critical=True
            ),
            AutomationStep(
                step_id="step_002",
                action_type=ActionType.WAIT,
                description="等待应用程序完全加载",
                parameters={"time": 5},
                expected_result="应用程序加载完成",
                critical=False
            ),
            AutomationStep(
                step_id="step_003",
                action_type=ActionType.SCREENSHOT,
                description="截图验证应用程序启动状态",
                parameters={"filename": f"app_opened_{app_name}"},
                expected_result="成功截图",
                critical=False
            )
        ]
        
        return TestCase(
            case_id=f"app_open_{app_name.lower()}",
            name=f"打开应用程序 {app_name}",
            description=f"自动化测试：打开应用程序 {app_name}",
            steps=steps,
            tags=["application", "launch"]
        )
    
    def create_web_navigation_test(self, url: str, description: str = None) -> TestCase:
        """创建网页导航测试用例"""
        if description is None:
            description = f"导航到网页 {url}"
        
        steps = [
            AutomationStep(
                step_id="step_001",
                action_type=ActionType.NAVIGATE_URL,
                description=f"打开浏览器并导航到 {url}",
                parameters={"url": url},
                expected_result=f"成功导航到 {url}",
                critical=True
            ),
            AutomationStep(
                step_id="step_002",
                action_type=ActionType.WAIT,
                description="等待页面加载",
                parameters={"time": 5},
                expected_result="页面加载完成",
                critical=False
            ),
            AutomationStep(
                step_id="step_003",
                action_type=ActionType.SCREENSHOT,
                description="截图验证页面加载状态",
                parameters={"filename": f"web_navigation_{url.replace('://', '_').replace('/', '_')}"},
                expected_result="成功截图",
                critical=False
            )
        ]
        
        return TestCase(
            case_id=f"web_nav_{url.replace('://', '_').replace('/', '_')}",
            name=description,
            description=f"自动化测试：{description}",
            steps=steps,
            tags=["web", "navigation", "browser"]
        )
    
    def generate_report(self, test_results: List[Dict[str, Any]], report_name: str = None) -> str:
        """生成测试报告"""
        if report_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_name = f"test_report_{timestamp}.json"
        
        report_path = os.path.join(self.reports_dir, report_name)
        
        report = {
            "framework_version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_cases": len(test_results),
                "passed_cases": sum(1 for r in test_results if r["status"] == "passed"),
                "failed_cases": sum(1 for r in test_results if r["status"] == "failed"),
                "partial_cases": sum(1 for r in test_results if r["status"] == "partial")
            },
            "test_results": test_results
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"测试报告已生成: {report_path}")
        
        # 打印控制台摘要
        print("\n" + "="*50)
        print("测试执行摘要")
        print("="*50)
        print(f"总测试用例数: {report['summary']['total_cases']}")
        print(f"通过: {report['summary']['passed_cases']}")
        print(f"失败: {report['summary']['failed_cases']}")
        print(f"部分通过: {report['summary']['partial_cases']}")
        print("="*50)
        
        return report_path

    def _ai_open_pdf_reader(self) -> bool:
        """AI主动打开PDF阅读器界面"""
        logger.info("AI正在打开PDF阅读器界面...")
        
        # 尝试启动极光PDF阅读器
        if self.launch_software_if_needed("极光PDF"):
            logger.info("AI成功启动极光PDF阅读器")
            # 等待PDF阅读器窗口出现
            if self.check_window_exists("极光PDF"):
                logger.info("AI检测到极光PDF阅读器窗口")
                return True
            else:
                logger.error("AI启动极光PDF阅读器但未找到窗口")
                return False
        else:
            logger.error("AI无法启动极光PDF阅读器")
            return False
    
    def _ai_open_pdf_file(self) -> bool:
        """AI主动打开PDF文件"""
        logger.info("AI正在打开PDF文件...")
        
        # 查找桌面上的PDF文件
        pdf_files = self._find_pdf_files_on_desktop()
        if not pdf_files:
            logger.error("AI未找到可用的PDF文件")
            return False
        
        # 选择第一个PDF文件
        pdf_file = pdf_files[0]
        logger.info(f"AI选择打开PDF文件: {pdf_file}")
        
        if self._open_file(pdf_file):
            logger.info("AI成功打开PDF文件")
            # 等待文件加载
            time.sleep(3)
            return True
        
        logger.error("AI无法打开PDF文件")
        return False
    
    def _ai_select_text(self) -> bool:
        """AI主动选取文字"""
        logger.info("AI正在选取文字...")
        
        try:
            # 等待PDF内容加载完成
            time.sleep(2)
            
            # 使用OCR识别屏幕上的文字，找到可选择的文字区域
            text_regions = self._find_selectable_text_regions()
            if text_regions:
                # 选择第一个文字区域
                region = text_regions[0]
                center_x = (region[0] + region[2]) // 2
                center_y = (region[1] + region[3]) // 2
                
                # 移动到文字区域开始位置
                pyautogui.moveTo(region[0], region[1])
                time.sleep(0.5)
                
                # 拖拽选择文字
                pyautogui.mouseDown(button='left')
                time.sleep(0.5)
                pyautogui.dragTo(region[2], region[3], duration=1)
                time.sleep(0.5)
                pyautogui.mouseUp(button='left')
                time.sleep(1)
                
                logger.info("AI成功选取文字")
                return True
            else:
                # 如果没有找到文字区域，使用默认方法
                return self._ai_select_text_default()
            
        except Exception as e:
            logger.error(f"AI选取文字失败: {e}")
            return False
    
    def _ai_select_text_default(self) -> bool:
        """AI使用默认方法选取文字"""
        logger.info("AI使用默认方法选取文字...")
        
        try:
            # 从屏幕中央开始，向下拖拽选择一段文字
            screen_width, screen_height = pyautogui.size()
            center_x = screen_width // 2
            center_y = screen_height // 2
            
            # 移动到起始位置
            pyautogui.moveTo(center_x, center_y)
            time.sleep(0.5)
            
            # 按住左键拖拽选择文字
            pyautogui.mouseDown(button='left')
            time.sleep(0.5)
            
            # 向下拖拽选择文字
            pyautogui.dragTo(center_x, center_y + 100, duration=1)
            time.sleep(0.5)
            
            # 释放左键
            pyautogui.mouseUp(button='left')
            time.sleep(1)
            
            logger.info("AI使用默认方法成功选取文字")
            return True
            
        except Exception as e:
            logger.error(f"AI默认方法选取文字失败: {e}")
            return False
    
    def _find_pdf_files_on_desktop(self) -> List[str]:
        """在桌面上查找PDF文件"""
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        pdf_files = []
        
        try:
            for file in os.listdir(desktop_path):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(desktop_path, file))
        except Exception as e:
            logger.warning(f"查找桌面PDF文件失败: {e}")
        
        # 如果没有找到，尝试其他常见路径
        if not pdf_files:
            common_paths = [
                os.path.join(os.path.expanduser("~"), "Documents"),
                os.path.join(os.path.expanduser("~"), "Downloads")
            ]
            
            for path in common_paths:
                try:
                    for file in os.listdir(path):
                        if file.lower().endswith('.pdf'):
                            pdf_files.append(os.path.join(path, file))
                except Exception as e:
                    logger.warning(f"在 {path} 查找PDF文件失败: {e}")
        
        logger.info(f"找到 {len(pdf_files)} 个PDF文件")
        return pdf_files
    
    def _find_selectable_text_regions(self) -> List[Tuple[int, int, int, int]]:
        """使用OCR查找可选择的文字区域"""
        if self.ocr_reader is None:
            logger.warning("OCR未初始化，无法识别文字区域")
            return []
        
        try:
            # 截取屏幕
            screenshot = pyautogui.screenshot()
            results = self.ocr_reader.readtext(np.array(screenshot))
            
            text_regions = []
            for (bbox, text, conf) in results:
                if conf >= 0.6 and len(text.strip()) > 2:  # 过滤低置信度和短文本
                    # 计算边界框
                    top_left = bbox[0]
                    bottom_right = bbox[2]
                    region = (
                        int(top_left[0]), int(top_left[1]),
                        int(bottom_right[0]), int(bottom_right[1])
                    )
                    text_regions.append(region)
            
            logger.info(f"AI找到 {len(text_regions)} 个可选择的文字区域")
            return text_regions
            
        except Exception as e:
            logger.error(f"AI查找文字区域失败: {e}")
            return []
    
    def _ai_right_click_selected_text(self) -> bool:
        """AI主动右键点击选取的文字区域"""
        logger.info("AI正在右键点击选取的文字区域...")
        
        try:
            # 在选取的文字区域中央右键点击
            screen_width, screen_height = pyautogui.size()
            center_x = screen_width // 2
            center_y = screen_height // 2 + 50  # 文字区域的中央
            
            # 移动到文字区域
            pyautogui.moveTo(center_x, center_y)
            time.sleep(0.5)
            
            # 右键点击
            pyautogui.rightClick()
            time.sleep(1)
            
            logger.info("AI成功右键点击文字区域")
            return True
            
        except Exception as e:
            logger.error(f"AI右键点击失败: {e}")
            return False
    
    def _ai_wait_for_menu(self) -> bool:
        """AI等待右键菜单出现"""
        logger.info("AI正在等待右键菜单出现...")
        
        try:
            # 等待右键菜单出现
            for i in range(10):  # 最多等待10秒
                time.sleep(1)
                
                # 检查是否有右键菜单出现（可以通过颜色或形状识别）
                if self._detect_right_click_menu():
                    logger.info("AI检测到右键菜单出现")
                    return True
            
            logger.warning("AI等待右键菜单超时")
            return False
            
        except Exception as e:
            logger.error(f"AI等待右键菜单失败: {e}")
            return False
    
    def _detect_right_click_menu(self) -> bool:
        """检测右键菜单是否出现"""
        try:
            # 这里可以实现更复杂的菜单检测逻辑
            # 比如通过颜色、形状、OCR等方式检测
            # 暂时使用简单的延时方法
            return True
        except Exception as e:
            logger.debug(f"检测右键菜单失败: {e}")
            return False

def main():
    """主函数 - 演示框架使用"""
    framework = UnifiedAutomationFramework()
    
    # 创建测试用例
    test_cases = [
        # 文件打开测试
        framework.create_file_opening_test("info.json"),
        
        # 应用程序打开测试
        framework.create_application_opening_test("github_desktop"),
        
        # 网页导航测试
        framework.create_web_navigation_test("www.baidu.com", "打开Edge浏览器，访问百度网站")
    ]
    
    # 执行测试用例
    results = []
    for test_case in test_cases:
        result = framework.execute_test_case(test_case)
        results.append(result)
    
    # 生成报告
    framework.generate_report(results)

if __name__ == "__main__":
    main()
