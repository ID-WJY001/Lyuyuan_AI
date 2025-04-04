"""
剧情管理器模块
负责管理游戏中的剧情系统，包括剧情触发、剧情状态等
"""

import logging
import random
from typing import Dict, Set, Optional, List

logger = logging.getLogger("StorylineManager")

class StorylineManager:
    def __init__(self):
        """初始化剧情管理器"""
        self.triggered_storylines = set()
        self.current_storyline = None
        self.storyline_progress = {}
        self.current_affection = 30  # 初始好感度
        self._init_storyline_data()
        
    def _init_storyline_data(self):
        """初始化剧情相关数据"""
        self.storyline_triggers = {
            30: "初始阶段",
            45: "渐渐熟悉",
            60: "成为朋友",
            75: "关系深入",
            90: "亲密关系",
            100: "甜蜜告白",
        }
        self.debug_mode = False
        
    def check_storyline_triggers(self, affection: float) -> Optional[str]:
        """检查是否触发新的剧情"""
        for threshold, storyline in self.storyline_triggers.items():
            if affection >= threshold and storyline not in self.triggered_storylines:
                self.triggered_storylines.add(storyline)
                return storyline
        return None
        
    def is_storyline_triggered(self, storyline: str) -> bool:
        """检查剧情是否已触发"""
        return storyline in self.triggered_storylines
        
    def get_all_triggered_storylines(self) -> List[str]:
        """获取所有已触发的剧情"""
        return list(self.triggered_storylines)
        
    def toggle_debug_mode(self) -> str:
        """切换调试模式"""
        self.debug_mode = not self.debug_mode
        return f"调试模式已{'开启' if self.debug_mode else '关闭'}"
        
    def is_debug_mode(self) -> bool:
        """检查是否处于调试模式"""
        return self.debug_mode
        
    def update_affection(self, value: int):
        """更新好感度值，用于与亲密度系统同步"""
        self.current_affection = value
        
        # 根据好感度可能触发特定剧情
        if value >= 80 and "告白" not in self.triggered_storylines:
            self.triggered_storylines.add("告白")
        elif value >= 60 and "约会" not in self.triggered_storylines and random.random() < 0.3:
            self.triggered_storylines.add("约会")
            
        # 检查并触发新的可用剧情
        self._check_new_storylines()
        
    def _check_new_storylines(self):
        """检查并触发新的剧情"""
        # 根据当前好感度检查是否有新剧情可以触发
        for threshold, storyline in self.storyline_triggers.items():
            if self.current_affection >= threshold and storyline not in self.triggered_storylines:
                self.triggered_storylines.add(storyline)
                logger.info(f"触发新剧情: {storyline}")
                # 如果需要可以在这里添加更多的剧情触发逻辑 