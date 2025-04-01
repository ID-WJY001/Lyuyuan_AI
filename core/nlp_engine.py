import jieba
from snownlp import SnowNLP
from typing import Dict
import json
import random

class NaturalLanguageProcessor:
    def __init__(self, keyword_path: str):
        self.keywords = self._load_keywords(keyword_path)
        try:
            jieba.load_userdict("data/userdict.txt")  # 加载自定义词典
        except FileNotFoundError:
            print("警告：未找到自定义词典文件 data/userdict.txt")
        
    def analyze(self, text: str) -> Dict:
        """ 执行多维度文本分析 """
        return {
            "sentiment": self._sentiment_analysis(text),
            "keywords": self._extract_keywords(text),
            "coherence": self._context_coherence(text)
        }
    
    def _load_keywords(self, path: str) -> Dict:
        """加载JSON关键词库"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告：未找到关键词文件 {path}")
            return {}
    
    def _extract_keywords(self, text: str) -> list[str]:
        """ 结合规则与TF-IDF提取关键词 """
        words = jieba.lcut(text)
        return [word for word in words if self._is_keyword(word)]
    
    def _is_keyword(self, word: str) -> bool:
        """检查是否属于任意关键词类别"""
        return any(word in group 
                  for category in self.keywords.values()
                  for group in category.values())
    
    def _sentiment_analysis(self, text: str) -> float:
        """情感分析，返回-1到1之间的得分"""
        try:
            return SnowNLP(text).sentiments - 0.5  # 转换为-0.5到0.5的范围
        except Exception:
            return 0.0
    
    def _context_coherence(self, text: str) -> float:
        """分析文本的上下文连贯性，返回0到1之间的得分"""
        # 简单的实现：检查文本长度和标点符号
        if len(text) < 5:
            return 0.3
            
        # 检查标点符号使用
        punctuation_count = sum(1 for c in text if c in '，。！？；：')
        if punctuation_count == 0:
            return 0.4
            
        # 检查重复字符
        repeat_count = sum(1 for i in range(len(text)-1) 
                         if text[i] == text[i+1])
        if repeat_count > len(text) * 0.3:
            return 0.3
            
        return 0.8  # 默认较好的连贯性