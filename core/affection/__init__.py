"""
好感度系统
处理角色好感度的变化、事件和阶段管理
"""

from .system import AffectionSystem
from .events import AffectionEvent, SocialRisk, Phase
from .dialogue_evaluator import DialogueEvaluator
from .keyword_analyzer import KeywordAnalyzer

__all__ = [
    'AffectionSystem',
    'AffectionEvent',
    'SocialRisk',
    'Phase',
    'DialogueEvaluator',
    'KeywordAnalyzer'
] 