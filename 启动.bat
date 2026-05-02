@echo off
chcp 65001 >nul
title 敏感信息加密工具
cd /d "%~dp0"

echo.
echo  ========================================
echo    敏感信息加密工具 - 启动中...
echo  ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

:: 检查依赖
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo  [提示] 首次运行，正在安装依赖...
    pip install -r requirements.txt -q
    echo  [完成] 依赖安装完成
    echo.
)

echo  [启动] 正在启动服务...
echo  [访问] http://localhost:5000
echo.

:: 自动打开浏览器
start http://localhost:5000

:: 启动 Flask
python app.py
pause
