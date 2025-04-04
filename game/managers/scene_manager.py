"""
场景管理器兼容层
为了保持向后兼容性，重定向到core.scene中的SceneManager实现
"""

import sys
import os
import logging

# 设置项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

# 导入核心场景管理器
try:
    from core.scene import SceneManager as CoreSceneManager
    
    # 为了向后兼容，创建一个包装类
    class SceneManager(CoreSceneManager):
        """
        场景管理器包装类
        提供向后兼容的接口，实际使用core.scene中的SceneManager实现
        """
        def __init__(self, *args, **kwargs):
            """初始化，直接调用CoreSceneManager的初始化"""
            super().__init__(*args, **kwargs)
            logging.getLogger("SceneManager").info("使用核心SceneManager实现")
            
except ImportError as e:
    logging.error(f"导入核心SceneManager失败: {e}")
    
    # 如果导入失败，保留旧的实现（但这种情况应该不会发生）
    class SceneManager:
        """旧版SceneManager，仅在导入新版失败时使用"""
        def __init__(self, initial_scene="烘焙社摊位", initial_affection=30):
            logging.error("使用旧版SceneManager实现（不应该发生）")
            # 旧版初始化代码...

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
        
    def update_affection(self, value: int):
        """更新好感度值，用于与亲密度系统同步"""
        self.current_affection = value 