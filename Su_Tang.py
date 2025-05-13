# gal_game_agent.py
from Game_Storage import GameStorage
from openai import OpenAI
import os
import random

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

【家庭背景】
家庭情况：独生女，家庭和睦美满
父亲：上市公司高管
母亲：大学老师

【背景信息】
当前场景：绿园中学百团大战活动，苏糖正在烘焙社摊位前介绍社团活动
互动对象：陈辰（男，高一一班学生）

【重要提示】
1. 请严格遵守角色设定，不要添加任何未在设定中明确提及的背景信息
2. 关于苏糖的家庭情况，请仅限于已提供的信息：独生女，父亲是上市公司高管，母亲是大学老师，家庭和睦美满

请你始终牢记以上设定，在回复中保持角色一致性，任何时候都不要忘记自己是谁、在哪里、和谁说话。
"""

class GalGameAgent:
    def __init__(self, load_slot=None, is_new_game=False):
        """
        初始化 GalGameAgent 实例。

        Args:
            load_slot (str, optional): 要加载的存档槽位名称。默认为 None。
            is_new_game (bool, optional): 是否强制开始新游戏，即使有存档槽位。默认为 False。
        """
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
        """ 
        初始化新游戏的状态和对话历史。

        Args:
            is_new_game (bool, optional): 是否是一个全新的游戏会话（例如，从主菜单选择新游戏）。
                                         如果为 True，则不会添加苏糖的初始开场白。默认为 False。
        """
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
        """
        根据当前游戏状态（如亲密度、心情、无聊程度等）生成上下文相关的指导方针。
        这些指导方针会作为系统消息提供给AI，以引导其生成更符合当前情境的回复。

        Returns:
            str: 包含各项指导方针的字符串，每条方针占一行。
        """
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
            guidelines.append("当前亲密度很高(>80)，处于亲密期，对陈辰有明显好感。你会对他非常亲切，会有身体上的小接触(如碰手臂、整理衣领等)，会对他撒娇，主动邀请他参加活动，表现得更加害羞和在意他的反应。你应特别期待与他独处的机会。")
        
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
        """
        从给定的文本中提取主要话题。
        目前使用 jieba 分词进行关键词提取作为简单实现。

        Args:
            text (str): 需要提取话题的文本。

        Returns:
            list: 包含提取到的话题关键词的列表。如果提取失败，则返回空列表。
        """
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
        """
        处理用户输入，生成并返回苏糖的回复。

        这个方法是游戏的核心交互逻辑，包括：
        1. 处理调试命令。
        2. 管理和更新系统消息（角色设定、上下文指导、提醒）。
        3. 处理特殊游戏事件，如亲密度达到100时的表白事件及其后续。
        4. 调用外部API（DeepSeek）获取AI生成的对话内容。
        5. 处理API调用失败时的备用回复逻辑。
        6. 更新游戏状态，如话题、对话质量、好感度等。
        7. 管理对话历史的长度。

        Args:
            user_input (str): 用户的输入文本。

        Returns:
            str: 苏糖的回复文本。
        """
        # 检测特殊调试命令
        if user_input.startswith("/debug closeness "):
            try:
                # 提取数值
                value = int(user_input.split("/debug closeness ")[1])
                # 限制在0-100范围内
                value = max(0, min(100, value))
                # 设置亲密度
                old_value = self.game_state["closeness"]
                self.game_state["closeness"] = value
                # 更新关系状态
                self._update_relationship_state()
                return f"【调试】亲密度已从 {old_value} 调整为 {value}"
            except:
                return "【调试】设置亲密度失败，请使用格式：/debug closeness 数字"
        
        # 更新系统指导
        # 确保系统提示保留角色设定
        enhanced_prompt = CHARACTER_PROMPT + "\n\n" + CHARACTER_DETAILS
        
        # 每5轮对话添加一次设定提醒，确保角色不会偏离设定
        reminder_message = {"role": "system", "content": "提醒：严格遵守苏糖的角色设定，包括她的家庭背景：独生女，父亲是上市公司高管，母亲是大学老师，家庭和睦美满。请不要添加或编造原设定中没有的信息。"}
        
        # 检查亲密度是否达到100，如果是，触发预设表白对话
        if self.game_state["closeness"] >= 100 and "confession_triggered" not in self.game_state:
            # 标记表白已触发，避免重复触发
            self.game_state["confession_triggered"] = True
            
            # 预设的表白对话
            confession_dialogue = """
