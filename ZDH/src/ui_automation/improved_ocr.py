"""
改进的OCR系统
提高文本识别精度，特别针对桌面文件识别优化
"""

import cv2
import numpy as np
import easyocr
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
from PIL import Image, ImageGrab, ImageEnhance, ImageFilter
import time
from src.utils.logger import get_logger
from src.utils.config_manager import config_manager


class ImprovedOCR:
    """改进的OCR系统"""
    
    def __init__(self):
        """初始化改进的OCR系统"""
        self.logger = get_logger("ImprovedOCR")
        self.config = config_manager.get_ui_config()
        
        # OCR配置
        self.ocr_config = self.config.get('ocr', {})
        self.confidence_threshold = self.ocr_config.get('confidence_threshold', 0.6)
        self.language = self.ocr_config.get('language', 'ch_sim+en')
        
        # 图像预处理配置
        self.preprocessing_config = {
            'enhance_contrast': True,
            'enhance_sharpness': True,
            'denoise': True,
            'resize_factor': 2.0,  # 放大倍数
            'adaptive_threshold': True,
            'morphology': True
        }
        
        # 初始化OCR引擎
        self.ocr_reader = None
        self._init_ocr()
        
        # 文本后处理配置
        self.text_postprocessing = {
            'remove_noise': True,
            'merge_similar_texts': True,
            'confidence_boost': True,
            'context_aware': True
        }
    
    def _init_ocr(self):
        """初始化OCR引擎"""
        try:
            # 使用更精确的OCR配置
            self.ocr_reader = easyocr.Reader(
                languages=self.language.split('+'),
                gpu=False,  # 确保CPU模式稳定
                model_storage_directory='data/ocr_models',
                download_enabled=True,
                recog_network='chinese_sim',  # 使用中文识别网络
                detector_network='craft'  # 使用CRAFT检测器
            )
            self.logger.info("改进OCR初始化成功")
        except Exception as e:
            self.logger.warning(f"改进OCR初始化失败: {e}")
            self.ocr_reader = None
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """图像预处理，提高OCR识别精度"""
        try:
            # 转换为PIL图像
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # 1. 放大图像
            if self.preprocessing_config['resize_factor'] > 1.0:
                new_size = (int(pil_image.width * self.preprocessing_config['resize_factor']),
                           int(pil_image.height * self.preprocessing_config['resize_factor']))
                pil_image = pil_image.resize(new_size, Image.LANCZOS)
            
            # 2. 增强对比度
            if self.preprocessing_config['enhance_contrast']:
                enhancer = ImageEnhance.Contrast(pil_image)
                pil_image = enhancer.enhance(1.5)  # 增强对比度
            
            # 3. 增强锐度
            if self.preprocessing_config['enhance_sharpness']:
                enhancer = ImageEnhance.Sharpness(pil_image)
                pil_image = enhancer.enhance(1.3)  # 增强锐度
            
            # 4. 降噪
            if self.preprocessing_config['denoise']:
                pil_image = pil_image.filter(ImageFilter.MedianFilter(size=3))
            
            # 5. 自适应阈值处理
            if self.preprocessing_config['adaptive_threshold']:
                # 转换为灰度图
                gray = pil_image.convert('L')
                # 自适应阈值
                gray_array = np.array(gray)
                adaptive_thresh = cv2.adaptiveThreshold(
                    gray_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY, 11, 2
                )
                pil_image = Image.fromarray(adaptive_thresh)
            
            # 6. 形态学操作
            if self.preprocessing_config['morphology']:
                gray_array = np.array(pil_image.convert('L'))
                kernel = np.ones((2, 2), np.uint8)
                gray_array = cv2.morphologyEx(gray_array, cv2.MORPH_CLOSE, kernel)
                pil_image = Image.fromarray(gray_array)
            
            # 转换回OpenCV格式
            processed_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            self.logger.debug("图像预处理完成")
            return processed_image
            
        except Exception as e:
            self.logger.error(f"图像预处理失败: {e}")
            return image
    
    def recognize_text(self, image: np.ndarray, target_text: str = None) -> List[Dict[str, Any]]:
        """识别图像中的文本，返回增强的结果"""
        if self.ocr_reader is None:
            self.logger.warning("OCR引擎未初始化")
            return []
        
        try:
            # 图像预处理
            processed_image = self.preprocess_image(image)
            
            # OCR识别
            start_time = time.time()
            results = self.ocr_reader.readtext(
                processed_image,
                detail=1,
                paragraph=False,
                contrast_ths=0.1,  # 降低对比度阈值
                adjust_contrast=0.5,  # 调整对比度
                text_threshold=0.6,  # 降低文本阈值
                link_threshold=0.4,  # 降低链接阈值
                low_text=0.3,  # 降低低文本阈值
                canvas_size=2560,  # 增加画布大小
                mag_ratio=1.5  # 增加放大比例
            )
            recognition_time = time.time() - start_time
            
            self.logger.debug(f"OCR识别完成，耗时: {recognition_time:.3f}秒，识别到 {len(results)} 个文本区域")
            
            # 结果后处理
            enhanced_results = self._postprocess_results(results, target_text)
            
            return enhanced_results
            
        except Exception as e:
            self.logger.error(f"OCR识别失败: {e}")
            return []
    
    def _postprocess_results(self, results: List, target_text: str = None) -> List[Dict[str, Any]]:
        """后处理OCR结果，提高准确性"""
        enhanced_results = []
        
        for bbox, text, confidence in results:
            # 1. 文本清理
            cleaned_text = self._clean_text(text)
            
            # 2. 置信度提升
            boosted_confidence = self._boost_confidence(confidence, cleaned_text, target_text)
            
            # 3. 创建增强结果
            enhanced_result = {
                'bbox': bbox,
                'original_text': text,
                'cleaned_text': cleaned_text,
                'confidence': confidence,
                'boosted_confidence': boosted_confidence,
                'center': self._calculate_center(bbox),
                'area': self._calculate_area(bbox),
                'text_length': len(cleaned_text)
            }
            
            enhanced_results.append(enhanced_result)
        
        # 4. 合并相似文本
        if self.text_postprocessing['merge_similar_texts']:
            enhanced_results = self._merge_similar_texts(enhanced_results)
        
        # 5. 按置信度排序
        enhanced_results.sort(key=lambda x: x['boosted_confidence'], reverse=True)
        
        return enhanced_results
    
    def _clean_text(self, text: str) -> str:
        """清理文本，去除噪声"""
        if not text:
            return ""
        
        # 去除常见噪声字符
        noise_chars = ['|', '\\', '/', '-', '_', '=', '+', '*', '&', '^', '%', '$', '#', '@', '!']
        cleaned = text
        
        for char in noise_chars:
            cleaned = cleaned.replace(char, '')
        
        # 去除多余空格
        cleaned = ' '.join(cleaned.split())
        
        # 去除首尾空白
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _boost_confidence(self, confidence: float, text: str, target_text: str = None) -> float:
        """提升置信度，基于文本质量和目标匹配度"""
        boosted = confidence
        
        # 1. 基于文本长度提升
        if len(text) >= 3:
            boosted += 0.1
        
        # 2. 基于文本质量提升
        if text.isalnum() or any(ext in text.lower() for ext in ['.txt', '.json', '.doc', '.pdf']):
            boosted += 0.15
        
        # 3. 基于目标匹配提升
        if target_text and target_text.lower() in text.lower():
            boosted += 0.2
        
        # 4. 基于文件扩展名提升
        if any(ext in text.lower() for ext in ['.json', '.txt', '.doc', '.pdf', '.jpg', '.png']):
            boosted += 0.1
        
        # 限制置信度范围
        return min(boosted, 1.0)
    
    def _calculate_center(self, bbox) -> Tuple[int, int]:
        """计算边界框中心点"""
        try:
            x1, y1 = bbox[0]
            x3, y3 = bbox[2]
            center_x = int((x1 + x3) / 2)
            center_y = int((y1 + y3) / 2)
            return (center_x, center_y)
        except:
            return (0, 0)
    
    def _calculate_area(self, bbox) -> int:
        """计算边界框面积"""
        try:
            x1, y1 = bbox[0]
            x3, y3 = bbox[2]
            width = abs(x3 - x1)
            height = abs(y3 - y1)
            return width * height
        except:
            return 0
    
    def _merge_similar_texts(self, results: List[Dict]) -> List[Dict]:
        """合并相似的文本区域"""
        if len(results) <= 1:
            return results
        
        merged = []
        used_indices = set()
        
        for i, result1 in enumerate(results):
            if i in used_indices:
                continue
            
            similar_group = [result1]
            used_indices.add(i)
            
            for j, result2 in enumerate(results[i+1:], i+1):
                if j in used_indices:
                    continue
                
                # 检查是否相似
                if self._are_texts_similar(result1['cleaned_text'], result2['cleaned_text']):
                    similar_group.append(result2)
                    used_indices.add(j)
            
            # 合并相似组
            if len(similar_group) > 1:
                merged_result = self._merge_text_group(similar_group)
                merged.append(merged_result)
            else:
                merged.append(result1)
        
        return merged
    
    def _are_texts_similar(self, text1: str, text2: str) -> bool:
        """检查两个文本是否相似"""
        if not text1 or not text2:
            return False
        
        # 简单的相似度检查
        text1_lower = text1.lower()
        text2_lower = text2.lower()
        
        # 检查是否包含相同的文件扩展名
        extensions1 = [ext for ext in ['.json', '.txt', '.doc', '.pdf'] if ext in text1_lower]
        extensions2 = [ext for ext in ['.json', '.txt', '.doc', '.pdf'] if ext in text2_lower]
        
        if extensions1 and extensions2 and extensions1 == extensions2:
            return True
        
        # 检查文本重叠
        if len(text1_lower) > 3 and len(text2_lower) > 3:
            common_chars = set(text1_lower) & set(text2_lower)
            if len(common_chars) >= min(len(text1_lower), len(text2_lower)) * 0.6:
                return True
        
        return False
    
    def _merge_text_group(self, group: List[Dict]) -> Dict:
        """合并文本组"""
        # 选择置信度最高的结果
        best_result = max(group, key=lambda x: x['boosted_confidence'])
        
        # 更新置信度为组内最高
        best_result['boosted_confidence'] = max(r['boosted_confidence'] for r in group)
        best_result['merged_count'] = len(group)
        
        return best_result
    
    def find_text(self, image: np.ndarray, target_text: str, 
                  min_confidence: float = None) -> Optional[Tuple[int, int]]:
        """查找指定文本，返回最佳匹配位置"""
        if min_confidence is None:
            min_confidence = self.confidence_threshold
        
        # 识别文本
        results = self.recognize_text(image, target_text)
        
        # 查找最佳匹配
        for result in results:
            if (result['boosted_confidence'] >= min_confidence and 
                target_text.lower() in result['cleaned_text'].lower()):
                
                self.logger.info(f"找到目标文本: {target_text}")
                self.logger.info(f"  原始文本: {result['original_text']}")
                self.logger.info(f"  清理文本: {result['cleaned_text']}")
                self.logger.info(f"  置信度: {result['confidence']:.3f}")
                self.logger.info(f"  提升置信度: {result['boosted_confidence']:.3f}")
                self.logger.info(f"  位置: {result['center']}")
                
                return result['center']
        
        self.logger.warning(f"未找到目标文本: {target_text}")
        return None
    
    def get_detailed_results(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """获取详细的OCR识别结果，用于调试和分析"""
        return self.recognize_text(image)


def main():
    """测试改进的OCR系统"""
    print("测试改进的OCR系统...")
    
    ocr = ImprovedOCR()
    
    # 截取屏幕
    screenshot = ImageGrab.grab()
    screenshot_np = np.array(screenshot)
    screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    
    print("正在识别屏幕文本...")
    results = ocr.get_detailed_results(screenshot_cv)
    
    print(f"识别到 {len(results)} 个文本区域:")
    for i, result in enumerate(results[:10]):  # 只显示前10个
        print(f"  {i+1}. 文本: '{result['cleaned_text']}'")
        print(f"     置信度: {result['confidence']:.3f} -> {result['boosted_confidence']:.3f}")
        print(f"     位置: {result['center']}")
        print(f"     面积: {result['area']}")
    
    # 测试查找特定文本
    print("\n测试查找 'info.json':")
    position = ocr.find_text(screenshot_cv, "info.json", min_confidence=0.5)
    if position:
        print(f"✅ 找到位置: {position}")
    else:
        print("❌ 未找到")


if __name__ == "__main__":
    main()
