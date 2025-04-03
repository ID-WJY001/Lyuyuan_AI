import json
import os
import sqlite3
from datetime import datetime

class Achievement:
    """
    成就类：定义单个成就的结构
    包含成就的基本信息、达成条件和解锁状态
    """
    def __init__(self, id, name, description, requirements, reward=None, icon=None, secret=False):
        """
        初始化成就对象
        参数:
            id: 成就唯一标识符
            name: 成就名称
            description: 成就描述
            requirements: 成就达成条件
            reward: 达成成就后的奖励，可选
            icon: 成就图标，可选
            secret: 是否为隐藏成就，默认为False
        """
        self.id = id
        self.name = name
        self.description = description
        self.requirements = requirements
        self.reward = reward
        self.icon = icon
        self.secret = secret  # 是否为隐藏成就
        self.unlocked = False
        self.unlock_date = None

class AchievementSystem:
    """
    成就系统类：管理游戏中的所有成就
    负责成就的定义、检查、解锁和查询
    """
    def __init__(self, db_path="data/dialogues.db"):
        """
        初始化成就系统
        参数:
            db_path: 数据库文件路径，默认使用dialogues.db
        """
        self.achievements = {}  # 存储所有成就对象
        self.db_path = db_path
        self._setup_db()  # 设置数据库
        self._load_achievements()  # 加载成就定义
    
    def _setup_db(self):
        """
        设置成就数据库表
        创建存储成就定义和玩家成就进度的表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建成就定义表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            requirements TEXT NOT NULL,
            reward TEXT,
            icon TEXT,
            secret INTEGER DEFAULT 0
        )
        ''')
        
        # 创建玩家成就进度表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            achievement_id TEXT NOT NULL,
            player_id TEXT DEFAULT 'default',
            unlocked INTEGER DEFAULT 0,
            unlock_date TEXT,
            progress REAL DEFAULT 0,
            FOREIGN KEY (achievement_id) REFERENCES achievements (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_achievements(self):
        """
        从数据库加载成就定义
        如果成就表为空，则初始化默认成就
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查成就表是否为空
        cursor.execute("SELECT COUNT(*) FROM achievements")
        count = cursor.fetchone()[0]
        
        # 如果为空，初始化默认成就
        if count == 0:
            self._initialize_default_achievements()
        
        # 加载所有成就
        cursor.execute("SELECT id, name, description, requirements, reward, icon, secret FROM achievements")
        for row in cursor.fetchall():
            achievement = Achievement(
                id=row[0],
                name=row[1],
                description=row[2],
                requirements=json.loads(row[3]),
                reward=row[4],
                icon=row[5],
                secret=bool(row[6])
            )
            self.achievements[achievement.id] = achievement
            
        # 加载玩家成就状态
        cursor.execute("""
            SELECT achievement_id, unlocked, unlock_date, progress
            FROM player_achievements
            WHERE player_id = 'default'
        """)
        
        for row in cursor.fetchall():
            achievement_id = row[0]
            if achievement_id in self.achievements:
                self.achievements[achievement_id].unlocked = bool(row[1])
                self.achievements[achievement_id].unlock_date = row[2]
                # 可以添加进度跟踪
        
        conn.close()
    
    def _initialize_default_achievements(self):
        """
        初始化默认成就列表
        定义游戏中的基本成就，包括各种类型的成就
        """
        default_achievements = [
            {
                "id": "first_meeting",
                "name": "初次见面",
                "description": "与苏糖的第一次对话",
                "requirements": json.dumps({
                    "type": "dialogue_count",
                    "character": "su_tang",
                    "count": 1
                }),
                "reward": "好感度+5",
                "icon": "🌱",
                "secret": 0
            },
            {
                "id": "sweet_talker",
                "name": "甜言蜜语",
                "description": "连续5次对话增加好感度",
                "requirements": json.dumps({
                    "type": "consecutive_positive",
                    "character": "su_tang",
                    "count": 5
                }),
                "reward": "好感度+10",
                "icon": "🍯",
                "secret": 0
            },
            {
                "id": "baking_enthusiast",
                "name": "烘焙爱好者",
                "description": "与苏糖讨论5次烘焙相关话题",
                "requirements": json.dumps({
                    "type": "topic_count",
                    "character": "su_tang",
                    "topic": "烘焙",
                    "count": 5
                }),
                "reward": "解锁新对话选项",
                "icon": "🍰",
                "secret": 0
            },
            {
                "id": "secret_admirer",
                "name": "暗恋者",
                "description": "好感度达到50",
                "requirements": json.dumps({
                    "type": "affection",
                    "character": "su_tang",
                    "level": 50
                }),
                "reward": "解锁新场景",
                "icon": "💌",
                "secret": 0
            },
            {
                "id": "close_friend",
                "name": "亲密好友",
                "description": "好感度达到75",
                "requirements": json.dumps({
                    "type": "affection",
                    "character": "su_tang",
                    "level": 75
                }),
                "reward": "解锁深入对话",
                "icon": "🌟",
                "secret": 0
            },
            {
                "id": "first_date",
                "name": "初次约会",
                "description": "与苏糖在非学校场景互动",
                "requirements": json.dumps({
                    "type": "scene",
                    "character": "su_tang",
                    "scenes": ["公园", "咖啡厅", "电影院", "游乐场"]
                }),
                "reward": "好感度+15",
                "icon": "🌈",
                "secret": 0
            },
            {
                "id": "sweet_confession",
                "name": "甜蜜告白",
                "description": "好感度达到100并告白成功",
                "requirements": json.dumps({
                    "type": "event",
                    "character": "su_tang",
                    "event": "confession_success"
                }),
                "reward": "游戏完成",
                "icon": "❤️",
                "secret": 0
            },
            {
                "id": "friend_of_friend",
                "name": "朋友的朋友",
                "description": "与林雨含互动5次",
                "requirements": json.dumps({
                    "type": "dialogue_count",
                    "character": "lin_yuhan",
                    "count": 5
                }),
                "reward": "好感度+5",
                "icon": "👭",
                "secret": 0
            },
            {
                "id": "sugar_bean_lover",
                "name": "糖豆粉丝",
                "description": "与苏糖的猫互动3次",
                "requirements": json.dumps({
                    "type": "event",
                    "character": "su_tang",
                    "event": "sugar_bean_interaction",
                    "count": 3
                }),
                "reward": "解锁糖豆相关对话",
                "icon": "🐱",
                "secret": 1
            },
            {
                "id": "scene_explorer",
                "name": "场景探索者",
                "description": "访问所有可能的场景",
                "requirements": json.dumps({
                    "type": "scene_collection",
                    "scenes": ["烘焙社摊位", "烘焙社", "教室", "操场", "图书馆", "公园", "食堂", "街道", "游乐场", "电影院", "咖啡厅"]
                }),
                "reward": "好感度+20",
                "icon": "🗺️",
                "secret": 0
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for achievement in default_achievements:
            cursor.execute(
                """INSERT INTO achievements (id, name, description, requirements, reward, icon, secret)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    achievement["id"],
                    achievement["name"],
                    achievement["description"],
                    achievement["requirements"],
                    achievement["reward"],
                    achievement["icon"],
                    achievement["secret"]
                )
            )
        
        conn.commit()
        conn.close()
    
    def check_achievements(self, game_manager):
        """
        检查是否有新的成就达成
        参数:
            game_manager: 游戏管理器对象，包含当前游戏状态
        返回值:
            新解锁的成就列表
        """
        unlocked = []
        
        # 获取当前游戏状态
        character_id = game_manager.active_character_id
        character_state = game_manager.character_states.get(character_id, {})
        affection = game_manager.game_state.get("closeness", 0)
        consecutive_positive = game_manager.game_state.get("consecutive_positive", 0)
        scenes_visited = character_state.get("scenes_visited", [])
        dialogue_count = game_manager.game_state.get("conversation_count", 0)
        
        # 遍历所有成就
        for achievement_id, achievement in self.achievements.items():
            if achievement.unlocked:
                continue
                
            # 根据成就类型检查是否达成
            requirements = achievement.requirements
            req_type = requirements.get("type", "")
            
            if req_type == "dialogue_count" and requirements.get("character") == character_id:
                if dialogue_count >= requirements.get("count", 0):
                    achievement.unlocked = True
                    unlocked.append(achievement)
                    
            elif req_type == "consecutive_positive" and requirements.get("character") == character_id:
                if consecutive_positive >= requirements.get("count", 0):
                    achievement.unlocked = True
                    unlocked.append(achievement)
                    
            elif req_type == "affection" and requirements.get("character") == character_id:
                if affection >= requirements.get("level", 0):
                    achievement.unlocked = True
                    unlocked.append(achievement)
                    
            elif req_type == "scene" and requirements.get("character") == character_id:
                required_scenes = set(requirements.get("scenes", []))
                if any(scene in scenes_visited for scene in required_scenes):
                    achievement.unlocked = True
                    unlocked.append(achievement)
                    
            elif req_type == "scene_collection":
                required_scenes = set(requirements.get("scenes", []))
                visited_scenes = set()
                for state in game_manager.character_states.values():
                    visited_scenes.update(state.get("scenes_visited", []))
                
                if required_scenes.issubset(visited_scenes):
                    achievement.unlocked = True
                    unlocked.append(achievement)
                    
            # 可以添加更多成就类型检查
            
        # 保存解锁的成就
        if unlocked:
            self._save_unlocked_achievements(unlocked)
            
        return unlocked
    
    def _save_unlocked_achievements(self, achievements):
        """
        保存解锁的成就到数据库
        参数:
            achievements: 已解锁的成就对象列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        unlock_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for achievement in achievements:
            achievement.unlock_date = unlock_date
            
            # 检查是否已有记录
            cursor.execute(
                "SELECT id FROM player_achievements WHERE achievement_id = ? AND player_id = 'default'",
                (achievement.id,)
            )
            
            if cursor.fetchone():
                # 更新现有记录
                cursor.execute(
                    """UPDATE player_achievements 
                    SET unlocked = 1, unlock_date = ? 
                    WHERE achievement_id = ? AND player_id = 'default'""",
                    (unlock_date, achievement.id)
                )
            else:
                # 插入新记录
                cursor.execute(
                    """INSERT INTO player_achievements 
                    (achievement_id, player_id, unlocked, unlock_date, progress)
                    VALUES (?, 'default', 1, ?, 1.0)""",
                    (achievement.id, unlock_date)
                )
        
        conn.commit()
        conn.close()
    
    def get_achievement_notification(self, achievement):
        """
        生成成就解锁通知文本
        参数:
            achievement: 成就对象
        返回值:
            格式化的成就解锁通知文本
        """
        return f"🏆 成就解锁: 【{achievement.name}】\n{achievement.description}\n奖励: {achievement.reward if achievement.reward else '无'}"
    
    def get_all_achievements(self, include_secret=False):
        """
        获取所有成就列表
        参数:
            include_secret: 是否包括未解锁的隐藏成就，默认为False
        返回值:
            成就信息字典列表
        """
        achievements_list = []
        
        for achievement in self.achievements.values():
            # 如果是隐藏成就且未解锁且不包括隐藏成就，则跳过
            if achievement.secret and not achievement.unlocked and not include_secret:
                continue
                
            achievements_list.append({
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description if achievement.unlocked or not achievement.secret else "???",
                "unlocked": achievement.unlocked,
                "unlock_date": achievement.unlock_date,
                "icon": achievement.icon,
                "reward": achievement.reward
            })
            
        return achievements_list
    
    def get_achievement_progress(self, achievement_id):
        """
        获取特定成就的完成进度
        参数:
            achievement_id: 成就ID
        返回值:
            成就完成进度百分比，范围为0.0到1.0
            如果成就不存在则返回None
        """
        if achievement_id not in self.achievements:
            return None
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT progress FROM player_achievements WHERE achievement_id = ? AND player_id = 'default'",
            (achievement_id,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        return 0.0 