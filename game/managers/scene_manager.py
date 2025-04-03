"""
场景管理器模块
负责管理游戏中的场景切换、场景限制和场景相关数据
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger("SceneManager")

class SceneManager:
    def __init__(self):
        """初始化场景管理器"""
        self.current_scene = "烘焙社摊位"
        self._init_scene_data()
        
    def _init_scene_data(self):
        """初始化场景相关数据"""
        # 场景跳转相关
        self.next_scene_hints = []
        self.scene_transition_keywords = {
            "下周": ["教室", "操场", "图书馆", "烘焙社"],
            "明天": ["教室", "食堂", "操场", "烘焙社"],
            "放学后": ["操场", "图书馆", "街道", "烘焙社"],
            "周末": ["公园", "游乐场", "电影院", "咖啡厅"],
            "下次": ["教室", "操场", "图书馆", "公园", "烘焙社"],
            "再见面": ["教室", "操场", "街道", "公园", "烘焙社"],
            "社团活动": ["烘焙社"]
        }
        self.farewell_keywords = ["再见", "拜拜", "回头见", "下次见", "明天见", "下周见", "周末见", "回见", "下次再聊"]
        
        # 场景时间限制
        self.scene_time_restrictions = {
            "烘焙社摊位": ["上午", "中午", "下午"],
            "烘焙社": ["下午", "傍晚"],
            "教室": ["上午", "中午", "下午"],
            "操场": ["上午", "中午", "下午", "傍晚"],
            "图书馆": ["上午", "中午", "下午", "傍晚"],
            "公园": ["上午", "中午", "下午", "傍晚"],
            "食堂": ["中午"],
            "街道": ["下午", "傍晚", "晚上"],
            "游乐场": ["上午", "中午", "下午"],
            "电影院": ["下午", "傍晚", "晚上"],
            "咖啡厅": ["上午", "中午", "下午", "傍晚", "晚上"]
        }
        
    def can_enter_scene(self, scene: str, current_time: str) -> bool:
        """检查是否可以在当前时间进入指定场景"""
        if scene not in self.scene_time_restrictions:
            return False
        return current_time in self.scene_time_restrictions[scene]
        
    def get_available_scenes(self, current_time: str) -> List[str]:
        """获取当前时间可用的场景列表"""
        return [scene for scene, times in self.scene_time_restrictions.items() 
                if current_time in times]
                
    def change_scene(self, new_scene: str) -> bool:
        """切换场景"""
        if new_scene in self.scene_time_restrictions:
            self.current_scene = new_scene
            return True
        return False
        
    def get_scene_transition_hints(self, keyword: str) -> List[str]:
        """获取场景转换提示"""
        return self.scene_transition_keywords.get(keyword, [])
        
    def is_farewell_keyword(self, text: str) -> bool:
        """检查是否是告别关键词"""
        return any(keyword in text for keyword in self.farewell_keywords) 