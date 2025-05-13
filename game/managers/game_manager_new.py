"""
游戏核心管理器模块 (`GameManager`)。

`GameManager` 类是整个游戏的中央协调器，负责管理和调度游戏中所有的主要子系统，
包括角色、场景、对话、剧情、好感度、成就等。
它处理玩家的输入，更新游戏状态，并根据游戏逻辑触发事件和结局。
该管理器也提供了与外部接口（如Web服务）交互的方法。
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
    """
    从指定的 YAML 文件路径加载配置数据。

    Args:
        path (str): YAML 配置文件的路径。

    Returns:
        Dict: 从 YAML 文件中加载的配置数据字典。
    """
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class GameManager:
    """游戏管理器类，负责协调各个子系统"""
    
    def __init__(self):
        """
        初始化 GameManager 及其所有核心子系统。
        
        这个过程包括：
        1. 加载角色和关键词等基础配置。
        2. 初始化自然语言处理器 (NLP)。
        3. 初始化场景、话题和剧情管理器。
        4. 初始化好感度系统。
        5. 通过角色工厂创建并获取当前激活的角色代理 (agent)。
        6. 设置角色的初始好感度。
        7. 初始化成就系统和对话系统。
        8. 初始化全局游戏状态和特定角色的状态追踪。
        9. 注册相关子系统到好感度管理器，并同步初始好感度值。
        """
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
        """
        初始化并返回全局游戏状态字典。

        包含了游戏进行中的一些关键动态数据，例如：
        - `closeness`: 当前玩家与主要角色的好感度。
        - `red_flags`: 触发的负面行为警告计数。
        - `last_affection`: 上一次记录的好感度值。
        - `consecutive_negative`/`positive`: 连续负面/正面对话的次数。
        - `conversation_count`: 总对话次数。
        - `pending_scene_change`: 若有场景将要切换，记录目标场景名称。
        - `scene_change_delay`: 场景切换的延迟计数器。
        - `significant_events`: 游戏中发生的重要事件列表。
        - `encountered_characters`: 玩家已经遇到过的角色ID列表。

        Returns:
            Dict: 包含初始游戏状态的字典。
        """
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
        """
        初始化并返回特定角色状态的字典。
        
        主要用于多角色场景下追踪每个角色的独立状态，例如苏糖的：
        - `affection`: 与该角色的好感度。
        - `relationship_stage`: 当前的关系阶段。
        - `conversation_history`: 与该角色的对话历史概要。
        - `significant_events`: 与该角色相关的特定重要事件。

        Returns:
            Dict: 包含各角色初始状态的字典。
        """
        return {
            "su_tang": {
                "affection": 30,
                "relationship_stage": "初始阶段",
                "conversation_history": [],
                "significant_events": []
            }
        }
        
    def _register_affection_systems(self):
        """
        将需要与好感度系统交互的子系统（如场景、话题、剧情管理器）
        注册到 `AffectionSystem` 实例中。
        这样好感度系统可以在其内部逻辑中调用这些子系统的方法或获取其状态。
        """
        self.affection.register_system(self.scene_manager)
        self.affection.register_system(self.topic_manager)
        self.affection.register_system(self.storyline_manager)
        
    def sync_affection_values(self):
        """
        同步当前的游戏好感度值到所有相关的系统和状态中。
        
        确保 `game_state['closeness']`, `character_states['su_tang']['affection']`,
        以及 `AffectionSystem` 内部的好感度值保持一致。
        """
        current_affection = self.game_state["closeness"]
        self.character_states["su_tang"]["affection"] = current_affection
        self.affection.update_value(current_affection)
        
    def process_dialogue(self, user_input: str, dialogue_history: List[str]) -> str:
        """
        处理用户的对话输入，并返回角色（AI）的回复。

        这个方法是对话交互的核心，它将用户的输入和当前的对话历史
        传递给 `DialogueSystem` 进行处理，以生成角色的响应。

        Args:
            user_input (str): 用户输入的对话文本。
            dialogue_history (List[str]): 当前的对话历史记录。

        Returns:
            str: 角色生成的回复文本。
        """
        return self.dialogue_system.process_dialogue(user_input, dialogue_history)
        
    def handle_player_action(self, action: str) -> str:
        """
        处理玩家的通用行为或输入。

        此方法首先检查输入是否为场景切换的关键词（如告别语）。
        如果是，则调用 `_handle_scene_change` 处理场景切换的逻辑。
        否则，它会更新当前话题的持续时间，并调用 `process_dialogue`
        来处理常规的对话交互。

        Args:
            action (str): 玩家输入的行为或对话文本。

        Returns:
            str: 根据行为类型返回相应的响应（可能是场景切换提示或对话回复）。
        """
        # 检查场景切换
        if self.scene_manager.is_farewell_keyword(action):
            return self._handle_scene_change(action)
            
        # 更新话题持续时间
        self.topic_manager.update_topic_duration(action)
        
        # 处理对话
        return self.process_dialogue(action, self.agent.dialogue_history)
        
    def _handle_scene_change(self, action: str) -> str:
        """
        处理与场景切换相关的逻辑。

        当玩家的输入暗示了离开当前场景的意图时调用此方法。
        它会向 `SceneManager` 查询可能的场景转换提示。

        Args:
            action (str): 玩家触发场景切换的输入文本。

        Returns:
            str: 提示玩家选择下一个想去的场景，或者通用的去向询问。
        """
        # 获取可能的场景转换提示
        hints = self.scene_manager.get_scene_transition_hints(action)
        if hints:
            return f"你想去{', '.join(hints)}中的哪个地方？"
        return "你想去哪里？"
        
    def show_ending(self, description: str):
        """
        在游戏达到某个结局条件时，向玩家显示结局描述。

        Args:
            description (str): 结局的文本描述。
        """
        print(f"\n{description}")
        
    def show_social_status(self) -> str:
        """
        生成并返回当前玩家的社交状态信息字符串。

        包括：
        - 当前所在场景。
        - 与主要角色的好感度。
        - 当前的关系阶段。
        - 已经触发的剧情线。

        Returns:
            str: 格式化后的社交状态信息。
        """
        status = []
        status.append(f"当前场景：{self.scene_manager.current_scene}")
        status.append(f"当前好感度：{self.game_state['closeness']}")
        status.append(f"关系阶段：{self.character_states['su_tang']['relationship_stage']}")
        status.append(f"已触发剧情：{', '.join(self.storyline_manager.get_all_triggered_storylines())}")
        return "\n".join(status)
        
    def view_dialogue_history(self, save_slot: str = "auto", limit: int = 10) -> List[str]:
        """
        获取并返回指定存档槽位的对话历史记录。

        此方法实际上调用的是角色代理 (`self.agent`) 上的相应方法。

        Args:
            save_slot (str, optional): 存档槽位的名称。默认为 "auto"。
            limit (int, optional): 要获取的最近对话条数。默认为 10。

        Returns:
            List[str]: 对话历史记录列表。
        """
        return self.agent.get_dialogue_history(save_slot, limit)
        
    def chat(self, user_input: str, dialogue_history_size: int = 100) -> str:
        """
        处理用户聊天输入，主要为Web界面或其他外部接口设计。

        此方法直接调用角色代理 (`self.agent`) 的 `chat` 方法来获取回复。
        它负责在调用前后进行状态同步，特别是好感度和关系阶段，
        并包含对角色代理对话历史异常的检查和修复尝试。

        Args:
            user_input (str): 用户输入的文本。
            dialogue_history_size (int, optional): 传递给角色代理的对话历史保留上限。默认为 100。

        Returns:
            str: 角色的回复文本。如果处理失败，则返回预设的错误提示。
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
        """
        保存当前游戏状态到指定的存档槽位。

        此方法主要为与Web界面等外部接口的兼容性而设计。
        它会确保在调用角色代理的 `save` 方法前，一些关键状态
        （如日期、时间、场景、好感度）已从 `GameManager` 同步到角色代理的 `game_state` 中。

        Args:
            slot (int or str, optional): 存档槽位的标识符。默认为 1。

        Returns:
            bool: 如果保存成功则返回 True，否则返回 False。
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
        """
        从指定的存档槽位加载游戏状态。

        此方法主要为与Web界面等外部接口的兼容性而设计。
        它调用角色代理的 `load` 方法来执行实际的加载操作。
        加载成功后，会将角色代理中的好感度同步回 `GameManager` 的 `game_state`，
        并更新所有相关的子系统。

        Args:
            slot (int or str, optional): 存档槽位的标识符。默认为 1。

        Returns:
            bool: 如果加载成功则返回 True，否则返回 False。
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
        """
        重置整个游戏到其初始状态。

        这包括：
        - 重新初始化 `GameManager` 的 `game_state` 和 `character_states`。
        - 重新通过 `CharacterFactory` 创建角色代理实例，相当于开始一个全新的游戏会话。
        - 将新创建的角色代理的初始好感度强制设为预设值 (例如30)。
        - 同步这个初始好感度到所有相关的子系统。

        Returns:
            bool: 通常返回 True，表示重置操作已执行。
        """
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