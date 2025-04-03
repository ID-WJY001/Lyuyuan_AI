"""
绿园中学物语：追女生模拟
Web版本启动入口
"""
import os
import sys
from web_app.app import app

# 设置API密钥
def setup_api_key():
    """设置API密钥"""
    try:
        # 尝试从.env文件加载
        if os.path.exists(".env"):
            print("检测到.env文件，尝试加载环境变量...")
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    key, value = line.split("=", 1)
                    os.environ[key] = value
                    if key == "DEEPSEEK_API_KEY":
                        print("成功从.env文件加载API密钥")
        
        # 检查环境变量中是否已有API密钥
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        
        # 如果没有API密钥，使用备用密钥（开发环境）
        if not api_key:
            api_key = "your-deepseek-api-key"  # 需要替换为有效的DeepSeek API密钥
            os.environ["DEEPSEEK_API_KEY"] = api_key
            print("警告：使用备用API密钥。在生产环境中，请设置正确的API密钥。")
        else:
            print("API密钥设置成功")
    except Exception as e:
        print(f"API密钥设置错误: {str(e)}")
        print("Web应用将继续，但可能无法获取在线响应。")

if __name__ == "__main__":
    print("正在启动'绿园中学物语：追女生模拟'Web版本...")
    
    # 确保工作目录正确
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 设置API密钥
    setup_api_key()
    
    # 创建保存目录
    os.makedirs("saves", exist_ok=True)
    
    # 运行Flask应用
    app.run(debug=True, host='0.0.0.0', port=5000) 