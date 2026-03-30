@echo off
chcp 65001 >nul
echo ============================================================
echo 表情识别系统 - 快速启动
echo ============================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 检查依赖包...
pip show deepface >nul 2>&1
if errorlevel 1 (
    echo [提示] 首次运行需要安装依赖包，这可能需要几分钟...
    echo.
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo [错误] 依赖包安装失败，请检查网络连接
        pause
        exit /b 1
    )
) else (
    echo [完成] 依赖包已安装
)

echo.
echo [2/3] 创建输出目录...
if not exist "output" mkdir output
if not exist "output\snapshots" mkdir output\snapshots
if not exist "output\videos" mkdir output\videos
if not exist "output\reports" mkdir output\reports
echo [完成] 目录创建完成

echo.
echo [3/3] 启动Web服务...
echo.
echo ============================================================
echo 系统启动成功！
echo 请在浏览器中打开: http://localhost:5000
echo 按 Ctrl+C 可以停止服务
echo ============================================================
echo.

python app.py

pause
