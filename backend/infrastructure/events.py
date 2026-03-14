"""事件系统 - 事件驱动架构核心模块

提供事件总线、事件类型定义、事件监听器等核心功能。
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """事件类型枚举"""

    # 对话事件
    MESSAGE_SENT = "message.sent"           # 用户发送消息
    MESSAGE_RECEIVED = "message.received"   # 角色接收消息
    RESPONSE_GENERATED = "response.generated"  # 角色生成回复

    # 状态变更事件
    CLOSENESS_CHANGED = "state.closeness_changed"  # 好感度变化
    MOOD_CHANGED = "state.mood_changed"            # 情绪变化
    RELATIONSHIP_CHANGED = "state.relationship_changed"  # 关系阶段变化

    # 游戏事件
    GAME_STARTED = "game.started"           # 游戏开始
    GAME_SAVED = "game.saved"               # 游戏保存
    GAME_LOADED = "game.loaded"             # 游戏加载
    CHARACTER_SWITCHED = "game.character_switched"  # 角色切换

    # 系统事件
    ERROR_OCCURRED = "system.error"         # 错误发生
    WARNING_ISSUED = "system.warning"       # 警告发出


@dataclass
class Event:
    """事件数据类"""

    event_type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    source: Optional[str] = None
    priority: int = 0  # 优先级，数字越大优先级越高

    def __str__(self) -> str:
        return f"Event({self.event_type}, id={self.event_id[:8]}, source={self.source})"


EventHandler = Callable[[Event], None]


class EventBus:
    """事件总线 - 中央事件分发器

    负责事件的注册、发布和分发。
    """

    def __init__(self):
        self._listeners: Dict[EventType, List[EventHandler]] = {}
        self._event_history: List[Event] = []
        self._max_history_size = 1000

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """订阅事件

        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []

        self._listeners[event_type].append(handler)
        logger.debug(f"Subscribed handler to {event_type}")

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """取消订阅事件

        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(handler)
                logger.debug(f"Unsubscribed handler from {event_type}")
            except ValueError:
                logger.warning(f"Handler not found for {event_type}")

    def publish(self, event: Event) -> None:
        """发布事件

        Args:
            event: 事件对象
        """
        logger.info(f"Publishing event: {event}")

        # 记录事件历史
        self._event_history.append(event)
        if len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)

        # 分发事件给所有订阅者
        if event.event_type in self._listeners:
            handlers = self._listeners[event.event_type]
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}", exc_info=True)

    def get_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Event]:
        """获取事件历史

        Args:
            event_type: 可选的事件类型过滤
            limit: 返回的最大事件数

        Returns:
            List[Event]: 事件列表
        """
        if event_type:
            filtered = [e for e in self._event_history if e.event_type == event_type]
        else:
            filtered = self._event_history

        return filtered[-limit:]

    def clear_history(self) -> None:
        """清空事件历史"""
        self._event_history.clear()
        logger.debug("Event history cleared")


# 全局事件总线实例
_global_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """获取全局事件总线实例

    Returns:
        EventBus: 全局事件总线
    """
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


__all__ = [
    "Event",
    "EventType",
    "EventBus",
    "EventHandler",
    "get_event_bus",
]