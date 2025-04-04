"""
绿园中学物语
Web版本启动入口
"""
import os
import sys
import logging
from utils.common import load_env_file, ensure_directories
from web_app.app import app

# 设置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 设置API密钥
def setup_api_key():
    """设置API密钥"""
    try:
        # 加载环境变量
        env_vars = load_env_file()
        
        # 设置OpenAI API密钥
        if 'DEEPSEEK_API_KEY' in env_vars:
            os.environ['DEEPSEEK_API_KEY'] = env_vars['DEEPSEEK_API_KEY']
            logger.info("API密钥已设置")
        else:
            logger.warning("找不到DEEPSEEK_API_KEY环境变量")
    except Exception as e:
        logger.error(f"设置API密钥时出错: {e}")

def main():
    """
    主函数
    """
    print("正在启动'绿园中学物语：追女生模拟'Web版本...")
    
    # 确保工作目录正确
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 设置API密钥
    setup_api_key()
    
    # 创建必要的目录
    ensure_directories("saves")
    
    try:
        # 运行Flask应用
        logger.info("正在启动Web应用，请访问 http://localhost:5000")
        app.run(debug=False, host='0.0.0.0', port=5000)
    except ImportError as e:
        logger.error(f"导入Web应用时出错: {e}")
    except Exception as e:
        logger.error(f"启动Web应用时出错: {e}")

if __name__ == "__main__":
    main() 