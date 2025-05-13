import json
import os
from datetime import datetime

class GameStorage:
    def __init__(self, save_dir="saves"):
        """
        初始化 GameStorage 实例。

        Args:
            save_dir (str, optional): 存档文件存放的目录路径。默认为 "saves"。
        """
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)  # 确保存档目录存在
    
    def _get_filepath(self, slot=1):
        """
        根据槽位号生成存档文件的完整路径。

        Args:
            slot (int or str, optional): 存档槽位的标识符。默认为 1。

        Returns:
            str: 存档文件的完整路径。
        """
        return os.path.join(self.save_dir, f"save_{slot}.json")

    def save_game(self, data, slot=1):
        """
        将游戏数据保存到指定的存档槽位。

        数据会以 JSON 格式存储，并包含一些元数据，如保存时间和版本号。
        如果数据中包含 `datetime` 对象 (在 `data['state']['date']`)，会将其格式化为 YYYY-MM-DD 字符串。

        Args:
            data (dict): 需要保存的游戏数据。
            slot (int or str, optional): 存档槽位的标识符。默认为 1。

        Returns:
            bool: 如果保存成功则返回 True，否则返回 False。
        """
        data["meta"] = {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        # 处理日期时间对象
        if "state" in data and "date" in data["state"] and isinstance(data["state"]["date"], datetime):
            data["state"]["date"] = data["state"]["date"].strftime("%Y-%m-%d")
        
        try:
            with open(self._get_filepath(slot), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存失败: {str(e)}")
            return False

    def load_game(self, slot=1):
        """
        从指定的存档槽位加载游戏数据。

        Args:
            slot (int or str, optional): 存档槽位的标识符。默认为 1。

        Returns:
            dict or None: 如果加载成功，则返回包含游戏数据的字典；
                          如果存档文件不存在或加载失败，则返回 None。
        """
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
        """
        列出存档目录中所有可用的存档文件。

        Returns:
            list: 包含所有存档文件名的列表 (例如, ["save_1.json", "save_happy_ending.json"])。
        """
        return [f for f in os.listdir(self.save_dir) if f.endswith(".json")]