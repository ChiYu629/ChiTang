# -*- coding: utf-8 -*-
"""
情绪分析核心类 - 统一的情绪检测逻辑
"""
import cv2
import numpy as np
from deepface import DeepFace
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

from .config import EMOTION_MAP, DETECTOR_BACKEND, get_font_path


class EmotionAnalyzer:
    """情绪分析器 - 封装DeepFace调用和结果处理"""

    def __init__(self):
        self.emotion_map = EMOTION_MAP
        self.detector_backend = DETECTOR_BACKEND
        self.font = self._load_font()

    def _load_font(self, size=24):
        """加载中文字体"""
        font_paths = get_font_path()

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception as e:
                    continue

        print("警告：无法加载中文字体，使用默认字体")
        return ImageFont.load_default()

    def analyze_frame(self, frame):
        """
        分析单帧图像
        返回: (是否成功, 情绪结果字典)
        """
        try:
            result = DeepFace.analyze(
                img_path=frame,
                detector_backend=self.detector_backend,
                actions=['emotion'],
                enforce_detection=False,
                silent=True
            )

            if result and isinstance(result, list) and len(result) > 0:
                face_data = result[0]
                return True, {
                    'emotion_en': face_data['dominant_emotion'],
                    'emotion_cn': self.emotion_map.get(face_data['dominant_emotion'], face_data['dominant_emotion']),
                    'region': face_data.get('region', {}),
                    'confidence': face_data.get('face_confidence', 0),
                    'emotion_scores': face_data.get('emotion', {})
                }
            return False, None

        except Exception as e:
            return False, None

    def draw_result(self, frame, result):
        """在帧上绘制检测结果"""
        if not result:
            return frame

        # 绘制人脸框
        region = result.get('region', {})
        if region:
            x, y, w, h = region.get('x', 0), region.get('y', 0), region.get('w', 0), region.get('h', 0)

            # 确保坐标为整数且在有效范围内
            x, y, w, h = int(x), int(y), int(w), int(h)
            x = max(0, x)
            y = max(0, y)

            # 使用OpenCV绘制矩形
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

            # 转换为PIL以绘制中文文字
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_img)

            # 绘制情绪标签（带背景）
            emotion_cn = result['emotion_cn']
            text_y = max(10, y - 40)

            # 绘制半透明背景
            bbox = draw.textbbox((x, text_y), emotion_cn, font=self.font)
            draw.rectangle(bbox, fill=(0, 0, 0, 180))

            # 绘制文字
            draw.text((x, text_y), emotion_cn, font=self.font, fill=(0, 255, 0))

            # 转换回OpenCV格式
            return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        return frame

    def draw_text(self, frame, text, position, color=(255, 255, 255)):
        """在帧上绘制中文文本"""
        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        draw.text(position, text, font=self.font, fill=color)
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
