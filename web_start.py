# web_start.py - [最终独立版]

import os
import logging
from dotenv import load_dotenv

# --- 内置核心功能，不再需要 utils ---

def setup_environment():
    """
    一个函数完成所有环境设置：加载.env和创建目录。
    """
    # 1. 确保我们是在项目根目录运行
    # 这让所有相对路径（如 'saves', 'prompts'）都能正常工作
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    logging.info(f"当前工作目录已设置为: {project_root}")

    # 2. 加载 .env 文件
    # python-dotenv 会自动寻找当前目录的 .env 文件
    if load_dotenv():
        logging.info("检测到.env文件，正在加载环境变量...")
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if api_key:
            # 为了安全，只打印部分key
            logging.info(f"成功从.env文件加载API密钥: {api_key[:5]}...{api_key[-4:]}")
        else:
            logging.warning("在.env文件中未找到DEEPSEEK_API_KEY。")
    else:
        logging.info("未找到.env文件，将依赖系统环境变量。")
        if not os.environ.get("DEEPSEEK_API_KEY"):
            logging.error("致命错误: 在系统环境变量中也未找到DEEPSEEK_API_KEY！")
            return False # 返回失败信号

    # 3. 确保必要的目录存在
    # os.makedirs 如果目录已存在会报错，所以加上 exist_ok=True
    try:
        saves_dir = "saves"
        os.makedirs(saves_dir, exist_ok=True)
        logging.info(f"确保目录 '{saves_dir}' 已存在。")
    except OSError as e:
        logging.error(f"创建目录 '{saves_dir}' 失败: {e}")
        return False # 返回失败信号
        
    return True # 所有设置成功

# --- 主启动逻辑 ---

def main():
    """
    主函数：设置环境并启动Web应用。
    """
    # 设置日志
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    print("\n" + "="*50)
    print("正在启动 '绿园中学物语' Web版本...")
    print("="*50)
    
    # 1. 设置环境
    if not setup_environment():
        print("\n环境设置失败，请检查错误日志。程序即将退出。")
        return # 失败则直接退出

    # 2. 动态导入Flask app
    #    这样可以确保环境设置完成后再加载Web应用的代码
    try:
        from web_app.app import app
        logging.info("Web应用模块导入成功。")
    except ImportError as e:
        logging.error(f"导入Web应用时出错: {e}")
        logging.error("请确保 web_app/app.py 和 web_app/game_core.py 文件存在且无语法错误。")
        return

    # 3. 运行Flask应用
    try:
        logging.info("正在启动Web服务器，请在浏览器中访问 http://127.0.0.1:5000")
        logging.info("按 CTRL+C 退出服务器。")
        # 使用 waitress 或 gunicorn 替换 app.run 是生产环境的最佳实践
        # 但对于开发，app.run 足够了
        app.run(debug=False, host='0.0.0.0', port=5000)
    except Exception as e:
        logging.error(f"启动Web应用时发生未知错误: {e}")

if __name__ == "__main__":
    main()