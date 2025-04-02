import jieba
from collections import Counter
import re

class KeywordAnalyzer:
    def __init__(self, config):
        """初始化关键词分析器"""
        self.keyword_usage_history = {}  # 记录关键词使用频率
        self.config = config
    
    def extract_topics(self, text):
        """从文本中提取主要话题"""
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
        """检查文本中是否包含不适当内容"""
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
        """获取关键词的类别"""
        keyword_categories = self.config.get("keyword_categories", {})
        for category, words in keyword_categories.items():
            if keyword in words:
                return category
        return None
    
    def analyze_keywords(self, keywords):
        """分析关键词并计算影响"""
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
            category = self.get_keyword_category(keyword)
            if category and category not in used_keywords:
                if category == "positive":
                    keyword_delta += 1.5  # 正面词汇加分
                    used_keywords.add(category)
                elif category == "negative":
                    keyword_delta -= 2.5  # 负面词汇扣分
                    used_keywords.add(category)
                elif category == "interest" and category not in used_keywords:
                    keyword_delta += 2.0  # 兴趣关键词奖励
                    used_keywords.add(category)
                
                matched_keywords.append(keyword)
        
        return {
            "delta": keyword_delta,
            "matched_keywords": matched_keywords
        } 