"""
Manager模块汇总
"""

# 导入所有管理器类
from .game_manager_new import GameManager
from .scene_manager import SceneManager
from .topic_manager import TopicManager
from .storyline_manager import StorylineManager

__all__ = ["GameManager", "SceneManager", "TopicManager", "StorylineManager"] 