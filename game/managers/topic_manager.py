"""
话题管理器模块
负责管理游戏中的话题系统，包括话题分类、糖豆系统等
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger("TopicManager")

class TopicManager:
    def __init__(self):
        """
        初始化话题管理器。
        
        调用 `_init_topic_data` 初始化所有话题相关的数据结构和默认值，
        包括可用话题、兴趣话题、糖豆系统参数和恋爱技巧提示。
        同时初始化当前话题、持续时间、历史、连续性和好感度等内部状态。
        """
        self._init_topic_data()
        self.last_topic = None
        self.topic_duration = 0
        self.active_topics = []
        self.topic_history = {}
        self.topic_continuity = 0
        self.current_affection = 30  # 初始化好感度
        self.interest_topics = []  # 添加兴趣话题列表
        
    def _init_topic_data(self):
        """
        初始化话题系统的核心数据。

        这包括：
        - `available_topics`: 一个字典，根据好感度阈值划分不同类别的话题列表。
        - `interest_topics`: 角色（苏糖）感兴趣的话题列表。
        - `sugar_bean_appearance_rate`: "糖豆"特殊事件的出现概率。
        - `sugar_bean_topics`: 与"糖豆"事件相关联的特定话题。
        - `dating_tips`: 提供给玩家的一系列恋爱技巧提示文本。
        """
        # 话题系统初始化
        self.available_topics = {
            "初始话题": {
                "threshold": 0,
                "topics": [
                    "烘焙社活动", "社团招新", "学校生活", "学习情况",
                    "兴趣爱好", "日常对话", "天气", "校园环境"
                ]
            },
            "熟悉话题": {
                "threshold": 40,
                "topics": [
                    "个人经历", "家庭情况", "未来规划", "音乐",
                    "电影", "书籍", "美食", "旅行"
                ]
            },
            "深入话题": {
                "threshold": 60,
                "topics": [
                    "人生理想", "价值观", "感情经历", "童年回忆",
                    "梦想", "烦恼", "压力", "快乐"
                ]
            },
            "亲密话题": {
                "threshold": 80,
                "topics": [
                    "感情", "未来", "理想生活", "共同规划",
                    "甜蜜回忆", "浪漫", "承诺", "期待"
                ]
            }
        }
        
        # 初始化兴趣话题
        self.interest_topics = ["烘焙", "甜点", "音乐", "阅读", "电影", "手工", "旅行"]
        
        # 糖豆相关
        self.sugar_bean_appearance_rate = 0.3
        self.sugar_bean_topics = [
            "烘焙社活动", "社团招新", "甜点制作", "烘焙技巧",
            "社团活动", "烘焙比赛", "社团展示"
        ]
        
        # 追女生技巧提示
        self.dating_tips = [
            "温馨提示: 保持对话的新鲜感和深度，避免重复和单调的对话",
            "温馨提示: 尊重对方，使用礼貌用语会提升她对你的好感",
            "温馨提示: 注意倾听并回应她的问题，不要自顾自地说话",
            "温馨提示: 过早表白可能会适得其反，需要足够的感情基础",
            "温馨提示: 与她分享共同兴趣可以快速拉近关系",
            "温馨提示: 连续的无聊对话会导致她失去兴趣",
            "温馨提示: 不当言论会严重损害关系，请保持绅士风度",
            "温馨提示: 游戏难度已提高，好感度更容易下降",
        ]
        self.last_tip_index = -1
        
    def get_available_topics(self, affection: float) -> List[str]:
        """
        根据当前的好感度值，获取所有当前可用的对话话题列表。

        遍历预定义的 `available_topics` 字典，将达到好感度阈值的话题类别
        中的所有话题收集起来并返回。

        Args:
            affection (float): 当前玩家与角色的好感度值。

        Returns:
            List[str]: 一个包含所有当前可用话题名称的列表。
        """
        available_topics = []
        for category, data in self.available_topics.items():
            if affection >= data["threshold"]:
                available_topics.extend(data["topics"])
        return available_topics
        
    def is_sugar_bean_topic(self, topic: str) -> bool:
        """
        检查给定的话题是否属于"糖豆"相关话题。

        Args:
            topic (str): 需要检查的话题名称。

        Returns:
            bool: 如果是"糖豆"话题则返回 True，否则返回 False。
        """
        return topic in self.sugar_bean_topics
        
    def should_show_sugar_bean(self) -> bool:
        """
        根据预设的出现概率，随机判断是否应该触发并显示"糖豆"事件。

        Returns:
            bool: 如果判断结果为是，则返回 True，否则返回 False。
        """
        import random
        return random.random() < self.sugar_bean_appearance_rate
        
    def get_next_tip(self) -> str:
        """
        获取并返回下一条"恋爱技巧"提示。
        
        提示会从预设的 `dating_tips` 列表中循环获取。

        Returns:
            str: 下一条提示的文本内容。
        """
        self.last_tip_index = (self.last_tip_index + 1) % len(self.dating_tips)
        return self.dating_tips[self.last_tip_index]
        
    def update_topic_duration(self, topic: str) -> None:
        """
        更新当前讨论话题的持续时间计数。

        如果新指定的话题与上一个话题相同，则持续时间加1；
        如果话题已改变，则将新话题设为当前话题，并将持续时间重置为1。

        Args:
            topic (str): 当前正在讨论或新开始的话题名称。
        """
        if topic == self.last_topic:
            self.topic_duration += 1
        else:
            self.last_topic = topic
            self.topic_duration = 1
            
    def get_topic_duration(self) -> int:
        """
        获取当前话题已经持续的对话轮数（或次数）。

        Returns:
            int: 当前话题的持续时间。
        """
        return self.topic_duration 

    def get_interest_topics(self) -> List[str]:
        """
        获取角色（苏糖）感兴趣的话题列表。

        Returns:
            List[str]: 一个包含角色兴趣话题名称的列表。
        """
        return self.interest_topics
    
    def update_affection(self, value: int):
        """
        更新话题管理器内部记录的好感度值，并尝试根据好感度调整可用话题。
        
        **注意**: 此方法中根据好感度动态添加"恋爱"或"个人秘密"到 `available_topics` 的
        逻辑存在问题，因为 `self.available_topics` 是一个字典，而代码使用了 `append`。
        这部分逻辑可能需要修正才能按预期工作。

        Args:
            value (int): 新的好感度值。
        """
        self.current_affection = value
        # 根据好感度调整可用话题
        if value >= 80 and "恋爱" not in self.available_topics:
            # 预期的行为可能是将"恋爱"话题添加到某个好感度区间的列表中，或者新增一个类别
            # 例如: self.available_topics.setdefault("亲密话题", {}).setdefault("topics", []).append("恋爱")
            # 或者直接修改特定阈值下的列表，但这取决于设计意图
            pass # 当前实现是错误的，暂时保留pass，待后续修正
        elif value >= 60 and "个人秘密" not in self.available_topics:
            pass # 当前实现是错误的，暂时保留pass，待后续修正 