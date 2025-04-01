import json
import os
from datetime import datetime

class GameStorage:
    def __init__(self, save_dir="saves"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)  # 确保存档目录存在
    
    def _get_filepath(self, slot=1):
        return os.path.join(self.save_dir, f"save_{slot}.json")

    def save_game(self, data, slot=1):
        """ 保存游戏数据 """
        data["meta"] = {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        try:
            with open(self._get_filepath(slot), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存失败: {str(e)}")
            return False

    def load_game(self, slot=1):
        """ 加载游戏数据 """
        try:
            with open(self._get_filepath(slot), 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 数据兼容性检查
                if "history" not in data:
                    raise ValueError("存档格式错误")
                return data
        except FileNotFoundError:
            print("存档不存在")
            return None
        except Exception as e:
            print(f"读取失败: {str(e)}")
            return None

    def list_saves(self):
        """ 列出所有存档 """
        return [f for f in os.listdir(self.save_dir) if f.endswith(".json")]