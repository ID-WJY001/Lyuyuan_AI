"""
游戏管理器兼容层
为了保持向后兼容性，重定向到新的GameManager实现
"""

import sys
import os
import logging

# 设置项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

# 导入新版GameManager
try:
    from game.managers.game_manager_new import GameManager as NewGameManager
    
    # 为了向后兼容，创建一个包装类
    class GameManager(NewGameManager):
        """
        游戏管理器包装类
        提供向后兼容的接口，实际使用新版GameManager的实现
        """
        def __init__(self, *args, **kwargs):
            """初始化，直接调用新版GameManager的初始化"""
            super().__init__(*args, **kwargs)
            logging.getLogger("GameManager").info("使用新版GameManager实现")
            
except ImportError as e:
    logging.error(f"导入新版GameManager失败: {e}")
    # 如果导入失败，保留旧的实现（但这种情况应该不会发生）
    from core import AffectionSystem, AffectionEvent, SocialRisk
    from core import NaturalLanguageProcessor
    from core import SceneManager
    from Character_Factory import CharacterFactory
    from achievement_system import AchievementSystem
    from game.affection_manager import AffectionManager
    from game.dialogue_system import DialogueSystem
    
    # 这里应该放旧版的GameManager实现，但实际上应该永远不会执行到这里
    # 因为新版GameManager应该始终可用
    
    class GameManager:
        """旧版GameManager，仅在导入新版失败时使用"""
        def __init__(self):
            logging.error("使用旧版GameManager实现（不应该发生）")
            # 旧版初始化代码... 