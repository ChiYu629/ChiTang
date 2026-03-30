# -*- coding: utf-8 -*-
"""
表情识别系统 - 统一Web界面
支持：摄像头实时检测、图片检测、视频检测
"""
from flask import Flask, render_template, Response, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import os
import threading
import time
from datetime import datetime
from utils.emotion_analyzer import EmotionAnalyzer
from utils.config import SNAPSHOT_DIR, VIDEO_DIR, REPORT_DIR, OUTPUT_DIR

app = Flask(__name__)
CORS(app)

# 配置静态文件路径
app.config['OUTPUT_FOLDER'] = OUTPUT_DIR

# 全局变量
analyzer = EmotionAnalyzer()
camera_running = False
latest_frame = None
camera_thread = None
cap = None
video_progress = {'status': 'idle', 'progress': 0, 'message': ''}
camera_stats = {'total_frames': 0, 'emotion_stats': {}}


def camera_loop():
    """摄像头检测循环"""
    global camera_running, latest_frame, cap, camera_stats

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    frame_count = 0
    camera_stats = {'total_frames': 0, 'emotion_stats': {}}

    while camera_running:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        camera_stats['total_frames'] = frame_count

        # 每5帧分析一次
        if frame_count % 5 == 0:
            success, result = analyzer.analyze_frame(frame)
            if success:
                frame = analyzer.draw_result(frame, result)
                emotion = result['emotion_en']
                camera_stats['emotion_stats'][emotion] = camera_stats['emotion_stats'].get(emotion, 0) + 1

        latest_frame = frame
        time.sleep(0.03)

    if cap:
        cap.release()


def generate_frames():
    """生成视频流"""
    global latest_frame
    while True:
        if camera_running and latest_frame is not None:
            ret, buffer = cv2.imencode('.jpg', latest_frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.03)


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/camera/start', methods=['POST'])
def start_camera():
    """启动摄像头检测"""
    global camera_running, camera_thread

    if not camera_running:
        camera_running = True
        camera_thread = threading.Thread(target=camera_loop, daemon=True)
        camera_thread.start()
        return jsonify({'status': 'success', 'message': '摄像头已启动'})
    return jsonify({'status': 'info', 'message': '摄像头已在运行'})


