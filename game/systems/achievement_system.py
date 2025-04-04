"""
成就系统模块
负责管理和跟踪游戏中的成就
"""

import json
import os
import sys
import sqlite3
import logging
from datetime import datetime

# 添加项目根目录到路径以便导入
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

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
    def __init__(self, db_path=None):
        """
        初始化成就系统
        参数:
            db_path: 数据库文件路径，默认使用data/dialogues.db
        """
        if db_path is None:
            db_path = os.path.join(ROOT_DIR, "data", "dialogues.db")
            
        self.achievements = {}  # 存储所有成就对象
        self.db_path = db_path
        self.logger = logging.getLogger("AchievementSystem")
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
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
        self.logger.info("成就数据库设置完成")
    
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
            self.logger.info("已初始化默认成就列表")
        
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
        self.logger.info(f"已加载 {len(self.achievements)} 个成就")
    
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
                "icon": "💕",
                "secret": 0
            },
            {
                "id": "love_confession",
                "name": "表白",
                "description": "好感度达到100",
                "requirements": json.dumps({
                    "type": "affection",
                    "character": "su_tang",
                    "level": 100
                }),
                "reward": "解锁特殊结局",
                "icon": "❤️",
                "secret": 0
            },
            {
                "id": "gossip_master",
                "name": "八卦达人",
                "description": "收集到10条学校八卦",
                "requirements": json.dumps({
                    "type": "gossip_count",
                    "count": 10
                }),
                "reward": "解锁新对话选项",
                "icon": "📱",
                "secret": 0
            },
            {
                "id": "early_bird",
                "name": "早起的鸟儿",
                "description": "在6-8点之间与苏糖对话5次",
                "requirements": json.dumps({
                    "type": "time_dialogue",
                    "character": "su_tang",
                    "time_range": {"start": "06:00", "end": "08:00"},
                    "count": 5
                }),
                "reward": "解锁早晨特殊对话",
                "icon": "🌅",
                "secret": 0
            },
            {
                "id": "night_owl",
                "name": "夜猫子",
                "description": "在22-24点之间与苏糖对话5次",
                "requirements": json.dumps({
                    "type": "time_dialogue",
                    "character": "su_tang",
                    "time_range": {"start": "22:00", "end": "24:00"},
                    "count": 5
                }),
                "reward": "解锁夜晚特殊对话",
                "icon": "🌙",
                "secret": 0
            },
            {
                "id": "explorer",
                "name": "探索者",
                "description": "访问游戏中的所有场景",
                "requirements": json.dumps({
                    "type": "visit_all_scenes"
                }),
                "reward": "解锁隐藏场景",
                "icon": "🗺️",
                "secret": 0
            },
            {
                "id": "weather_watcher",
                "name": "天气观察员",
                "description": "在四种不同天气下与苏糖对话",
                "requirements": json.dumps({
                    "type": "weather_variety",
                    "character": "su_tang",
                    "count": 4
                }),
                "reward": "解锁天气相关对话",
                "icon": "🌦️",
                "secret": 0
            },
            {
                "id": "persistent_suitor",
                "name": "锲而不舍",
                "description": "连续10天与苏糖对话",
                "requirements": json.dumps({
                    "type": "consecutive_days",
                    "character": "su_tang",
                    "count": 10
                }),
                "reward": "好感度+15",
                "icon": "📅",
                "secret": 0
            },
            {
                "id": "memory_keeper",
                "name": "回忆收藏家",
                "description": "收集5个特殊回忆事件",
                "requirements": json.dumps({
                    "type": "memory_count",
                    "count": 5
                }),
                "reward": "解锁回忆录功能",
                "icon": "📓",
                "secret": 0
            },
            {
                "id": "gift_giver",
                "name": "送礼达人",
                "description": "送给苏糖5件不同的礼物",
                "requirements": json.dumps({
                    "type": "gift_variety",
                    "character": "su_tang",
                    "count": 5
                }),
                "reward": "解锁礼物商店新物品",
                "icon": "🎁",
                "secret": 0
            },
            {
                "id": "secret_ending",
                "name": "???",
                "description": "发现隐藏结局",
                "requirements": json.dumps({
                    "type": "secret_ending"
                }),
                "reward": "???",
                "icon": "❓",
                "secret": 1
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for achievement in default_achievements:
            cursor.execute("""
                INSERT INTO achievements (id, name, description, requirements, reward, icon, secret)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                achievement["id"],
                achievement["name"],
                achievement["description"],
                achievement["requirements"],
                achievement.get("reward"),
                achievement.get("icon"),
                achievement.get("secret", 0)
            ))
            
        conn.commit()
        conn.close()
    
    def check_achievements(self, game_manager):
        """
        检查成就解锁条件
        根据游戏状态检查各个成就的解锁条件，更新并返回新解锁的成就
        参数:
            game_manager: 游戏管理器实例，包含游戏状态和数据
        返回值:
            新解锁的成就列表
        """
        newly_unlocked = []
        
        for achievement_id, achievement in self.achievements.items():
            # 跳过已解锁的成就
            if achievement.unlocked:
                continue
                
            # 解析成就要求
            requirements = achievement.requirements
            req_type = requirements.get("type", "")
            
            # 根据不同类型的成就检查解锁条件
            unlocked = False
            
            if req_type == "dialogue_count":
                # 对话次数成就
                character = requirements.get("character")
                required_count = requirements.get("count", 1)
                
                current_count = game_manager.get_dialogue_count(character)
                unlocked = current_count >= required_count
                
            elif req_type == "consecutive_positive":
                # 连续增加好感度成就
                character = requirements.get("character")
                required_count = requirements.get("count", 5)
                
                current_streak = game_manager.get_positive_affection_streak(character)
                unlocked = current_streak >= required_count
                
            elif req_type == "topic_count":
                # 特定话题讨论次数成就
                character = requirements.get("character")
                topic = requirements.get("topic")
                required_count = requirements.get("count", 5)
                
                current_count = game_manager.get_topic_discussion_count(character, topic)
                unlocked = current_count >= required_count
                
            elif req_type == "affection":
                # 好感度等级成就
                character = requirements.get("character")
                required_level = requirements.get("level", 50)
                
                current_level = game_manager.get_affection_level(character)
                unlocked = current_level >= required_level
                
            elif req_type == "time_dialogue":
                # 特定时间对话成就
                character = requirements.get("character")
                time_range = requirements.get("time_range", {})
                required_count = requirements.get("count", 5)
                
                start_time = time_range.get("start", "00:00")
                end_time = time_range.get("end", "23:59")
                
                current_count = game_manager.get_time_dialogue_count(
                    character, start_time, end_time
                )
                unlocked = current_count >= required_count
                
            elif req_type == "visit_all_scenes":
                # 访问所有场景成就
                unlocked = game_manager.has_visited_all_scenes()
                
            elif req_type == "consecutive_days":
                # 连续天数对话成就
                character = requirements.get("character")
                required_days = requirements.get("count", 10)
                
                current_days = game_manager.get_consecutive_days(character)
                unlocked = current_days >= required_days
            
            # 其他类型的成就检查...
            
            # 如果解锁了，更新成就状态
            if unlocked:
                achievement.unlocked = True
                achievement.unlock_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                newly_unlocked.append(achievement)
        
        # 保存新解锁的成就
        if newly_unlocked:
            self._save_unlocked_achievements(newly_unlocked)
            
        return newly_unlocked
    
    def _save_unlocked_achievements(self, achievements):
        """
        保存解锁的成就到数据库
        参数:
            achievements: 需要保存的成就对象列表
        """
        if not achievements:
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for achievement in achievements:
            # 检查是否已存在该玩家的成就记录
            cursor.execute("""
                SELECT id FROM player_achievements
                WHERE achievement_id = ? AND player_id = 'default'
            """, (achievement.id,))
            
            result = cursor.fetchone()
            
            if result:
                # 更新现有记录
                cursor.execute("""
                    UPDATE player_achievements
                    SET unlocked = 1, unlock_date = ?
                    WHERE achievement_id = ? AND player_id = 'default'
                """, (achievement.unlock_date, achievement.id))
            else:
                # 创建新记录
                cursor.execute("""
                    INSERT INTO player_achievements
                    (achievement_id, player_id, unlocked, unlock_date, progress)
                    VALUES (?, 'default', 1, ?, 100)
                """, (achievement.id, achievement.unlock_date))
                
        conn.commit()
        conn.close()
        
        self.logger.info(f"已保存 {len(achievements)} 个新解锁的成就")
    
    def get_achievement_notification(self, achievement):
        """
        获取成就解锁通知文本
        参数:
            achievement: 成就对象
        返回值:
            格式化的通知文本
        """
        return f"🏆 成就解锁: 【{achievement.name}】\n{achievement.description}\n奖励: {achievement.reward or '无'}"
    
    def get_all_achievements(self, include_secret=False):
        """
        获取所有成就列表
        参数:
            include_secret: 是否包含隐藏成就，默认为False
        返回值:
            成就列表，每个成就包含id、名称、描述、图标、是否解锁等信息
        """
        achievement_list = []
        
        for achievement_id, achievement in self.achievements.items():
            # 如果是隐藏成就且未解锁，且不包含隐藏成就，则跳过
            if achievement.secret and not achievement.unlocked and not include_secret:
                continue
                
            # 添加成就信息
            achievement_info = {
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "icon": achievement.icon,
                "unlocked": achievement.unlocked,
                "unlock_date": achievement.unlock_date,
                "secret": achievement.secret
            }
            
            # 如果是隐藏成就且未解锁，隐藏详细信息
            if achievement.secret and not achievement.unlocked:
                achievement_info["name"] = "???"
                achievement_info["description"] = "成就未解锁"
                
            achievement_list.append(achievement_info)
            
        return achievement_list
    
    def get_achievement_progress(self, achievement_id):
        """
        获取指定成就的完成进度
        参数:
            achievement_id: 成就ID
        返回值:
            成就完成进度百分比（0-100）
        """
        if achievement_id not in self.achievements:
            return 0
            
        achievement = self.achievements[achievement_id]
        
        # 如果已解锁，进度为100%
        if achievement.unlocked:
            return 100
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取存储的进度
        cursor.execute("""
            SELECT progress FROM player_achievements
            WHERE achievement_id = ? AND player_id = 'default'
        """, (achievement_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        
        return 0 