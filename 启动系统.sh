#!/bin/bash

echo "============================================================"
echo "表情识别系统 - 快速启动"
echo "============================================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装Python 3.8或更高版本"
    exit 1
fi

echo "[1/3] 检查依赖包..."
if ! python3 -c "import deepface" &> /dev/null; then
    echo "[提示] 首次运行需要安装依赖包，这可能需要几分钟..."
    echo ""
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖包安装失败，请检查网络连接"
        exit 1
    fi
else
    echo "[完成] 依赖包已安装"
fi

echo ""
echo "[2/3] 创建输出目录..."
mkdir -p output/snapshots output/videos output/reports
echo "[完成] 目录创建完成"

echo ""
echo "[3/3] 启动Web服务..."
echo ""
echo "============================================================"
echo "系统启动成功！"
echo "请在浏览器中打开: http://localhost:5000"
echo "按 Ctrl+C 可以停止服务"
echo "============================================================"
echo ""

python3 app.py
