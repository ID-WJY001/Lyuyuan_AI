"""
自然语言处理 (NLP) 模块。

该模块定义了 `NaturalLanguageProcessor` 类，用于对文本进行多维度分析，
包括情感分析、关键词提取和上下文连贯性评估。
它依赖 `jieba`进行分词，`SnowNLP` 进行情感分析，并可以加载自定义词典和关键词库。
"""
import jieba
from snownlp import SnowNLP
from typing import Dict
import json
import random
import os

class NaturalLanguageProcessor:
    def __init__(self, keyword_path: str):
        """
        初始化自然语言处理器。

        Args:
            keyword_path (str): 指向关键词库JSON文件的路径。
                                该文件定义了用于关键词提取的词汇。
        
        在初始化过程中，会加载关键词库，并尝试从项目的 `data/userdict.txt` 
        路径加载 `jieba` 的自定义用户词典以提高分词准确性。
        """
        self.keywords = self._load_keywords(keyword_path)
        try:
            # 获取项目根目录
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            userdict_path = os.path.join(root_dir, "data/userdict.txt")
            jieba.load_userdict(userdict_path)  # 加载自定义词典
            print(f"成功加载自定义词典: {userdict_path}")
        except FileNotFoundError as e:
            print(f"警告：未找到自定义词典文件: {e}")
        
    def analyze(self, text: str) -> Dict:
        """
        对输入的文本执行多维度的自然语言分析。

        Args:
            text (str): 需要分析的文本字符串。

        Returns:
            Dict: 一个包含以下分析结果的字典：
                  - "sentiment": 情感得分 (范围通常在 -0.5 到 0.5)。
                  - "keywords": 从文本中提取的关键词列表。
                  - "coherence": 文本的上下文连贯性得分 (范围通常在 0 到 1)。
        """
        return {
            "sentiment": self._sentiment_analysis(text),
            "keywords": self._extract_keywords(text),
            "coherence": self._context_coherence(text)
        }
    
    def _load_keywords(self, path: str) -> Dict:
        """
        从指定的JSON文件路径加载关键词库。
        
        关键词库的期望格式是一个嵌套字典，例如：
        `{"category1": {"groupA": ["keyword1", "keyword2"]}}`

        Args:
            path (str): 关键词库JSON文件的路径。

        Returns:
            Dict: 加载的关键词字典。如果文件未找到或格式错误，则返回空字典并打印警告。
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告：未找到关键词文件 {path}")
            return {}
    
    def _extract_keywords(self, text: str) -> list[str]:
        """
        从输入文本中提取关键词。
        
        该方法首先使用 `jieba` 对文本进行分词，然后遍历分词结果，
        通过 `_is_keyword` 方法检查每个词是否在预加载的关键词库中定义。

        Args:
            text (str): 需要提取关键词的文本。

        Returns:
            list[str]: 包含所有在文本中找到的、且存在于关键词库中的关键词列表。
        """
        words = jieba.lcut(text)
        return [word for word in words if self._is_keyword(word)]
    
    def _is_keyword(self, word: str) -> bool:
        """
        检查给定的词是否属于预加载关键词库中的任何一个类别或分组。

        Args:
            word (str): 需要检查的单个词汇。

        Returns:
            bool: 如果该词存在于关键词库的任何一个分组中，则返回 True，否则返回 False。
        """
        return any(word in group 
                  for category in self.keywords.values()
                  for group in category.values())
    
    def _sentiment_analysis(self, text: str) -> float:
        """
        对输入文本进行情感分析，并返回一个标准化的情感得分。

        使用 `SnowNLP` 库计算原始情感值 (通常在 0 到 1 之间)，
        然后将其减去 0.5，使得结果范围大致在 -0.5 (负面) 到 0.5 (正面) 之间。
        如果分析过程中发生任何异常，则默认返回 0.0 (中性)。

        Args:
            text (str): 需要进行情感分析的文本。

        Returns:
            float: 情感得分。
        """
        try:
            return SnowNLP(text).sentiments - 0.5  # 转换为-0.5到0.5的范围
        except Exception:
            return 0.0
    
    def _context_coherence(self, text: str) -> float:
        """
        评估输入文本的上下文连贯性。

        这是一个基于简单启发式规则的实现：
        - 文本过短，则连贯性较低。
        - 缺乏标点符号，则连贯性较低。
        - 重复字符过多，则连贯性较低。
        - 其他情况，给予一个较高的默认连贯性得分。
        
        Args:
            text (str): 需要评估连贯性的文本。

        Returns:
            float: 上下文连贯性得分 (0 到 1 之间)。
        """
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