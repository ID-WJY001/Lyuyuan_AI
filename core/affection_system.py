# affection_system.py
import random
import json
from enum import Enum
import re
import jieba
from collections import Counter

class AffectionEvent(Enum):
    NORMAL_DIALOGUE = 1      # 普通对话
    SHARED_INTEREST = 2      # 兴趣共鸣
    DATE_ACCEPTED = 3        # 成功邀约
    CONFESSION = 4           # 玩家表白
    TABOO_TOPIC = 5          # 触犯禁忌
    BORING_TALK = 6          # 无聊对话
    RUDE_BEHAVIOR = 7        # 粗鲁行为
    INAPPROPRIATE = 8        # 不得体言论

class SocialRisk:
    """社交风险评估"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class AffectionSystem:
    def __init__(self, nlp_processor):
        self.nlp = nlp_processor
        self.affection = 30  # 初始值设为30
        self.phase_history = []
        self.load_config("config/affection_config.json")
        self.last_inputs = []  # 记录最近的输入，用于检测重复
        self.keyword_usage_history = {}  # 记录关键词使用频率
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
        self.red_flags = []        # 记录严重负面行为
        self.social_balance = 50   # 社交平衡度(0-100)，影响整体评价

    def process_dialogue(self, user_input, dialogue_history):
        """处理对话并更新亲密度"""
        # 空输入或过短输入检测
        if not user_input or user_input.isspace() or len(user_input) < 2:
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 5)
            return {
                "delta": 0,
                "current_affection": self.affection,
                "event": None,
                "message": "输入太短",
                "debug_info": {"reason": "输入过短", "social_risk": SocialRisk.LOW}
            }
            
        # 重复输入检测
        if user_input in self.last_inputs:
            self.conversation_state["boring_count"] += 1
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 10)
            return {
                "delta": -2,  # 加重惩罚
                "current_affection": max(0, self.affection - 2),
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
        
        # 检测不得体的言论（简单实现）
        inappropriate_words = self._check_inappropriate(user_input)
        if inappropriate_words:
            penalty = min(30, 8 * len(inappropriate_words))  # 根据不当言论数量加重惩罚
            self.conversation_state["mood"] = max(0, self.conversation_state["mood"] - 20)
            self.conversation_state["rude_count"] += 1
            self.red_flags.append("不当言论")
            self.social_balance = max(0, self.social_balance - 15)
            
            # 严重的社交失误，断崖式下跌
            return {
                "delta": -penalty,
                "current_affection": max(0, self.affection - penalty),
                "event": AffectionEvent.INAPPROPRIATE,
                "message": "这种言论让人很不舒服",
                "debug_info": {"reason": f"不得体言论: {inappropriate_words}", "social_risk": SocialRisk.HIGH}
            }
        
        # 计算对话的"绅士风度"分数
        gentlemanly_score, gentlemanly_factors = self._evaluate_gentlemanly(user_input, dialogue_history)
        
        # 计算对话的"无聊度"
        boring_score, boring_factors = self._evaluate_boringness(user_input, dialogue_history)
        
        # 无聊度过高，触发无聊事件
        if boring_score > 7:
            self.conversation_state["boring_count"] += 1
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 10)
            self.conversation_state["mood"] = max(0, self.conversation_state["mood"] - 10)
            
            # 连续三次无聊对话，断崖式下跌
            if self.conversation_state["boring_count"] >= 3:
                penalty = 15
                self.social_balance = max(0, self.social_balance - 10)
                return {
                    "delta": -penalty,
                    "current_affection": max(0, self.affection - penalty),
                    "event": AffectionEvent.BORING_TALK,
                    "message": "持续的无聊对话让人失去兴趣",
                    "debug_info": {
                        "reason": "持续无聊对话", 
                        "boring_factors": boring_factors,
                        "social_risk": SocialRisk.HIGH
                    }
                }
            else:
                return {
                    "delta": -boring_score * 0.5,
                    "current_affection": max(0, self.affection - boring_score * 0.5),
                    "event": AffectionEvent.BORING_TALK,
                    "message": "对话有点无聊",
                    "debug_info": {
                        "reason": "无聊对话", 
                        "boring_factors": boring_factors,
                        "social_risk": SocialRisk.MEDIUM
                    }
                }
        
        # 计算情感影响
        sentiment_delta = analysis["sentiment"] * 3  # 调低情感权重
        
        # 检查关键词匹配
        keywords = analysis["keywords"]
        keyword_delta = 0
        matched_keywords = []
        used_keywords = set()  # 防止同一类别的多个关键词都加分
        
        for keyword in keywords:
            # 检查关键词是否已经过度使用
            if keyword in self.keyword_usage_history:
                uses = self.keyword_usage_history[keyword]
                if uses >= 3:  # 同一关键词使用超过3次，效果衰减
                    continue
                self.keyword_usage_history[keyword] = uses + 1
            else:
                self.keyword_usage_history[keyword] = 1
            
            # 分类处理关键词
            category = self._get_keyword_category(keyword)
            if category and category not in used_keywords:
                if category == "positive":
                    keyword_delta += 1.5
                    used_keywords.add(category)
                elif category == "negative":
                    keyword_delta -= 2
                    used_keywords.add(category)
                elif category == "interest" and category not in used_keywords:
                    keyword_delta += 2  # 降低兴趣关键词奖励
                    used_keywords.add(category)
                
                matched_keywords.append(keyword)
        
        # 计算上下文连贯性影响（与前一次对话的联系）
        coherence_score = analysis["coherence"]
        context_bonus = self._evaluate_context_relevance(user_input, dialogue_history)
        context_delta = coherence_score * 2 + context_bonus
        
        # 计算输入长度和质量影响
        quality_delta = self._evaluate_input_quality(user_input)
        
        # 整合绅士风度评分
        if gentlemanly_score > 0:
            # 加入绅士风度奖励
            gentlemanly_delta = gentlemanly_score * 1.2
            self.conversation_state["mood"] = min(100, self.conversation_state["mood"] + 5)
            self.social_balance = min(100, self.social_balance + 3)
        else:
            # 如果不够绅士，则有负面影响
            gentlemanly_delta = gentlemanly_score
            if gentlemanly_score < -3:
                self.conversation_state["rude_count"] += 1
                self.conversation_state["mood"] = max(0, self.conversation_state["mood"] - 8)
                self.social_balance = max(0, self.social_balance - 5)
                
                # 连续三次粗鲁行为，断崖式下跌
                if self.conversation_state["rude_count"] >= 3:
                    penalty = 20
                    self.red_flags.append("持续粗鲁行为")
                    return {
                        "delta": -penalty,
                        "current_affection": max(0, self.affection - penalty),
                        "event": AffectionEvent.RUDE_BEHAVIOR,
                        "message": "你的行为很不尊重人",
                        "debug_info": {
                            "reason": "持续粗鲁行为", 
                            "rude_factors": gentlemanly_factors,
                            "social_risk": SocialRisk.HIGH
                        }
                    }
            
        # 合并所有影响因素
        total_delta = sentiment_delta + keyword_delta + context_delta + quality_delta + gentlemanly_delta
        
        # 应用社交平衡调整
        social_balance_factor = self.social_balance / 50  # 1.0为标准值，小于1降低收益，大于1提高收益
        if total_delta > 0:
            total_delta *= social_balance_factor
        
        # 应用心情和耐心调整
        mood_factor = self.conversation_state["mood"] / 50  # 1.0为标准值
        patience_factor = self.conversation_state["patience"] / 100  # 1.0为最大耐心
        
        # 心情差时负面因素加重，心情好时正面因素增强
        if total_delta < 0:
            total_delta *= (2 - mood_factor)  # 心情越差，负面影响越大
        else:
            total_delta *= mood_factor  # 心情越好，正面影响越大
        
        # 耐心影响整体亲密度变化
        total_delta *= patience_factor
        
        # 限制单次变化幅度
        total_delta = max(-8, min(6, total_delta))  # 扩大负面影响范围，限制正面影响上限
        
        # 应用动态衰减
        decay_factor = self._get_decay_factor()
        total_delta *= decay_factor
        
        # 更新亲密度
        old_affection = self.affection
        self.affection = max(0, min(100, self.affection + total_delta))
        self._update_phase()
        
        # 正向对话会改善心情
        if total_delta > 0:
            self.conversation_state["mood"] = min(100, self.conversation_state["mood"] + total_delta * 2)
            if gentlemanly_score > 2:  # 有礼貌的对话可以恢复耐心
                self.conversation_state["patience"] = min(100, self.conversation_state["patience"] + 5)
                
        # 无聊但不至于触发事件的对话会降低心情和耐心
        elif boring_score > 4:
            self.conversation_state["mood"] = max(0, self.conversation_state["mood"] - 3)
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 3)
            
        # 重置无聊计数（如果这次对话不无聊）
        if boring_score < 4:
            self.conversation_state["boring_count"] = 0
            
        # 重置粗鲁计数（如果这次对话有礼貌）
        if gentlemanly_score > 0:
            self.conversation_state["rude_count"] = 0
        
        # 检查是否触发特殊事件
        event = None
        event_message = ""
        if "表白" in user_input or "喜欢你" in user_input or "爱你" in user_input:
            # 表白需要足够的亲密度，否则会适得其反
            if self.affection < 60 or self.conversation_state["mood"] < 40:
                # 过早表白导致断崖式下跌
                penalty = min(25, max(10, self.affection * 0.3))
                self.affection = max(0, self.affection - penalty)
                self.conversation_state["mood"] = max(0, self.conversation_state["mood"] - 20)
                self.red_flags.append("过早表白")
                self.social_balance = max(0, self.social_balance - 10)
                return {
                    "delta": -penalty,
                    "current_affection": self.affection,
                    "event": AffectionEvent.CONFESSION,
                    "message": "过早表白让人感到压力和不适",
                    "debug_info": {"reason": "过早表白", "social_risk": SocialRisk.HIGH}
                }
            event = "confess"
            event_message = "表白事件触发"
        elif any(keyword in matched_keywords for keyword in self.config["interest_keywords"]) and len(matched_keywords) >= 2:
            # 要求至少匹配两个关键词才会触发兴趣共鸣
            event = "share_interest"
            event_message = "共同兴趣点发现"
            
        # 构建详细的调试信息
        debug_info = {
            "sentiment": sentiment_delta,
            "keywords": keyword_delta,
            "context": context_delta,
            "quality": quality_delta,
            "gentlemanly": gentlemanly_delta,
            "boring_score": boring_score,
            "mood_factor": mood_factor,
            "patience_factor": patience_factor,
            "social_balance": social_balance_factor,
            "decay": decay_factor,
            "matched_keywords": matched_keywords,
            "used_categories": list(used_keywords),
            "mood": self.conversation_state["mood"],
            "patience": self.conversation_state["patience"],
            "social_balance": self.social_balance,
            "red_flags": self.red_flags,
            "social_risk": self._evaluate_social_risk()
        }
            
        return {
            "delta": round(total_delta, 2),
            "current_affection": self.affection,
            "previous_affection": old_affection,
            "event": event,
            "message": event_message,
            "matched_keywords": matched_keywords if matched_keywords else None,
            "debug_info": debug_info
        }
    
    def _evaluate_gentlemanly(self, user_input, dialogue_history):
        """评估对话的绅士风度"""
        score = 0
        factors = []
        
        # 礼貌用语加分
        polite_words = ["请", "谢谢", "抱歉", "打扰", "麻烦", "您好", "感谢"]
        for word in polite_words:
            if word in user_input:
                score += 1
                factors.append(f"礼貌用语: {word}")
                break
                
        # 尊重表达加分
        respect_phrases = ["你觉得", "你认为", "你喜欢", "如果你", "你的想法"]
        for phrase in respect_phrases:
            if phrase in user_input:
                score += 1.5
                factors.append("尊重对方的表达")
                break
                
        # 不打断对方（如果上一条是AI的回复，且包含问题，玩家有回应加分）
        if len(dialogue_history) >= 2:
            last_msg = dialogue_history[-1]
            if last_msg.get("role") == "assistant" and ("?" in last_msg["content"] or "？" in last_msg["content"]):
                if "?" in user_input or "？" in user_input or len(user_input) > 15:
                    score += 2
                    factors.append("回应了问题")
        
        # 负面因素：命令式语气
        command_patterns = [r"^[给去]我", r"^告诉我", r"^快[点些]", r"^你[必须应该]"]
        for pattern in command_patterns:
            if re.search(pattern, user_input):
                score -= 3
                factors.append("命令式语气")
                break
                
        # 负面因素：过于自我中心
        self_centered_patterns = [r"^我[想要需]", r"^我.*我.*我", r"^[^？]+\?"]
        for pattern in self_centered_patterns:
            if re.search(pattern, user_input) and "你" not in user_input:
                score -= 2
                factors.append("过于自我中心")
                break
        
        # 负面因素：打断对话或不关注对方提问
        if len(dialogue_history) >= 2:
            last_msg = dialogue_history[-1]
            if last_msg.get("role") == "assistant" and ("?" in last_msg["content"] or "？" in last_msg["content"]):
                # 对方提问，但自己完全转移话题
                is_ignoring = True
                for word in jieba.lcut(last_msg["content"])[-10:]:  # 分析最后部分的关键词
                    if word in user_input and len(word) > 1:
                        is_ignoring = False
                        break
                if is_ignoring and len(user_input) < 10:  # 简短回复且无关联
                    score -= 4
                    factors.append("忽视对方的问题")
        
        return score, factors
    
    def _evaluate_boringness(self, user_input, dialogue_history):
        """评估对话的无聊程度 (0-10分，分数越高越无聊)"""
        score = 0
        factors = []
        
        # 过短的回复
        if len(user_input) < 8:
            score += 2
            factors.append("回复过短")
            
        # 缺乏信息量
        info_words = len(set(jieba.lcut(user_input)))
        if info_words < 5:
            score += 2
            factors.append("信息量少")
            
        # 重复的话题
        topics = self._extract_topics(user_input)
        if set(topics) & set(self.conversation_state["recent_topics"]):
            score += 3
            factors.append("话题重复")
        else:
            # 更新最近话题
            self.conversation_state["recent_topics"] = topics + self.conversation_state["recent_topics"]
            if len(self.conversation_state["recent_topics"]) > 5:
                self.conversation_state["recent_topics"] = self.conversation_state["recent_topics"][:5]
                
        # 重复的句式
        if len(dialogue_history) >= 4:
            user_messages = [msg["content"] for msg in dialogue_history if msg.get("role") == "user"]
            if len(user_messages) >= 2:
                last_msg = user_messages[-1]
                if (
                    (last_msg.endswith("?") and user_input.endswith("?")) or
                    (last_msg.endswith("！") and user_input.endswith("！")) or
                    (last_msg.endswith("。") and user_input.endswith("。") and len(user_input) < 15)
                ):
                    score += 2
                    factors.append("句式重复")
        
        # 缺乏深度（简单是否提问）
        if "?" not in user_input and "？" not in user_input and len(user_input) < 20:
            score += 1
            factors.append("缺乏交流深度")
            
        # 过于礼貌但没实质内容
        polite_only = all(word in user_input for word in ["你好", "谢谢", "再见"]) and len(user_input) < 15
        if polite_only:
            score += 2
            factors.append("只有礼节性用语")
            
        # 避免高强度无内容灌水
        if len(dialogue_history) >= 6:
            recent_msgs = [msg for msg in dialogue_history[-6:] if msg.get("role") == "user"]
            if len(recent_msgs) >= 3 and all(len(msg["content"]) < 10 for msg in recent_msgs):
                score += 3
                factors.append("连续简短回复")
        
        return min(10, score), factors
    
    def _extract_topics(self, text):
        """从文本中提取主要话题"""
        # 简单实现，实际应用可能需要更复杂的NLP
        import jieba.analyse
        try:
            # 提取前3个关键词作为话题
            topics = jieba.analyse.extract_tags(text, topK=3)
            return topics
        except:
            # 如果提取失败，返回空列表
            return []
    
    def _check_inappropriate(self, text):
        """检查文本中是否包含不适当的内容"""
        # 简单实现，实际中可能需要更复杂的模型或规则
        inappropriate_words = [
            "脱衣", "色情", "裸体", "性感", "约炮", "一夜情", "啪啪",
            "胸部", "隐私", "内裤", "内衣", "骚", "贱", "婊", 
            "傻逼", "操你", "滚", "去死", "白痴", "蠢货", "智障"
        ]
        
        found_words = []
        for word in inappropriate_words:
            if word in text:
                found_words.append(word)
                
        return found_words
    
    def _evaluate_social_risk(self):
        """评估当前社交风险级别"""
        if len(self.red_flags) >= 2 or self.conversation_state["patience"] < 30:
            return SocialRisk.HIGH
        elif self.conversation_state["boring_count"] >= 2 or self.conversation_state["rude_count"] >= 1:
            return SocialRisk.MEDIUM
        return SocialRisk.LOW
    
    def _get_keyword_category(self, keyword):
        """确定关键词属于哪个类别"""
        if keyword in self.config["positive_keywords"]:
            return "positive"
        elif keyword in self.config["negative_keywords"]:
            return "negative"
        elif keyword in self.config["interest_keywords"]:
            return "interest"
        return None
    
    def _evaluate_context_relevance(self, user_input, dialogue_history):
        """评估用户输入与对话历史的相关性"""
        if len(dialogue_history) < 3:
            return 0
            
        # 获取最近的助手回复
        assistant_messages = [msg for msg in dialogue_history if msg.get("role") == "assistant"]
        if not assistant_messages:
            return 0
            
        last_assistant_message = assistant_messages[-1]["content"]
        
        # 提取上一条助手消息中的关键词
        last_keywords = self.nlp._extract_keywords(last_assistant_message)
        user_keywords = self.nlp._extract_keywords(user_input)
        
        # 计算关键词重叠
        overlap = len(set(last_keywords) & set(user_keywords))
        
        # 上下文关联分数
        if overlap > 0:
            return min(2, overlap * 0.8)  # 最多加2分
            
        return 0
    
    def _evaluate_input_quality(self, user_input):
        """评估用户输入的质量"""
        # 基于长度的基础分
        length = len(user_input)
        if length < 5:
            length_score = 0
        elif 5 <= length <= 15:
            length_score = 0.5
        elif 15 < length <= 30:
            length_score = 1.0
        elif 30 < length <= 60:
            length_score = 1.5
        else:
            length_score = 1.0  # 过长文本略微减分
            
        # 评估语句的复杂度（简单估计）
        sentences = re.split(r'[。！？.!?]', user_input)
        sentences = [s for s in sentences if s.strip()]
        
        # 句子数量评分
        if len(sentences) > 1:
            sentence_score = min(1.5, len(sentences) * 0.5)
        else:
            sentence_score = 0
            
        # 检查是否包含问句（以提问为主动交流加分）
        question_score = 0.5 if '?' in user_input or '？' in user_input else 0
            
        return length_score + sentence_score + question_score

    def load_config(self, path):
        """加载配置文件"""
        with open(path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 确保配置中包含所有必要字段
        if "event_effects" not in self.config:
            self.config["event_effects"] = {}
        
        # 添加新事件效果
        if "6" not in self.config["event_effects"]:  # BORING_TALK
            self.config["event_effects"]["6"] = -5
        if "7" not in self.config["event_effects"]:  # RUDE_BEHAVIOR
            self.config["event_effects"]["7"] = -10
        if "8" not in self.config["event_effects"]:  # INAPPROPRIATE
            self.config["event_effects"]["8"] = -15
            
        # 转换概率配置为枚举键
        self.confession_prob = {
            int(k): v for k, v in self.config["confession_probability"].items()
        }

    def handle_event(self, event_type, **kwargs):
        """处理事件影响"""
        delta = 0
        
        if event_type == AffectionEvent.CONFESSION:
            return self._handle_confession(kwargs.get('is_player_initiated', False))
        
        # 基础事件影响
        delta += self.config["event_effects"].get(str(event_type.value), 0)
        
        # 动态衰减机制
        delta *= self._get_decay_factor()
        
        self.affection = max(0, min(100, self.affection + delta))
        self._update_phase()
        return {"delta": delta, "new_value": self.affection}

    def _handle_confession(self, is_player_initiated):
        """处理表白逻辑"""
        if self.affection >= 100:
            return {"success": True, "ending": "already_max"}
            
        result = {}
        current_phase = self.current_phase.name
        
        # 玩家主动表白
        if is_player_initiated:
            # 考虑心情和社交平衡
            mood_modifier = self.conversation_state["mood"] / 50  # 1.0是标准值
            social_modifier = self.social_balance / 50  # 1.0是标准值
            
            # 心情好，社交平衡好，增加成功概率
            threshold = 80 if self.affection >= 80 else 50
            base_prob = self.confession_prob.get(threshold, 0.2)
            adjusted_prob = base_prob * mood_modifier * social_modifier
            
            if random.random() < adjusted_prob:
                result["success"] = True
                bonus = 100 - self.affection if self.affection >=80 else 20
                self.affection = min(100, self.affection + bonus)
                result["ending"] = "good_ending" if self.affection ==100 else "early_ending"
            else:
                result["success"] = False
                # 心情越差，惩罚越重
                penalty = -30 if self.affection >=50 else -50
                penalty *= (2 - mood_modifier)
                self.affection = max(0, self.affection + penalty)
                self.conversation_state["mood"] = max(0, self.conversation_state["mood"] - 20)
                result["message"] = random.choice(self.config["rejection_phrases"])
                
            return result
        
        # NPC主动表白（暂未实现）
        return {"success": False}

    @property
    def current_phase(self):
        """获取当前关系阶段"""
        phases = [
            (0, "Stranger"), 
            (40, "Acquaintance"),
            (70, "Friend"),
            (90, "CloseFriend")
        ]
        for threshold, name in reversed(phases):
            if self.affection >= threshold:
                return Phase(threshold, name)
        return Phase(0, "Unknown")

    def _get_decay_factor(self):
        """获取动态衰减系数"""
        if len(self.phase_history) > 3:
            same_phase_count = sum(1 for p in self.phase_history[-3:] 
                                 if p == self.current_phase.name)
            return 1.0 - same_phase_count * 0.15  # 减轻衰减幅度
        return 1.0

    def _update_phase(self):
        """记录阶段变化"""
        if not self.phase_history or self.phase_history[-1] != self.current_phase.name:
            self.phase_history.append(self.current_phase.name)

    def check_ending(self):
        """检查是否触发结局"""
        if self.affection <= 0:
            return "bad_ending"
        elif self.affection >= 100:
            return "good_ending"
        return None

class Phase:
    def __init__(self, threshold, name):
        self.threshold = threshold
        self.name = name
        
    def __repr__(self):
        return f"Phase({self.name}, threshold={self.threshold})"