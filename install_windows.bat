@echo off
echo =================================================
echo 绿园中学物语: Windows环境依赖安装脚本
echo =================================================

REM 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python! 请安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "web_venv" (
    echo 创建Python虚拟环境...
    python -m venv web_venv
)

REM 激活虚拟环境
call web_venv\Scripts\activate.bat

REM 升级pip
echo 升级pip...
python -m pip install --upgrade pip

REM 安装核心依赖
echo 安装核心依赖...

REM 单独安装各个依赖包，使用--prefer-binary选项
echo 安装Flask...
pip install --prefer-binary flask==2.3.3

echo 安装Werkzeug...
pip install --prefer-binary werkzeug==2.3.7

echo 安装Jinja2...
pip install --prefer-binary jinja2==3.1.2

echo 安装依赖: itsdangerous, click...
pip install --prefer-binary itsdangerous==2.1.2 click==8.1.7

echo 安装中文NLP依赖: jieba, snownlp...
pip install --prefer-binary jieba==0.42.1 snownlp==0.12.3

echo 安装Pillow图像处理库...
pip install --prefer-binary pillow==10.1.0

echo 安装YAML支持...
pip install --prefer-binary pyyaml==6.0.1

echo 安装OpenAI API客户端...
pip install --prefer-binary openai==1.19.0

echo 所有依赖安装完成!
echo 现在可以运行: python web_start.py

pause 