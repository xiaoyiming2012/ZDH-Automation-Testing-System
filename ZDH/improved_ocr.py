#!/usr/bin/env python3
"""
改进的OCR系统 - 提高文本识别精度
"""

import cv2
import numpy as np
import easyocr
from PIL import Image, ImageGrab, ImageEnhance
import time

class ImprovedOCR:
    """改进的OCR系统"""
    
    def __init__(self):
        """初始化"""
        print("正在初始化改进的OCR系统...")
        
        # OCR配置
        self.confidence_threshold = 0.5  # 降低阈值
        self.language = ['ch_sim', 'en']  # 修复语言参数格式
        
        # 初始化OCR引擎
        try:
            self.ocr_reader = easyocr.Reader(
                self.language,  # 直接传递语言列表
                gpu=False,
                verbose=False  # 减少输出
            )
            print("✅ OCR初始化成功")
        except Exception as e:
            print(f"❌ OCR初始化失败: {e}")
            # 尝试备用初始化方法
            try:
                self.ocr_reader = easyocr.Reader(self.language)
                print("✅ OCR备用初始化成功")
            except Exception as e2:
                print(f"❌ OCR备用初始化也失败: {e2}")
                self.ocr_reader = None
    
    def preprocess_image(self, image):
        """图像预处理"""
        try:
            # 转换为PIL图像
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # 放大图像
            new_size = (int(pil_image.width * 2), int(pil_image.height * 2))
            pil_image = pil_image.resize(new_size, Image.LANCZOS)
            
            # 增强对比度
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(1.5)
            
            # 增强锐度
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(1.3)
            
            # 转换回OpenCV格式
            processed = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            return processed
            
        except Exception as e:
            print(f"图像预处理失败: {e}")
            return image
    
    def recognize_text(self, image):
        """识别文本"""
        if not self.ocr_reader:
            return []
        
        try:
            # 预处理
            processed_image = self.preprocess_image(image)
            
            # OCR识别 - 使用简化的参数
            results = self.ocr_reader.readtext(
                processed_image,
                detail=1,
                paragraph=False
            )
            
            # 后处理结果
            enhanced_results = []
            for bbox, text, confidence in results:
                # 清理文本
                cleaned_text = self.clean_text(text)
                
                # 提升置信度
                boosted_confidence = self.boost_confidence(confidence, cleaned_text)
                
                # 计算中心点
                center = self.calculate_center(bbox)
                
                enhanced_results.append({
                    'bbox': bbox,
                    'original_text': text,
                    'cleaned_text': cleaned_text,
                    'confidence': confidence,
                    'boosted_confidence': boosted_confidence,
                    'center': center
                })
            
            # 按提升后的置信度排序
            enhanced_results.sort(key=lambda x: x['boosted_confidence'], reverse=True)
            
            return enhanced_results
            
        except Exception as e:
            print(f"OCR识别失败: {e}")
            return []
    
    def clean_text(self, text):
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
    
    def boost_confidence(self, confidence, text):
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
        
        return min(boosted, 1.0)
    
    def calculate_center(self, bbox):
        """计算中心点"""
        try:
            x1, y1 = bbox[0]
            x3, y3 = bbox[2]
            center_x = int((x1 + x3) / 2)
            center_y = int((y1 + y3) / 2)
            return (center_x, center_y)
        except:
            return (0, 0)
    
    def find_text(self, image, target_text, min_confidence=0.5):
        """查找指定文本"""
        results = self.recognize_text(image)
        
        for result in results:
            if (result['boosted_confidence'] >= min_confidence and 
                target_text.lower() in result['cleaned_text'].lower()):
                
                print(f"✅ 找到目标文本: {target_text}")
                print(f"   原始文本: {result['original_text']}")
                print(f"   清理文本: {result['cleaned_text']}")
                print(f"   置信度: {result['confidence']:.3f} -> {result['boosted_confidence']:.3f}")
                print(f"   位置: {result['center']}")
                
                return result['center']
        
        print(f"❌ 未找到目标文本: {target_text}")
        return None

def main():
    """测试函数"""
    print("=" * 50)
    print("改进OCR系统测试")
    print("=" * 50)
    
    # 初始化OCR
    ocr = ImprovedOCR()
    
    # 截取屏幕
    print("\n正在截取屏幕...")
    screenshot = ImageGrab.grab()
    screenshot_np = np.array(screenshot)
    screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    print("✅ 屏幕截图完成")
    
    # 识别文本
    print("\n正在识别屏幕文本...")
    results = ocr.recognize_text(screenshot_cv)
    
    print(f"\n识别到 {len(results)} 个文本区域:")
    for i, result in enumerate(results[:10]):
        print(f"  {i+1}. '{result['cleaned_text']}'")
        print(f"     置信度: {result['confidence']:.3f} -> {result['boosted_confidence']:.3f}")
        print(f"     位置: {result['center']}")
    
    # 测试查找特定文本
    print("\n测试查找 'info.json':")
    position = ocr.find_text(screenshot_cv, "info.json", min_confidence=0.4)
    
    if position:
        print(f"✅ 成功找到位置: {position}")
    else:
        print("❌ 未找到目标文本")
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()