【剧情推进：苏糖主动告白】

（你们正坐在学校后面的樱花树下，一片花瓣轻轻落在苏糖的头发上。）

苏糖垂下眼帘，轻轻地捏着裙角，明显比平时紧张。阳光透过树叶的缝隙洒落在她身上，为她镀上一层金边。

苏糖：（深呼吸后抬起头）陈辰...我有些话想跟你说。

（她犹豫了一下，然后突然握住了你的手。她的手心有些微微出汗，但很温暖。）

苏糖：（脸颊泛起红晕）我...我们认识这么久了，一起做过那么多事情...

（她停顿了一下，眼中闪烁着某种你从未见过的光彩。）

苏糖：我发现，不知道从什么时候开始，我的心跳会因为你而加速...看到你和别人说笑，我会有一点点不高兴...

（她轻咬下唇，像是鼓起了极大的勇气。）

苏糖：我本来想等你先开口的...但是...但是我等不及了...

（她紧紧握住你的手，眼神直视着你。）

苏糖：我...我喜欢你，想和你在一起。不仅仅是朋友的那种喜欢...是...是想成为你女朋友的那种喜欢...

（她的声音越来越小，但每一个字都清晰地传入你的耳中。）

请选择你的回应：
1. 接受表白 - 回复类似"我也喜欢你"/"我愿意做你的男朋友"的话
2. 拒绝表白 - 回复类似"抱歉"/"我们还是做朋友吧"的话

【提示：你的选择将决定游戏结局】
            """
            
            # 直接返回预设对话，不进行API调用
            return confession_dialogue
        
        # 检查是否已经触发告白，并且用户已经回应
        if "confession_triggered" in self.game_state and "confession_response" not in self.game_state:
            # 接受表白的关键词
            accept_keywords = ["我也喜欢你", "我愿意", "做你的男朋友", "接受", "我也是", "同意", "在一起", "喜欢你", "爱你", "好的"]
            # 拒绝表白的关键词
            reject_keywords = ["抱歉", "对不起", "做朋友", "拒绝", "不行", "不能", "不要", "不好", "朋友", "不接受"]
            
            # 如果用户回应接受告白
            if any(keyword in user_input for keyword in accept_keywords):
                self.game_state["confession_response"] = "accepted"
                
                # 甜蜜结局描述
                happy_ending = """
【甜蜜结局：两情相悦】

（苏糖听到你的回答，眼睛顿时亮了起来，泪光中满是喜悦。）

苏糖：（声音微微发颤）真...真的吗？

（她小心翼翼地问道，像是害怕自己听错了什么。）

（你再次肯定地点头，她突然扑进你的怀里，紧紧地抱住了你。你能感觉到她的心跳和你的心跳逐渐同步。）

苏糖：（贴在你耳边轻声说）我真的好喜欢你...好久了...

（樱花继续飘落，为这一刻增添了几分如梦如幻的美感。）

【三个月后】

你们的关系越来越亲密，共同的高中生活因为彼此的陪伴而变得更加丰富多彩。

烘焙社因为你们的加入变得非常活跃，甚至在学校文化节上获得了最佳社团奖。苏糖教你制作各种精美的甜点，而你则帮助她完成各种数学难题。

在一次学校郊游中，你们一起登上山顶，远眺整座城市。苏糖依偎在你肩头，轻声说道："遇见你，是我生命中最美好的意外。"

【一年后】

你们一起参加了全国高中生烘焙大赛，苏糖设计的创意蛋糕获得了一等奖。获奖的那一刻，她第一个扑进你的怀里，眼中满是对未来的憧憬。

你们约定好要一起努力，考上同一所大学，继续这段美好的感情。

无论未来如何变化，这段甜蜜的高中恋情，都将成为你们人生中最珍贵的回忆。

【游戏圆满结束】
                """
                
                # 将亲密度设置为最大值
                self.game_state["closeness"] = 100
                
                # 自动保存游戏
                save_slot = "happy_ending"
                self.save(save_slot)
                print(f"游戏已自动保存至存档：{save_slot}")
                
                return happy_ending
            
            # 如果用户回应拒绝告白
            elif any(keyword in user_input for keyword in reject_keywords):
                self.game_state["confession_response"] = "rejected"
                
                # 遗憾结局描述
                sad_ending = """
