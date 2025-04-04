@echo off
echo 正在启动"绿园中学物语：追女生模拟"Web版本...

REM 检查venv目录是否存在
if not exist "web_venv" (
    echo 创建Python虚拟环境...
    python -m venv web_venv
)

REM 激活虚拟环境
call web_venv\Scripts\activate.bat

REM 检查依赖
python -c "from utils.common import ensure_dependencies; ensure_dependencies()" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 安装所需依赖...
    python -m pip install -r web_app\requirements.txt
)

REM 确保工作目录正确
cd /d %~dp0

REM 启动应用
echo 启动Web应用...
python scripts\tools\web_starter.py

if %ERRORLEVEL% NEQ 0 (
  echo 启动失败，请尝试运行install.py脚本进行完整安装
  echo 命令: python install.py
  pause
) else (
  echo 服务器已启动，请在浏览器中访问: http://localhost:5000
  echo 按Ctrl+C可停止服务器
  pause
) 