"""
游戏管理器模块
负责统一管理游戏的各个子系统和状态
"""

import yaml
import os
import sys
import logging
from typing import Dict, List, Optional
import json
import random
from datetime import datetime, timedelta
import re

# 获取项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

# 添加项目根目录到sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# 尝试导入核心组件，如果不存在则使用相对路径
try:
    from core import AffectionSystem, AffectionEvent, SocialRisk
    from core import NaturalLanguageProcessor
    from core.character import CharacterFactory
    from core.achievement import AchievementSystem
    from core.dialogue import DialogueSystem
except ImportError:
    from Character_Factory import CharacterFactory
    from achievement_system import AchievementSystem
    from game.dialogue_system import DialogueSystem
    from core import AffectionSystem, AffectionEvent, SocialRisk
    from core import NaturalLanguageProcessor

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
        
        # 确保数据文件的绝对路径
        config_path = os.path.join(ROOT_DIR, "config/character.yaml")
        keyword_path = os.path.join(ROOT_DIR, "data/keyword_groups.json")
        
        # 加载配置和初始化必要的组件
        self.char_config = load_config(config_path)
        self.nlp_processor = NaturalLanguageProcessor(keyword_path)
        
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
        
        # 强制设置角色初始好感度为30
        if hasattr(self.agent, 'game_state'):
            self.agent.game_state["closeness"] = 30
            self.agent.game_state["relationship_state"] = "初始阶段"
        
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
        
    def chat(self, user_input: str, dialogue_history_size: int = 100) -> str:
        """处理用户聊天输入，返回角色回复
        
        这个方法是为web界面特别添加的，调用agent的chat方法进行对话处理
        
        Args:
            user_input: 用户输入的文本
            dialogue_history_size: 保留的对话历史消息数量上限，默认100条
            
        Returns:
            角色的回复文本
        """
        # 记录旧的好感度值，用于后续比较
        old_closeness = self.game_state["closeness"]
        
        # 检查角色智能体是否正常初始化
        if not hasattr(self.agent, 'dialogue_history') or not isinstance(self.agent.dialogue_history, list):
            logger.error("发现对话历史格式异常，重新初始化对话历史")
            # 重新初始化对话历史为列表
            self.agent.dialogue_history = []
            # 添加默认系统消息
            if hasattr(self.agent, '_init_new_game'):
                self.agent._init_new_game(False)
            
        # 直接调用角色智能体的chat方法处理对话
        try:
            # 如果智能体支持设置对话历史大小的参数
            if hasattr(self.agent, 'set_dialogue_history_size'):
                self.agent.set_dialogue_history_size(dialogue_history_size)
                
            response = self.agent.chat(user_input)
        except AttributeError as e:
            # 如果出现属性错误，可能是对话历史出现问题
            logger.error(f"聊天处理时出现错误: {str(e)}")
            # 尝试修复对话历史
            if hasattr(self.agent, 'dialogue_history') and not isinstance(self.agent.dialogue_history, list):
                self.agent.dialogue_history = []
                # 添加默认系统消息
                if hasattr(self.agent, '_init_new_game'):
                    self.agent._init_new_game(False)
                    
            # 使用备用方法获取响应
            if hasattr(self.agent, '_get_backup_reply'):
                response = self.agent._get_backup_reply()
            else:
                response = "抱歉，系统出现了一点小问题，请稍后再试。"
        
        # 从角色智能体同步好感度到游戏状态
        # 注意：Su_Tang.py中的chat方法会在内部更新好感度值
        if "closeness" in self.agent.game_state:
            new_closeness = self.agent.game_state["closeness"]
            
            # 如果好感度发生了变化，更新并记录
            if new_closeness != old_closeness:
                logger.info(f"好感度变化: {old_closeness} -> {new_closeness}")
                self.game_state["last_affection"] = old_closeness
                self.game_state["closeness"] = new_closeness
                
                # 更新其它系统的好感度
                self.sync_affection_values()
                
                # 同步关系状态到游戏状态
                if "relationship_state" in self.agent.game_state:
                    self.game_state["relationship_state"] = self.agent.game_state["relationship_state"]
                    logger.info(f"关系状态已更新为: {self.game_state['relationship_state']}")
        
        return response
        
    def save(self, slot: int = 1) -> bool:
        """保存游戏，用于web接口兼容
        
        Args:
            slot: 存档槽位
            
        Returns:
            是否保存成功
        """
        try:
            # 确保必要的游戏状态更新
            self.agent.game_state["date"] = self.agent.game_state.get("date", "")
            self.agent.game_state["time_period"] = self.agent.game_state.get("time_period", "")
            self.agent.game_state["scene"] = self.agent.game_state.get("scene", "")
            
            # 同步好感度到代理状态
            self.agent.game_state["closeness"] = self.game_state["closeness"]
            
            # 保存游戏
            return self.agent.save(slot)
        except Exception as e:
            logger.error(f"保存游戏失败: {e}")
            return False
            
    def load(self, slot: int = 1) -> bool:
        """加载游戏，用于web接口兼容
        
        Args:
            slot: 存档槽位
            
        Returns:
            是否加载成功
        """
        try:
            # 加载游戏
            result = self.agent.load(slot)
            if result:
                # 同步好感度从代理状态
                self.game_state["closeness"] = self.agent.game_state.get("closeness", 30)
                # 确保好感度同步到亲密度系统
                self.sync_affection_values()
            return result
        except Exception as e:
            logger.error(f"加载游戏失败: {e}")
            return False

    def reset_game(self):
        """重置游戏状态为初始状态"""
        logger.info("重置游戏状态...")
        
        # 重置游戏状态
        self.game_state = self._init_game_state()
        
        # 重置角色状态
        self.character_states = self._init_character_states()
        
        # 如果角色代理存在，重置其状态
        if hasattr(self, 'agent') and self.agent:
            # 重新初始化角色代理
            self.agent = self.character_factory.get_character(self.active_character_id, is_new_game=True)
            
            # 确保角色好感度重置为30
            if hasattr(self.agent, 'game_state'):
                self.agent.game_state["closeness"] = 30
                self.agent.game_state["relationship_state"] = "初始阶段"
        
        # 同步重置后的好感度到所有系统
        self.sync_affection_values()
        
        logger.info("游戏状态已重置")
        return True 