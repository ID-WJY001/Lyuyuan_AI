"""事件监听器示例

展示如何使用事件系统创建自定义监听器。
"""
from __future__ import annotations

import logging
from typing import Dict, List

from backend.infrastructure.events import Event, EventType, get_event_bus

logger = logging.getLogger(__name__)


class EventLogger:
    """日志监听器 - 记录所有事件到日志"""

    def __init__(self, log_level: int = logging.INFO):
        self.log_level = log_level
        self.event_bus = get_event_bus()

    def start(self):
        """开始监听所有事件"""
        for event_type in EventType:
            self.event_bus.subscribe(event_type, self.handle_event)
        logger.info("EventLogger started")

    def handle_event(self, event: Event):
        """处理事件"""
        logger.log(
            self.log_level,
            f"[{event.event_type.value}] {event.source}: {event.data}"
        )


class GameStatistics:
    """统计监听器 - 统计游戏数据"""

    def __init__(self):
        self.event_bus = get_event_bus()
        self.stats: Dict[str, int] = {
            "games_started": 0,
            "games_saved": 0,
            "games_loaded": 0,
            "messages_sent": 0,
            "responses_generated": 0,
            "closeness_changes": 0,
            "relationship_changes": 0,
        }
        self.closeness_history: List[Dict] = []

    def start(self):
        """开始监听统计相关事件"""
        self.event_bus.subscribe(EventType.GAME_STARTED, self._on_game_started)
        self.event_bus.subscribe(EventType.GAME_SAVED, self._on_game_saved)
        self.event_bus.subscribe(EventType.GAME_LOADED, self._on_game_loaded)
        self.event_bus.subscribe(EventType.MESSAGE_SENT, self._on_message_sent)
        self.event_bus.subscribe(EventType.RESPONSE_GENERATED, self._on_response_generated)
        self.event_bus.subscribe(EventType.CLOSENESS_CHANGED, self._on_closeness_changed)
        self.event_bus.subscribe(EventType.RELATIONSHIP_CHANGED, self._on_relationship_changed)
        logger.info("GameStatistics started")

    def _on_game_started(self, event: Event):
        self.stats["games_started"] += 1

    def _on_game_saved(self, event: Event):
        self.stats["games_saved"] += 1

    def _on_game_loaded(self, event: Event):
        self.stats["games_loaded"] += 1

    def _on_message_sent(self, event: Event):
        self.stats["messages_sent"] += 1

    def _on_response_generated(self, event: Event):
        self.stats["responses_generated"] += 1

    def _on_closeness_changed(self, event: Event):
        self.stats["closeness_changes"] += 1
        self.closeness_history.append({
            "character": event.data.get("character"),
            "old_value": event.data.get("old_value"),
            "new_value": event.data.get("new_value"),
            "delta": event.data.get("delta"),
            "timestamp": event.timestamp
        })

    def _on_relationship_changed(self, event: Event):
        self.stats["relationship_changes"] += 1

    def get_stats(self) -> Dict:
        """获取统计数据"""
        return {
            **self.stats,
            "total_closeness_gain": sum(
                h["delta"] for h in self.closeness_history if h["delta"] > 0
            ),
            "total_closeness_loss": sum(
                h["delta"] for h in self.closeness_history if h["delta"] < 0
            ),
        }

    def print_stats(self):
        """打印统计数据"""
        print("\n" + "=" * 60)
        print("Game Statistics")
        print("=" * 60)
        stats = self.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print("=" * 60)


class AchievementSystem:
    """成就系统监听器 - 监听事件解锁成就"""

    def __init__(self):
        self.event_bus = get_event_bus()
        self.achievements: Dict[str, bool] = {
            "first_friend": False,      # 第一次达到"朋友"关系
            "best_friend": False,       # 达到"好朋友"关系
            "intimate": False,          # 达到"亲密关系"
            "save_master": False,       # 保存游戏10次
            "chat_enthusiast": False,   # 发送100条消息
        }
        self.save_count = 0
        self.message_count = 0

    def start(self):
        """开始监听成就相关事件"""
        self.event_bus.subscribe(EventType.RELATIONSHIP_CHANGED, self._check_relationship_achievements)
        self.event_bus.subscribe(EventType.GAME_SAVED, self._check_save_achievements)
        self.event_bus.subscribe(EventType.MESSAGE_SENT, self._check_message_achievements)
        logger.info("AchievementSystem started")

    def _check_relationship_achievements(self, event: Event):
        """检查关系相关成就"""
        new_state = event.data.get("new_state")

        if new_state == "朋友" and not self.achievements["first_friend"]:
            self._unlock_achievement("first_friend", "第一次成为朋友！")

        if new_state == "好朋友" and not self.achievements["best_friend"]:
            self._unlock_achievement("best_friend", "成为好朋友了！")

        if new_state == "亲密关系" and not self.achievements["intimate"]:
            self._unlock_achievement("intimate", "达到亲密关系！")

    def _check_save_achievements(self, event: Event):
        """检查保存相关成就"""
        self.save_count += 1
        if self.save_count >= 10 and not self.achievements["save_master"]:
            self._unlock_achievement("save_master", "保存大师：保存游戏10次！")

    def _check_message_achievements(self, event: Event):
        """检查消息相关成就"""
        self.message_count += 1
        if self.message_count >= 100 and not self.achievements["chat_enthusiast"]:
            self._unlock_achievement("chat_enthusiast", "聊天达人：发送100条消息！")

    def _unlock_achievement(self, achievement_id: str, message: str):
        """解锁成就"""
        self.achievements[achievement_id] = True
        print(f"\n🏆 成就解锁: {message}")
        logger.info(f"Achievement unlocked: {achievement_id}")

    def get_unlocked_achievements(self) -> List[str]:
        """获取已解锁的成就"""
        return [k for k, v in self.achievements.items() if v]


# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 创建监听器
    event_logger = EventLogger()
    stats = GameStatistics()
    achievements = AchievementSystem()

    # 启动监听器
    event_logger.start()
    stats.start()
    achievements.start()

    print("Event listeners started!")
    print("Now you can run the game and see events being logged.")
    print("\nTo see statistics, call: stats.print_stats()")
    print("To see achievements, call: achievements.get_unlocked_achievements()")


__all__ = [
    "EventLogger",
    "GameStatistics",
    "AchievementSystem",
]