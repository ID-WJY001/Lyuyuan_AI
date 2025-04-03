"""
剧情管理器模块
负责管理游戏中的剧情系统，包括剧情触发、剧情状态等
"""

import logging
from typing import Dict, Set, Optional

logger = logging.getLogger("StorylineManager")

class StorylineManager:
    def __init__(self):
        """初始化剧情管理器"""
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
        self.triggered_storylines = set()
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
        
    def get_all_triggered_storylines(self) -> Set[str]:
        """获取所有已触发的剧情"""
        return self.triggered_storylines.copy()
        
    def toggle_debug_mode(self) -> str:
        """切换调试模式"""
        self.debug_mode = not self.debug_mode
        return f"调试模式已{'开启' if self.debug_mode else '关闭'}"
        
    def is_debug_mode(self) -> bool:
        """检查是否处于调试模式"""
        return self.debug_mode 