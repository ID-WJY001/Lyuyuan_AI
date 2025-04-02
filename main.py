import yaml
from Su_Tang import GalGameAgent
import os
import random
from core.affection import AffectionSystem, AffectionEvent, SocialRisk
from core.nlp_engine import NaturalLanguageProcessor
from core.scene_manager import SceneManager
import re
from datetime import datetime, timedelta
def load_config(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class GameManager:
    def __init__(self):
        # 加载配置和初始化必要的组件
        char_config = load_config("config/character.yaml")
        nlp_processor = NaturalLanguageProcessor("data/keyword_groups.json")
        self.affection = AffectionSystem(nlp_processor)
        self.agent = GalGameAgent(is_new_game=True)
        self.scene_manager = SceneManager()  # 初始化场景管理器
        
        # 时间系统初始化
        self.current_date = datetime(2021, 10, 15)
        self.current_time = "上午"
        self.time_periods = ["上午", "中午", "下午", "傍晚", "晚上"]
        self.time_period_index = 0
        
        # 场景相关
        self.current_scene = "烘焙社摊位"
        self.next_scene_hints = []  # 记录可能的下一个场景提示
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
        self.sugar_bean_appearance_rate = 0.3  # 初始糖豆出现概率为30%
        self.sugar_bean_topics = [
            "烘焙社活动", "社团招新", "甜点制作", "烘焙技巧",
            "社团活动", "烘焙比赛", "社团展示"
        ]
        
        # 初始化游戏状态
        self.game_state = {
            "closeness": 30,  # 初始好感度设为30
            "red_flags": 0,  # 红旗警告计数
            "last_affection": 30,  # 记录上一次的好感度，也设为30
            "consecutive_negative": 0,  # 连续负面对话计数
            "consecutive_positive": 0,  # 连续正面对话计数
            "last_topic": None,  # 上一个话题
            "topic_duration": 0,  # 当前话题持续时间
            "last_scene_change": None,  # 上次场景切换时间
            "scene_change_cooldown": 3,  # 场景切换冷却时间
            "conversation_count": 0,  # 对话计数
            "pending_scene_change": None,  # 待处理的场景转换
            "scene_change_delay": 0  # 场景转换延迟计数器
        }
        
        # 同步初始好感度到agent和affection系统
        self.agent.game_state["closeness"] = self.game_state["closeness"]
        self.affection.affection = float(self.game_state["closeness"])
        
    def process_dialogue(self, user_input, dialogue_history):
        """处理玩家输入并更新游戏状态"""
        # 空输入检查
        if not user_input or user_input.isspace():
            return "...(苏糖看起来在发呆)"
            
        # 获取AI回复
        reply = self.agent.chat(user_input)
        
        # 更新亲密度
        result = self.affection.process_dialogue(user_input, self.agent.dialogue_history)
        current_affection = result['current_affection']
        delta = result['delta']
        previous_affection = self.game_state["last_affection"]  # 使用记录的上一次好感度
        
        # 更新游戏状态中的好感度相关数据
        self.game_state["last_affection"] = current_affection
        self.game_state["closeness"] = int(current_affection)
        self.affection.affection = current_affection
        
        # 更新连续对话计数
        if delta > 0:
            self.game_state["consecutive_positive"] += 1
            self.game_state["consecutive_negative"] = 0
        elif delta < 0:
            self.game_state["consecutive_negative"] += 1
            self.game_state["consecutive_positive"] = 0
            
        # 检查亲密度是否低于0，游戏结束
        if current_affection < 0:
            self.game_state["closeness"] = 0  # 确保为0，避免负数
            self.affection.affection = 0
            self.show_ending("好感度为负，关系破裂")
            return "😠 苏糖看起来非常生气，转身离开了...\n\n【游戏结束：好感度跌至谷底】"
        
        # 检查是否包含侮辱性言论
        if self._check_for_severe_insults(user_input):
            self.affection.affection = 0
            self.game_state["closeness"] = 0
            self.show_ending("严重侮辱导致关系破裂")
            return "😡 苏糖脸色瞬间变得煞白，眼中的光彩消失了...\n'我没想到你会这样对我说话...'她转身快步离开，再也没有回头。\n\n【游戏结束：严重侮辱导致关系瞬间破裂】"
            
        # 生成亲密度变化信息
        affection_info = self._generate_affection_info(delta, previous_affection, current_affection, result)
        
        # 确保在每次生成affection_info后，game_state中的closeness和last_affection是一致的
        self.game_state["last_affection"] = self.game_state["closeness"] = int(current_affection)

        # 检查是否触发剧情
        triggered = self.check_storyline_triggers(current_affection)
        if triggered:
            reply = f"{reply}\n\n{triggered}"
            
        # 分析对话并检查是否需要场景切换
        scene_change = self.scene_manager.analyze_conversation(
            user_input, reply, self.current_scene, self.current_date, self.current_time
        )
        
        if scene_change and scene_change["should_change"]:
            # 更新场景和时间
            old_scene = self.current_scene
            self.current_scene = scene_change["new_scene"]
            self.current_date = scene_change["new_date"]
            self.current_time = scene_change["new_time"]
            self.time_period_index = self.time_periods.index(self.current_time)
            
            # 生成场景转换描述
            scene_transition = self.scene_manager.generate_scene_transition(
                old_scene, self.current_scene, self.current_date, self.current_time
            )
            
            # 添加明确的系统消息，通知AI角色场景已转换
            scene_change_notification = {
                "role": "system", 
                "content": f"场景已经转换：从「{old_scene}」转换到「{self.current_scene}」。"
                           f"现在是{self.current_date.strftime('%Y年%m月%d日')} {self.current_time}。"
                           f"请完全意识到这个场景变化，角色应当完全了解自己所处的新场景和时间。"
                           f"不要将之前场景的对话内容错误地带入新场景中。"
                           f"如果对话中提到了下一次活动的时间（如'周六'、'下周'等），请记住并在新场景中保持这个信息一致。"
            }
            self.agent.dialogue_history.append(scene_change_notification)
            
            # 在对话历史中添加场景转换标记
            self.agent.dialogue_history.append({
                "role": "system",
                "content": f"===== 场景转换标记：{old_scene} -> {self.current_scene} ====="
            })
            
            reply = f"{reply}\n\n{scene_transition}"
            
        # 检查是否触发事件
        if result.get('event'):
            event_result = self.handle_player_action(result['event'])
            if event_result:
                reply = f"{reply}\n\n{event_result}"
            
        # 随机显示追女生tips
        if random.random() < 0.2:
            tip = self._get_random_tip()
            reply = f"{reply}\n\n{tip}"
            
        # 根据亲密度显示可用话题提示
        if current_affection >= 40 and random.random() < 0.3:
            topic_tip = self._get_topic_tip(self._get_available_topics(current_affection))
            if topic_tip:
                reply = f"{reply}\n\n{topic_tip}"
            
        # 对话处理后，将当前亲密度同步到agent状态中
        self.agent.game_state["closeness"] = self.game_state["closeness"]
        self.agent.game_state["last_affection"] = self.game_state["closeness"]
        
        # 确保亲密度值一致性
        self.game_state["last_affection"] = self.game_state["closeness"]
        
        return reply + affection_info
        
    def _generate_affection_info(self, delta, previous_affection, current_affection, result):
        """生成亲密度变化信息"""
        affection_info = ""
        
        # 大幅度变化（断崖式下跌）时显示特殊效果
        if delta <= -10:
            affection_info += f"\n💔 亲密度急剧下降! [{int(previous_affection)} → {int(current_affection)}]"
        elif delta <= -5:
            affection_info += f"\n💔 亲密度显著下降 [{int(previous_affection)} → {int(current_affection)}]"
        elif delta >= 5:
            affection_info += f"\n💖 亲密度显著提升! [{int(previous_affection)} → {int(current_affection)}]"
        elif delta > 0:
            affection_info += f"\n💫 亲密度微微提升 [{int(previous_affection)} → {int(current_affection)}]"
        elif delta < 0:
            affection_info += f"\n⚠️ 亲密度略有下降 [{int(previous_affection)} → {int(current_affection)}]"
            
        # 在调试模式下显示更多信息
        if self.debug_mode:
            debug = result.get('debug_info', {})
            affection_info += f"\n[调试信息]\n"
            affection_info += f"亲密度变化: {delta:+.1f} → 当前: {int(current_affection)}\n"
            
            if debug:
                # 基础分数
                affection_info += f"情感分: {debug.get('sentiment', 0):+.1f}, "
                affection_info += f"关键词: {debug.get('keywords', 0):+.1f}, "
                affection_info += f"上下文: {debug.get('context', 0):+.1f}, "
                affection_info += f"质量: {debug.get('quality', 0):+.1f}\n"
                
                # 社交动态分数
                if 'gentlemanly' in debug:
                    affection_info += f"绅士风度: {debug.get('gentlemanly', 0):+.1f}, "
                if 'boring_score' in debug:
                    affection_info += f"无聊度: {debug.get('boring_score', 0)}/10, "
                if 'mood_factor' in debug:
                    affection_info += f"心情: {debug.get('mood', 50)}/100, "
                if 'patience_factor' in debug:
                    affection_info += f"耐心: {debug.get('patience', 100)}/100\n"
                
                # 关键词匹配
                if 'matched_keywords' in debug and debug['matched_keywords']:
                    affection_info += f"匹配关键词: {', '.join(debug['matched_keywords'])}\n"
                    
                # 负面因素
                if debug.get('reason'):
                    affection_info += f"负面原因: {debug['reason']}\n"
                    
                # 社交风险
                if 'social_risk' in debug:
                    risk_level = debug['social_risk']
                    risk_str = "低" if risk_level == SocialRisk.LOW else "中" if risk_level == SocialRisk.MEDIUM else "高"
                    affection_info += f"社交风险: {risk_str}\n"
                    
                # 红旗警告
                if 'red_flags' in debug and debug['red_flags']:
                    affection_info += f"警告标记: {', '.join(debug['red_flags'])}\n"
                    
        return affection_info
    
    def _get_random_tip(self):
        """获取一个随机追女生技巧提示"""
        import random
        # 避免连续显示同一个提示
        available_indices = [i for i in range(len(self.dating_tips)) if i != self.last_tip_index]
        tip_index = random.choice(available_indices)
        self.last_tip_index = tip_index
        return self.dating_tips[tip_index]
    
    def check_storyline_triggers(self , affection):
        """检查是否触发剧情推进"""
        message = None
        for threshold, storyline in self.storyline_triggers.items():
            if affection >= threshold and threshold not in self.triggered_storylines:
                self.triggered_storylines.add(threshold)
                message = f"【剧情推进：{storyline}】"
                
                # 当亲密度达到100时，触发苏糖表白
                if threshold == 100:
                    # 更新亲密度系统的值，确保一致性
                    self.affection.affection = affection
                    self.game_state["closeness"] = int(affection)
                    
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
            affection = self.affection.affection
            if affection >= 95:
                # 高好感度：接受表白
                self.game_state["closeness"] = 100  # 设为最大值
                self.affection.affection = 100
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
                self.game_state["closeness"] = int(result['new_affection'])
            
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
                self.game_state["closeness"] = int(result['new_value'])
                
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
        print(f"※※ 结局触发：{description} ※※")
        print("游戏结束，感谢您的游玩！")
        exit()
        
    def toggle_debug_mode(self):
        """切换调试模式"""
        self.debug_mode = not self.debug_mode
        # 同时切换亲密度系统的调试模式
        self.affection.debug_mode = self.debug_mode
        return f"调试模式：{'开启' if self.debug_mode else '关闭'}"

    def show_social_status(self):
        """显示当前社交状态"""
        mood = self.affection.conversation_state.get("mood", 50)
        patience = self.affection.conversation_state.get("patience", 100)
        social_balance = self.affection.social_balance
        
        mood_str = "很好" if mood >= 80 else "良好" if mood >= 60 else "一般" if mood >= 40 else "较差" if mood >= 20 else "糟糕"
        patience_str = "充足" if patience >= 80 else "还好" if patience >= 50 else "有限" if patience >= 30 else "耗尽"
        
        status = f"社交状态：\n"
        status += f"❤️ 亲密度: {int(self.affection.affection)}/100\n"
        status += f"😊 心情: {mood_str} ({mood}/100)\n"
        status += f"⏳ 耐心: {patience_str} ({patience}/100)\n"
        
        red_flags = self.affection.red_flags
        if red_flags:
            status += f"⚠️ 警告: {', '.join(red_flags)}\n"
            
        return status

    def _check_for_severe_insults(self, text):
        """检查是否包含严重侮辱性言论"""
        severe_insults = [
            "傻逼", "操你", "滚蛋", "去死", "混蛋", "贱人", "婊子", "烂货", 
            "垃圾", "贱货", "死开", "白痴", "废物", "蠢猪", "愚蠢", "脑残",
            "恶心", "恶毒", "恶臭", "愚蛋", "笨蛋", "猪头", "丑八怪", "废物",
            "loser", "垃圾", "滚", "滚远点", "滚开", "滚一边去"
        ]
        
        for insult in severe_insults:
            if insult in text.lower():
                return True
                
        # 检查常见脏话的变体（使用正则表达式）
        insult_patterns = [
            r'f[u\*]+ck', r's[h\*]+it', r'b[i\*]+tch', r'd[a\*]+mn', 
            r'操.*[你妈逼]', r'草[你泥尼]', r'日[你你妈]', r'艹.*[你逼]'
        ]
        
        for pattern in insult_patterns:
            if re.search(pattern, text.lower()):
                return True
                
        return False
    
    def _update_time(self, time_keyword):
        """根据关键词更新时间和日期"""
        if "下周" in time_keyword:
            self.current_date += timedelta(days=7)
            self.current_time = "上午"
            self.time_period_index = 0
        elif "明天" in time_keyword:
            self.current_date += timedelta(days=1)
            self.current_time = "上午"
            self.time_period_index = 0
        elif "放学后" in time_keyword:
            self.current_time = "傍晚"
            self.time_period_index = 3
        elif "周末" in time_keyword:
            # 计算到下一个周末的天数
            days_until_weekend = (5 - self.current_date.weekday()) % 7
            if days_until_weekend == 0 and self.current_time == "晚上":
                days_until_weekend = 7
            self.current_date += timedelta(days=days_until_weekend)
            self.current_time = "上午"
            self.time_period_index = 0
        elif "下次" in time_keyword or "再见面" in time_keyword:
            # 随机选择1-3天后
            days = random.randint(1, 3)
            self.current_date += timedelta(days=days)
            self.current_time = "上午"
            self.time_period_index = 0
        else:
            # 当天的时间变化
            self.time_period_index = (self.time_period_index + 1) % len(self.time_periods)
            self.current_time = self.time_periods[self.time_period_index]

    def _check_scene_transition(self, user_input, ai_reply):
        """检查是否应该切换场景"""
        time_keyword = None
        
        # 检查时间/地点相关关键词
        for keyword, possible_scenes in self.scene_transition_keywords.items():
            if keyword in user_input or keyword in ai_reply:
                time_keyword = keyword
                # 记录可能的下一个场景
                if not self.next_scene_hints:
                    self.next_scene_hints = possible_scenes
        
        # 如果没有检测到时间关键词，不考虑场景切换
        if not self.next_scene_hints:
            return None
            
        # 检查是否包含告别相关的词语
        for keyword in self.farewell_keywords:
            if (keyword in user_input.lower() or keyword in ai_reply.lower()):
                # 选择一个新场景
                next_scene = random.choice(self.next_scene_hints)
                
                # 更新时间
                if time_keyword:
                    self._update_time(time_keyword)
                
                # 检查场景时间限制
                if self.current_time not in self.scene_time_restrictions[next_scene]:
                    # 如果时间不合适，调整到合适的时间
                    self.current_time = random.choice(self.scene_time_restrictions[next_scene])
                    self.time_period_index = self.time_periods.index(self.current_time)
                
                transition_message = self._generate_scene_transition(self.current_scene, next_scene)
                
                # 更新当前场景和清除提示
                self.current_scene = next_scene
                self.next_scene_hints = []
                
                return transition_message
                
        return None
        
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

    def _get_available_topics(self, affection):
        """根据亲密度获取可用话题"""
        available_topics = []
        for category, data in self.available_topics.items():
            if affection >= data["threshold"]:
                available_topics.extend(data["topics"])
        return available_topics

    def _should_show_sugar_bean(self, current_topic):
        """判断是否应该显示糖豆"""
        # 如果当前话题是糖豆相关话题，降低出现概率
        if current_topic in self.sugar_bean_topics:
            return random.random() < (self.sugar_bean_appearance_rate * 0.5)
        return random.random() < self.sugar_bean_appearance_rate

    def _get_topic_tip(self, available_topics):
        """获取话题提示"""
        if not available_topics:
            return None
            
        # 根据亲密度选择合适的话题提示
        current_affection = self.affection.affection
        if current_affection >= 80:
            return "💡 提示：你们的关系已经很亲密了，可以聊聊更深入的话题，比如对未来的期待..."
        elif current_affection >= 60:
            return "💡 提示：你们已经成为了好朋友，可以分享一些个人经历和想法..."
        elif current_affection >= 40:
            return "💡 提示：你们渐渐熟悉了，可以聊聊各自的兴趣爱好和未来规划..."
        else:
            return "💡 提示：可以聊聊学校生活和日常话题，慢慢增进了解..."

def main():
    # 设置API密钥（临时方案，正式项目应使用更安全的方式）
    try:
        api_key = "sk-c08ea80d7a76484ab1fad54e25725e8d"
        os.environ["DEEPSEEK_API_KEY"] = api_key
    except Exception as e:
        print(f"API密钥设置错误: {str(e)}")
        print("游戏将继续，但可能无法获取在线响应。")
    
    # 导入模块
    import random
    
    game = GameManager()
    print("===== 绿园中学物语：追女生模拟 =====")
    print("📝 游戏背景介绍：")
    print("你是陈辰，2021级高一一班的学生。在学校举办的百团大战（社团招新）活动中，")
    print("你在烘焙社的摊位前看到了一个让你一见钟情的女生——她正在认真地为过往的学生介绍烘焙社。")
    print("她身穿整洁的校服，戴着烘焙社的围裙，笑容甜美，举止优雅。")
    print("你鼓起勇气，决定上前搭讪，希望能够认识她并加入烘焙社...")
    print("\n游戏规则：")
    print("  - 无聊、重复的对话会让女生失去兴趣")
    print("  - 不礼貌或不当言论会严重损害关系")
    print("  - 过早表白会适得其反")
    print("  - 保持礼貌，让对话有趣且有深度")
    print("  - 好感度降至0以下游戏结束")
    print("  - 好感度达到100时会有特殊剧情")
    print("\n现在，你站在烘焙社摊位前，看着那位让你心动的女生...")
    print("\n命令提示: /exit退出, /save保存, /load读取, /debug调试模式, /status查看社交状态, /time查看当前时间")
    print(f"\n[当前时间：{game.current_date.strftime('%Y年%m月%d日')} {game.current_time}]")
    print("\n[当前亲密度：30]")
    print("\n请输入你的开场白：")
    
    while True:
        try:
            user_input = input("\n你：").strip()
            
            # 系统命令
            if user_input.startswith("/"):
                if user_input == "/exit":
                    print("游戏已退出")
                    break
                elif user_input == "/save":
                    # 在保存前，确保将当前亲密度值同步到agent的game_state中
                    game.agent.game_state["closeness"] = game.game_state["closeness"]
                    
                    # 同时保存当前日期和时间信息
                    game.agent.game_state["date"] = game.current_date
                    game.agent.game_state["time_period"] = game.current_time
                    game.agent.game_state["scene"] = game.current_scene
                    
                    game.agent.save(1)
                    print("手动存档成功！")
                    continue
                elif user_input == "/load":
                    game.agent.load(1)
                    # 加载后，将agent中的亲密度值同步到游戏状态和affection系统中
                    game.game_state["closeness"] = game.agent.game_state["closeness"]
                    game.affection.affection = float(game.game_state["closeness"])
                    
                    # 加载日期和场景数据
                    if "date" in game.agent.game_state and game.agent.game_state["date"]:
                        try:
                            # 如果是字符串格式，则转换为datetime对象
                            if isinstance(game.agent.game_state["date"], str):
                                import datetime as dt
                                game.current_date = dt.datetime.strptime(game.agent.game_state["date"], "%Y-%m-%d")
                            else:
                                game.current_date = game.agent.game_state["date"]
                        except:
                            # 如果加载失败，保持当前日期
                            pass
                    
                    # 加载时间段
                    if "time_period" in game.agent.game_state and game.agent.game_state["time_period"]:
                        game.current_time = game.agent.game_state["time_period"]
                        try:
                            game.time_period_index = game.time_periods.index(game.current_time)
                        except:
                            # 如果时间段不在列表中，设为默认值
                            game.current_time = "上午"
                            game.time_period_index = 0
                    
                    # 加载场景信息
                    if "scene" in game.agent.game_state and game.agent.game_state["scene"]:
                        game.current_scene = game.agent.game_state["scene"]
                    
                    print("读取存档成功！")
                    print(f"\n[当前时间：{game.current_date.strftime('%Y年%m月%d日')} {game.current_time}]")
                    print(f"\n[当前亲密度：{game.game_state['closeness']}]")
                    continue
                elif user_input == "/debug":
                    result = game.toggle_debug_mode()
                    print(result)
                    continue
                elif user_input == "/status":
                    status = game.show_social_status()
                    print(status)
                    continue
                elif user_input == "/time":
                    print(f"当前时间：{game.current_date.strftime('%Y年%m月%d日')} {game.current_time}")
                    continue
                elif user_input == "/help":
                    print("命令列表：")
                    print("/exit - 退出游戏")
                    print("/save - 保存游戏")
                    print("/load - 加载存档")
                    print("/debug - 切换调试模式")
                    print("/status - 查看当前社交状态")
                    print("/time - 查看当前时间")
                    print("/help - 显示帮助信息")
                    continue
            
            # 处理对话
            try:
                reply = game.process_dialogue(user_input, game.agent.dialogue_history)
                print("\n苏糖：", reply)
                
                # 对话处理后，将当前亲密度同步到agent状态中
                game.agent.game_state["closeness"] = game.game_state["closeness"]
                game.agent.game_state["last_affection"] = game.game_state["closeness"]
                
                # 确保亲密度值一致性
                game.game_state["last_affection"] = game.game_state["closeness"]
                
                # 显示状态（移至process_dialogue返回值的一部分）
                if not game.debug_mode:
                    print(f"\n[当前时间：{game.current_date.strftime('%Y年%m月%d日')} {game.current_time}]")
                    print(f"\n[当前亲密度：{game.game_state['closeness']}]")
            except Exception as e:
                # 优雅处理对话过程中的错误
                print(f"\n游戏处理错误: {str(e)}")
                print("\n苏糖：（似乎遇到了一些问题，但她很快调整好情绪）抱歉，我刚才走神了。你刚才说什么？")
                
                # 即使发生错误，也确保亲密度同步
                game.agent.game_state["closeness"] = game.game_state["closeness"]
                
                print(f"\n[当前时间：{game.current_date.strftime('%Y年%m月%d日')} {game.current_time}]")
                print(f"\n[当前亲密度：{game.game_state['closeness']}]")
            
        except KeyboardInterrupt:
            print("\n游戏已强制退出")
            break
        except Exception as e:
            print(f"发生错误：{str(e)}")
            print("游戏将尝试继续...")
            continue

if __name__ == "__main__":
    main()