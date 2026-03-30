# -*- coding: utf-8 -*-
"""
简单示例：摄像头实时检测
用于快速测试摄像头实时表情识别
"""
import cv2
from utils.emotion_analyzer import EmotionAnalyzer

def main():
    """摄像头实时检测主函数"""
    print("=" * 60)
    print("摄像头实时表情检测")
    print("按 'q' 键退出")
    print("=" * 60)

    # 创建分析器
    analyzer = EmotionAnalyzer()

    # 打开摄像头
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("错误：无法打开摄像头")
        return

    frame_count = 0
    emotion_stats = {}

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("错误：无法读取摄像头画面")
                break

            frame_count += 1

            # 每5帧分析一次（提高性能）
            if frame_count % 5 == 0:
                success, result = analyzer.analyze_frame(frame)
                if success:
                    frame = analyzer.draw_result(frame, result)
                    emotion = result['emotion_en']
                    emotion_stats[emotion] = emotion_stats.get(emotion, 0) + 1

            # 添加统计信息
            y_offset = 30
            for emotion_en, count in sorted(emotion_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
                emotion_cn = analyzer.emotion_map.get(emotion_en, emotion_en)
                text = f"{emotion_cn}: {count}"
                frame = analyzer.draw_text(frame, text, (10, y_offset), (255, 255, 255))
                y_offset += 35

            # 显示画面
            cv2.imshow("实时表情检测 (按 q 退出)", frame)

            # 按 'q' 退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n程序被用户中断")

    finally:
        # 释放资源
        cap.release()
        cv2.destroyAllWindows()

        # 打印统计
        print("\n" + "=" * 60)
        print("检测统计")
        print("=" * 60)
        print(f"总帧数: {frame_count}")
        print("\n表情分布:")
        for emotion_en, count in sorted(emotion_stats.items(), key=lambda x: x[1], reverse=True):
            emotion_cn = analyzer.emotion_map.get(emotion_en, emotion_en)
            ratio = count / frame_count * 100 if frame_count > 0 else 0
            print(f"  {emotion_cn}: {count}帧 ({ratio:.2f}%)")


if __name__ == "__main__":
    main()
