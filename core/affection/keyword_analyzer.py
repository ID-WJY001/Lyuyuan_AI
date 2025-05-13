"""
关键词分析器模块。

定义了 `KeywordAnalyzer` 类，负责从文本中提取话题、检测不当内容（如侮辱、
性暗示、不尊重言论），以及根据预定义的关键词类别和使用频率分析关键词对
情感系统的潜在影响。
"""
import jieba
from collections import Counter
import re

class KeywordAnalyzer:
    def __init__(self, config):
        """
        初始化关键词分析器。

        Args:
            config (dict): 一个配置字典，通常来源于情感系统的配置文件。
                           期望包含 `keyword_categories` 等关键词相关设置。
        
        `keyword_usage_history` 用于追踪每个关键词的使用频率，以实现效果衰减。
        """
        self.keyword_usage_history = {}  # 记录关键词使用频率
        self.config = config
    
    def extract_topics(self, text):
        """
        从输入文本中提取主要话题（一个简单的实现）。

        使用 `jieba` 分词，并进行基本的过滤（去除过短词、数字、常见停用词），
        然后返回最多前3个符合条件的词作为识别出的话题。

        Args:
            text (str): 需要提取话题的原始文本。

        Returns:
            list[str]: 一个包含识别出的话题字符串的列表 (最多3个)。
                       如果提取失败或无有效话题，则返回空列表。
        """
        try:
            # 简单实现，使用结巴分词
            seg_list = jieba.lcut(text)
            filtered_words = []
            for word in seg_list:
                if len(word) >= 2 and not re.match(r'[0-9]+', word) and word not in ["什么", "怎么", "为什么", "如何"]:
                    filtered_words.append(word)
            return filtered_words[:3]  # 取前3个作为主题
        except Exception:
            return []
    
    def check_inappropriate(self, text):
        """
        检查输入文本中是否包含不适当或冒犯性的内容。

        通过正则表达式匹配预定义的多种不当言论模式，包括：
        - 侮辱性词汇 (例如 "笨蛋", "垃圾")
        - 不当性暗示 (例如 "脱光", "操你")
        - 不尊重的指令或言论 (例如 "闭嘴", "滚开")

        Args:
            text (str): 需要检查的原始文本。

        Returns:
            list[str]: 一个包含所有检测到的不当内容类别描述字符串的列表。
                       例如：["侮辱性言论", "不适当的性暗示"]。
                       如果未检测到不当内容，则返回空列表。
        """
        # 侮辱性词汇
        insult_patterns = [
            r"笨蛋", r"白痴", r"废物", r"垃圾", r"傻[逼比屄]", r"贱[人货]", 
            r"蠢[猪货]", r"智障", r"脑残", r"神经病", r"白痴", r"猪脑子", 
            r"婊子", r"骚[货逼]", r"臭表子", r"破鞋", r"贱货", r"烂货", r"荡妇"
        ]
        
        # 不当性暗示
        sexual_patterns = [
            r"脱[光衣]", r"射[精了]", r"高潮", r"操[你他她它]", r"艹", r"日[你他她它]", 
            r"[睡日草操艹透]服", r"做爱", r"爱爱", r"肏", r"插[进入你]", r"鸡巴", r"屌",
            r"[大小]奶", r"摸奶", r"摸胸", r"丝袜", r"调教", r"抚摸", r"摸.*腿", r"脱.*裤",
            r"揉.*胸", r"舌吻", r"啪啪", r"打炮", r"一夜情", r"约炮", r"想上", r"想操", r"猥亵"
        ]
        
        # 不尊重的指令
        disrespectful_patterns = [
            r"闭嘴", r"滚开", r"滚蛋", r"放屁", r"去死", r"^你敢", r"我命令你", 
            r"给我服[从软]", r"^跪[下来着]", r"听话", r"乖乖", r"别[废话BB逼逼]", 
            r"别装", r"装什么", r"^废话", r"^放[屁P]", r"[你谁]算[老几什么]"
        ]
        
        # 检查冒犯性内容
        found_inappropriate = []
        
        # 检查所有模式
        for pattern in insult_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                found_inappropriate.append("侮辱性言论")
                break
                
        for pattern in sexual_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                found_inappropriate.append("不适当的性暗示")
                break
                
        for pattern in disrespectful_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                found_inappropriate.append("不尊重的言论")
                break
                
        return found_inappropriate
    
    def get_keyword_category(self, keyword):
        """
        根据提供的关键词，从配置中查找并返回其所属的预定义类别。

        配置项 `keyword_categories` 期望的格式为：
        `{"positive": ["开心", "喜欢"], "negative": ["讨厌", "难过"]}`

        Args:
            keyword (str): 需要查询类别的单个关键词。

        Returns:
            str or None: 如果找到，则返回关键词的类别名称 (例如 "positive")；
                         否则返回 None。
        """
        keyword_categories = self.config.get("keyword_categories", {})
        for category, words in keyword_categories.items():
            if keyword in words:
                return category
        return None
    
    def analyze_keywords(self, keywords):
        """
        分析提供的关键词列表，计算它们对亲密度的综合影响值 (delta)。

        处理逻辑包括：
        1. 效果衰减：如果一个关键词在近期被多次使用 (超过3次)，其效果会降低或消失。
        2. 分类计分：根据关键词的预定义类别 (正面、负面、兴趣等)给予不同的分数。
           使用 `used_keywords` 集合确保同一类别的多个不同关键词在本轮分析中不重复计分。
        
        Args:
            keywords (list[str]): 从文本中提取出的关键词列表。

        Returns:
            dict: 一个包含两项的字典：
                  - "delta" (float): 所有分析的关键词产生的总亲密度影响值。
                  - "matched_keywords" (list[str]): 在分析过程中实际被处理并计分的关键词列表。
        """
        keyword_delta = 0
        matched_keywords = []
        used_keywords = set()  # 用于确保同一情感类别的关键词在本轮分析中只计一次分
        
        for keyword in keywords:
            # 检查关键词是否已经因过度使用而效果衰减
            if keyword in self.keyword_usage_history:
                uses = self.keyword_usage_history[keyword]
                if uses >= 3:  # 同一关键词使用超过3次，不再产生影响
                    continue # 跳过此关键词
                self.keyword_usage_history[keyword] = uses + 1
            else:
                self.keyword_usage_history[keyword] = 1 # 首次使用，计数为1
            
            # 获取关键词分类并据此计算影响
            category = self.get_keyword_category(keyword)
            if category and category not in used_keywords: # 必须有分类且该分类未被用于本轮计分
                if category == "positive":
                    keyword_delta += self.config.get("keyword_effects", {}).get("positive", 1.5)
                    used_keywords.add(category)
                elif category == "negative":
                    keyword_delta -= self.config.get("keyword_effects", {}).get("negative", 2.5)
                    used_keywords.add(category)
                elif category == "interest": # 兴趣类可以独立于 positive/negative 单独加分
                    keyword_delta += self.config.get("keyword_effects", {}).get("interest", 2.0)
                    # 注意：如果一个词同时是positive和interest，这里只按interest加了一次used_keywords，
                    # 如果希望分开判断，used_keywords可能需要更复杂的逻辑或按类别分别判断。
                    # 但当前实现是合理的，避免了例如"喜欢烘焙"中的"喜欢"和"烘焙"分别按正面和兴趣加两次大分。
                    # 更好的做法可能是让 get_keyword_category 返回所有匹配的类别，然后分别处理。
                    # 不过当前逻辑下，一个关键词只会属于一个主要类别。若要支持多类别，配置和get_keyword_category需调整。
                    used_keywords.add(category) # 兴趣类也只让同类词生效一次
                
                matched_keywords.append(keyword) # 记录实际参与计分的关键词
        
        return {
            "delta": keyword_delta,
            "matched_keywords": matched_keywords
        } 