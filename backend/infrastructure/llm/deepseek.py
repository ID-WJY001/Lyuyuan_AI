"""DeepSeek LLM Provider实现"""
from __future__ import annotations

import json
import logging
from typing import AsyncIterator, Dict, List, Optional

import httpx

from .base import BaseLLMProvider, LLMResponse, Message

logger = logging.getLogger(__name__)


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek API提供商实现"""

    DEFAULT_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        endpoint: Optional[str] = None,
        **kwargs
    ):
        super().__init__(api_key, model, **kwargs)
        self.endpoint = endpoint or self.DEFAULT_ENDPOINT

    async def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """发送聊天请求到DeepSeek API"""
        payload = {
            "model": self.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "temperature": self._get_temperature(temperature),
            "max_tokens": self._get_max_tokens(max_tokens),
        }
        payload.update(kwargs)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.endpoint,
                headers=headers,
                json=payload,
            )

            if response.status_code != 200:
                error_msg = f"DeepSeek API Error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            data = response.json()
            logger.debug(f"DeepSeek API Response: {data}")

            choice = data["choices"][0]
            return LLMResponse(
                content=choice["message"]["content"],
                model=data.get("model", self.model),
                usage=data.get("usage"),
                finish_reason=choice.get("finish_reason"),
            )

    async def chat_stream(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """发送流式聊天请求到DeepSeek API"""
        payload = {
            "model": self.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "temperature": self._get_temperature(temperature),
            "max_tokens": self._get_max_tokens(max_tokens),
            "stream": True,
        }
        payload.update(kwargs)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                self.endpoint,
                headers=headers,
                json=payload,
            ) as response:
                if response.status_code != 200:
                    error_msg = f"DeepSeek API Error {response.status_code}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse SSE data: {data_str}")
                            continue
