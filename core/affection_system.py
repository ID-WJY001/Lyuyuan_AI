# affection_system.py - 兼容层
# 从新的模块化结构中导入
from core.affection import AffectionSystem, AffectionEvent, SocialRisk, Phase

# 重新导出所有实体以保持向后兼容性
__all__ = ['AffectionSystem', 'AffectionEvent', 'SocialRisk', 'Phase']