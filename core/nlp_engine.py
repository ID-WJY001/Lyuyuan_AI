# nlp_engine.py - 兼容层
from core.nlp import NaturalLanguageProcessor

# 重新导出所有实体以保持向后兼容性
__all__ = ['NaturalLanguageProcessor']