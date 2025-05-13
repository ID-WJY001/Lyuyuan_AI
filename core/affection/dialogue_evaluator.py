"""
对话评估器模块。

定义了 `DialogueEvaluator` 类，该类负责从多个维度评估用户对话的质量，
包括"绅士风度"（礼貌性）、"无聊度"、与上下文的"关联度"以及输入的整体"质量"。
评估结果通常供 `AffectionSystem` 用来计算亲密度变化。
它依赖一个 `KeywordAnalyzer` 实例来辅助进行话题提取等操作。
"""
import re
from collections import Counter

class DialogueEvaluator:
    def __init__(self, keyword_analyzer):
        """
        初始化对话评估器。

        Args:
            keyword_analyzer (KeywordAnalyzer): 一个关键词分析器实例，
                                              主要用于在评估过程中提取话题。
        """
        self.keyword_analyzer = keyword_analyzer
    
    def evaluate_gentlemanly(self, user_input, dialogue_history):
        """
        评估用户输入的"绅士风度"或礼貌程度。

        通过检查是否存在礼貌用语、尊重性表达、是否恰当回应问题，
        以及是否存在命令式语气、过于自我中心的表达等因素来综合计分。

        Args:
            user_input (str): 用户的最新对话输入文本。
            dialogue_history (list): 对话历史记录。

        Returns:
            tuple[float, list[str]]: 
                - score (float): 绅士风度总得分，正值表示更礼貌，负值表示欠缺礼貌。
                - factors (list[str]): 一个包含具体评分因素描述的字符串列表。
        """
        score = 0
        factors = []
        
        # 检查礼貌用语 (例如: "请", "谢谢")
        polite_words = ["请", "谢谢", "抱歉", "打扰", "麻烦", "您好", "感谢"]
        for word in polite_words:
            if word in user_input:
                score += 1
                factors.append(f"礼貌用语: {word}")
                break
                
        # 检查尊重对方的表达 (例如: "你觉得", "你认为")
        respect_phrases = ["你觉得", "你认为", "你喜欢", "如果你", "你的想法"]
        for phrase in respect_phrases:
            if phrase in user_input:
                score += 1.5
                factors.append("尊重对方的表达")
                break
                
        # 检查是否回应了AI提出的问题
        if len(dialogue_history) >= 2:
            last_msg = dialogue_history[-1]
            if last_msg.get("role") == "assistant" and ("?" in last_msg["content"] or "？" in last_msg["content"]):
                # 如果用户回复中也包含问号 (可能在反问或确认)，或者回复长度足够，视为有效回应
                if "?" in user_input or "？" in user_input or len(user_input) > 15:
                    score += 2
                    factors.append("回应了AI提出的问题")
        
        # 负面因素：检查命令式语气 (例如: "给我...", "你必须...")
        command_patterns = [r"^[给去]我", r"^告诉我", r"^快[点些]", r"^你[必须应该]"]
        for pattern in command_patterns:
            if re.search(pattern, user_input):
                score -= 3
                factors.append("命令式语气")
                break
                
        # 负面因素：检查过于自我中心的表达 (例如: "我想要...", 连续多个 "我")
        self_centered_patterns = [r"^我[想要需]", r"^我.*我.*我", r"^[^？]+\?"] # 最后一个匹配如"我很好你呢？"这种句式，避免误判
        for pattern in self_centered_patterns:
            if re.search(pattern, user_input):
                score -= 2
                factors.append("过于自我中心")
                break
        
        return score, factors
        
    def evaluate_boringness(self, user_input, dialogue_history, current_affection):
        """
        评估用户输入的"无聊程度"。得分越高表示越无聊 (0-10分范围)。

        综合考虑回复长度、是否仅为简单情绪词、信息量、话题重复度、
        纯语气词占比、字符重复等因素。
        在高好感度 (>=80) 时，对某些因素（如短回复、简单情绪词）的判断会更宽容。

        Args:
            user_input (str): 用户的最新对话输入文本。
            dialogue_history (list): 对话历史记录。
            current_affection (float): 当前的亲密度值。

        Returns:
            tuple[float, list[str]]:
                - score (float): 无聊度总得分。
                - factors (list[str]): 一个包含具体评分因素描述的字符串列表。
        """
        score = 0
        factors = []
        
        is_high_affection = current_affection >= 80 # 判断是否处于高好感度阶段
        
        # 因素1: 回复过短
        if len(user_input) < 8:
            score += 0.5 if is_high_affection else 2 # 高好感度时，对短回复容忍度稍高
            factors.append("回复过短")
            
        # 因素2: 是否为简单情绪词的简单回复 (例如 "哇", "嗯")
        simple_emotion_words = ["哇", "哇哦", "棒", "好棒", "真棒", "厉害", "太好了", "呀", "哦", "嗯"]
        is_simple_emotion_reply = any(word in user_input for word in simple_emotion_words) and len(user_input) < 10
        
        if is_simple_emotion_reply:
            if not is_high_affection:
                score += 2
                factors.append("回复过于简单，仅为情绪词")
            else:
                # 高好感度时，这类简单回应可能被视为亲昵表现，反而降低无聊度
                score -= 1 
                factors.append("高好感下的亲昵简单回应") 
        
        # 因素3: 缺乏信息量 (基于分词后的独立词数量)
        import jieba # 确保jieba被导入
        try:
            info_words_count = len(set(jieba.lcut(user_input)))
            if info_words_count < 5:
                score += 2
                factors.append("信息量不足 (独立词少于5个)")
        except Exception:
            pass # Jieba分词如果出错，则跳过此项检查
            
        # 因素4: 重复的话题
        try:
            current_topics = self.keyword_analyzer.extract_topics(user_input)
            recent_topics_history = []
            for msg in dialogue_history[-5:]: # 分析最近5条对话历史
                if msg.get("role") == "user":
                    extracted_recent = self.keyword_analyzer.extract_topics(msg.get("content", ""))
                    recent_topics_history.extend(extracted_recent)
            
            if current_topics and recent_topics_history: # 仅在双方都有话题时判断
                topic_overlap_count = sum(1 for topic in current_topics if topic in recent_topics_history)
                if topic_overlap_count > 0 and len(current_topics) > 0:
                    repetition_ratio = topic_overlap_count / len(current_topics)
                    if repetition_ratio > 0.5: # 如果一半以上的话题是重复的
                        score += 2
                        factors.append("话题与近期重复度较高")
        except Exception:
            pass # 话题提取如果出错，则跳过此项检查
                
        # 因素5: 是否主要是纯语气词回复 (例如 "哈哈哈", "嗯嗯嗯")
        emotion_only_char_count = sum(1 for char_in_input in user_input if char_in_input in "哈呵嘻嘿哦啊呀哇嗯额呃")
        if len(user_input) > 0 and emotion_only_char_count / len(user_input) > 0.6: # 语气词占比超过60%
            score += 2
            factors.append("回复主要由纯语气词构成")
            
        # 因素6: 单个字符的过度重复
        char_counts = Counter(user_input)
        if char_counts:
            most_common_char, most_common_count = char_counts.most_common(1)[0]
            if most_common_count > 3 and most_common_char not in ".,?!，。？！ ": # 排除常见标点和空格
                score += 2
                factors.append(f"字符 '{most_common_char}' 重复次数过多 ({most_common_count}次)")
            
        return max(0, min(10, score)), factors #确保分数在0-10之间
        
    def evaluate_context_relevance(self, user_input, dialogue_history):
        """
        评估用户输入与当前对话上下文的关联程度。

        主要通过比较用户输入的话题与AI上一条回复的话题的重叠度。
        如果AI上一条是提问，且用户输入被认为是有效回应，则会增加关联度得分。

        Args:
            user_input (str): 用户的最新对话输入文本。
            dialogue_history (list): 对话历史记录。

        Returns:
            float: 上下文关联度得分 (通常乘以一个系数放大效果)。
        """
        if len(dialogue_history) < 1: # 至少需要一条历史（AI的上一条）
            return 0
            
        last_ai_message_content = None
        for msg in reversed(dialogue_history):
            if msg.get("role") == "assistant":
                last_ai_message_content = msg.get("content", "")
                break
                
        if not last_ai_message_content:
            return 0 # 没有找到AI的上一条回复
            
        try:
            # 提取AI上一条消息和用户当前输入的话题
            ai_message_topics = self.keyword_analyzer.extract_topics(last_ai_message_content)
            user_input_topics = self.keyword_analyzer.extract_topics(user_input)
            
            if not user_input_topics or not ai_message_topics: # 如果任一方无法提取出话题
                return 0
            
            # 计算话题重叠数量 (更宽松的匹配，包含即可)
            overlap_count = sum(1 for u_topic in user_input_topics 
                              if any(u_topic in ai_topic or ai_topic in u_topic 
                                     for ai_topic in ai_message_topics))
            
            # 重叠值，用于计算关联度得分。范围可能是0到用户话题数量
            context_score = overlap_count / len(user_input_topics) if user_input_topics else 0
            
            # AI上一条是提问，且用户有较好回应
            is_ai_question = "?" in last_ai_message_content or "？" in last_ai_message_content
            if is_ai_question and (len(user_input) > 10 or context_score > 0): 
                context_score += 0.3 # 对问题的回应，额外加分
            
            return context_score * 2 # 适当放大效果
        
        except Exception:
            return 0 # 计算过程中出错，返回0分
    
    def evaluate_input_quality(self, user_input):
        """
        评估用户输入的整体质量。

        考虑因素包括长度、词语多样性、标点使用恰当性、
        句子结构完整性等。高质量的回复通常会增加亲密度。

        Args:
            user_input (str): 用户的对话输入文本。

        Returns:
            float: 输入质量得分 (通常为0到5之间)。
        """
        # 基础分：1分
        score = 1.0
        
        # 因素1: 长度加分
        if len(user_input) >= 15:
            score += 0.5
            if len(user_input) >= 30:
                score += 0.5
                
        # 因素2: 词语多样性 (基于分词结果)
        try:
            import jieba
            words = jieba.lcut(user_input)
            unique_words = set(words)
            
            if len(unique_words) >= 5:
                score += 0.5
                if len(unique_words) >= 10:
                    score += 0.5
                    
            # 词语重复率检查
            if len(words) > 0:
                repetition_rate = 1 - (len(unique_words) / len(words))
                if repetition_rate > 0.5: # 词语重复率超过50%
                    score -= 0.5
        except Exception:
            pass # 分词出错则跳过

        # 因素3: 标点使用 (恰当使用标点往往意味着更正式和完整的表达)
        punctuation = "，。！？；：,.!?;:"
        if any(p in user_input for p in punctuation):
            score += 0.5
            
        # 因素4: 句子结构检查 (简单实现: 是否包含主谓结构)
        sentence_structure_patterns = [
            r"我[^，。！？]+[了吗呢吧]", # 例如: "我喜欢你的笑容"
            r"你[^，。！？]+[了吗呢吧]", # 例如: "你觉得这家餐厅怎么样？"
            r".+是.+", # 例如: "今天是个好天气"
        ]
        
        if any(re.search(pattern, user_input) for pattern in sentence_structure_patterns):
            score += 0.5
            
        return max(0, min(5, score)) # 确保分数在0到5之间 