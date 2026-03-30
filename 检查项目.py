# -*- coding: utf-8 -*-
"""
项目完整性检查脚本
检查所有必需的文件和目录是否存在
"""
import os
import sys

# 设置Windows控制台UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_file(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print(f"[OK] {description}: {filepath}")
        return True
    else:
        print(f"[X] {description}: {filepath} [缺失]")
        return False

def check_directory(dirpath, description):
    """检查目录是否存在"""
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        print(f"[OK] {description}: {dirpath}")
        return True
    else:
        print(f"[!] {description}: {dirpath} [不存在，将自动创建]")
        try:
            os.makedirs(dirpath, exist_ok=True)
            print(f"    已创建: {dirpath}")
            return True
        except Exception as e:
            print(f"    创建失败: {e}")
            return False

def main():
    print("=" * 60)
    print("表情识别系统 - 项目完整性检查")
    print("=" * 60)
    print()

    all_ok = True

    # 检查核心文件
    print("【核心文件】")
    all_ok &= check_file("app.py", "主程序")
    all_ok &= check_file("requirements.txt", "依赖列表")
    all_ok &= check_file("README.md", "用户手册")
    print()

    # 检查工具模块
    print("【工具模块】")
    all_ok &= check_directory("utils", "工具目录")
    all_ok &= check_file("utils/__init__.py", "包初始化")
    all_ok &= check_file("utils/config.py", "配置文件")
    all_ok &= check_file("utils/emotion_analyzer.py", "分析器")
    print()

    # 检查模板
    print("【网页模板】")
    all_ok &= check_directory("templates", "模板目录")
    all_ok &= check_file("templates/index.html", "主页面")
    print()

    # 检查输出目录
    print("【输出目录】")
    check_directory("output", "输出根目录")
    check_directory("output/snapshots", "图片结果")
    check_directory("output/videos", "视频结果")
    check_directory("output/reports", "分析报告")
    print()

    # 检查示例程序
    print("【示例程序】")
    check_file("example_camera.py", "摄像头示例")
    check_file("example_image.py", "图片示例")
    check_file("example_video.py", "视频示例")
    print()

    # 检查文档
    print("【文档文件】")
    check_file("项目说明.md", "代码详解")
    check_file("安全说明.md", "安全文档")
    check_file("项目总结.md", "项目总结")
    print()

    # 检查启动脚本
    print("【启动脚本】")
    check_file("启动系统.bat", "Windows启动")
    check_file("启动系统.sh", "Linux/Mac启动")
    print()

    # 检查Python环境
    print("【Python环境】")
    print(f"[OK] Python版本: {sys.version}")
    print()

    # 检查依赖包
    print("【依赖包检查】")
    required_packages = [
        ('deepface', 'DeepFace'),
        ('cv2', 'OpenCV'),
        ('flask', 'Flask'),
        ('PIL', 'Pillow'),
        ('numpy', 'NumPy')
    ]

    missing_packages = []
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"[OK] {name}: 已安装")
        except ImportError:
            print(f"[X] {name}: 未安装")
            missing_packages.append(name)
    print()

    # 总结
    print("=" * 60)
    if missing_packages:
        print("[!] 检测到缺失的依赖包，请运行以下命令安装：")
        print()
        print("   pip install -r requirements.txt")
        print()
    else:
        print("[OK] 所有依赖包已安装")
        print()

    if all_ok and not missing_packages:
        print("[成功] 项目完整性检查通过！")
        print()
        print("快速启动：")
        print("  Windows: 双击 '启动系统.bat'")
        print("  Linux/Mac: ./启动系统.sh")
        print("  或运行: python app.py")
    else:
        print("[警告] 发现一些问题，请根据上述提示修复")

    print("=" * 60)

if __name__ == "__main__":
    main()
