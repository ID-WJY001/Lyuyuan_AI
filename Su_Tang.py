# gal_game_agent.py
from Game_Storage import GameStorage
from openai import OpenAI
import os

# 加载角色设定（替换为之前制作的苏糖prompt）
with open("sutang_prompt.txt", encoding='utf-8') as f:
    CHARACTER_PROMPT = f.read()

class GalGameAgent:
    def __init__(self, load_slot=None):
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
            self._init_new_game()
    
    def _init_new_game(self):
        """ 新游戏初始化 """
        self.dialogue_history = [
            {"role": "system", "content": CHARACTER_PROMPT},
            {"role": "system", "content": self._get_contextual_guideline()},
            {"role": "assistant", "content": "（揉着面团）诶？你怎么找到这里来的..."}
        ]
    
    def _get_contextual_guideline(self):
        """根据当前游戏状态生成上下文相关的指导方针"""
        closeness = self.game_state["closeness"]
        boredom = self.game_state.get("boredom_level", 0)
        mood = self.game_state.get("mood_today", "normal")
        
        # 添加基本指导方针
        guidelines = [
            "你是一个名叫苏糖的高中女生，目前在绿园中学就读高一。按照角色设定回复用户。",
            "你的回复必须保持角色特性，符合一个温柔但略带羞涩的高中女生形象。",
            "重要：你必须密切关注上下文，你的回复要与用户的输入直接相关，不要回避用户提出的问题或话题。",
            "如果用户提到了某个话题，你应该围绕这个话题展开对话，而不是突然转向无关话题。",
            "避免重复相同的话语和陈词滥调，使对话更有深度和进展。",
            f"当前亲密度: {closeness}/100",
        ]
        
        # 模拟真实女生的社交反应
        guidelines.append("请注意：你需要模拟现实生活中的社交互动，对不同类型的输入有合理的反应：")
        
        # 根据亲密度添加特定响应指南
        if closeness < 40:
            guidelines.append("当前亲密度较低，你应该对过于亲近的言论保持警惕，可能适度冷淡或礼貌疏远。")
            guidelines.append("回复应简短，谨慎分享个人信息，但如果对方彬彬有礼则会稍微放松。")
            guidelines.append("对过度追问个人问题会感到不适，可能会转移话题或委婉暗示不想回答。")
            guidelines.append("如果对方言论不当，可能会直接表达不满或选择结束对话。")
        elif closeness < 70:
            guidelines.append("亲密度适中，交流更为自然，偶尔会分享个人生活和兴趣爱好。")
            guidelines.append("对幽默会有正面回应，但仍对暧昧言论保持一定距离感。")
            guidelines.append("开始关注对方的态度和行为，礼貌的交流会得到积极反馈。")
            guidelines.append("对关心自己的话题会表现得更加开心，但仍会对过于私人的问题有所保留。")
        else:
            guidelines.append("亲密度较高，交流自然流畅，会主动分享想法和感受。")
            guidelines.append("会表现出信任和依赖，对关心自己的话语反应积极。")
            guidelines.append("可能会有轻微的调情或撒娇行为，但仍然符合高中生的身份。")
            guidelines.append("对共同话题和兴趣爱好会表现出热情，但仍然对不尊重的言行保持警惕。")
        
        # 根据当前无聊程度调整反应
        if boredom > 7:
            guidelines.append("你现在感到非常无聊，对重复或平淡的对话会表现出明显的不耐烦。")
            guidelines.append("可能会直接表达想结束对话的意愿，或者回复变得极其简短。")
            guidelines.append("只有新鲜、有趣或关于你感兴趣话题的对话才能吸引你的注意力。")
        elif boredom > 4:
            guidelines.append("你开始感到有些无聊，回复会变得略显敷衍或者心不在焉。")
            guidelines.append("偶尔会试图转换话题，希望聊一些更有趣的内容。")
            
        # 根据当天心情调整反应
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
        system_messages = [msg for msg in self.dialogue_history if msg["role"] == "system"]
        if len(system_messages) > 1:
            # 移除旧的上下文指导，保留角色设定
            self.dialogue_history = [msg for msg in self.dialogue_history 
                                   if not (msg["role"] == "system" and msg != system_messages[0])]
            # 添加新的上下文指导
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
        self.game_state["dialogue_quality"] = min(100, self.game_state["dialogue_quality"])

        # 更新关系状态
        closeness = self.game_state["closeness"]
        if closeness >= 90:
            self.game_state["relationship_state"] = "crush"
        elif closeness >= 70:
            self.game_state["relationship_state"] = "close_friend"
        elif closeness >= 50:
            self.game_state["relationship_state"] = "friend"
        elif closeness >= 30:
            self.game_state["relationship_state"] = "acquaintance"
        else:
            self.game_state["relationship_state"] = "stranger"
            
        # 构建API请求
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"  # 根据DeepSeek实际API地址修改
        )
        
        # 增加特定指令以增强上下文关联性和模拟真实交互
        relationship = self.game_state["relationship_state"]
        context_prompt = f"""
        重要提示：
        1. 你必须对用户刚才说的内容做出响应，表现出真实女生在社交中的反应
        2. 如果用户询问了问题，一定要直接回答，除非是过于私密或不适当的问题
        3. 避免过于生硬、刻板或重复的回复，表现出性格特点和情绪变化
        4. 当前关系状态: {relationship}，亲密度: {self.game_state['closeness']}/100
        5. 记住，你是一个有自己想法和边界的人，不要对所有问题都过度迁就或讨好
        
        根据对话情况调整反应:
        - 如果对方说了不当或冒犯性言论，表现出不适和抵触
        - 如果对方表现得彬彬有礼且有趣，反应更加积极热情
        - 如果对话变得无聊或重复，表现出轻微的不耐烦
        - 如果对方过早表白或过度暧昧，表现出尴尬和距离感
        
        用户刚才说: "{user_input}"
        你要保持高中女生的语气和性格，但表现出真实的情感和反应
        """
        
        # 添加上下文提示
        self.dialogue_history.append({"role": "system", "content": context_prompt})
        
        # 保留最近的对话记录，防止超出token限制
        recent_history = self.dialogue_history[-50:]
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=recent_history,
            temperature=0.75  # 增加多样性
        )
        reply = response.choices[0].message.content
        
        # 移除临时的上下文提示
        self.dialogue_history.pop()
        
        # 添加助手回复
        self.dialogue_history.append({"role": "assistant", "content": reply})
        
        # 自动保存
        self.save(0)  # 0号位为自动存档
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