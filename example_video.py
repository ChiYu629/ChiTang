# -*- coding: utf-8 -*-
"""
简单示例：视频表情检测
用于快速测试视频文件的表情识别
"""
import cv2
from utils.emotion_analyzer import EmotionAnalyzer
from utils.config import VIDEO_DIR, REPORT_DIR
from datetime import datetime
import os


def detect_video(input_path):
    """检测视频中的表情"""
    # 检查文件是否存在
    if not os.path.exists(input_path):
        print(f"错误：文件不存在 - {input_path}")
        return

    print("=" * 60)
    print(f"正在处理视频: {input_path}")
    print("=" * 60)

    # 创建分析器
    analyzer = EmotionAnalyzer()

    # 打开视频
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"错误：无法打开视频 - {input_path}")
        return

    # 获取视频参数
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"视频信息: {width}x{height} @ {fps}fps, 总帧数: {total_frames}")

    # 创建输出视频
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"output_{timestamp}.mp4"
    output_path = os.path.join(VIDEO_DIR, output_filename)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_count = 0
    emotion_stats = {}

    print("\n开始处理...")

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # 每3帧分析一次
            if frame_count % 3 == 0:
                success, result = analyzer.analyze_frame(frame)
                if success:
                    frame = analyzer.draw_result(frame, result)
                    emotion = result['emotion_en']
                    emotion_stats[emotion] = emotion_stats.get(emotion, 0) + 1

            # 写入输出视频
            out.write(frame)

            # 显示进度
            if frame_count % 30 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"进度: {progress:.1f}% ({frame_count}/{total_frames})")

    except KeyboardInterrupt:
        print("\n处理被用户中断")

    finally:
        cap.release()
        out.release()

        # 生成报告
        report_filename = f"report_{timestamp}.txt"
        report_path = os.path.join(REPORT_DIR, report_filename)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("视频表情分析报告\n")
            f.write("=" * 60 + "\n")
            f.write(f"输入视频: {input_path}\n")
            f.write(f"输出视频: {output_path}\n")
            f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总帧数: {frame_count}\n\n")
            f.write("表情分布:\n")

            for emotion_en, count in sorted(emotion_stats.items(), key=lambda x: x[1], reverse=True):
                emotion_cn = analyzer.emotion_map.get(emotion_en, emotion_en)
                ratio = count / frame_count * 100 if frame_count > 0 else 0
                f.write(f"  {emotion_cn}: {count}帧 ({ratio:.2f}%)\n")

        # 打印结果
        print("\n" + "=" * 60)
        print("处理完成！")
        print("=" * 60)
        print(f"输出视频: {output_path}")
        print(f"分析报告: {report_path}")
        print("\n表情分布:")
        for emotion_en, count in sorted(emotion_stats.items(), key=lambda x: x[1], reverse=True):
            emotion_cn = analyzer.emotion_map.get(emotion_en, emotion_en)
            ratio = count / frame_count * 100 if frame_count > 0 else 0
            print(f"  {emotion_cn}: {count}帧 ({ratio:.2f}%)")


if __name__ == "__main__":
    # 示例：检测视频
    # 请将下面的路径替换为你的视频路径
    video_path = "data/video.mp4"

    detect_video(video_path)
