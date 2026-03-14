"""LLM Provider抽象基类

定义统一的LLM接口，支持多个提供商。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator, Dict, List, Optional


@dataclass
class Message:
    """消息数据类"""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """LLM响应数据类"""
    content: str
    model: str
    usage: Optional[Dict] = None
    finish_reason: Optional[str] = None


class BaseLLMProvider(ABC):
    """LLM提供商抽象基类"""

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.8,
        max_tokens: int = 1500,
        timeout: int = 45,
        **kwargs
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.extra_params = kwargs

    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """发送聊天请求并返回完整响应

        Args:
            messages: 消息列表
            temperature: 温度参数（可选，使用实例默认值）
            max_tokens: 最大token数（可选，使用实例默认值）
            **kwargs: 其他提供商特定参数

        Returns:
            LLMResponse: LLM响应对象
        """
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """发送聊天请求并返回流式响应

        Args:
            messages: 消息列表
            temperature: 温度参数（可选，使用实例默认值）
            max_tokens: 最大token数（可选，使用实例默认值）
            **kwargs: 其他提供商特定参数

        Yields:
            str: 流式响应的文本片段
        """
        pass

    def _get_temperature(self, temperature: Optional[float]) -> float:
        """获取温度参数，优先使用传入值"""
        return temperature if temperature is not None else self.temperature

    def _get_max_tokens(self, max_tokens: Optional[int]) -> int:
        """获取max_tokens参数，优先使用传入值"""
        return max_tokens if max_tokens is not None else self.max_tokens

