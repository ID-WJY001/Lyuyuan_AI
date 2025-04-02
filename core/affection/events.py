from enum import Enum

class AffectionEvent(Enum):
    NORMAL_DIALOGUE = 1      # 普通对话
    SHARED_INTEREST = 2      # 兴趣共鸣
    DATE_ACCEPTED = 3        # 成功邀约
    CONFESSION = 4           # 玩家表白
    TABOO_TOPIC = 5          # 触犯禁忌
    BORING_TALK = 6          # 无聊对话
    RUDE_BEHAVIOR = 7        # 粗鲁行为
    INAPPROPRIATE = 8        # 不得体言论

class SocialRisk:
    """社交风险评估"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Phase:
    def __init__(self, threshold, name):
        self.threshold = threshold
        self.name = name
        
    def __repr__(self):
        return f"Phase({self.name}, {self.threshold})" 