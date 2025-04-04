"""
游戏存储工具
负责游戏存档和读档功能
"""

import os
import sys
import json
import logging
from datetime import datetime

# 添加项目根目录到路径以便导入
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

class GameStorage:
    """游戏存储管理类"""
    
    def __init__(self, save_dir=None):
        """
        初始化存储系统
        参数:
            save_dir: 保存目录路径，默认为"saves"
        """
        if save_dir is None:
            save_dir = os.path.join(ROOT_DIR, "saves")
            
        self.save_dir = save_dir
        self.logger = logging.getLogger("GameStorage")
        
        # 确保存档目录存在
        os.makedirs(self.save_dir, exist_ok=True)
    
    def save_game(self, game_state, slot="auto"):
        """
        保存游戏状态
        参数:
            game_state: 游戏状态字典
            slot: 存档槽位，默认为"auto"
        返回值:
            成功返回True，失败返回False
        """
        try:
            # 添加保存时间
            game_state['save_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 构建存档文件路径
            file_path = os.path.join(self.save_dir, f"{slot}.json")
            
            # 写入存档文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"游戏已保存到槽位 {slot}")
            return True
        except Exception as e:
            self.logger.error(f"保存游戏失败: {e}")
            return False
    
    def load_game(self, slot="auto"):
        """
        加载游戏状态
        参数:
            slot: 存档槽位，默认为"auto"
        返回值:
            成功返回游戏状态字典，失败返回None
        """
        try:
            # 构建存档文件路径
            file_path = os.path.join(self.save_dir, f"{slot}.json")
            
            # 检查存档文件是否存在
            if not os.path.exists(file_path):
                self.logger.warning(f"找不到存档 {slot}")
                return None
                
            # 读取存档文件
            with open(file_path, 'r', encoding='utf-8') as f:
                game_state = json.load(f)
                
            self.logger.info(f"游戏已从槽位 {slot} 加载")
            return game_state
        except Exception as e:
            self.logger.error(f"加载游戏失败: {e}")
            return None
    
    def list_saves(self):
        """
        列出所有存档
        返回值:
            存档信息字典列表，按保存时间降序排序
        """
        saves = []
        
        try:
            # 遍历所有存档文件
            for file in os.listdir(self.save_dir):
                if file.endswith('.json'):
                    file_path = os.path.join(self.save_dir, file)
                    slot = file.split('.')[0]
                    
                    try:
                        # 读取存档信息
                        with open(file_path, 'r', encoding='utf-8') as f:
                            game_state = json.load(f)
                            
                        # 提取存档信息
                        save_info = {
                            'slot': slot,
                            'save_time': game_state.get('save_time', '未知'),
                            'character': game_state.get('character_name', '未知'),
                            'affection': game_state.get('affection', 0),
                            'scene': game_state.get('current_scene', '未知')
                        }
                        
                        saves.append(save_info)
                    except Exception as e:
                        self.logger.error(f"读取存档 {slot} 失败: {e}")
            
            # 按保存时间排序，最新的在前
            saves.sort(key=lambda x: x['save_time'], reverse=True)
            
            return saves
        except Exception as e:
            self.logger.error(f"列出存档失败: {e}")
            return []
    
    def delete_save(self, slot):
        """
        删除指定的存档
        参数:
            slot: 存档槽位
        返回值:
            成功返回True，失败返回False
        """
        try:
            # 构建存档文件路径
            file_path = os.path.join(self.save_dir, f"{slot}.json")
            
            # 检查存档文件是否存在
            if not os.path.exists(file_path):
                self.logger.warning(f"找不到存档 {slot}")
                return False
                
            # 删除存档文件
            os.remove(file_path)
            self.logger.info(f"存档 {slot} 已删除")
            return True
        except Exception as e:
            self.logger.error(f"删除存档 {slot} 失败: {e}")
            return False 