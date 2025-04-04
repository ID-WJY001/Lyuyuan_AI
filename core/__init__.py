"""
绿园中学物语 - 核心系统
包含游戏的核心功能组件
"""

# 导入核心模块
from core.nlp.processor import NaturalLanguageProcessor
from core.affection.system import AffectionSystem, AffectionEvent, SocialRisk, Phase
from core.scene.manager import SceneManager

# 直接导出核心类，使它们可以通过core包直接访问
# 例如：from core import NaturalLanguageProcessor
__all__ = [
    'NaturalLanguageProcessor',
    'AffectionSystem',
    'AffectionEvent',
    'SocialRisk',
    'Phase',
    'SceneManager'
]
