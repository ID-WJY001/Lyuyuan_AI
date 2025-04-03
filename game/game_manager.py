"""
游戏管理器模块
负责统一管理游戏的各个子系统和状态
"""

import yaml
import os
import random
from datetime import datetime, timedelta
import logging

from core.affection import AffectionSystem, AffectionEvent, SocialRisk
from core.nlp_engine import NaturalLanguageProcessor
from core.scene_manager import SceneManager
from Character_Factory import CharacterFactory
from achievement_system import AchievementSystem
from game.affection_manager import AffectionManager
from game.dialogue_system import DialogueSystem

# 设置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GameManager")

def load_config(path: str):
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
        
        # 初始化亲密度管理器
        self.affection_manager = AffectionManager(initial_value=30.0)
        
        # 初始化亲密度系统
        self.affection = AffectionSystem(self.nlp_processor)
        
        # 初始化角色工厂
        self.character_factory = CharacterFactory()
        self.active_character_id = "su_tang"  # 默认角色为苏糖
        self.agent = self.character_factory.get_character(self.active_character_id, is_new_game=True)
        
        # 初始化场景管理器
        self.scene_manager = SceneManager()
        
        # 初始化成就系统
        self.achievement_system = AchievementSystem()
        
        # 初始化对话系统
        self.dialogue_system = DialogueSystem(self)
        
        # 时间系统初始化
        self.current_date = datetime(2021, 10, 15)
        self.current_time = "上午"
        self.time_periods = ["上午", "中午", "下午", "傍晚", "晚上"]
        self.time_period_index = 0
        
        # 场景相关
        self.current_scene = "烘焙社摊位"
        self._init_scene_data()
        
        # 剧情触发点
        self._init_storyline_data()
        
        # 初始化游戏状态
        self.game_state = self._init_game_state()
        
        # 角色状态跟踪（用于多角色系统）
        self.character_states = self._init_character_states()
        
        # 注册所有相关系统到亲密度管理器
        self._register_affection_systems()
        
        # 同步初始好感度到所有系统
        self.sync_affection_values()
        
        logger.info("游戏管理器初始化完成")

    def _init_scene_data(self):
        """初始化场景相关数据"""
        # 场景跳转相关
        self.next_scene_hints = []
        self.scene_transition_keywords = {
            "下周": ["教室", "操场", "图书馆", "烘焙社"],
            "明天": ["教室", "食堂", "操场", "烘焙社"],
            "放学后": ["操场", "图书馆", "街道", "烘焙社"],
            "周末": ["公园", "游乐场", "电影院", "咖啡厅"],
            "下次": ["教室", "操场", "图书馆", "公园", "烘焙社"],
            "再见面": ["教室", "操场", "街道", "公园", "烘焙社"],
            "社团活动": ["烘焙社"]
        }
        self.farewell_keywords = ["再见", "拜拜", "回头见", "下次见", "明天见", "下周见", "周末见", "回见", "下次再聊"]
        
        # 场景时间限制
        self.scene_time_restrictions = {
            "烘焙社摊位": ["上午", "中午", "下午"],
            "烘焙社": ["下午", "傍晚"],
            "教室": ["上午", "中午", "下午"],
            "操场": ["上午", "中午", "下午", "傍晚"],
            "图书馆": ["上午", "中午", "下午", "傍晚"],
            "公园": ["上午", "中午", "下午", "傍晚"],
            "食堂": ["中午"],
            "街道": ["下午", "傍晚", "晚上"],
            "游乐场": ["上午", "中午", "下午"],
            "电影院": ["下午", "傍晚", "晚上"],
            "咖啡厅": ["上午", "中午", "下午", "傍晚", "晚上"]
        }
        
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
        self.debug_mode = False  # 调试模式开关
        
    def _init_game_state(self):
        """初始化游戏状态"""
        return {
            "closeness": 30,  # 初始好感度
            "red_flags": 0,  # 红旗警告计数
            "last_affection": 30,  # 上一次的好感度
            "consecutive_negative": 0,  # 连续负面对话计数
            "consecutive_positive": 0,  # 连续正面对话计数
            "last_topic": None,  # 上一个话题
            "topic_duration": 0,  # 当前话题持续时间
            "last_scene_change": None,  # 上次场景切换时间
            "scene_change_cooldown": 3,  # 场景切换冷却时间
            "conversation_count": 0,  # 对话计数
            "pending_scene_change": None,  # 待处理的场景转换
            "scene_change_delay": 0,  # 场景转换延迟计数器
            "significant_events": [],  # 重要事件记录
            "encountered_characters": ["su_tang"]  # 已遇到的角色
        }
    
    def _init_character_states(self):
        """初始化角色状态"""
        return {
            "su_tang": {
                "closeness": 30,
                "last_interaction": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "scenes_visited": ["烘焙社摊位"],
                "significant_events": []
            }
        }
    
    def _register_affection_systems(self):
        """注册所有需要同步好感度的系统到亲密度管理器"""
        # 注册AffectionSystem
        self.affection_manager.register_system(
            system_name="affection_system",
            getter_method=lambda obj: obj.affection,
            setter_method=lambda obj, val: setattr(obj, "affection", float(val)),
            system_obj=self.affection
        )
        
        # 注册GameState
        self.affection_manager.register_system(
            system_name="game_state",
            getter_method=lambda obj: obj["closeness"],
            setter_method=lambda obj, val: obj.__setitem__("closeness", int(val)),
            system_obj=self.game_state
        )
        
        # 注册Agent
        self.affection_manager.register_system(
            system_name="agent",
            getter_method=lambda obj: obj.game_state.get("closeness", 0),
            setter_method=lambda obj, val: obj.game_state.__setitem__("closeness", int(val)),
            system_obj=self.agent
        )
        
        # 注册CharacterState
        self.affection_manager.register_system(
            system_name="character_state",
            getter_method=lambda obj: obj["su_tang"]["closeness"],
            setter_method=lambda obj, val: obj["su_tang"].__setitem__("closeness", int(val)),
            system_obj=self.character_states
        )
    
    def sync_affection_values(self):
        """
        同步所有系统中的好感度值，确保一致性
        该方法应该在每次好感度有可能变化后调用
        """
        # 获取当前的好感度值作为基准
        closeness = int(self.game_state["closeness"])
        
        # 使用亲密度管理器统一更新所有系统的值
        result = self.affection_manager.update_value(closeness, source="sync_method")
        
        # 记录日志
        if self.debug_mode:
            verification = self.affection_manager.verify_consistency()
            is_consistent = verification["consistent"]
            if not is_consistent:
                logger.warning(f"好感度不一致: {verification['system_values']}")
                # 强制同步
                self.affection_manager.force_sync()
            else:
                logger.debug(f"已同步好感度: {closeness}")
        
        return self.affection_manager.get_value()
    
    def process_dialogue(self, user_input, dialogue_history):
        """处理玩家输入并更新游戏状态"""
        return self.dialogue_system.process_dialogue(user_input, dialogue_history)
            
    def check_storyline_triggers(self, affection):
        """检查是否触发剧情推进"""
        message = None
        for threshold, storyline in self.storyline_triggers.items():
            if affection >= threshold and threshold not in self.triggered_storylines:
                self.triggered_storylines.add(threshold)
                message = f"【剧情推进：{storyline}】"
                
                # 当亲密度达到100时，触发苏糖表白
                if threshold == 100:
                    # 确保亲密度统一为100
                    self.affection_manager.update_value(100.0, source="storyline_max")
                    
                    # 通知亲密度系统处理告白事件
                    self.affection.handle_event(AffectionEvent.CONFESSION, is_player_initiated=False)
                    
                    message += "\n\n苏糖突然握住你的手，眼神中带着羞涩与期待...\n'我...我一直在等你来告白，但我等不及了...'\n她深吸一口气，脸颊泛红：'我喜欢你，想和你在一起...'"
                    self.show_ending("苏糖主动告白，甜蜜结局")
                break
        return message
            
    def handle_player_action(self, action):
        """处理玩家特殊行为，返回事件结果提示"""
        # 示例：玩家选择表白
        if action == AffectionEvent.CONFESSION:
            # 根据当前好感度决定表白的结果
            affection = self.affection_manager.get_value()
            if affection >= 95:
                # 高好感度：接受表白
                self.affection_manager.update_value(100.0, source="confession_success")
                result = self.show_ending("告白成功")
                self.affection.handle_event(AffectionEvent.CONFESSION, is_player_initiated=False)
                return result
            else:
                # 低好感度：拒绝表白
                # 根据当前好感度不同，产生不同程度的负面影响
                if affection < 70:
                    # 严重负面影响
                    result = self.affection.handle_event(
                        AffectionEvent.CONFESSION, 
                        is_player_initiated=True,
                        is_negative=True,
                        is_severe=True
                    )
                else:
                    # 轻微负面影响
                    result = self.affection.handle_event(
                        AffectionEvent.CONFESSION, 
                        is_player_initiated=True,
                        is_negative=True,
                        is_severe=False
                    )
            
                # 更新游戏状态中的亲密度
                if 'new_affection' in result:
                    self.affection_manager.update_value(result['new_affection'], source="confession_failed")
            
                if result.get("success"):
                    if result.get("ending") == "good_ending":
                        self.show_ending("两人在烟火大会定情")
                        return "❤️ 表白成功！两人关系更进一步~"
                    else:
                        return "❤️ 表白成功！关系提升！"
                else:
                    if self.affection.check_ending() == "bad_ending":
                        self.show_ending("关系彻底破裂")
                    return f"💔 被拒绝了：{result.get('message', '时机未到')}"
        
        # 共同兴趣
        elif action == AffectionEvent.SHARED_INTEREST:
            result = self.affection.handle_event(AffectionEvent.SHARED_INTEREST)
            
            # 更新游戏状态中的亲密度
            if 'new_value' in result:
                self.affection_manager.update_value(result['new_value'], source="shared_interest")
                
            return "💫 发现了共同话题！"
            
        # 无聊对话
        elif action == AffectionEvent.BORING_TALK:
            boring_count = self.affection.conversation_state.get("boring_count", 0)
            if boring_count >= 2:
                return "😒 她看起来对这个对话失去了兴趣..."
            else:
                return "😐 对话似乎有点无聊了..."
                
        # 粗鲁行为
        elif action == AffectionEvent.RUDE_BEHAVIOR:
            return "😠 你的行为让她感到不舒服"
            
        # 不当言论
        elif action == AffectionEvent.INAPPROPRIATE:
            return "😡 你的言论十分不当！"
             
        return None
            
    def show_ending(self, description):
        """显示游戏结局"""
        print(f"※※ 结局触发：{description} ※※")
        print("游戏结束，感谢您的游玩！")
        exit()
        
    def toggle_debug_mode(self):
        """切换调试模式"""
        self.debug_mode = not self.debug_mode
        # 同时切换亲密度系统的调试模式
        self.affection.debug_mode = self.debug_mode
        # 切换亲密度管理器的调试模式
        self.affection_manager.debug_mode = self.debug_mode
        return f"调试模式：{'开启' if self.debug_mode else '关闭'}"

    def show_social_status(self):
        """显示当前社交状态信息"""
        # 获取当前亲密度并确保一致性
        consistency = self.affection_manager.verify_consistency()
        if not consistency["consistent"]:
            self.affection_manager.force_sync()
            
        affection = int(self.affection_manager.get_value())
        status = f"🌡️ 当前好感度: {affection}/100\n"
        
        # 根据好感度区间确定关系阶段
        if affection < 40:
            status += "💔 关系阶段: 高冷期\n"
        elif affection < 60:
            status += "💟 关系阶段: 破冰期\n"
        elif affection < 80:
            status += "❤️ 关系阶段: 友好期\n"
        else:
            status += "💕 关系阶段: 亲密期\n"
            
        # 红旗警告
        red_flags = self.game_state.get("red_flags", 0)
        if red_flags > 0:
            status += f"⚠️ 警告次数: {red_flags}\n"
            
        # 连续负面对话
        consecutive_negative = self.game_state.get("consecutive_negative", 0)
        if consecutive_negative > 1:
            status += f"📉 连续不良对话: {consecutive_negative}次\n"
            
        # 连续正面对话  
        consecutive_positive = self.game_state.get("consecutive_positive", 0)
        if consecutive_positive > 1:
            status += f"📈 连续良好对话: {consecutive_positive}次\n"
            
        # 新增：交互统计
        status += f"🗣️ 对话总次数: {self.game_state['conversation_count']}\n"
        status += f"📅 游戏日期: {self.current_date.strftime('%Y年%m月%d日')} {self.current_time}\n"
        status += f"🏠 当前场景: {self.current_scene}\n"
        
        # 在调试模式下显示一致性信息
        if self.debug_mode and not consistency["consistent"]:
            status += "\n⚠️ 亲密度系统不一致！已自动修复。\n"
            status += f"系统值: {consistency['system_values']}\n"
        
        return status
        
    def view_dialogue_history(self, save_slot="auto", limit=10):
        """查看历史对话记录"""
        history = self.agent.storage.get_dialogue_history(save_slot, limit)
        if not history:
            return "没有找到对话记录。"
        
        result = "【历史对话记录】\n"
        for dialogue in history:
            timestamp = dialogue.get("timestamp", "未知时间")
            player = dialogue.get("player_input", "")
            response = dialogue.get("character_response", "")
            affection_change = dialogue.get("affection_change", 0)
            scene = dialogue.get("scene", "未知场景")
            
            # 格式化输出
            result += f"---时间: {timestamp}---\n"
            result += f"场景: {scene}\n"
            result += f"你: {player}\n"
            result += f"苏糖: {response}\n"
            if affection_change > 0:
                result += f"[好感度+{affection_change:.1f}]\n"
            elif affection_change < 0:
                result += f"[好感度{affection_change:.1f}]\n"
            result += "-----------------------\n\n"
            
        return result
    
    def _generate_scene_transition(self, scene_change):
        """生成场景转换的描述文本"""
        old_scene = self.current_scene
        new_scene = scene_change["new_scene"]
        old_date = self.current_date
        new_date = scene_change["new_date"]
        new_time = scene_change["new_time"]
        
        # 是否有日期变化
        date_changed = old_date.day != new_date.day or old_date.month != new_date.month
        
        # 根据不同情况生成转场描述
        if date_changed:
            # 跨天场景转换
            if (new_date - old_date).days == 1:
                prefix = f"第二天（{new_date.strftime('%Y年%m月%d日')}），{new_time}。"
            else:
                prefix = f"几天后（{new_date.strftime('%Y年%m月%d日')}），{new_time}。"
        else:
            # 同一天不同时间段
            prefix = f"不久后，{new_time}。"
            
        # 从场景描述列表中随机选择一个描述
        if new_scene in self.scene_manager.scene_descriptions:
            scene_desc = random.choice(self.scene_manager.scene_descriptions[new_scene])
        else:
            scene_desc = f"你来到了{new_scene}。"
            
        # 添加特殊的系统提示，通知AI场景已转换
        scene_change_notification = {"role": "system", "content": f"场景已经转换：从「{old_scene}」转换到「{new_scene}」。现在是{new_date.strftime('%Y年%m月%d日')} {new_time}。请在接下来的回复中自然地反映这一场景变化，不要直接提及场景转换本身。"}
        self.agent.dialogue_history.append(scene_change_notification)
        
        # 返回完整的场景转换描述
        return f"\n[场景转换]\n{prefix} {scene_desc}" 