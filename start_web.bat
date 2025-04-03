@echo off
echo 启动绿园中学物语：追女生模拟 - Web版本
echo 请稍候...

python web_start.py

if %ERRORLEVEL% NEQ 0 (
  echo 启动失败，请确保已安装所需依赖
  echo 可尝试运行: pip install -r web_app/requirements.txt
  pause
) else (
  echo 服务器已启动，请在浏览器中访问: http://localhost:5000
  echo 按Ctrl+C可停止服务器
  pause
) 