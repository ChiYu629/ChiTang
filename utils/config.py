# -*- coding: utf-8 -*-
"""
配置文件 - 统一管理项目配置
"""
import os
import platform

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 情绪中英文映射
EMOTION_MAP = {
    'angry': '生气',
    'disgust': '厌恶',
    'fear': '害怕',
    'happy': '高兴',
    'sad': '伤心',
    'surprise': '惊讶',
    'neutral': '中性'
}

# DeepFace检测器后端
DETECTOR_BACKEND = 'yolov8'

# 字体路径配置
def get_font_path():
    """根据操作系统获取字体路径"""
    system = platform.system()
    font_paths = []

    if system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc",
        ]
    elif system == "Darwin":  # macOS
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
    else:  # Linux
        font_paths = [
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

    # 添加项目本地字体
    font_paths.append(os.path.join(BASE_DIR, "simhei.ttf"))

    return font_paths

# 输出目录配置
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SNAPSHOT_DIR = os.path.join(OUTPUT_DIR, "snapshots")
VIDEO_DIR = os.path.join(OUTPUT_DIR, "videos")
REPORT_DIR = os.path.join(OUTPUT_DIR, "reports")

# 创建输出目录
for directory in [OUTPUT_DIR, SNAPSHOT_DIR, VIDEO_DIR, REPORT_DIR]:
    os.makedirs(directory, exist_ok=True)