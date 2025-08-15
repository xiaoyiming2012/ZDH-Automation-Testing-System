#!/usr/bin/env python3
"""
优化的OCR系统
基于测试结果选择最佳的预处理方法和参数配置
"""

import cv2
import numpy as np
import easyocr
from PIL import Image, ImageGrab, ImageEnhance, ImageFilter
import time
from pathlib import Path

class OptimizedOCRSystem:
    """优化的OCR系统"""
    
    def __init__(self):
        """初始化"""
        print("正在初始化优化的OCR系统...")
        
        # OCR配置
        self.ocr_reader = None
        self._init_ocr()
        
        # 基于测试结果的最佳配置
        self.optimized_config = {
            'preprocessing_method': 'enhance_sharpness',  # 最佳方法
            'confidence_threshold': 0.6,  # 降低阈值提高召回率
            'resize_factor': 1.5,  # 适中的放大倍数
            'enhance_contrast': 1.3,  # 适中的对比度增强
            'enhance_sharpness': 1.3,  # 适中的锐度增强
            'denoise_enabled': True,  # 启用降噪
            'morphology_enabled': True  # 启用形态学处理
        }
        
        print("✅ 优化的OCR系统初始化完成")
    
    def _init_ocr(self):
        """初始化OCR"""
        try:
            self.ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False, verbose=False)
            print("✅ OCR初始化成功")
        except Exception as e:
            print(f"❌ OCR初始化失败: {e}")
            self.ocr_reader = None
    
    def preprocess_image_optimized(self, image):
        """优化的图像预处理"""
        try:
            # 转换为PIL图像
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # 1. 适度放大
            new_size = (int(pil_image.width * self.optimized_config['resize_factor']),
                       int(pil_image.height * self.optimized_config['resize_factor']))
            pil_image = pil_image.resize(new_size, Image.LANCZOS)
            
            # 2. 增强对比度
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(self.optimized_config['enhance_contrast'])
            
            # 3. 增强锐度（最佳方法）
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(self.optimized_config['enhance_sharpness'])
            
            # 4. 降噪处理
            if self.optimized_config['denoise_enabled']:
                pil_image = pil_image.filter(ImageFilter.MedianFilter(size=3))
            
            # 5. 形态学处理
            if self.optimized_config['morphology_enabled']:
                gray_array = np.array(pil_image.convert('L'))
                kernel = np.ones((2, 2), np.uint8)
                gray_array = cv2.morphologyEx(gray_array, cv2.MORPH_CLOSE, kernel)
                pil_image = Image.fromarray(gray_array)
            
            # 转换回OpenCV格式
            processed_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            return processed_image
            
        except Exception as e:
            print(f"图像预处理失败: {e}")
            return image
    
    def recognize_text_optimized(self, image, target_text=None):
        """优化的文本识别"""
        if not self.ocr_reader:
            return []
        
        try:
            # 优化的预处理
            processed_image = self.preprocess_image_optimized(image)
            
            # OCR识别
            results = self.ocr_reader.readtext(
                processed_image,
                detail=1,
                paragraph=False
            )
            
            # 结果后处理
            enhanced_results = []
            for bbox, text, confidence in results:
                # 清理文本
                cleaned_text = self._clean_text(text)
                
                # 提升置信度
                boosted_confidence = self._boost_confidence(confidence, cleaned_text, target_text)
                
                # 计算中心点
                center = self._calculate_center(bbox)
                
                enhanced_results.append({
                    'bbox': bbox,
                    'original_text': text,
                    'cleaned_text': cleaned_text,
                    'confidence': confidence,
                    'boosted_confidence': boosted_confidence,
                    'center': center,
                    'area': self._calculate_area(bbox)
                })
            
            # 按提升后的置信度排序
            enhanced_results.sort(key=lambda x: x['boosted_confidence'], reverse=True)
            
            return enhanced_results
            
        except Exception as e:
            print(f"OCR识别失败: {e}")
            return []
    
    def _clean_text(self, text):
        """清理文本"""
        if not text:
            return ""
        
        # 去除噪声字符
        noise_chars = ['|', '\\', '/', '-', '_', '=', '+', '*', '&', '^', '%', '$', '#', '@', '!']
        cleaned = text
        for char in noise_chars:
            cleaned = cleaned.replace(char, '')
        
        # 去除多余空格
        cleaned = ' '.join(cleaned.split())
        return cleaned.strip()
    
    def _boost_confidence(self, confidence, text, target_text=None):
        """提升置信度"""
        boosted = confidence
        
        # 基于文本长度提升
        if len(text) >= 3:
            boosted += 0.1
        
        # 基于文件扩展名提升
        if any(ext in text.lower() for ext in ['.txt', '.json', '.doc', '.pdf']):
            boosted += 0.15
        
        # 基于文本质量提升
        if text.isalnum():
            boosted += 0.1
        
        # 基于目标匹配提升
        if target_text and target_text.lower() in text.lower():
            boosted += 0.2
        
        return min(boosted, 1.0)
    
    def _calculate_center(self, bbox):
        """计算中心点"""
        try:
            x1, y1 = bbox[0]
            x3, y3 = bbox[2]
            center_x = int((x1 + x3) / 2)
            center_y = int((y1 + y3) / 2)
            return (center_x, center_y)
        except:
            return (0, 0)
    
    def _calculate_area(self, bbox):
        """计算面积"""
        try:
            x1, y1 = bbox[0]
            x3, y3 = bbox[2]
            width = abs(x3 - x1)
            height = abs(y3 - y1)
            return width * height
        except:
            return 0
    
    def find_text_optimized(self, image, target_text, min_confidence=0.5):
        """优化的文本查找"""
        results = self.recognize_text_optimized(image, target_text)
        
        for result in results:
            if (result['boosted_confidence'] >= min_confidence and 
                target_text.lower() in result['cleaned_text'].lower()):
                
                print(f"✅ 找到目标文本: {target_text}")
                print(f"   原始文本: {result['original_text']}")
                print(f"   清理文本: {result['cleaned_text']}")
                print(f"   置信度: {result['confidence']:.3f} -> {result['boosted_confidence']:.3f}")
                print(f"   位置: {result['center']}")
                print(f"   面积: {result['area']}")
                
                return result['center']
        
        print(f"❌ 未找到目标文本: {target_text}")
        return None
    
    def get_detailed_analysis(self, image):
        """获取详细的文本分析"""
        results = self.recognize_text_optimized(image)
        
        # 分析结果
        analysis = {
            'total_texts': len(results),
            'file_like_texts': [],
            'high_confidence_texts': [],
            'text_statistics': {}
        }
        
        for result in results:
            # 文件样本文本
            if self._looks_like_filename(result['cleaned_text']):
                analysis['file_like_texts'].append(result)
            
            # 高置信度文本
            if result['boosted_confidence'] > 0.8:
                analysis['high_confidence_texts'].append(result)
            
            # 文本长度统计
            text_length = len(result['cleaned_text'])
            if text_length not in analysis['text_statistics']:
                analysis['text_statistics'][text_length] = 0
            analysis['text_statistics'][text_length] += 1
        
        return analysis
    
    def _looks_like_filename(self, text):
        """判断是否像文件名"""
        if not text or len(text) < 2:
            return False
        
        # 包含文件扩展名
        if any(ext in text.lower() for ext in ['.txt', '.json', '.doc', '.pdf', '.jpg', '.png']):
            return True
        
        # 包含数字和字母的组合
        import re
        if re.search(r'[a-zA-Z].*\d|\d.*[a-zA-Z]', text):
            return True
        
        # 长度适中
        if 3 <= len(text) <= 50:
            return True
        
        return False

