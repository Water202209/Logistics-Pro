@echo off
echo 正在重启后端...

REM 关闭已有 Python 后端进程（粗暴但有效）
taskkill /f /im python.exe >nul 2>nul

REM 等待1秒
timeout /t 1 >nul

REM 进入 backend 目录
cd /d %~dp0

echo 启动后端...

REM 启动后端
start cmd /k python main.py