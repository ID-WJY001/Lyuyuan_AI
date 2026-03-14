"""Simple LLM Provider Test"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.infrastructure.llm import LLMFactory, Message


async def test_deepseek():
    """Test DeepSeek Provider"""
    print("\n" + "="*50)
    print("Testing DeepSeek Provider")
    print("="*50 + "\n")

    try:
        provider = LLMFactory.create("deepseek")
        print("[OK] Provider created")

        messages = [
            Message(role="system", content="You are a helpful AI assistant."),
            Message(role="user", content="Say hello in one sentence."),
        ]

        print("\nTesting chat...")
        response = await provider.chat(messages, max_tokens=50)
        print(f"[OK] Response: {response.content[:100]}")

        print("\n[SUCCESS] DeepSeek Provider test passed!")
        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_deepseek())
    sys.exit(0 if success else 1)
