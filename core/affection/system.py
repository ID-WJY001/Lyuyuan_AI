import random
import json
import re
from collections import Counter
from .events import AffectionEvent, SocialRisk, Phase
from .keyword_analyzer import KeywordAnalyzer
from .dialogue_evaluator import DialogueEvaluator

class AffectionSystem:
    def __init__(self, nlp_processor):
        self.nlp = nlp_processor
        self.affection = 30  # 初始值设为30
        self.phase_history = []
        
        # 加载配置
        self.config = self.load_config("config/affection_config.json")
        
        # 初始化子模块
        self.keyword_analyzer = KeywordAnalyzer(self.config)
        self.dialogue_evaluator = DialogueEvaluator(self.keyword_analyzer)
        
        # 状态管理
        self.last_inputs = []  # 记录最近的输入，用于检测重复
        self.red_flags = []    # 记录严重负面行为
        self.conversation_state = {
            "last_topic": None,
            "topic_continuity": 0,
            "dialogue_quality": 0,
            "boring_count": 0,     # 无聊对话计数
            "rude_count": 0,       # 粗鲁行为计数
            "mood": 50,            # 当前心情(0-100)
            "patience": 100,       # 耐心值(0-100)
            "recent_topics": []    # 最近的话题，用于检测话题重复
        }
        
        self.social_balance = 50   # 社交平衡度(0-100)，影响整体评价
        self.difficulty_factor = 1.2  # 难度系数，降低为1.2（原来是1.8）
        self.debug_mode = False  # 调试模式开关

    def process_dialogue(self, user_input, dialogue_history):
        """处理对话并更新亲密度"""
        previous_affection = self.affection  # 记录修改前的亲密度
        
        # 空输入或过短输入检测
        if not user_input or user_input.isspace() or len(user_input) < 2:
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 5)
            return {
                "delta": 0,
                "current_affection": self.affection,
                "previous_affection": previous_affection,
                "event": None,
                "message": "输入太短",
                "debug_info": {"reason": "输入过短", "social_risk": SocialRisk.LOW}
            }
            
        # 重复输入检测
        if user_input in self.last_inputs:
            self.conversation_state["boring_count"] += 1
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 10)
            penalty = 3 * self.difficulty_factor  # 降低惩罚（原来是4）
            self.affection = max(0, self.affection - penalty)
            return {
                "delta": -penalty,
                "current_affection": self.affection,
                "previous_affection": previous_affection,
                "event": AffectionEvent.BORING_TALK,
                "message": "重复输入让人感到无聊",
                "debug_info": {"reason": "完全重复的输入", "social_risk": SocialRisk.MEDIUM}
            }
            
        # 更新最近输入记录
        self.last_inputs.append(user_input)
        if len(self.last_inputs) > 5:
            self.last_inputs.pop(0)
        
        # 分析用户输入
        analysis = self.nlp.analyze(user_input)
        
        # 检测重复的单词（例如"猫咪猫咪猫咪"）
        word_counter = Counter(re.findall(r'\w+', user_input))
        repetitive_words = [word for word, count in word_counter.items() if count > 2 and len(word) > 1]
        
        if repetitive_words:
            self.conversation_state["boring_count"] += 1
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 8)
            return {
                "delta": -3,
                "current_affection": max(0, self.affection - 3),
                "event": AffectionEvent.BORING_TALK,
                "message": "重复词汇让人厌烦",
                "debug_info": {"reason": f"重复词汇: {repetitive_words}", "social_risk": SocialRisk.MEDIUM}
            }
            
        # 过于频繁的对话会让人感到压力
        if len(self.last_inputs) >= 3 and all(len(inp) < 15 for inp in self.last_inputs[-3:]):
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 5)
            self.social_balance = max(0, self.social_balance - 3)
        
        # 检测不得体的言论
        inappropriate_words = self.keyword_analyzer.check_inappropriate(user_input)
        if inappropriate_words:
            # 根据检测到的不当言论类型和数量确定惩罚力度
            has_severe_insult = "侮辱性言论" in inappropriate_words
            has_sexual_hint = "不适当的性暗示" in inappropriate_words
            
            # 侮辱性言论可能导致好感度直接归零
            if has_severe_insult:
                # 90%的概率导致大幅降分，10%的概率直接归零
                if random.random() < 0.1 or len(inappropriate_words) >= 2:
                    # 直接归零
                    self.affection = 0
                    return {
                        "delta": -previous_affection,  # 扣除全部好感度
                        "current_affection": 0,
                        "previous_affection": previous_affection,
                        "event": AffectionEvent.INAPPROPRIATE,
                        "message": "你的言论让对方极度不适",
                        "debug_info": {"reason": f"严重侮辱性言论: {inappropriate_words}", "social_risk": SocialRisk.HIGH}
                    }
                else:
                    # 大幅降分，但不至于直接归零
                    penalty = min(80, 20 * len(inappropriate_words) * self.difficulty_factor)
                    
            # 性暗示言论也有可能导致好感度直接归零
            elif has_sexual_hint:
                # 70%的概率导致大幅降分，30%的概率直接归零（亲密度低于60时）
                if (random.random() < 0.3 and self.affection < 60) or len(inappropriate_words) >= 3:
                    # 直接归零
                    self.affection = 0
                    return {
                        "delta": -previous_affection,  # 扣除全部好感度
                        "current_affection": 0,
                        "previous_affection": previous_affection,
                        "event": AffectionEvent.INAPPROPRIATE,
                        "message": "你的不当言论让对方极度不适",
                        "debug_info": {"reason": f"不适当的性暗示: {inappropriate_words}", "social_risk": SocialRisk.HIGH}
                    }
                else:
                    # 大幅降分，但不至于直接归零
                    penalty = min(60, 15 * len(inappropriate_words) * self.difficulty_factor)
            else:
                # 其他不当言论
                penalty = min(40, 10 * len(inappropriate_words) * self.difficulty_factor)  # 增加惩罚
            
            self.conversation_state["rude_count"] += 1
            self.social_balance = max(0, self.social_balance - 20)
            
            # 严重的社交失误，断崖式下跌
            self.affection = max(0, self.affection - penalty)
            return {
                "delta": -penalty,
                "current_affection": self.affection,
                "previous_affection": previous_affection,
                "event": AffectionEvent.INAPPROPRIATE,
                "message": "这种言论让人很不舒服",
                "debug_info": {"reason": f"不得体言论: {inappropriate_words}", "social_risk": SocialRisk.HIGH}
            }
        
        # 计算对话的"绅士风度"分数
        gentlemanly_score, gentlemanly_factors = self.dialogue_evaluator.evaluate_gentlemanly(user_input, dialogue_history)
        
        # 计算对话的"无聊度"
        boring_score, boring_factors = self.dialogue_evaluator.evaluate_boringness(user_input, dialogue_history, self.affection)
        
        # 无聊度过高，触发无聊事件
        if boring_score > 7:
            self.conversation_state["boring_count"] += 1
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 10)
            self.conversation_state["mood"] = max(0, self.conversation_state["mood"] - 10)
            
            # 连续三次无聊对话，断崖式下跌
            if self.conversation_state["boring_count"] >= 3:
                penalty = 15 * self.difficulty_factor  # 降低惩罚（原来是20）
                self.social_balance = max(0, self.social_balance - 15)
                self.affection = max(0, self.affection - penalty)
                return {
                    "delta": -penalty,
                    "current_affection": self.affection,
                    "previous_affection": previous_affection,
                    "event": AffectionEvent.BORING_TALK,
                    "message": "持续的无聊对话让人失去兴趣",
                    "debug_info": {
                        "reason": "持续无聊对话", 
                        "boring_factors": boring_factors,
                        "social_risk": SocialRisk.HIGH
                    }
                }
            else:
                penalty = boring_score * 0.6 * self.difficulty_factor  # 降低惩罚（原来是0.8）
                self.affection = max(0, self.affection - penalty)
                return {
                    "delta": -penalty,
                    "current_affection": self.affection,
                    "previous_affection": previous_affection,
                    "event": AffectionEvent.BORING_TALK,
                    "message": "对话有点无聊",
                    "debug_info": {
                        "reason": "无聊对话", 
                        "boring_factors": boring_factors,
                        "social_risk": SocialRisk.MEDIUM
                    }
                }
        
        # 计算情感影响
        sentiment_delta = analysis["sentiment"] * 2.5  # 提高情感权重
        
        # 检查关键词匹配
        keywords = analysis["keywords"]
        keyword_analysis = self.keyword_analyzer.analyze_keywords(keywords)
        keyword_delta = keyword_analysis["delta"]
        matched_keywords = keyword_analysis["matched_keywords"]
        
        # 计算上下文连贯性影响（与前一次对话的联系）
        coherence_score = analysis["coherence"]
        context_bonus = self.dialogue_evaluator.evaluate_context_relevance(user_input, dialogue_history)
        context_delta = coherence_score * 2 + context_bonus
        
        # 计算输入长度和质量影响
        quality_delta = self.dialogue_evaluator.evaluate_input_quality(user_input)
        
        # 风度评分：礼貌、尊重、回应问题等
        gentleman_delta = gentlemanly_score / 2.0  # 降低影响（原来是/1.5）
        
        # 汇总各项评分
        total_delta = sentiment_delta + keyword_delta + context_delta + quality_delta + gentleman_delta
        
        # 添加随机波动（增加互动的趣味性和挑战性）
        random_factor = random.uniform(-0.5, 1.0)  # 偏向正面一些（原来是-0.8到0.8）
        total_delta += random_factor
        
        # 应用心情和耐心调整
        mood_factor = self.conversation_state["mood"] / 50  # 1.0为标准值
        patience_factor = self.conversation_state["patience"] / 100  # 1.0为最大耐心
        
        # 心情差时负面因素加重，心情好时正面因素增强
        if total_delta < 0:
            total_delta *= (2 - mood_factor) * self.difficulty_factor  # 心情越差，负面影响越大
        else:
            total_delta *= mood_factor * 0.85  # 心情越好，正面影响越大，收益增加（原来是0.7）
        
        # 耐心影响整体亲密度变化
        total_delta *= patience_factor
        
        # 限制单次变化幅度
        if total_delta > 0:
            total_delta = min(6, total_delta)  # 增加单次最大加分（原来是5）
        else:
            total_delta = max(-6 * self.difficulty_factor, total_delta)  # 减少负面变化（原来是-8）
            
        # 随机降分机制，增加游戏难度
        # 降低触发概率为10%（原来是25%）
        if random.random() < 0.1:
            random_penalty = random.uniform(0.3, 1.0) * self.difficulty_factor  # 降低随机降分幅度
            total_delta -= random_penalty
            if self.debug_mode:
                print(f"随机降分: -{random_penalty:.1f}")
                
        # 更新亲密度
        self.affection = max(0, self.affection + total_delta)
        
        # 更新情绪和耐心状态
        if total_delta > 0:
            # 正面变化，提升心情和耐心
            self.conversation_state["mood"] = min(100, self.conversation_state["mood"] + total_delta * 2)
            if self.conversation_state["patience"] < 80:
                self.conversation_state["patience"] = min(100, self.conversation_state["patience"] + 2)
        else:
            # 负面变化，降低心情和耐心
            self.conversation_state["mood"] = max(0, self.conversation_state["mood"] + total_delta)
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 3)
            
        # 确定事件类型
        event = None
        if total_delta > 4:
            event = AffectionEvent.SHARED_INTEREST
        elif total_delta < -4:
            event = AffectionEvent.RUDE_BEHAVIOR
        else:
            event = AffectionEvent.NORMAL_DIALOGUE
            
        # 构建结果
        result = {
            "delta": total_delta,
            "current_affection": self.affection,
            "previous_affection": previous_affection,
            "event": event,
            "message": "",
            "debug_info": {
                "sentiment_delta": sentiment_delta,
                "keyword_delta": keyword_delta,
                "context_delta": context_delta,
                "quality_delta": quality_delta,
                "gentleman_delta": gentleman_delta,
                "matched_keywords": matched_keywords,
                "boringness": boring_score,
                "boring_factors": boring_factors,
                "gentlemanly": gentlemanly_score,
                "gentlemanly_factors": gentlemanly_factors,
                "social_risk": self._evaluate_social_risk()
            }
        }
            
        return result
    
    def _evaluate_social_risk(self):
        """评估社交风险水平"""
        if self.conversation_state["boring_count"] > 3 or self.conversation_state["rude_count"] > 1:
            return SocialRisk.HIGH
        elif self.conversation_state["boring_count"] > 1 or self.conversation_state["patience"] < 50:
            return SocialRisk.MEDIUM
        else:
            return SocialRisk.LOW
    
    def load_config(self, path):
        """加载配置文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 确保配置中包含所有必要字段
            if "event_effects" not in config:
                config["event_effects"] = {}
                
            # 添加新事件效果
            if "6" not in config["event_effects"]:  # BORING_TALK
                config["event_effects"]["6"] = -5
            if "7" not in config["event_effects"]:  # RUDE_BEHAVIOR
                config["event_effects"]["7"] = -10
            if "8" not in config["event_effects"]:  # INAPPROPRIATE
                config["event_effects"]["8"] = -15
                
            # 转换概率配置为枚举键
            config["confession_prob"] = {
                int(k): v for k, v in config.get("confession_probability", {}).items()
            }
            
            return config
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            # 返回默认配置
            return {
                "event_effects": {
                    "1": 1,    # NORMAL_DIALOGUE
                    "2": 5,    # SHARED_INTEREST
                    "3": 10,   # DATE_ACCEPTED
                    "4": 0,    # CONFESSION (特殊处理)
                    "5": -10,  # TABOO_TOPIC
                    "6": -5,   # BORING_TALK
                    "7": -10,  # RUDE_BEHAVIOR
                    "8": -15   # INAPPROPRIATE
                },
                "confession_prob": {
                    30: 0.01,  # 好感度30时，成功率1%
                    50: 0.1,   # 好感度50时，成功率10%
                    70: 0.5,   # 好感度70时，成功率50%
                    90: 0.9    # 好感度90时，成功率90%
                }
            }

    def handle_event(self, event, is_player_initiated=True, **kwargs):
        """处理特殊事件对亲密度的影响"""
        event_type = str(event.value)
        effect = self.config["event_effects"].get(event_type, 0)
        old_affection = self.affection  # 保存修改前的值
        
        if event == AffectionEvent.CONFESSION:
            # 告白事件的特殊处理
            # 获取当前剧情阶段
            phase = self._get_current_phase()
            
            # 如果是玩家发起的告白
            if is_player_initiated:
                # 告白成功的条件
                success = False
                # 亲密度达到高级别，且没有严重的负面标记
                if self.affection >= 75 and len(self.red_flags) <= 1:
                    success = True
                    if self.affection >= 90:
                        # 特别好的结局
                        ending = "good_ending"
                        boost = 15  # 大幅提升亲密度，直接在内部更新
                        self.affection += boost  # 直接在内部更新，不返回delta
                        message = "苏糖的脸红了，眼中闪烁着幸福的光芒...'我也喜欢你，很久了...'"
                    else:
                        # 普通成功结局
                        ending = "normal_ending"
                        boost = 10
                        self.affection += boost  # 直接在内部更新，不返回delta
                        message = "苏糖微笑着点了点头，'嗯，我也是...'"
                    
                    return {
                        "success": True, 
                        "message": message, 
                        "ending": ending,
                        "old_affection": old_affection,
                        "new_affection": self.affection
                    }
                else:
                    # 失败的情况
                    penalty = -15 if self.affection < 50 else -8
                    # 亲密度过低时会直接造成游戏结束
                    if self.affection < 40:
                        ending = "bad_ending"
                        message = "苏糖看起来很尴尬，'对不起，我们还是..保持普通同学关系比较好...'"
                        self.affection = 0  # 直接归零
                    else:
                        ending = "continue"
                        message = "苏糖有些惊讶，'啊？这..有点突然...我们可以先多了解一下彼此吗？'"
                        self.affection = max(0, self.affection + penalty)
                    
                    return {
                        "success": False, 
                        "message": message, 
                        "ending": ending,
                        "old_affection": old_affection,
                        "new_affection": self.affection
                    }
            else:
                # AI主动告白（当且仅当亲密度达到很高时）
                return {"success": True, "message": "告白成功！", "ending": "special_ending"}
                
        elif event == AffectionEvent.SHARED_INTEREST:
            # 发现共同兴趣的加成
            boost = 5
            old_value = self.affection
            self.affection = min(100, self.affection + boost)
            return {"delta": boost, "old_value": old_value, "new_value": self.affection}
            
        else:
            # 其他事件的通用处理
            old_value = self.affection
            self.affection = max(0, min(100, self.affection + effect))
            return {"delta": effect, "old_value": old_value, "new_value": self.affection}

    def check_ending(self):
        """根据当前状态检查是否应该触发结局"""
        if self.affection <= 0:
            return "bad_ending"
        elif self.affection >= 100:
            return "good_ending"
        else:
            return None

    def _get_current_phase(self):
        """获取当前的亲密度阶段"""
        if self.affection < 30:
            return "stranger"
        elif self.affection < 50:
            return "acquaintance"
        elif self.affection < 75:
            return "friend"
        elif self.affection < 90:
            return "close_friend"
        else:
            return "romantic" 