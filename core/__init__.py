# core/__init__.py
from .scene_manager import SceneManager
from .nlp_engine import NaturalLanguageProcessor
from .affection_system import AffectionSystem, AffectionEvent, SocialRisk, Phase

__all__ = [
    'SceneManager',
    'NaturalLanguageProcessor',
    'AffectionSystem',
    'AffectionEvent',
    'SocialRisk',
    'Phase'
]
