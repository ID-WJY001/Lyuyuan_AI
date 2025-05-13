"""
剧情管理器模块
负责管理和追踪游戏中的各个剧情线（Storylines）。
它根据好感度等条件判断剧情的触发，记录已触发的剧情，
并提供查询剧情状态的接口。也包含一个简单的调试模式开关。
"""

import logging
import random
from typing import Dict, Set, Optional, List

logger = logging.getLogger("StorylineManager")

class StorylineManager:
    def __init__(self):
        """
        初始化剧情管理器。
        
        设置已触发剧情线的集合、当前剧情线（暂未使用）、剧情进展（暂未使用）、
        当前好感度的内部记录，并调用 `_init_storyline_data` 初始化剧情触发规则。
        """
        self.triggered_storylines = set()
        self.current_storyline = None
        self.storyline_progress = {}
        self.current_affection = 30  # 初始好感度
        self._init_storyline_data()
        
    def _init_storyline_data(self):
        """
        初始化剧情相关的核心数据。
        
        主要定义了 `storyline_triggers` 字典，该字典将好感度阈值映射到特定的剧情线名称。
        当玩家与角色的好感度达到或超过某个阈值时，对应的剧情线将被视为可触发。
        同时初始化调试模式为关闭。
        """
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
        """
        根据当前的好感度检查是否有新的剧情线被触发。

        遍历 `storyline_triggers` 中定义的剧情线及其触发阈值。
        如果当前好感度达到某个剧情线的阈值，并且该剧情线尚未被触发过，
        则将该剧情线标记为已触发，并返回其名称。

        Args:
            affection (float): 当前的好感度值。

        Returns:
            Optional[str]: 如果有新的剧情线被触发，则返回该剧情线的名称字符串；
                           否则返回 None。
        """
        for threshold, storyline in self.storyline_triggers.items():
            if affection >= threshold and storyline not in self.triggered_storylines:
                self.triggered_storylines.add(storyline)
                return storyline
        return None
        
    def is_storyline_triggered(self, storyline: str) -> bool:
        """
        检查指定的剧情线名称是否已经被触发过。

        Args:
            storyline (str): 需要查询的剧情线名称。

        Returns:
            bool: 如果剧情线已触发，则返回 True；否则返回 False。
        """
        return storyline in self.triggered_storylines
        
    def get_all_triggered_storylines(self) -> List[str]:
        """
        获取当前所有已经被触发的剧情线的列表。

        Returns:
            List[str]: 一个包含所有已触发剧情线名称的列表。
        """
        return list(self.triggered_storylines)
        
    def toggle_debug_mode(self) -> str:
        """
        切换剧情管理器的调试模式状态（开启/关闭）。

        Returns:
            str: 返回一条表示调试模式当前状态的消息。
        """
        self.debug_mode = not self.debug_mode
        return f"调试模式已{'开启' if self.debug_mode else '关闭'}"
        
    def is_debug_mode(self) -> bool:
        """
        检查当前剧情管理器是否处于调试模式。

        Returns:
            bool: 如果调试模式为开启，则返回 True；否则返回 False。
        """
        return self.debug_mode
        
    def update_affection(self, value: int):
        """
        更新剧情管理器内部记录的好感度值，并根据此值检查和触发剧情。

        此方法首先更新内部的 `current_affection`。
        然后，它包含一些特殊的、硬编码的剧情触发逻辑（例如"告白"和"约会"）。
        最后，调用 `_check_new_storylines` 来处理基于 `storyline_triggers` 的常规剧情触发。

        Args:
            value (int): 新的好感度值。
        """
        self.current_affection = value
        
        # 根据好感度可能触发特定剧情
        if value >= 80 and "告白" not in self.triggered_storylines:
            self.triggered_storylines.add("告白")
        elif value >= 60 and "约会" not in self.triggered_storylines and random.random() < 0.3:
            self.triggered_storylines.add("约会")
            
        # 检查并触发新的可用剧情
        self._check_new_storylines()
        
    def _check_new_storylines(self):
        """
        内部方法，用于检查并触发新的常规剧情线。
        
        基于当前 `self.current_affection` 和 `self.storyline_triggers` 中的定义，
        将所有达到触发条件且尚未被触发的剧情线标记为已触发，并记录日志。
        未来可在此处扩展更复杂的剧情触发逻辑。
        """
        # 根据当前好感度检查是否有新剧情可以触发
        for threshold, storyline in self.storyline_triggers.items():
            if self.current_affection >= threshold and storyline not in self.triggered_storylines:
                self.triggered_storylines.add(storyline)
                logger.info(f"触发新剧情: {storyline}")
                # 如果需要可以在这里添加更多的剧情触发逻辑 