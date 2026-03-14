"""记忆卡片系统 - 让 AI 记住玩家的重要信息"""
from typing import Dict, List, Optional
from datetime import datetime
import json


class MemoryCard:
    """单条记忆"""
    def __init__(self, content: str, category: str, importance: int = 1):
        self.content = content
        self.category = category  # player_info, shared_moment, promise, preference
        self.importance = importance  # 1-5
        self.created_at = datetime.now().isoformat()
        self.last_mentioned = self.created_at
        self.mention_count = 0

    def to_dict(self):
        return {
            "content": self.content,
            "category": self.category,
            "importance": self.importance,
            "created_at": self.created_at,
            "last_mentioned": self.last_mentioned,
            "mention_count": self.mention_count
        }

    @staticmethod
    def from_dict(data):
        card = MemoryCard(data["content"], data["category"], data["importance"])
        card.created_at = data.get("created_at", card.created_at)
        card.last_mentioned = data.get("last_mentioned", card.last_mentioned)
        card.mention_count = data.get("mention_count", 0)
        return card


class MemorySystem:
    """记忆管理系统"""
    def __init__(self):
        self.memories: List[MemoryCard] = []

    def add_memory(self, content: str, category: str, importance: int = 1):
        """添加新记忆"""
        # 避免重复
        if any(m.content == content for m in self.memories):
            return
        self.memories.append(MemoryCard(content, category, importance))
        # 保持最多 50 条记忆
        if len(self.memories) > 50:
            self.memories.sort(key=lambda m: m.importance * m.mention_count, reverse=True)
            self.memories = self.memories[:50]

    def get_relevant_memories(self, context: str = "", top_k: int = 5) -> List[str]:
        """获取相关记忆（简单版：返回最重要的）"""
        sorted_memories = sorted(
            self.memories,
            key=lambda m: m.importance * (m.mention_count + 1),
            reverse=True
        )
        return [m.content for m in sorted_memories[:top_k]]

    def mark_mentioned(self, content: str):
        """标记某条记忆被提及"""
        for m in self.memories:
            if content in m.content or m.content in content:
                m.last_mentioned = datetime.now().isoformat()
                m.mention_count += 1

    def to_dict(self):
        return {"memories": [m.to_dict() for m in self.memories]}

    def from_dict(self, data: Dict):
        self.memories = [MemoryCard.from_dict(m) for m in data.get("memories", [])]