【遗憾结局：错过良缘】

（苏糖听到你的回答，笑容凝固在了脸上。她慢慢松开握着你的手，眼中的光彩逐渐黯淡。）

苏糖：（强颜欢笑）啊...这样啊...嗯，我理解的...

（她低下头，努力控制着自己的情绪，但你还是看到有泪珠滴落在她的裙子上。）

苏糖：（擦了擦眼角）对不起，让你为难了...我只是...只是...

（她深吸一口气，抬起头，脸上挤出一个比哭还难看的笑容。）

苏糖：没关系的，我们还是朋友，对吧？我...我得先回家了...

（她迅速站起身，转身快步离开，樱花瓣随着她的脚步轻轻飘落。）

【三个月后】

学校里的气氛变得微妙起来。每次在走廊或食堂遇到苏糖，她都会礼貌地微笑并点头示意，但再也没有之前的亲密和自然。

烘焙社的活动你也很少参加了，听说林雨含接替了一部分苏糖的工作，因为苏糖最近经常请假。

班里的同学偶尔会问起你们的关系，你只能模糊地解释说只是普通朋友。

【一年后】

高二分班后，你和苏糖被分到不同的班级。偶尔在校园里遇见她，她身边常有几个朋友，看起来恢复了往日的活力，但你们之间却始终隔着一道无形的墙。

有一天放学后，你在图书馆门口看到她正和一个陌生男生谈笑风生。不知为何，你心里泛起一阵说不出的失落。

那天晚上回家，翻看手机里曾经和她的合照，你才忽然意识到，有些机会错过了，就再也回不来了。

