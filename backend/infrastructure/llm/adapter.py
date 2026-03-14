"""LLM适配器 - 将异步LLM接口适配为同步接口

这个适配器用于在过渡期间，让现有的同步代码能够使用新的异步LLM接口。
未来当整个系统迁移到异步后，可以移除这个适配器。
"""
from __future__ import annotations

import asyncio
import logging
from typing import Dict, List

from backend import settings
from .factory import LLMFactory
from .base import Message

logger = logging.getLogger(__name__)


class LLMAdapter:
    """LLM适配器 - 提供同步接口"""

    def __init__(self):
        """初始化LLM适配器"""
        self.provider_name = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.timeout = settings.LLM_TIMEOUT

        logger.info(
            f"Initializing LLM Adapter: provider={self.provider_name}, "
            f"model={self.model or 'default'}"
        )

        # 创建LLM提供商实例
        self._provider = LLMFactory.create(
            provider_name=self.provider_name,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout,
        )

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """同步聊天接口

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            **kwargs: 其他参数（temperature, max_tokens等）

        Returns:
            str: LLM响应文本
        """
        # 转换消息格式
        llm_messages = [Message(role=msg["role"], content=msg["content"]) for msg in messages]

        # 运行异步方法
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(
                self._provider.chat(llm_messages, **kwargs)
            )
            return response.content
        finally:
            loop.close()
