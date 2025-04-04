"""
话题管理器模块
负责管理游戏中的话题系统，包括话题分类、糖豆系统等
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger("TopicManager")

class TopicManager:
    def __init__(self):
        """初始化话题管理器"""
        self._init_topic_data()
        self.last_topic = None
        self.topic_duration = 0
        self.active_topics = []
        self.topic_history = {}
        self.topic_continuity = 0
        self.current_affection = 30  # 初始化好感度
        self.interest_topics = []  # 添加兴趣话题列表
        
    def _init_topic_data(self):
        """初始化话题相关数据"""
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
        """获取当前好感度下可用的话题"""
        available_topics = []
        for category, data in self.available_topics.items():
            if affection >= data["threshold"]:
                available_topics.extend(data["topics"])
        return available_topics
        
    def is_sugar_bean_topic(self, topic: str) -> bool:
        """检查是否是糖豆话题"""
        return topic in self.sugar_bean_topics
        
    def should_show_sugar_bean(self) -> bool:
        """检查是否应该显示糖豆"""
        import random
        return random.random() < self.sugar_bean_appearance_rate
        
    def get_next_tip(self) -> str:
        """获取下一个提示"""
        self.last_tip_index = (self.last_tip_index + 1) % len(self.dating_tips)
        return self.dating_tips[self.last_tip_index]
        
    def update_topic_duration(self, topic: str) -> None:
        """更新话题持续时间"""
        if topic == self.last_topic:
            self.topic_duration += 1
        else:
            self.last_topic = topic
            self.topic_duration = 1
            
    def get_topic_duration(self) -> int:
        """获取当前话题持续时间"""
        return self.topic_duration 

    def get_interest_topics(self) -> List[str]:
        """获取当前兴趣话题"""
        return self.interest_topics
    
    def update_affection(self, value: int):
        """更新好感度值，用于与亲密度系统同步"""
        self.current_affection = value
        # 根据好感度调整可用话题
        if value >= 80 and "恋爱" not in self.available_topics:
            self.available_topics.append("恋爱")
        elif value >= 60 and "个人秘密" not in self.available_topics:
            self.available_topics.append("个人秘密") 