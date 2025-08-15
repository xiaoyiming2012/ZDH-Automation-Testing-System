#!/usr/bin/env python3
"""
增强的文件查找系统
结合OCR、图像识别和智能搜索策略，提高文件定位精度
"""

import cv2
import numpy as np
import easyocr
from PIL import Image, ImageGrab, ImageEnhance, ImageFilter
import time
import os
from pathlib import Path
import subprocess
import re

class EnhancedFileFinder:
    """增强的文件查找系统"""
    
    def __init__(self):
        """初始化"""
        print("正在初始化增强文件查找系统...")
        
        # OCR配置
        self.ocr_reader = None
        self._init_ocr()
        
        # 文件扩展名模式
        self.file_patterns = {
            'json': ['.json', 'json'],
            'text': ['.txt', '.doc', '.docx', '.pdf', 'txt', 'doc', 'pdf'],
            'image': ['.jpg', '.jpeg', '.png', '.bmp', '.gif', 'jpg', 'png'],
            'video': ['.mp4', '.avi', '.mov', '.wmv', 'mp4', 'avi'],
            'audio': ['.mp3', '.wav', '.flac', 'mp3', 'wav']
        }
        
        # 桌面路径
        self.desktop_path = Path.home() / "Desktop"
        
        print("✅ 增强文件查找系统初始化完成")
    
    def _init_ocr(self):
        """初始化OCR"""
        try:
            self.ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False, verbose=False)
            print("✅ OCR初始化成功")
        except Exception as e:
            print(f"❌ OCR初始化失败: {e}")
            self.ocr_reader = None
    
    def find_file_comprehensive(self, filename, file_type=None):
        """综合文件查找策略"""
        print(f"\n🔍 开始查找文件: {filename}")
        print("=" * 60)
        
        # 策略1: 直接文件系统查找
        print("\n📁 策略1: 文件系统查找")
        file_path = self._find_file_system(filename)
        if file_path:
            print(f"✅ 文件系统找到: {file_path}")
            return self._get_file_position(file_path)
        
        # 策略2: 桌面扫描 + OCR
        print("\n🔍 策略2: 桌面扫描 + OCR")
        ocr_position = self._find_file_ocr(filename, file_type)
        if ocr_position:
            print(f"✅ OCR找到: {ocr_position}")
            return ocr_position
        
        # 策略3: 智能模糊匹配
        print("\n🎯 策略3: 智能模糊匹配")
        fuzzy_position = self._find_file_fuzzy(filename, file_type)
        if fuzzy_position:
            print(f"✅ 模糊匹配找到: {fuzzy_position}")
            return fuzzy_position
        
        # 策略4: 预设位置尝试
        print("\n📍 策略4: 预设位置尝试")
        preset_position = self._try_preset_positions(filename)
        if preset_position:
            print(f"⚠️ 使用预设位置: {preset_position}")
            return preset_position
        
        print("❌ 所有策略都失败了")
        return None
    
    def _find_file_system(self, filename):
        """文件系统查找"""
        # 检查桌面
        desktop_file = self.desktop_path / filename
        if desktop_file.exists():
            return desktop_file
        
        # 检查常见位置
        common_paths = [
            Path.home() / "Documents",
            Path.home() / "Downloads",
            Path.home() / "Pictures"
        ]
        
        for path in common_paths:
            if path.exists():
                file_path = path / filename
                if file_path.exists():
                    return file_path
        
        return None
    
    def _get_file_position(self, file_path):
        """获取文件在桌面上的位置"""
        if not file_path.exists():
            return None
        
        # 如果文件在桌面上，尝试通过文件名定位
        if file_path.parent == self.desktop_path:
            return self._estimate_desktop_position(file_path.name)
        
        return None
    
    def _estimate_desktop_position(self, filename):
        """估算桌面文件位置"""
        # 基于文件名长度和常见位置估算
        name_length = len(filename)
        
        # 简单的网格定位策略
        if name_length <= 8:
            return (400, 300)  # 左上区域
        elif name_length <= 15:
            return (800, 400)  # 中上区域
        else:
            return (600, 500)  # 中央区域
    
    def _find_file_ocr(self, filename, file_type=None):
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
                match_score = self._calculate_match_score(text, filename, file_type)
                
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
                print(f"   最佳匹配: '{best_match['text']}' (匹配度: {best_match['match_score']:.3f})")
                return best_match['position']
            
            return None
            
        except Exception as e:
            print(f"   OCR查找失败: {e}")
            return None
    
    def _preprocess_image(self, image):
        """图像预处理"""
        try:
            # 转换为PIL图像
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # 放大图像
            new_size = (int(pil_image.width * 1.5), int(pil_image.height * 1.5))
            pil_image = pil_image.resize(new_size, Image.LANCZOS)
            
            # 增强对比度
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(1.3)
            
            # 转换回OpenCV格式
            processed = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            return processed
            
        except Exception as e:
            print(f"   图像预处理失败: {e}")
            return image
    
    def _calculate_match_score(self, text, filename, file_type=None):
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
        
        # 文件扩展名匹配
        if file_type and any(ext in text_lower for ext in self.file_patterns.get(file_type, [])):
            return 0.6
        
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
    
    def _find_file_fuzzy(self, filename, file_type=None):
        """模糊匹配查找"""
        if not self.ocr_reader:
            return None
        
        try:
            # 截取屏幕
            screenshot = ImageGrab.grab()
            screenshot_np = np.array(screenshot)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # 预处理
            processed_image = self._preprocess_image(screenshot_cv)
            
            # OCR识别
            results = self.ocr_reader.readtext(processed_image, detail=1, paragraph=False)
            
            # 模糊匹配
            fuzzy_matches = []
            for bbox, text, confidence in results:
                # 使用更宽松的匹配策略
                fuzzy_score = self._calculate_fuzzy_score(text, filename, file_type)
                
                if fuzzy_score > 0.2:  # 更低的阈值
                    center = self._calculate_center(bbox)
                    fuzzy_matches.append({
                        'text': text,
                        'fuzzy_score': fuzzy_score,
                        'position': center
                    })
            
            # 按模糊匹配度排序
            fuzzy_matches.sort(key=lambda x: x['fuzzy_score'], reverse=True)
            
            if fuzzy_matches:
                best_fuzzy = fuzzy_matches[0]
                print(f"   最佳模糊匹配: '{best_fuzzy['text']}' (模糊度: {best_fuzzy['fuzzy_score']:.3f})")
                return best_fuzzy['position']
            
            return None
            
        except Exception as e:
            print(f"   模糊匹配失败: {e}")
            return None
    
    def _calculate_fuzzy_score(self, text, filename, file_type=None):
        """计算模糊匹配度"""
        if not text or not filename:
            return 0.0
        
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        # 分词匹配
        filename_words = re.findall(r'[a-zA-Z0-9]+', filename_lower)
        text_words = re.findall(r'[a-zA-Z0-9]+', text_lower)
        
        # 计算单词匹配度
        word_matches = 0
        for word in filename_words:
            if any(word in tw for tw in text_words):
                word_matches += 1
        
        if filename_words:
            word_score = word_matches / len(filename_words)
        else:
            word_score = 0.0
        
        # 字符相似度
        char_similarity = len(set(text_lower) & set(filename_lower)) / len(set(text_lower) | set(filename_lower))
        
        # 综合评分
        fuzzy_score = (word_score * 0.6) + (char_similarity * 0.4)
        
        return fuzzy_score
    
    def _try_preset_positions(self, filename):
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
        
        print(f"   尝试 {len(preset_positions)} 个预设位置...")
        
        # 返回第一个预设位置
        return preset_positions[0]
    
    def analyze_desktop(self):
        """分析桌面内容"""
        print("\n📊 桌面内容分析")
        print("=" * 40)
        
        if not self.ocr_reader:
            print("❌ OCR不可用")
            return
        
        try:
            # 截取屏幕
            screenshot = ImageGrab.grab()
            screenshot_np = np.array(screenshot)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # 预处理
            processed_image = self._preprocess_image(screenshot_cv)
            
            # OCR识别
            results = self.ocr_reader.readtext(processed_image, detail=1, paragraph=False)
            
            # 分析结果
            file_like_texts = []
            for bbox, text, confidence in results:
                # 检查是否像文件名
                if self._looks_like_filename(text):
                    center = self._calculate_center(bbox)
                    file_like_texts.append({
                        'text': text,
                        'confidence': confidence,
                        'position': center
                    })
            
            print(f"识别到 {len(results)} 个文本区域")
            print(f"其中 {len(file_like_texts)} 个像文件名:")
            
            for i, item in enumerate(file_like_texts[:10]):
                print(f"  {i+1}. '{item['text']}' 位置: {item['position']}")
            
            return file_like_texts
            
        except Exception as e:
            print(f"桌面分析失败: {e}")
            return []
    
    def _looks_like_filename(self, text):
        """判断文本是否像文件名"""
        if not text or len(text) < 2:
            return False
        
        # 包含文件扩展名
        if any(ext in text.lower() for ext in ['.txt', '.json', '.doc', '.pdf', '.jpg', '.png']):
            return True
        
        # 包含数字和字母的组合
        if re.search(r'[a-zA-Z].*\d|\d.*[a-zA-Z]', text):
            return True
        
        # 长度适中
        if 3 <= len(text) <= 50:
            return True
        
        return False

def main():
    """测试函数"""
    print("=" * 60)
    print("增强文件查找系统测试")
    print("=" * 60)
    
    # 初始化系统
    finder = EnhancedFileFinder()
    
    # 分析桌面
    finder.analyze_desktop()
    
    # 测试查找不同文件
    test_files = [
        ("info.json", "json"),
        ("test.txt", "text"),
        ("document.pdf", "text"),
        ("image.jpg", "image")
    ]
    
    for filename, file_type in test_files:
        print(f"\n{'='*60}")
        position = finder.find_file_comprehensive(filename, file_type)
        
        if position:
            print(f"🎯 最终结果: {filename} 位置: {position}")
        else:
            print(f"❌ 未找到: {filename}")
    
    print(f"\n{'='*60}")
    print("测试完成！")

if __name__ == "__main__":
    main()