def main():
    """测试函数"""
    print("=" * 60)
    print("优化的OCR系统测试")
    print("=" * 60)
    
    # 初始化系统
    ocr = OptimizedOCRSystem()
    
    # 截取屏幕
    print("\n📸 截取屏幕...")
    screenshot = ImageGrab.grab()
    screenshot_np = np.array(screenshot)
    screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    print("✅ 屏幕截图完成")
    
    # 获取详细分析
    print("\n🔍 获取详细文本分析...")
    analysis = ocr.get_detailed_analysis(screenshot_cv)
    
    print(f"\n📊 分析结果:")
    print(f"  总文本数: {analysis['total_texts']}")
    print(f"  文件样本文本数: {len(analysis['file_like_texts'])}")
    print(f"  高置信度文本数: {len(analysis['high_confidence_texts'])}")
    
    # 显示文件样本文本
    if analysis['file_like_texts']:
        print(f"\n📁 文件样本文本 (前10个):")
        for i, item in enumerate(analysis['file_like_texts'][:10]):
            print(f"  {i+1}. '{item['cleaned_text']}' 位置: {item['center']}")
    
    # 测试查找特定文本
    print(f"\n🎯 测试查找 'info.json':")
    position = ocr.find_text_optimized(screenshot_cv, "info.json", min_confidence=0.4)
    
    if position:
        print(f"✅ 成功找到位置: {position}")
    else:
        print("❌ 未找到目标文本")
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()
