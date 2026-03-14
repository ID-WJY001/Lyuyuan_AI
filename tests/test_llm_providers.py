"""测试LLM Provider实现"""
import asyncio
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.infrastructure.llm import LLMFactory, Message


async def test_provider(provider_name: str):
    """测试指定的LLM提供商"""
    print(f"\n{'='*50}")
    print(f"Testing {provider_name.upper()} Provider")
    print(f"{'='*50}\n")

    try:
        # 创建提供商实例
        provider = LLMFactory.create(provider_name)
        print(f"✓ Provider created successfully")

        # 准备测试消息
        messages = [
            Message(role="system", content="你是一个友好的AI助手。"),
            Message(role="user", content="你好，请用一句话介绍你自己。"),
        ]

        # 测试普通聊天
        print(f"\n测试普通聊天...")
        response = await provider.chat(messages, max_tokens=100)
        print(f"✓ Response: {response.content}")
        print(f"  Model: {response.model}")
        print(f"  Usage: {response.usage}")

        # 测试流式聊天
        print(f"\n测试流式聊天...")
        print(f"✓ Stream response: ", end="", flush=True)
        async for chunk in provider.chat_stream(messages, max_tokens=100):
            print(chunk, end="", flush=True)
        print()

        print(f"\n✓ {provider_name.upper()} Provider测试通过！")
        return True

    except Exception as e:
        print(f"\n✗ {provider_name.upper()} Provider测试失败:")
        print(f"  Error: {e}")
        return False


async def main():
    """主测试函数"""
    print("LLM Provider测试")
    print("="*50)

    # 列出所有可用的提供商
    providers = LLMFactory.list_providers()
    print(f"\n可用的提供商: {', '.join(providers)}")

    # 测试每个提供商
    results = {}
    for provider_name in providers:
        # 检查是否有API密钥
        env_key_map = {
            "deepseek": "DEEPSEEK_API_KEY",
            "openai": "OPENAI_API_KEY",
        }
        env_key = env_key_map.get(provider_name)
        if env_key and not os.environ.get(env_key):
            print(f"\n[SKIP] {provider_name.upper()}: {env_key} not set")
            continue

        results[provider_name] = await test_provider(provider_name)

    # 打印总结
    print(f"\n{'='*50}")
    print("测试总结")
    print(f"{'='*50}")
    for provider, success in results.items():
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{provider.upper()}: {status}")


if __name__ == "__main__":
    asyncio.run(main())
