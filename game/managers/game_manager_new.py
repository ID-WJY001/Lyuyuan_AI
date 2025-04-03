"""
游戏管理器模块
负责统一管理游戏的各个子系统和状态
"""

import yaml
import os
import logging
from typing import Dict, List, Optional

# 尝试导入核心组件，如果不存在则使用相对路径
try:
    from core.affection import AffectionSystem, AffectionEvent, SocialRisk
    from core.nlp_engine import NaturalLanguageProcessor
    from core.character import CharacterFactory
    from core.achievement import AchievementSystem
    from core.dialogue import DialogueSystem
except ImportError:
    from Character_Factory import CharacterFactory
    from achievement_system import AchievementSystem
    from game.dialogue_system import DialogueSystem
    from core.affection import AffectionSystem, AffectionEvent, SocialRisk
    from core.nlp_engine import NaturalLanguageProcessor

from .scene_manager import SceneManager
from .topic_manager import TopicManager
from .storyline_manager import StorylineManager

# 设置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GameManager")

def load_config(path: str) -> Dict:
    """加载配置文件"""
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class GameManager:
    """游戏管理器类，负责协调各个子系统"""
    
    def __init__(self):
        """初始化游戏管理器及所有子系统"""
        logger.info("初始化游戏管理器...")
        
        # 加载配置和初始化必要的组件
        self.char_config = load_config("config/character.yaml")
        self.nlp_processor = NaturalLanguageProcessor("data/keyword_groups.json")
        
        # 初始化各个管理器
        self.scene_manager = SceneManager()
        self.topic_manager = TopicManager()
        self.storyline_manager = StorylineManager()
        
        # 初始化亲密度系统
        self.affection = AffectionSystem(self.nlp_processor)
        
        # 初始化角色工厂
        self.character_factory = CharacterFactory()
        self.active_character_id = "su_tang"  # 默认角色为苏糖
        self.agent = self.character_factory.get_character(self.active_character_id, is_new_game=True)
        
        # 初始化成就系统
        self.achievement_system = AchievementSystem()
        
        # 初始化对话系统
        self.dialogue_system = DialogueSystem(self)
        
        # 初始化游戏状态
        self.game_state = self._init_game_state()
        
        # 角色状态跟踪（用于多角色系统）
        self.character_states = self._init_character_states()
        
        # 注册所有相关系统到亲密度管理器
        self._register_affection_systems()
        
        # 同步初始好感度到所有系统
        self.sync_affection_values()
        
        logger.info("游戏管理器初始化完成")
        
    def _init_game_state(self) -> Dict:
        """初始化游戏状态"""
        return {
            "closeness": 30,  # 初始好感度
            "red_flags": 0,  # 红旗警告计数
            "last_affection": 30,  # 上一次的好感度
            "consecutive_negative": 0,  # 连续负面对话计数
            "consecutive_positive": 0,  # 连续正面对话计数
            "conversation_count": 0,  # 对话计数
            "pending_scene_change": None,  # 待处理的场景转换
            "scene_change_delay": 0,  # 场景转换延迟计数器
            "significant_events": [],  # 重要事件记录
            "encountered_characters": ["su_tang"]  # 已遇到的角色
        }
        
    def _init_character_states(self) -> Dict:
        """初始化角色状态"""
        return {
            "su_tang": {
                "affection": 30,
                "relationship_stage": "初始阶段",
                "conversation_history": [],
                "significant_events": []
            }
        }
        
    def _register_affection_systems(self):
        """注册所有相关系统到亲密度管理器"""
        self.affection.register_system(self.scene_manager)
        self.affection.register_system(self.topic_manager)
        self.affection.register_system(self.storyline_manager)
        
    def sync_affection_values(self):
        """同步好感度到所有系统"""
        current_affection = self.game_state["closeness"]
        self.character_states["su_tang"]["affection"] = current_affection
        self.affection.update_value(current_affection)
        
    def process_dialogue(self, user_input: str, dialogue_history: List[str]) -> str:
        """处理用户对话"""
        return self.dialogue_system.process_dialogue(user_input, dialogue_history)
        
    def handle_player_action(self, action: str) -> str:
        """处理玩家动作"""
        # 检查场景切换
        if self.scene_manager.is_farewell_keyword(action):
            return self._handle_scene_change(action)
            
        # 更新话题持续时间
        self.topic_manager.update_topic_duration(action)
        
        # 处理对话
        return self.process_dialogue(action, self.agent.dialogue_history)
        
    def _handle_scene_change(self, action: str) -> str:
        """处理场景切换"""
        # 获取可能的场景转换提示
        hints = self.scene_manager.get_scene_transition_hints(action)
        if hints:
            return f"你想去{', '.join(hints)}中的哪个地方？"
        return "你想去哪里？"
        
    def show_ending(self, description: str):
        """显示结局"""
        print(f"\n{description}")
        
    def show_social_status(self) -> str:
        """显示社交状态"""
        status = []
        status.append(f"当前场景：{self.scene_manager.current_scene}")
        status.append(f"当前好感度：{self.game_state['closeness']}")
        status.append(f"关系阶段：{self.character_states['su_tang']['relationship_stage']}")
        status.append(f"已触发剧情：{', '.join(self.storyline_manager.get_all_triggered_storylines())}")
        return "\n".join(status)
        
    def view_dialogue_history(self, save_slot: str = "auto", limit: int = 10) -> List[str]:
        """查看对话历史"""
        return self.agent.get_dialogue_history(save_slot, limit) 