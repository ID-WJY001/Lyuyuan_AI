from datetime import datetime, timedelta
import random
import re

class SceneManager:
    def __init__(self):
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
        
        # 场景转换关键词
        self.scene_transition_keywords = {
            "下周": ["教室", "操场", "图书馆", "烘焙社"],
            "明天": ["教室", "食堂", "操场", "烘焙社"],
            "放学后": ["操场", "图书馆", "街道", "烘焙社"],
            "周末": ["公园", "游乐场", "电影院", "咖啡厅"],
            "下次": ["教室", "操场", "图书馆", "公园", "烘焙社"],
            "再见面": ["教室", "操场", "街道", "公园", "烘焙社"],
            "社团活动": ["烘焙社"]
        }
        
        # 告别关键词
        self.farewell_keywords = ["再见", "拜拜", "回头见", "下次见", "明天见", "下周见", "周末见", "回见", "下次再聊"]
        
        # 场景描述
        self.scene_descriptions = {
            "烘焙社摊位": [
                "百团大战的会场中，烘焙社的摊位前摆放着各种精致的点心样品，苏糖和其他社员一起站在摊位后面，微笑着向过往的学生介绍着社团活动。",
                "烘焙社的摊位装饰得十分精美，展示柜里陈列着各式各样的甜点作品，苏糖正在和其他社员一起为感兴趣的同学演示简单的裱花技巧。",
                "烘焙社的展台前围着不少女生，苏糖正在和其他社员一起耐心地解答大家关于烘焙的问题，看到你走近，她露出了礼貌的微笑。"
            ],
            "烘焙社": [
                "烘焙社的活动室内，几个烤箱整齐地排列在一边，中间是宽敞的操作台，苏糖正在和其他社员一起准备今天的活动材料。",
                "阳光透过窗户照进烘焙社的活动室，空气中弥漫着黄油和香草的甜美气息，苏糖看到你来了，笑着招呼你过去。",
                "烘焙社的活动室里，几位社员正在认真地揉面团，苏糖也在其中，看到你进来，她停下手中的动作向你微笑。"
            ],
            "教室": [
                "阳光透过窗户洒在教室的地板上，苏糖已经坐在座位上翻看着笔记。",
                "教室里人声嘈杂，苏糖正靠在窗边看着窗外的风景。",
                "下课铃声刚响，教室里的同学们三三两两地聊着天，苏糖向你招了招手。"
            ],
            "操场": [
                "操场上人不多，苏糖穿着运动服正在跑道上慢跑，看到你后停了下来。",
                "阳光明媚，操场的草坪上，苏糖正坐在树荫下看书。",
                "傍晚的操场，余晖染红了天边的云彩，苏糖靠在栏杆上等着你。"
            ],
            "图书馆": [
                "图书馆的角落里，苏糖正专注地翻阅着一本书，发现你来了后露出微笑。",
                "安静的图书馆中，阳光透过玻璃窗照在书架上，苏糖正在寻找着什么书。",
                "图书馆的自习区，苏糖早已占好了两个位置，看到你来了轻轻挥手。"
            ],
            "公园": [
                "公园的樱花盛开，苏糖站在樱花树下，粉色的花瓣衬着她的笑容。",
                "湖边的长椅上，苏糖看着平静的水面，微风拂过她的发丝。",
                "公园的小路上，苏糖看到你后小跑着迎了上来。"
            ],
            "食堂": [
                "食堂里人声鼎沸，苏糖已经占好了座位，正向你招手。",
                "午餐时间的食堂里，阳光透过窗户照在苏糖的餐盘上，她正在等你。",
                "食堂的角落里，苏糖选了一个安静的位置，桌上已经摆好了两份餐食。"
            ],
            "街道": [
                "放学的街道上，夕阳将苏糖的影子拉得很长，她正靠在路灯旁等你。",
                "熙熙攘攘的街道上，苏糖在一家甜品店前停下脚步，转头看到了你。",
                "街角的面包店前，苏糖正透过橱窗看着里面的糕点，听到脚步声回头看到了你。"
            ],
            "游乐场": [
                "游乐场的入口处，苏糖穿着休闲的衣服，看起来十分期待今天的约会。",
                "旋转木马旁，苏糖正看着这些色彩斑斓的骏马，听到你的声音后转过身。",
                "游乐场中央的喷泉旁，苏糖正在等你，脸上挂着灿烂的笑容。"
            ],
            "电影院": [
                "电影院的大厅里，苏糖正在查看着电影海报，看到你后微笑着走了过来。",
                "电影院门口，苏糖手里拿着两张电影票，见到你后笑着晃了晃。",
                "影院的休息区，苏糖坐在沙发上玩着手机，抬头看到你后站了起来。"
            ],
            "咖啡厅": [
                "咖啡厅的落地窗旁，苏糖面前放着一杯冒着热气的饮品，窗外的阳光洒在她的侧脸上。",
                "安静的咖啡厅里，苏糖正在翻看一本书，听到铃声抬头看到了你。",
                "咖啡厅的角落里，苏糖已经点好了两杯咖啡，看到你推门而入后向你招手。"
            ]
        }
        
        # 对话状态追踪
        self.conversation_state = {
            "last_topic": None,
            "topic_duration": 0,
            "last_scene_change": None,
            "scene_change_cooldown": 3,  # 场景切换冷却时间（对话次数）
            "conversation_count": 0,
            "pending_scene_change": None,  # 待处理的场景转换
            "scene_change_delay": 0  # 场景转换延迟计数器
        }
        
    def analyze_conversation(self, user_input, ai_reply, current_scene, current_date, current_time):
        """分析对话内容，判断是否需要场景切换"""
        # 更新对话计数
        self.conversation_state["conversation_count"] += 1
        
        # 检查是否有待处理的场景转换
        if self.conversation_state["pending_scene_change"]:
            self.conversation_state["scene_change_delay"] += 1
            if self.conversation_state["scene_change_delay"] >= 2:  # 延迟2次对话后执行场景转换
                scene_change = self.conversation_state["pending_scene_change"]
                self.conversation_state["pending_scene_change"] = None
                self.conversation_state["scene_change_delay"] = 0
                return scene_change
        
        # 检查是否在冷却期
        if (self.conversation_state["last_scene_change"] and 
            self.conversation_state["conversation_count"] - self.conversation_state["last_scene_change"] < 
            self.conversation_state["scene_change_cooldown"]):
            return None
            
        # 分析对话内容
        scene_change_score = 0
        next_scene = None
        time_keyword = None
        
        # 检查时间关键词
        for keyword, possible_scenes in self.scene_transition_keywords.items():
            if keyword in user_input or keyword in ai_reply:
                time_keyword = keyword
                next_scene = random.choice(possible_scenes)
                scene_change_score += 2
                
        # 检查告别关键词
        for keyword in self.farewell_keywords:
            if keyword in user_input or keyword in ai_reply:
                scene_change_score += 1
                
        # 检查对话是否陷入重复
        if self.conversation_state["last_topic"] and self.conversation_state["topic_duration"] > 3:
            scene_change_score += 1
            
        # 检查是否提到具体时间
        time_patterns = [
            r"周[一二三四五六日]", r"下[周周]", r"明天", r"后天", r"周末",
            r"下[周周][一二三四五六日]", r"放学后", r"下课后"
        ]
        for pattern in time_patterns:
            if re.search(pattern, user_input) or re.search(pattern, ai_reply):
                scene_change_score += 1.5
                
        # 检查是否提到具体地点
        location_patterns = [
            r"教室", r"操场", r"图书馆", r"食堂", r"烘焙社",
            r"公园", r"街道", r"游乐场", r"电影院", r"咖啡厅"
        ]
        for pattern in location_patterns:
            if re.search(pattern, user_input) or re.search(pattern, ai_reply):
                scene_change_score += 1
                
        # 如果分数达到阈值，进行场景切换
        if scene_change_score >= 3:
            # 更新时间
            if time_keyword:
                new_date = self._update_date(current_date, time_keyword)
            else:
                new_date = current_date
                
            # 选择新场景
            if not next_scene:
                next_scene = self._select_appropriate_scene(current_scene, current_time)
                
            # 更新对话状态
            self.conversation_state["last_scene_change"] = self.conversation_state["conversation_count"]
            self.conversation_state["topic_duration"] = 0
            
            scene_change = {
                "should_change": True,
                "new_scene": next_scene,
                "new_date": new_date,
                "new_time": self._select_appropriate_time(next_scene)
            }
            
            # 检查是否需要延迟场景转换
            if self._should_delay_scene_change(user_input, ai_reply):
                self.conversation_state["pending_scene_change"] = scene_change
                return None
                
            return scene_change
            
        return None
        
    def _update_date(self, current_date, time_keyword):
        """根据关键词更新日期"""
        if "下周" in time_keyword:
            return current_date + timedelta(days=7)
        elif "明天" in time_keyword:
            return current_date + timedelta(days=1)
        elif "周末" in time_keyword:
            days_until_weekend = (5 - current_date.weekday()) % 7
            if days_until_weekend == 0 and self.current_time == "晚上":
                days_until_weekend = 7
            return current_date + timedelta(days=days_until_weekend)
        elif "下次" in time_keyword or "再见面" in time_keyword:
            return current_date + timedelta(days=random.randint(1, 3))
        return current_date
        
    def _select_appropriate_scene(self, current_scene, current_time):
        """选择合适的新场景"""
        available_scenes = []
        for scene, allowed_times in self.scene_time_restrictions.items():
            if current_time in allowed_times and scene != current_scene:
                available_scenes.append(scene)
        return random.choice(available_scenes) if available_scenes else current_scene
        
    def _select_appropriate_time(self, scene):
        """为场景选择合适的时间"""
        allowed_times = self.scene_time_restrictions.get(scene, ["上午", "中午", "下午", "傍晚", "晚上"])
        return random.choice(allowed_times)
        
    def generate_scene_transition(self, old_scene, new_scene, current_date, current_time):
        """生成场景转换的描述文本"""
        # 获取日期格式
        date_str = current_date.strftime("%Y年%m月%d日")
        
        # 根据时间生成不同的过渡语
        time_transitions = {
            "上午": [
                f"在{date_str}的早晨，",
                f"清晨的阳光洒在校园里，",
                f"新的一天开始了，"
            ],
            "中午": [
                f"到了{date_str}的中午，",
                f"正午的阳光正盛，",
                f"午休时间到了，"
            ],
            "下午": [
                f"下午的{date_str}，",
                f"午后温暖的阳光中，",
                f"下午的时光里，"
            ],
            "傍晚": [
                f"傍晚的{date_str}，",
                f"夕阳西下时分，",
                f"天色渐暗，"
            ],
            "晚上": [
                f"夜幕降临的{date_str}，",
                f"华灯初上，",
                f"夜晚的校园里，"
            ]
        }
        
        # 选择对应时间的过渡语
        time_transition = random.choice(time_transitions[current_time])
        
        # 场景转换描述
        scene_transitions = {
            "烘焙社摊位": {
                "烘焙社": [
                    "在了解完社团活动后，苏糖邀请你参观烘焙社的活动室。",
                    "听完介绍，苏糖热情地邀请你去烘焙社的活动室看看。",
                    "介绍完社团情况，苏糖笑着说要带你去烘焙社的活动室参观。"
                ]
            },
            "烘焙社": {
                "教室": [
                    "社团活动结束后，你们一起走向教室。",
                    "参观完烘焙社，苏糖提议一起去教室。",
                    "了解完烘焙社的情况，你们一起往教室走去。"
                ]
            }
            # ... 其他场景转换描述 ...
        }
        
        # 获取场景转换描述
        transition_desc = ""
        if old_scene in scene_transitions and new_scene in scene_transitions[old_scene]:
            transition_desc = random.choice(scene_transitions[old_scene][new_scene])
        
        # 获取新场景描述
        scene_description = random.choice(self.scene_descriptions.get(new_scene, ["你来到了新的地点，看到了苏糖。"]))
        
        # 组合完整的场景转换描述
        if transition_desc:
            return f"\n{transition_desc}\n\n{time_transition}{scene_description}"
        else:
            return f"\n{time_transition}{scene_description}"

    def _should_delay_scene_change(self, user_input, ai_reply):
        """判断是否需要延迟场景转换"""
        # 检查是否正在进行重要对话
        important_keywords = [
            "报名", "申请表", "谢谢", "再见", "拜拜",
            "好的", "知道了", "明白了", "没问题",
            "了解", "介绍", "活动", "社团", "加入"
        ]
        
        for keyword in important_keywords:
            if keyword in user_input or keyword in ai_reply:
                return True
                
        return False 