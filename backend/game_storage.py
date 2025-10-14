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
        # 合并/补全 meta（避免覆盖上层写入的角色、名称等信息）
        meta = data.get("meta", {})
        meta.update({
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",
        })
        data["meta"] = meta
        
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

    def list_saves_detailed(self):
        """列出包含详细信息的存档列表。

        返回每个存档的：
        - id: 去除扩展名后的标识（如 save_1）
        - filename: 完整文件名
        - slot: 槽位/标识（从文件名中提取 '1' 或 'happy_ending'）
        - meta: 文件中保存的 meta（若有）
        - size_bytes: 文件大小
        - mtime: 修改时间 ISO 字符串
        """
        result = []
        for fname in self.list_saves():
            fpath = os.path.join(self.save_dir, fname)
            try:
                stat = os.stat(fpath)
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                meta = content.get('meta', {}) if isinstance(content, dict) else {}
                slot = fname.replace('save_', '').replace('.json', '')
                result.append({
                    'id': fname[:-5],
                    'filename': fname,
                    'slot': slot,
                    'meta': meta,
                    'size_bytes': stat.st_size,
                    'mtime': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })
            except Exception as e:
                # 跳过无法解析的存档
                result.append({
                    'id': fname[:-5],
                    'filename': fname,
                    'slot': fname.replace('save_', '').replace('.json', ''),
                    'meta': { 'error': str(e) },
                    'size_bytes': None,
                    'mtime': None,
                })
        return sorted(result, key=lambda x: (x['mtime'] or ''), reverse=True)