@app.route('/camera/stop', methods=['POST'])
def stop_camera():
    """停止摄像头检测"""
    global camera_running, camera_stats

    if camera_running:
        camera_running = False
        if camera_thread:
            camera_thread.join(timeout=2)

        # 生成统计报告
        report = {
            'total_frames': camera_stats['total_frames'],
            'emotion_stats': camera_stats['emotion_stats'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return jsonify({
            'status': 'success',
            'message': '摄像头已停止',
            'report': report
        })
    return jsonify({'status': 'info', 'message': '摄像头未运行'})


@app.route('/camera/feed')
def camera_feed():
    """摄像头视频流"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/camera/stats', methods=['GET'])
def get_camera_stats():
    """获取摄像头实时统计数据"""
    global camera_stats
    return jsonify(camera_stats)


@app.route('/image/detect', methods=['POST'])
def detect_image():
    """检测上传的图片"""
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': '未上传文件'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': '文件名为空'})

    # 验证文件类型
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        return jsonify({'status': 'error', 'message': '不支持的文件格式，请上传JPG、PNG或BMP图片'})

    # 保存上传的文件（使用安全的文件名）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_filename = f"upload_{timestamp}{file_ext}"
    filepath = os.path.join(SNAPSHOT_DIR, safe_filename)
    file.save(filepath)

    # 读取并分析图片
    frame = cv2.imread(filepath)
    success, result = analyzer.analyze_frame(frame)

    if success:
        # 绘制结果并保存
        result_frame = analyzer.draw_result(frame, result)
        result_filename = f"result_{timestamp}{file_ext}"
        result_path = os.path.join(SNAPSHOT_DIR, result_filename)
        cv2.imwrite(result_path, result_frame)

        return jsonify({
            'status': 'success',
            'emotion_cn': result['emotion_cn'],
            'emotion_en': result['emotion_en'],
            'confidence': result['confidence'],
            'result_image': result_filename
        })

    return jsonify({'status': 'error', 'message': '未检测到人脸'})


@app.route('/video/detect', methods=['POST'])
def detect_video():
    """检测上传的视频"""
    global video_progress

    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': '未上传文件'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': '文件名为空'})

    # 验证文件类型
    allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        return jsonify({'status': 'error', 'message': '不支持的文件格式，请上传MP4、AVI或MOV视频'})

    # 保存上传的视频（使用安全的文件名）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    input_filename = f"input_{timestamp}{file_ext}"
    input_path = os.path.join(VIDEO_DIR, input_filename)
    file.save(input_path)

    # 处理视频
    output_filename = f"output_{timestamp}.mp4"
    output_path = os.path.join(VIDEO_DIR, output_filename)
    report_filename = f"report_{timestamp}.txt"
    report_path = os.path.join(REPORT_DIR, report_filename)

    # 重置进度
    video_progress = {'status': 'processing', 'progress': 0, 'message': '正在处理视频...'}

    # 在后台线程处理视频
    def process_video():
        global video_progress
        cap = cv2.VideoCapture(input_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_count = 0
        emotion_stats = {}

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # 更新进度
            if total_frames > 0:
                progress = int((frame_count / total_frames) * 100)
                video_progress['progress'] = progress
                video_progress['message'] = f'正在处理: {frame_count}/{total_frames} 帧'

            # 每3帧分析一次
            if frame_count % 3 == 0:
                success, result = analyzer.analyze_frame(frame)
                if success:
                    frame = analyzer.draw_result(frame, result)
                    emotion = result['emotion_en']
                    emotion_stats[emotion] = emotion_stats.get(emotion, 0) + 1

            out.write(frame)

        cap.release()
        out.release()

        # 生成报告
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 50 + "\n")
            f.write("视频表情分析报告\n")
            f.write("=" * 50 + "\n")
            f.write(f"总帧数: {frame_count}\n")
            f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("表情分布:\n")

            for emotion_en, count in sorted(emotion_stats.items(), key=lambda x: x[1], reverse=True):
                emotion_cn = analyzer.emotion_map.get(emotion_en, emotion_en)
                ratio = count / frame_count * 100
                f.write(f"  {emotion_cn}: {count}帧 ({ratio:.2f}%)\n")

        # 标记完成
        video_progress['status'] = 'completed'
        video_progress['progress'] = 100
        video_progress['message'] = '处理完成'
        video_progress['output_video'] = output_filename
        video_progress['report'] = report_filename
        video_progress['emotion_stats'] = emotion_stats
        video_progress['total_frames'] = frame_count

    threading.Thread(target=process_video, daemon=True).start()

    return jsonify({
        'status': 'success',
        'message': '视频上传成功，开始处理...'
    })


@app.route('/static/snapshots/<filename>')
def serve_snapshot(filename):
    """提供快照文件访问"""
    # 安全检查：防止路径遍历攻击
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'status': 'error', 'message': '非法文件名'}), 400
    return send_from_directory(SNAPSHOT_DIR, filename)


@app.route('/static/videos/<filename>')
def serve_video(filename):
    """提供视频文件访问"""
    # 安全检查：防止路径遍历攻击
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'status': 'error', 'message': '非法文件名'}), 400
    return send_from_directory(VIDEO_DIR, filename)


@app.route('/static/reports/<filename>')
def serve_report(filename):
    """提供报告文件访问"""
    # 安全检查：防止路径遍历攻击
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'status': 'error', 'message': '非法文件名'}), 400
    return send_from_directory(REPORT_DIR, filename)


@app.route('/video/progress', methods=['GET'])
def get_video_progress():
    """获取视频处理进度"""
    global video_progress
    return jsonify(video_progress)


if __name__ == '__main__':
    print("=" * 60)
    print("表情识别系统启动")
    print("访问地址: http://localhost:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
