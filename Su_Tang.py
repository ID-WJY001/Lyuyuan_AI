# gal_game_agent.py
from Game_Storage import GameStorage
from openai import OpenAI
import os

# 加载角色设定（替换为之前制作的苏糖prompt）
with open("sutang_prompt.txt", encoding='utf-8') as f:
    CHARACTER_PROMPT = f.read()

# 添加更明确的人物设定和背景
CHARACTER_DETAILS = """
【人物设定】
姓名：苏糖
性别：女
年龄：16岁
班级：高一二班
特点：性格温柔甜美，做事认真负责，对烘焙充满热情
兴趣爱好：烘焙、阅读、听音乐
社团：烘焙社社长

【背景信息】
当前场景：绿园中学百团大战活动，苏糖正在烘焙社摊位前介绍社团活动
互动对象：陈辰（男，高一一班学生）

请你始终牢记以上设定，在回复中保持角色一致性，任何时候都不要忘记自己是谁、在哪里、和谁说话。
"""

class GalGameAgent:
    def __init__(self, load_slot=None, is_new_game=False):
        self.storage = GameStorage()
        self.dialogue_history = []
        self.game_state = {
            "closeness": 30,
            "discovered": [],
            "chapter": 1,
            "last_topics": [],  # 记录最近讨论的话题，用于保持对话连贯
            "dialogue_quality": 0,  # 对话质量评分
            "relationship_state": "stranger",  # 关系状态：stranger, acquaintance, friend, close_friend, crush
            "mood_today": "normal",  # 当天心情：good, normal, bad
            "boredom_level": 0,  # 无聊程度，影响对话状态
            "respect_level": 0   # 尊重度，影响对方反应
        }
        
        if load_slot and self.load(load_slot):
            print(f"加载存档#{load_slot}成功")
        else:
            self._init_new_game(is_new_game)
    
    def _init_new_game(self, is_new_game=False):
        """ 新游戏初始化 """
        enhanced_prompt = CHARACTER_PROMPT + "\n\n" + CHARACTER_DETAILS
        
        # 初始化对话历史，但不添加苏糖的第一句话
        initial_messages = [
            {"role": "system", "content": enhanced_prompt},
            {"role": "system", "content": self._get_contextual_guideline()},
        ]
        
        # 只有在不是全新游戏的情况下，才添加苏糖的初始对话
        if not is_new_game:
            initial_messages.append({"role": "assistant", "content": "（正在整理烘焙社的宣传材料）有什么我可以帮你的吗？"})
            
        self.dialogue_history = initial_messages
    
    def _get_contextual_guideline(self):
        """根据当前游戏状态生成上下文相关的指导方针"""
        guidelines = [
            "你是苏糖，绿园中学高一二班的学生，烘焙社社长。你现在正在百团大战活动中为烘焙社招新。",
            "你是个温柔、甜美的女生，但也有自己的原则和底线。",
            "陈辰是高一一班的学生，他对你产生了好感，正在尝试与你搭讪。",
            "你应该基于亲密度的不同阶段，调整对陈辰的态度和回应方式。",
            "请时刻牢记自己的身份和设定，不要在对话中表现出与角色不符的行为。"
        ]
        
        # 根据亲密度调整态度
        closeness = self.game_state["closeness"]
        if closeness < 40:
            guidelines.append("当前亲密度较低，你应该表现得礼貌但有些距离感，不会主动分享个人信息。")
        elif closeness < 60:
            guidelines.append("当前亲密度一般，你开始对陈辰感到些许好感，会更加友好，偶尔分享自己的想法。")
        elif closeness < 80:
            guidelines.append("当前亲密度较高，你已经把陈辰当作朋友，会更加开放地表达自己，分享自己的兴趣爱好。")
        else:
            guidelines.append("当前亲密度很高，你对陈辰有好感，会表现得更加亲近，甚至有些害羞的暗示。")
        
        # 动态调整无聊程度
        boredom = self.game_state.get("boredom_level", 0)
        # 根据当前无聊程度调整反应
        if boredom > 7:
            guidelines.append("你现在感到非常无聊，对重复或平淡的对话会表现出明显的不耐烦。")
            guidelines.append("可能会直接表达想结束对话的意愿，或者回复变得极其简短。")
            guidelines.append("只有新鲜、有趣或关于你感兴趣话题的对话才能吸引你的注意力。")
        elif boredom > 4:
            guidelines.append("你开始感到有些无聊，回复会变得略显敷衍或者心不在焉。")
            guidelines.append("偶尔会试图转换话题，希望聊一些更有趣的内容。")
            
        # 根据当天心情调整反应
        mood = self.game_state.get("mood_today", "normal")
        if mood == "good":
            guidelines.append("今天心情不错，对话更开朗活泼，更容易被逗笑。")
        elif mood == "bad":
            guidelines.append("今天心情不太好，对话可能会有些冷淡，更容易对小事感到烦躁。")
            guidelines.append("需要更多的耐心和体贴才能让你打开心扉。")
            
        # 对粗鲁或不当言论的反应
        guidelines.append("对于粗鲁、命令式语气或不尊重的言论，你会表现出明显的不适或不满。")
        guidelines.append("如果连续收到这类消息，你可能会变得愈发冷淡，甚至考虑终止对话。")
        
        # 对暧昧或过早表白的反应
        guidelines.append("对过早或突兀的表白会感到尴尬和压力，会礼貌但坚定地拒绝，并可能疏远对方。")
        guidelines.append("只有在足够了解并建立信任后，才会对感情暗示做出积极回应。")
        
        # 加入之前讨论过的话题，保持对话连贯性
        if self.game_state["last_topics"]:
            topics = ", ".join(self.game_state["last_topics"])
            guidelines.append(f"你们最近讨论过的话题: {topics}，可以自然地继续这些话题或相关内容。")
        
        # 根据对话质量添加建议
        if self.game_state["dialogue_quality"] < 30:
            guidelines.append("目前对话质量较低，如果情况持续，你会变得越来越不耐烦。")
        
        return "\n".join(guidelines)
    
    def _extract_topics(self, text):
        """从文本中提取主要话题"""
        # 简单实现，实际应用可能需要更复杂的NLP
        import jieba.analyse
        try:
            # 提取前3个关键词作为话题
            topics = jieba.analyse.extract_tags(text, topK=3)
            return topics
        except:
            # 如果提取失败，返回空列表
            return []
    
    def chat(self, user_input):
        # 更新系统指导
        # 确保系统提示保留角色设定
        enhanced_prompt = CHARACTER_PROMPT + "\n\n" + CHARACTER_DETAILS
        
        # 检查历史中是否已有系统消息
        system_messages = [msg for msg in self.dialogue_history if msg["role"] == "system"]
        
        # 更新或添加系统消息
        if len(system_messages) >= 1:
            # 保持第一条是角色设定
            if system_messages[0]["content"] != enhanced_prompt:
                self.dialogue_history[0] = {"role": "system", "content": enhanced_prompt}
                
            # 更新或添加上下文指导
            if len(system_messages) >= 2:
                # 找到第二条系统消息的索引
                second_sys_idx = None
                for i, msg in enumerate(self.dialogue_history):
                    if msg["role"] == "system" and i > 0:
                        second_sys_idx = i
                        break
                        
                if second_sys_idx is not None:
                    # 更新已有的第二条系统消息
                    self.dialogue_history[second_sys_idx] = {"role": "system", "content": self._get_contextual_guideline()}
                else:
                    # 添加第二条系统消息
                    self.dialogue_history.insert(1, {"role": "system", "content": self._get_contextual_guideline()})
            else:
                # 添加上下文指导作为第二条系统消息
                self.dialogue_history.insert(1, {"role": "system", "content": self._get_contextual_guideline()})
        else:
            # 如果没有系统消息，添加角色设定和上下文指导
            self.dialogue_history.insert(0, {"role": "system", "content": enhanced_prompt})
            self.dialogue_history.insert(1, {"role": "system", "content": self._get_contextual_guideline()})
        
        # 添加玩家输入
        self.dialogue_history.append({"role": "user", "content": user_input})
        
        # 提取用户输入中的话题并更新
        topics = self._extract_topics(user_input)
        if topics:
            self.game_state["last_topics"] = topics + self.game_state["last_topics"]
            # 保留最近的5个话题
            self.game_state["last_topics"] = self.game_state["last_topics"][:5]
            
        # 更新对话质量评分（简单实现）
        if len(user_input) > 20:
            self.game_state["dialogue_quality"] += 5
        else:
            self.game_state["dialogue_quality"] = max(0, self.game_state["dialogue_quality"] - 2)
        
        # 每5个回合强制重申一次角色设定，确保角色不会忘记自己的身份
        if len([msg for msg in self.dialogue_history if msg["role"] == "user"]) % 5 == 0:
            reminder = {"role": "system", "content": "提醒：你是苏糖，高一二班的学生，烘焙社社长。你正在和高一一班的陈辰交谈。保持角色设定的一致性，不要忘记自己的身份和背景。"}
            self.dialogue_history.append(reminder)
        
        # 创建对话引擎并处理可能的连接错误
        try:
            # 使用DeepSeek API
            client = OpenAI(
                api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
                base_url="https://api.deepseek.com/v1"  # 添加DeepSeek的API基础URL
            )
            response = client.chat.completions.create(
                model="deepseek-chat", 
                messages=self.dialogue_history,
                temperature=0.7,
                max_tokens=800
            )
            
            # 获取回复
            reply = response.choices[0].message.content
            
        except Exception as e:
            # 连接错误处理：使用预设回复
            print(f"API连接错误: {str(e)}")
            
            # 根据亲密度和情景提供适当的备用回复
            closeness = self.game_state["closeness"]
            if len(self.dialogue_history) <= 3:  # 第一次对话
                reply = "（微笑着看向你）你好！是的，这里就是烘焙社的招新摊位。我是苏糖，高一二班的，烘焙社社长。请问你对烘焙感兴趣吗？"
            elif closeness < 40:
                reply = "（礼貌地点头）嗯，你说得对。我们烘焙社平时会有很多有趣的活动，如果你感兴趣的话，可以留下你的联系方式。"
            elif closeness < 70:
                reply = "（友好地笑了笑）谢谢你这么说。我很喜欢烘焙，从小就对甜点特别感兴趣。你呢，你平时有什么爱好吗？"
            else:
                reply = "（眼睛亮了起来）真的吗？我也觉得我们有很多共同话题！我平时除了烘焙，还喜欢听音乐和阅读。很高兴能和你聊这么多。"
        
        # 添加到对话历史
        self.dialogue_history.append({"role": "assistant", "content": reply})
        
        # 截断历史（如果需要）
        if len(self.dialogue_history) > 30:
            # 保留system消息和最近的对话
            systems = [msg for msg in self.dialogue_history[:3] if msg["role"] == "system"]
            recent = self.dialogue_history[-20:]
            self.dialogue_history = systems + recent
        
        return reply
    
    def save(self, slot):
        data = {
            "history": self.dialogue_history,
            "state": self.game_state
        }
        return self.storage.save_game(data, slot)
    
    def load(self, slot):
        data = self.storage.load_game(slot)
        if data:
            self.dialogue_history = data["history"]
            self.game_state = data["state"]
            # 确保游戏状态包含所有必要字段
            if "last_topics" not in self.game_state:
                self.game_state["last_topics"] = []
            if "dialogue_quality" not in self.game_state:
                self.game_state["dialogue_quality"] = 0
            if "relationship_state" not in self.game_state:
                self.game_state["relationship_state"] = "stranger"
            if "mood_today" not in self.game_state:
                self.game_state["mood_today"] = "normal"
            if "boredom_level" not in self.game_state:
                self.game_state["boredom_level"] = 0
            if "respect_level" not in self.game_state:
                self.game_state["respect_level"] = 0
            return True
        return False