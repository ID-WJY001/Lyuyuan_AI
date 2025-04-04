"""
测试DeepSeek API连接
"""
import os
import sys
from openai import OpenAI
from utils.common import load_env_file, disable_proxy

def test_api():
    # 从环境变量加载API密钥
    load_env_file()
        
    # 获取API密钥
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("错误: API密钥未设置")
        return
        
    # 确保禁用代理设置
    disable_proxy()
        
    print("正在测试API连接...")
    try:
        # 严格按照官方示例创建客户端，明确指定http客户端实现
        client = OpenAI(
            api_key=api_key, 
            base_url="https://api.deepseek.com",
            http_client=None,  # 使用默认http客户端
        )
        
        # 使用最简单的消息格式
        print("发送API请求...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello"},
            ],
            stream=False
        )
        
        # 输出结果
        print("\n=== API响应 ===")
        print(response.choices[0].message.content)
        print("=============")
        print("API调用成功!")
    except Exception as e:
        print(f"API调用失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误详情: {str(e)}")
        
        # 尝试使用最简单的配置
        try:
            print("\n尝试使用最简单配置...")
            simple_client = OpenAI(api_key=api_key)
            simple_client.base_url = "https://api.deepseek.com"
            
            response = simple_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "user", "content": "Hello"},
                ],
            )
            print("简单配置API调用成功!")
            print(response.choices[0].message.content)
        except Exception as e2:
            print(f"简单配置也失败了: {e2}")
        
if __name__ == "__main__":
    test_api() 