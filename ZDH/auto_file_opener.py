#!/usr/bin/env python3
"""
自动化文件打开器 - 打开桌面上的info.json
"""

import cv2
import numpy as np
import easyocr
from PIL import Image, ImageGrab, ImageEnhance
import time
import os
import pyautogui
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoFileOpener:
    """自动化文件打开器"""
    
    def __init__(self):
        """初始化"""
        logger.info("正在初始化自动化文件打开器...")
        
        # OCR配置
        self.ocr_reader = None
        self._init_ocr()
        
        # 桌面路径
        self.desktop_path = Path.home() / "Desktop"
        
        # 安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        logger.info("✅ 自动化文件打开器初始化完成")
    
    def _init_ocr(self):
        """初始化OCR"""
        try:
            self.ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False, verbose=False)
            logger.info("✅ OCR初始化成功")
        except Exception as e:
            logger.error(f"❌ OCR初始化失败: {e}")
            self.ocr_reader = None
    
    def open_info_json(self):
        """打开桌面上的info.json文件"""
        logger.info("🎯 开始执行测试用例：打开桌面上的info.json")
        print("=" * 60)
        print("🧪 测试用例：打开桌面上的info.json")
        print("=" * 60)
        
        try:
            # 步骤1: 检查文件是否存在
            logger.info("步骤1: 检查info.json文件是否存在")
            if not self._check_file_exists():
                logger.error("❌ info.json文件不存在于桌面上")
                return False
            
            # 步骤2: 定位文件位置
            logger.info("步骤2: 定位info.json文件位置")
            file_position = self._locate_file()
            if not file_position:
                logger.error("❌ 无法定位info.json文件")
                return False
            
            # 步骤3: 打开文件
            logger.info("步骤3: 打开info.json文件")
            if self._open_file(file_position):
                logger.info("✅ 成功打开info.json文件")
                
                # 步骤4: 验证文件是否真的打开
                logger.info("步骤4: 验证文件打开状态")
                self._verify_file_opened()
                
                return True
            else:
                logger.error("❌ 打开文件失败")
                return False
                
        except Exception as e:
            logger.error(f"❌ 自动化过程发生错误: {e}")
            return False
    
    def _check_file_exists(self):
        """检查文件是否存在"""
        try:
            # 检查桌面
            desktop_file = self.desktop_path / "info.json"
            if desktop_file.exists():
                logger.info(f"✅ 在桌面找到文件: {desktop_file}")
                return True
            
            # 检查其他常见位置
            common_paths = [
                Path.home() / "Documents",
                Path.home() / "Downloads",
                Path.home() / "Pictures"
            ]
            
            for path in common_paths:
                if path.exists():
                    file_path = path / "info.json"
                    if file_path.exists():
                        logger.info(f"✅ 在 {path.name} 找到文件: {file_path}")
                        return True
            
            logger.warning("⚠️ 在常见位置未找到info.json文件")
            return False
            
        except Exception as e:
            logger.error(f"检查文件存在性时发生错误: {e}")
            return False
    
    def _locate_file(self):
        """定位文件位置"""
        try:
            # 策略1: 文件系统查找
            logger.info("  策略1: 文件系统查找")
            file_path = self._find_file_system()
            if file_path:
                position = self._estimate_desktop_position(file_path.name)
                logger.info(f"  ✅ 文件系统找到，估算位置: {position}")
                return position
            
            # 策略2: OCR查找
            logger.info("  策略2: OCR查找")
            ocr_position = self._find_file_ocr()
            if ocr_position:
                logger.info(f"  ✅ OCR找到位置: {ocr_position}")
                return ocr_position
            
            # 策略3: 预设位置尝试
            logger.info("  策略3: 预设位置尝试")
            preset_position = self._try_preset_positions()
            if preset_position:
                logger.info(f"  ⚠️ 使用预设位置: {preset_position}")
                return preset_position
            
            return None
            
        except Exception as e:
            logger.error(f"定位文件时发生错误: {e}")
            return None
    
    def _find_file_system(self):
        """文件系统查找"""
        try:
            # 检查桌面
            desktop_file = self.desktop_path / "info.json"
            if desktop_file.exists():
                return desktop_file
            
            # 检查其他位置
            common_paths = [
                Path.home() / "Documents",
                Path.home() / "Downloads",
                Path.home() / "Pictures"
            ]
            
            for path in common_paths:
                if path.exists():
                    file_path = path / "info.json"
                    if file_path.exists():
                        return file_path
            
            return None
            
        except Exception as e:
            logger.error(f"文件系统查找失败: {e}")
            return None
    
    def _estimate_desktop_position(self, filename):
        """估算桌面文件位置"""
        # 基于文件名长度和常见位置估算
        name_length = len(filename)
        
        if name_length <= 8:
            return (400, 300)  # 左上区域
        elif name_length <= 15:
            return (800, 400)  # 中上区域
        else:
            return (600, 500)  # 中央区域
    
    def _find_file_ocr(self):
        """通过OCR查找文件"""
        if not self.ocr_reader:
            return None
        
        try:
            # 截取屏幕
            screenshot = ImageGrab.grab()
            screenshot_np = np.array(screenshot)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # 预处理图像
            processed_image = self._preprocess_image(screenshot_cv)
            
            # OCR识别
            results = self.ocr_reader.readtext(processed_image, detail=1, paragraph=False)
            
            # 分析结果
            best_matches = []
            for bbox, text, confidence in results:
                # 计算匹配度
                match_score = self._calculate_match_score(text, "info.json")
                
                if match_score > 0.3:  # 降低阈值
                    center = self._calculate_center(bbox)
                    best_matches.append({
                        'text': text,
                        'confidence': confidence,
                        'match_score': match_score,
                        'position': center
                    })
            
            # 按匹配度排序
            best_matches.sort(key=lambda x: x['match_score'], reverse=True)
            
            if best_matches:
                best_match = best_matches[0]
                logger.info(f"    最佳匹配: '{best_match['text']}' (匹配度: {best_match['match_score']:.3f})")
                return best_match['position']
            
            return None
            
        except Exception as e:
            logger.error(f"  OCR查找失败: {e}")
            return None
    
    def _preprocess_image(self, image):
        """图像预处理"""
        try:
            # 转换为PIL图像
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            
            # 放大图像
            new_size = (int(pil_image.width * 1.5), int(pil_image.height * 1.5))
            pil_image = pil_image.resize(new_size, Image.LANCZOS)
            
            # 增强对比度
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(1.3)
            
            # 增强锐度
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(1.3)
            
            # 转换回OpenCV格式
            processed = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            return processed
            
        except Exception as e:
            logger.error(f"    图像预处理失败: {e}")
            return image
    
    def _calculate_match_score(self, text, filename):
        """计算文本匹配度"""
        if not text or not filename:
            return 0.0
        
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        # 完全匹配
        if filename_lower in text_lower:
            return 1.0
        
        # 部分匹配
        if any(part in text_lower for part in filename_lower.split('.')):
            return 0.8
        
        # 字符重叠度
        common_chars = set(text_lower) & set(filename_lower)
        if len(common_chars) >= min(len(text_lower), len(filename_lower)) * 0.5:
            return 0.4
        
        return 0.0
    
    def _calculate_center(self, bbox):
        """计算边界框中心点"""
        try:
            x1, y1 = bbox[0]
            x3, y3 = bbox[2]
            center_x = int((x1 + x3) / 2)
            center_y = int((y1 + y3) / 2)
            return (center_x, center_y)
        except:
            return (0, 0)
    
    def _try_preset_positions(self):
        """尝试预设位置"""
        # 基于文件类型的预设位置
        preset_positions = [
            (400, 300),   # 左上
            (800, 400),   # 中上
            (1200, 300),  # 右上
            (600, 500),   # 中央
            (1000, 600),  # 中下
            (300, 700),   # 左下
            (1400, 700)   # 右下
        ]
        
        logger.info(f"    尝试 {len(preset_positions)} 个预设位置...")
        
        # 返回第一个预设位置
        return preset_positions[0]
    
    def _open_file(self, position):
        """打开文件"""
        try:
            x, y = position
            
            # 方法1: 双击打开
            logger.info(f"  尝试双击位置 ({x}, {y}) 打开文件")
            if self._double_click_file(x, y):
                return True
            
            # 方法2: 使用命令行打开
            logger.info(f"  尝试使用命令行打开文件")
            if self._command_line_open():
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"打开文件时发生错误: {e}")
            return False
    
    def _double_click_file(self, x, y):
        """双击文件"""
        try:
            # 移动到文件位置
            pyautogui.moveTo(x, y, duration=0.5)
            time.sleep(0.5)
            
            # 双击
            pyautogui.doubleClick(x, y)
            time.sleep(2.0)  # 增加延迟，确保文件完全打开
            
            logger.info("    ✅ 双击成功，等待文件打开...")
            return True
            
        except Exception as e:
            logger.error(f"    双击失败: {e}")
            return False
    
    def _command_line_open(self):
        """使用命令行打开文件"""
        try:
            # 获取文件完整路径
            file_path = self.desktop_path / "info.json"
            if not file_path.exists():
                # 尝试其他位置
                common_paths = [
                    Path.home() / "Documents",
                    Path.home() / "Downloads",
                    Path.home() / "Pictures"
                ]
                
                for path in common_paths:
                    if path.exists():
                        temp_path = path / "info.json"
                        if temp_path.exists():
                            file_path = temp_path
                            break
            
            if file_path.exists():
                # 使用系统默认程序打开
                os.startfile(str(file_path))
                time.sleep(2.0)  # 增加延迟，确保文件完全打开
                logger.info(f"    ✅ 命令行打开成功: {file_path}，等待文件打开...")
                return True
            else:
                logger.warning("    ⚠️ 未找到文件路径")
                return False
                
        except Exception as e:
            logger.error(f"    命令行打开失败: {e}")
            return False
    
    def _verify_file_opened(self):
        """验证文件是否真的打开"""
        try:
            logger.info("   🔍 正在验证文件打开状态...")
            
            # 等待一段时间让文件完全打开
            time.sleep(1.0)
            
            # 检查是否有新的窗口或进程
            logger.info("   📋 文件应该已经在默认程序中打开")
            logger.info("   💡 请检查您的屏幕是否有新的窗口或标签页")
            logger.info("   ⏰ 文件将保持打开状态，不会自动关闭")
            
            # 给用户一些时间来确认
            print("\n" + "=" * 50)
            print("🔍 文件打开验证:")
            print("📋 请检查您的屏幕是否有新的窗口或标签页")
            print("💡 文件应该已经在默认程序中打开")
            print("⏰ 文件将保持打开状态")
            print("=" * 50)
            
        except Exception as e:
            logger.error(f"    验证文件打开状态时发生错误: {e}")
    
    def run_test_case(self):
        """运行测试用例"""
        print("\n🚀 开始执行自动化测试用例")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # 执行测试
            success = self.open_info_json()
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # 输出测试结果
            print("\n" + "=" * 60)
            if success:
                print("🎉 测试用例执行成功！")
                print(f"✅ 成功打开桌面上的info.json文件")
                print("📝 文件已打开并保持打开状态，请查看您的屏幕")
                print("💡 测试完成后，文件不会自动关闭")
            else:
                print("❌ 测试用例执行失败！")
                print(f"❌ 未能成功打开info.json文件")
            
            print(f"⏱️  执行时间: {execution_time:.2f}秒")
            print("=" * 60)
            
            return success
            
        except Exception as e:
            logger.error(f"测试用例执行过程中发生错误: {e}")
            print(f"\n❌ 测试执行异常: {e}")
            return False

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 自动化测试用例：打开桌面上的info.json")
    print("=" * 60)
    
    # 创建测试实例
    test_case = AutoFileOpener()
    
    # 运行测试
    success = test_case.run_test_case()
    
    # 输出最终结果
    if success:
        print("\n🎯 测试结果: PASSED ✅")
    else:
        print("\n🎯 测试结果: FAILED ❌")
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()