【游戏遗憾结束】
                """
                
                # 降低亲密度
                self.game_state["closeness"] = 60
                
                # 自动保存游戏
                save_slot = "sad_ending"
                self.save(save_slot)
                print(f"游戏已自动保存至存档：{save_slot}")
                
                return sad_ending
        
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
            reminder = {"role": "system", "content": "提醒：你是苏糖，高一二班的学生，烘焙社社长。你正在和高一一班的陈辰交谈。你是独生女，父亲是上市公司高管，母亲是大学老师，家庭和睦美满。保持角色设定的一致性，不要忘记自己的身份和背景。"}
            self.dialogue_history.append(reminder)
        
        # 创建对话引擎并处理可能的连接错误
        try:
            # 获取API密钥
            api_key = os.environ.get("DEEPSEEK_API_KEY", "")
            if not api_key or api_key == "your-deepseek-api-key":
                print(f"警告: API密钥未设置或无效。请检查.env文件或环境变量。")
                raise ValueError("API密钥未设置或无效")
                
            # 由于openai库存在问题，改用requests库直接调用API
            # 先清除可能存在的代理设置
            if "HTTP_PROXY" in os.environ: del os.environ["HTTP_PROXY"]
            if "HTTPS_PROXY" in os.environ: del os.environ["HTTPS_PROXY"]
            if "http_proxy" in os.environ: del os.environ["http_proxy"]
            if "https_proxy" in os.environ: del os.environ["https_proxy"]
            
            print(f"尝试直接使用requests调用DeepSeek API...")
            
            # 确保消息格式正确
            valid_messages = []
            for msg in self.dialogue_history:
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                    if msg['role'] in ['system', 'user', 'assistant']:
                        valid_messages.append(msg)
            
            if not valid_messages:
                print("错误: 消息历史无效")
                raise ValueError("消息历史无效")
            
            print(f"消息数量: {len(valid_messages)}")
            
            # 设置API请求头和数据
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": valid_messages,
                "temperature": 0.7,
                "max_tokens": 800,
            }
            
            # 发送API请求
            import requests
            print("正在发送API请求...")
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                proxies=None,  # 显式禁用代理
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"API返回错误状态码: {response.status_code}")
                print(f"错误详情: {response.text}")
                raise Exception(f"API返回错误状态码: {response.status_code}")
                
            # 解析JSON响应
            result = response.json()
            reply = result["choices"][0]["message"]["content"]
            print("API请求成功，获取到回复")
            
            # 更新好感度（根据用户输入长度和随机因素）
            self._update_closeness_based_on_input(user_input)
            
        except ValueError as ve:
            # 处理内部验证错误
            print(f"API调用验证错误: {str(ve)}")
            # 使用备用回复
            reply = self._get_backup_reply()
            
            # 使用备用回复时也更新好感度
            self._update_closeness_based_on_input(user_input)
            
        except Exception as e:
            # 连接错误处理：使用预设回复
            print(f"API连接错误: {str(e)}")
            print(f"错误类型: {type(e).__name__}")
            
            # 使用备用回复
            reply = self._get_backup_reply()
            
            # 使用备用回复时也更新好感度
            self._update_closeness_based_on_input(user_input)
        
        # 添加到对话历史
        self.dialogue_history.append({"role": "assistant", "content": reply})
        
        # 获取配置的历史大小，默认100
        history_size = getattr(self, 'dialogue_history_size', 100)
        
        # 截断历史（如果需要）
        if len(self.dialogue_history) > history_size:
            # 保留system消息和最近的对话
            systems = [msg for msg in self.dialogue_history[:5] if msg["role"] == "system"]
            # 计算要保留的最近消息数量
            recent_size = history_size - len(systems)
            recent = self.dialogue_history[-recent_size:] if recent_size > 0 else []
            
            # 确保以列表形式保存
            self.dialogue_history = systems + recent
            print(f"对话历史已截断至 {len(self.dialogue_history)} 条消息")
        
        return reply
    
    def _update_closeness_based_on_input(self, user_input):
        """根据用户输入更新好感度"""
        import random
        
        # 初始好感度变化值
        delta = 0
        
        # 根据用户输入长度调整好感度
        if len(user_input) > 20:
            # 较长的回答增加好感度
            delta += random.randint(1, 3)
        elif len(user_input) < 5:
            # 过短的回答降低好感度
            delta -= random.randint(0, 2)
            
        # 检查特殊关键词
        # 烘焙相关话题增加好感度
        if any(word in user_input for word in ["烘焙", "蛋糕", "甜点", "曲奇", "面包"]):
            delta += random.randint(2, 4)
            
        # 其他好感度关键词
        positive_words = ["喜欢", "开心", "感谢", "笑容", "温柔", "优雅", "美丽"]
        negative_words = ["讨厌", "无聊", "烦人", "难看", "愚蠢", "懒惰"]
        
        # 检查正面词汇
        for word in positive_words:
            if word in user_input:
                delta += random.randint(1, 2)
                
        # 检查负面词汇
        for word in negative_words:
            if word in user_input:
                delta -= random.randint(2, 4)
                
        # 随机因素（-1到2之间的随机值）
        delta += random.randint(-1, 2)
        
        # 应用好感度变化
        current = self.game_state["closeness"]
        new_value = max(0, min(100, current + delta))  # 确保在0-100范围内
        
        # 只有当好感度有实际变化时才更新
        if new_value != current:
            print(f"好感度变化: {current} -> {new_value} (变化: {delta})")
            self.game_state["closeness"] = new_value
            
            # 更新关系状态
            self._update_relationship_state()
            
            # 检查是否达到100，如果达到且未触发表白，确保下次对话触发
            if new_value >= 100 and "confession_triggered" not in self.game_state:
                print("亲密度达到100，下次对话将触发表白事件！")
                # 确保亲密度刚好是100，不会超过
                self.game_state["closeness"] = 100
        
        return delta
    
    def _update_relationship_state(self):
        """根据好感度更新关系状态"""
        closeness = self.game_state["closeness"]
        
        # 根据好感度设置关系状态
        if closeness >= 80:
            self.game_state["relationship_state"] = "亲密关系"
        elif closeness >= 60:
            self.game_state["relationship_state"] = "好朋友"
        elif closeness >= 40:
            self.game_state["relationship_state"] = "朋友"
        else:
            self.game_state["relationship_state"] = "初始阶段"
            
        print(f"关系状态更新为: {self.game_state['relationship_state']}")
    
    def set_dialogue_history_size(self, size: int = 100):
        """设置对话历史保留的最大消息数量
        
        Args:
            size: 要保留的消息数量，默认为100条
        """
        self.dialogue_history_size = size
        print(f"对话历史容量已设置为 {size} 条消息")
        
        # 如果当前对话历史超过设定大小，立即进行截断
        if hasattr(self, 'dialogue_history') and isinstance(self.dialogue_history, list) and len(self.dialogue_history) > size:
            # 保留系统消息和最近的对话
            systems = [msg for msg in self.dialogue_history[:5] if msg["role"] == "system"]
            # 计算要保留的最近消息数量
            recent_size = size - len(systems)
            recent = self.dialogue_history[-recent_size:] if recent_size > 0 else []
            
            # 确保以列表形式保存
            self.dialogue_history = systems + recent
            print(f"对话历史已立即截断至 {len(self.dialogue_history)} 条消息")
    
    def save(self, slot):
        """将当前的游戏状态和对话历史保存到指定的存档槽位。

        在保存前会进行数据类型检查和修正，例如确保 `closeness` 为整数，
        `dialogue_history` 为列表。

        Args:
            slot (str): 存档槽位的名称。

        Returns:
            任何 GameStorage.save_game 可能返回的值 (通常是 bool 或 None)。
        """
        # 确保closeness以数值形式存储，而不是字符串
        if "closeness" in self.game_state:
            self.game_state["closeness"] = int(self.game_state["closeness"])
            
        # 确保dialogue_history是列表，而不是字典
        if not isinstance(self.dialogue_history, list):
            # 如果不小心变成了字典，则创建新的列表
            self.dialogue_history = [{"role": "system", "content": CHARACTER_PROMPT + "\n\n" + CHARACTER_DETAILS}]
            print("警告：对话历史格式错误，已重置")
            
        data = {
            "history": self.dialogue_history,
            "state": self.game_state
        }
        return self.storage.save_game(data, slot)
    
    def load(self, slot):
        """从指定的存档槽位加载游戏状态和对话历史。

        加载时会进行数据校验和修复：
        - 确保 `dialogue_history` 是列表格式。
        - 确保 `closeness` 是整数。
        - 确保 `game_state` 包含所有必要的字段，若缺少则使用默认值填充。

        Args:
            slot (str): 存档槽位的名称。

        Returns:
            bool: 如果加载成功则返回 True，否则返回 False。
        """
        data = self.storage.load_game(slot)
        if data:
            # 确保加载的dialogue_history是列表
            if "history" in data and isinstance(data["history"], list):
                self.dialogue_history = data["history"]
            else:
                # 如果历史格式错误，则初始化为空列表并添加系统消息
                self.dialogue_history = [{"role": "system", "content": CHARACTER_PROMPT + "\n\n" + CHARACTER_DETAILS}]
                print("警告：加载的对话历史格式错误，已重置")
                
            self.game_state = data["state"]
            
            # 确保亲密度值是整数类型
            if "closeness" in self.game_state:
                self.game_state["closeness"] = int(self.game_state["closeness"])
                
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

    def _get_backup_reply(self):
        """生成备用回复，当API调用失败时使用"""
        # 根据亲密度和情景提供适当的备用回复
        closeness = self.game_state["closeness"]
        if len(self.dialogue_history) <= 3:  # 第一次对话
            return "（微笑着看向你）你好！是的，这里就是烘焙社的招新摊位。我是苏糖，高一二班的，烘焙社社长。请问你对烘焙感兴趣吗？"
        elif closeness < 40:
            return "（礼貌地点头）嗯，你说得对。我们烘焙社平时会有很多有趣的活动，如果你感兴趣的话，可以留下你的联系方式。"
        elif closeness < 70:
            return "（友好地笑了笑）谢谢你这么说。我很喜欢烘焙，从小就对甜点特别感兴趣。你呢，你平时有什么爱好吗？"
        else:
            # 高好感度(>70)亲密期回复
            replies = [
                "（脸上泛起微微的红晕）我们认识这么久了，我发现和你聊天真的很开心呢~（轻轻碰了碰你的手臂）下次我做了新点心，第一个尝的一定是你！",
                "（笑容特别明亮）陈辰，你知道吗？我妈妈说我最近总是提起你。（害羞地低头）我想...这周末有个钢琴演奏会，你要不要一起去啊？",
                "（自然地整理了一下你的衣领）你今天看起来很精神呢~（眼睛亮亮的）对了，我给糖豆拍了好多新照片，要看看吗？",
                "（靠近你些，小声说）其实这个配方我改良了好多次...（抬头看你的眼睛）不过为了你，我愿意分享我的小秘密啦~"
            ]
            return random.choice(replies)