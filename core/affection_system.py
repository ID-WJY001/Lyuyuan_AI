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
        
        # 检测不得体的言论（简单实现）
        inappropriate_words = self._check_inappropriate(user_input)
        if inappropriate_words:
            # 根据检测到的不当言论类型和数量确定惩罚力度
            has_severe_insult = "严重侮辱性言论" in self.red_flags
            has_sexual_hint = "不适当的性暗示" in self.red_flags
            
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
        sentiment_delta = analysis["sentiment"] * 2.5  # 提高情感权重（原来是2）
        
        # 检查关键词匹配
        keywords = analysis["keywords"]
        keyword_delta = 0
        matched_keywords = []
        used_keywords = set()  # 防止同一类别的多个关键词都加分
        
        for keyword in keywords:
            # 检查关键词是否已经过度使用
            if keyword in self.keyword_usage_history:
                uses = self.keyword_usage_history[keyword]
                if uses >= 3:  # 同一关键词使用超过3次，效果衰减（恢复为3次，原来改成了2）
                    continue
                self.keyword_usage_history[keyword] = uses + 1
            else:
                self.keyword_usage_history[keyword] = 1
            
            # 分类处理关键词
            category = self._get_keyword_category(keyword)
            if category and category not in used_keywords:
                if category == "positive":
                    keyword_delta += 1.5  # 提高正面词汇的加分（原来是1.0）
                    used_keywords.add(category)
                elif category == "negative":
                    keyword_delta -= 2.5 * self.difficulty_factor  # 降低负面词汇的扣分（原来是3）
                    used_keywords.add(category)
                elif category == "interest" and category not in used_keywords:
                    keyword_delta += 2.0  # 提高兴趣关键词奖励（原来是1.5）
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
            total_delta *= social_balance_factor * 0.85  # 提高正面收益（原来是0.7）
        
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
            random_penalty = random.uniform(0.3, 1.0) * self.difficulty_factor  # 降低随机降分幅度（原来是0.5-2.0）
            total_delta -= random_penalty
            if self.debug_mode:
                print(f"随机降分: -{random_penalty:.1f}")
                
        # 更新亲密度
        self.affection = max(0, self.affection + total_delta)
        
        # 准备调试信息
        debug_info = {
            "sentiment": sentiment_delta,
            "keywords": keyword_delta,
            "context": context_delta,
            "quality": quality_delta,
            "gentlemanly": gentlemanly_delta,
            "mood": self.conversation_state["mood"],
            "patience": self.conversation_state["patience"],
            "social_balance": self.social_balance,
            "matched_keywords": matched_keywords,
            "boring_score": boring_score,
            "difficulty_factor": self.difficulty_factor
        }
        
        # 检测是否触发了特殊事件
        event = None
        if boring_score > 5:
            event = AffectionEvent.BORING_TALK
            
        # 如果有共同兴趣话题，触发共同兴趣事件
        if keyword_delta >= 2:
            event = AffectionEvent.SHARED_INTEREST
            
        return {
            "delta": total_delta,
            "current_affection": self.affection,
            "previous_affection": previous_affection,
            "event": event,
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
        # 扩展不适当词汇列表，分类处理
        inappropriate_words = {
            # 性暗示相关（严重）
            "性暗示": ["脱衣", "色情", "裸体", "性感", "约炮", "一夜情", "啪啪",
                  "胸部", "隐私", "内裤", "内衣", "开房", "上床", "睡觉", 
                  "亲热", "摸", "亲", "抱", "睡你"],
            
            # 侮辱性言论（极其严重）
            "侮辱": ["傻逼", "操你", "滚蛋", "去死", "混蛋", "贱人", "婊子", "烂货", 
                  "垃圾", "贱货", "死开", "白痴", "废物", "蠢猪", "愚蠢", "脑残",
                  "恶心", "恶毒", "恶臭", "愚蛋", "笨蛋", "猪头", "丑八怪"],
            
            # 不尊重言论（中度严重）
            "不尊重": ["闭嘴", "住口", "不要说话", "烦人", "讨厌", "无聊", "无趣", 
                   "没意思", "无视", "不听", "不想理你", "懒得理你"],
            
            # 过度亲昵言论（轻度不适）
            "过度亲昵": ["老婆", "媳妇", "宝贝", "亲爱的", "我的", "专属"]
        }
        
        # 正则表达式匹配模式（主要针对变体脏话和模糊表达）
        inappropriate_patterns = [
            r'f[u\*]+ck', r's[h\*]+it', r'b[i\*]+tch', r'd[a\*]+mn', 
            r'操.*[你妈逼]', r'草[你泥尼]', r'日[你你妈]', r'艹.*[你逼]',
            r'sb', r'nmsl', r'cnm', r'wcnm', r'fw', r'jb', r'cbcb'
        ]
        
        # 分类结果
        found_words = []
        found_categories = set()
        
        # 检查不适当词汇
        for category, words in inappropriate_words.items():
            for word in words:
                if word in text.lower():
                    found_words.append(word)
                    found_categories.add(category)
        
        # 检查正则表达式匹配
        for pattern in inappropriate_patterns:
            if re.search(pattern, text.lower()):
                found_words.append("脏话")
                found_categories.add("侮辱")
                break
        
        # 设置红旗警告
        if "侮辱" in found_categories:
            self.red_flags.append("严重侮辱性言论")
            # 极大降低心情和耐心
            self.conversation_state["mood"] = max(0, self.conversation_state["mood"] - 50)
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 70)
        
        if "性暗示" in found_categories:
            self.red_flags.append("不适当的性暗示")
            # 大幅降低心情和耐心
            self.conversation_state["mood"] = max(0, self.conversation_state["mood"] - 40)
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 50)
            
        if "不尊重" in found_categories:
            self.red_flags.append("不尊重言论")
            # 中度降低心情和耐心
            self.conversation_state["mood"] = max(0, self.conversation_state["mood"] - 30)
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 35)
        
        # 返回分类信息而不仅仅是词语列表
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

class Phase:
    def __init__(self, threshold, name):
        self.threshold = threshold
        self.name = name
        
    def __repr__(self):
        return f"Phase({self.name}, threshold={self.threshold})"