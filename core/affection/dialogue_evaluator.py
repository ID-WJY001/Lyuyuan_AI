import re
from collections import Counter

class DialogueEvaluator:
    def __init__(self, keyword_analyzer):
        """初始化对话评估器"""
        self.keyword_analyzer = keyword_analyzer
    
    def evaluate_gentlemanly(self, user_input, dialogue_history):
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
            if re.search(pattern, user_input):
                score -= 2
                factors.append("过于自我中心")
                break
        
        return score, factors
        
    def evaluate_boringness(self, user_input, dialogue_history, current_affection):
        """评估对话的无聊程度 (0-10分，分数越高越无聊)"""
        score = 0
        factors = []
        
        # 判断是否在亲密期
        is_high_affection = current_affection >= 80
        
        # 过短的回复 (亲密期降低惩罚)
        if len(user_input) < 8:
            if is_high_affection:
                # 亲密期对短消息更宽容
                score += 0.5
            else:
                score += 2
            factors.append("回复过短")
            
        # 简单情绪词判断("哇哦"、"好棒"等词在亲密期被视为可爱的反应而非无聊)
        simple_emotion_words = ["哇", "哇哦", "棒", "好棒", "真棒", "厉害", "太好了", "呀", "哦", "嗯"]
        if any(word in user_input for word in simple_emotion_words) and len(user_input) < 10:
            # 在亲密期，这些词被视为表达好感的方式，不计入无聊度
            if not is_high_affection:
                score += 2
                factors.append("情感词过于简单")
            else:
                # 高好感情况下，简单情绪词被认为是自然的亲密表达
                score -= 1
        
        # 缺乏信息量
        import jieba
        info_words = len(set(jieba.lcut(user_input)))
        if info_words < 5:
            score += 2
            factors.append("信息量少")
            
        # 重复的话题
        topics = self.keyword_analyzer.extract_topics(user_input)
        recent_topics = []
        for msg in dialogue_history[-5:]:
            if msg.get("role") == "user":
                extracted = self.keyword_analyzer.extract_topics(msg.get("content", ""))
                recent_topics.extend(extracted)
                
        # 检查话题重复
        topic_overlap = sum(1 for topic in topics if topic in recent_topics)
        if topic_overlap > 0 and len(topics) > 0:
            repetition_ratio = topic_overlap / len(topics)
            if repetition_ratio > 0.5:
                score += 2
                factors.append("话题重复")
                
        # 分析是否是仅情感词回复而缺乏实质内容
        emotion_words_ratio = sum(1 for word in user_input if word in "哈呵嘻嘿哦啊呀哇") / max(1, len(user_input))
        if emotion_words_ratio > 0.3:
            score += 2
            factors.append("纯情感词回复")
            
        # 重复字符检测
        char_counts = Counter(user_input)
        most_common = char_counts.most_common(1)
        if most_common and most_common[0][1] > 3 and most_common[0][0] not in ".,?!，。？！":
            score += 2
            factors.append(f"重复字符: {most_common[0][0]}")
            
        return score, factors
    
    def evaluate_context_relevance(self, user_input, dialogue_history):
        """评估上下文关联度"""
        # 如果历史消息少于2条，没有足够的上下文进行评估
        if len(dialogue_history) < 2:
            return 0
            
        # 获取最后一条AI消息
        last_ai_message = None
        for msg in reversed(dialogue_history):
            if msg.get("role") == "assistant":
                last_ai_message = msg.get("content", "")
                break
                
        if not last_ai_message:
            return 0
            
        # 提取双方消息的关键词
        ai_topics = self.keyword_analyzer.extract_topics(last_ai_message)
        user_topics = self.keyword_analyzer.extract_topics(user_input)
        
        # 计算话题重叠度
        overlap = sum(1 for topic in user_topics if any(ai_topic in topic or topic in ai_topic for ai_topic in ai_topics))
        
        # 计算上下文关联分数
        if len(user_topics) == 0:
            return 0
            
        relevance_score = overlap / len(user_topics) if user_topics else 0
        
        # 检查是否响应了问题
        if "?" in last_ai_message or "？" in last_ai_message:
            if len(user_input) > 10:
                relevance_score += 1  # 有效回应加分
                
        return relevance_score * 2  # 放大效果
        
    def evaluate_input_quality(self, user_input):
        """评估输入质量"""
        quality_score = 0
        
        # 长度评分
        if len(user_input) >= 30:
            quality_score += 2  # 较长的输入被认为更有质量
        elif len(user_input) >= 15:
            quality_score += 1
        elif len(user_input) <= 5:
            quality_score -= 1  # 过短的输入被认为低质量
            
        # 多样性评分
        unique_chars = len(set(user_input))
        if unique_chars >= 10:
            quality_score += 1  # 字符多样性高的输入被认为更有质量
            
        # 检查标点符号使用
        punctuation = sum(1 for c in user_input if c in "，。！？；：,.!?;:")
        if punctuation >= 2:
            quality_score += 1  # 适当使用标点的输入被认为更有质量
            
        # 检查句子复杂性
        sentence_count = sum(1 for c in user_input if c in "。.!！?？")
        if sentence_count >= 2:
            quality_score += 1  # 包含多个句子的输入被认为更有质量
            
        return quality_score 