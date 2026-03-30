# -*- coding: utf-8 -*-
"""
简单示例：图片表情检测
用于快速测试单张图片的表情识别
"""
import cv2
from utils.emotion_analyzer import EmotionAnalyzer
from utils.config import SNAPSHOT_DIR
import os

def detect_image(image_path):
    """检测图片中的表情"""
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"错误：文件不存在 - {image_path}")
        return

    # 创建分析器
    analyzer = EmotionAnalyzer()

    # 读取图片
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"错误：无法读取图片 - {image_path}")
        return

    print(f"正在分析图片: {image_path}")

    # 分析表情
    success, result = analyzer.analyze_frame(frame)

    if success:
        print("\n检测成功！")
        print(f"表情: {result['emotion_cn']} ({result['emotion_en']})")
        print(f"置信度: {result['confidence']:.2f}")

        # 绘制结果
        result_frame = analyzer.draw_result(frame, result)

        # 保存结果
        output_path = os.path.join(SNAPSHOT_DIR, f"result_{os.path.basename(image_path)}")
        cv2.imwrite(output_path, result_frame)
        print(f"\n结果已保存: {output_path}")

        # 显示结果
        cv2.imshow("表情检测结果", result_frame)
        print("\n按任意键关闭窗口...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("\n未检测到人脸，请确保图片中有清晰的正面人脸。")


if __name__ == "__main__":
    # 示例：检测图片
    # 请将下面的路径替换为你的图片路径
    image_path = "data/pic003.png"

    detect_image(image_path)
