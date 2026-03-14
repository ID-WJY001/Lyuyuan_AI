"""主动对话系统 - 让 AI 主动打招呼和分享"""
from datetime import datetime, timedelta
from typing import Optional, Dict
import random


class ProactiveSystem:
    """主动性管理"""

    def __init__(self, character_name: str = "角色"):
        self.character_name = character_name
        self.last_chat_time: Optional[datetime] = None

    def should_greet_proactively(self, current_time: datetime) -> bool:
        """判断是否需要主动问候"""
        if not self.last_chat_time:
            return False

        time_gap = current_time - self.last_chat_time
        # 超过 0.1 小时（6 分钟）主动问候
        return time_gap > timedelta(hours=0.1)

    def generate_greeting(self, time_gap_hours: float, relationship_state: str, closeness: int) -> Optional[str]:
        """生成主动问候语"""
        if time_gap_hours < 0.1:
            return None

        # 根据关系亲密度选择问候方式
        if closeness < 40:
            greetings = [
                "好久不见，最近还好吗？",
                "嗨，这几天过得怎么样？"
            ]
        elif closeness < 70:
            greetings = [
                "好久没聊天了，有点想你呢。最近忙什么？",
                "这几天都没见到你，还好吗？"
            ]
        else:
            greetings = [
                "终于等到你了~ 这几天一直在想你呢。",
                "好想你啊，这几天都在干嘛？"
            ]

        return random.choice(greetings)

    def update_last_chat_time(self, time: Optional[datetime] = None):
        """更新最后聊天时间"""
        self.last_chat_time = time or datetime.now()

    def to_dict(self) -> Dict:
        return {
            "last_chat_time": self.last_chat_time.isoformat() if self.last_chat_time else None
        }

    def from_dict(self, data: Dict):
        last_time = data.get("last_chat_time")
        if last_time:
            self.last_chat_time = datetime.fromisoformat(last_time)
