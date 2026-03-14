"""LLM Provider工厂类"""
from __future__ import annotations

import logging
import os
from typing import Dict, Optional, Type

from .base import BaseLLMProvider
from .deepseek import DeepSeekProvider
from .openai import OpenAIProvider

logger = logging.getLogger(__name__)


class LLMFactory:
    """LLM提供商工厂类"""

    _providers: Dict[str, Type[BaseLLMProvider]] = {
        "deepseek": DeepSeekProvider,
        "openai": OpenAIProvider,
    }

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseLLMProvider]):
        """注册新的LLM提供商

        Args:
            name: 提供商名称
            provider_class: 提供商类
        """
        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered LLM provider: {name}")

    @classmethod
    def create(
        cls,
        provider_name: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> BaseLLMProvider:
        """创建LLM提供商实例

        Args:
            provider_name: 提供商名称 (deepseek, openai等)
            api_key: API密钥（可选，从环境变量读取）
            model: 模型名称（可选，使用默认值）
            **kwargs: 其他提供商特定参数

        Returns:
            BaseLLMProvider: LLM提供商实例

        Raises:
            ValueError: 如果提供商不存在或API密钥缺失
        """
        provider_name = provider_name.lower()

        if provider_name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown LLM provider: {provider_name}. "
                f"Available providers: {available}"
            )

        # 获取API密钥
        if api_key is None:
            # 尝试从环境变量读取
            env_key_map = {
                "deepseek": "DEEPSEEK_API_KEY",
                "openai": "OPENAI_API_KEY",
            }
            env_key = env_key_map.get(provider_name)
            if env_key:
                api_key = os.environ.get(env_key)

            if not api_key:
                raise ValueError(
                    f"API key not provided and not found in environment variable {env_key}"
                )

        # 创建提供商实例
        provider_class = cls._providers[provider_name]
        if model:
            kwargs["model"] = model

        logger.info(f"Creating LLM provider: {provider_name}")
        return provider_class(api_key=api_key, **kwargs)

    @classmethod
    def list_providers(cls) -> list[str]:
        """列出所有已注册的提供商"""
        return list(cls._providers.keys())
