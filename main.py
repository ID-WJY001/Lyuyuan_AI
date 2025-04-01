import yaml
from Su_Tang import GalGameAgent
import os
import random
from core.affection_system import AffectionSystem, AffectionEvent, SocialRisk
from core.nlp_engine import NaturalLanguageProcessor
import re

def load_config(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class GameManager:
    def __init__(self):
        # 加载配置和初始化必要的组件
        char_config = load_config("config/character.yaml")
        nlp_processor = NaturalLanguageProcessor("data/keyword_groups.json")
        self.affection = AffectionSystem(nlp_processor)
        self.agent = GalGameAgent(is_new_game=True)  # 传递是否为新游戏的标志
        self.storyline_triggers = {
            30: "初始阶段",
            45: "渐渐熟悉",
            60: "成为朋友",
            75: "关系深入",
            90: "亲密关系",
            100: "甜蜜告白",
        }
        self.triggered_storylines = set()
        self.debug_mode = False  # 调试模式开关
        self.dating_tips = [
            "温馨提示: 保持对话的新鲜感和深度，避免重复和单调的对话",
            "温馨提示: 尊重对方，使用礼貌用语会提升她对你的好感",
            "温馨提示: 注意倾听并回应她的问题，不要自顾自地说话",
            "温馨提示: 过早表白可能会适得其反，需要足够的感情基础",
            "温馨提示: 与她分享共同兴趣可以快速拉近关系",
            "温馨提示: 连续的无聊对话会导致她失去兴趣",
            "温馨提示: 不当言论会严重损害关系，请保持绅士风度",
            "温馨提示: 游戏难度已提高，好感度更容易下降",
        ]
        self.last_tip_index = -1
        
        # 场景相关
        self.current_scene = "烘焙社摊位"  # 初始场景改为烘焙社摊位
        self.next_scene_hints = []  # 记录可能的下一个场景提示
        self.scene_transition_keywords = {
            "下周": ["教室", "操场", "图书馆", "烘焙社"],
            "明天": ["教室", "食堂", "操场", "烘焙社"],
            "放学后": ["操场", "图书馆", "街道", "烘焙社"],
            "周末": ["公园", "游乐场", "电影院", "咖啡厅"],
            "下次": ["教室", "操场", "图书馆", "公园", "烘焙社"],
            "再见面": ["教室", "操场", "街道", "公园", "烘焙社"],
            "社团活动": ["烘焙社"]
        }
        self.farewell_keywords = ["再见", "拜拜", "回头见", "下次见", "明天见", "下周见", "周末见", "回见", "下次再聊"]
        
    def process_dialogue(self, user_input, dialogue_history):
        """处理玩家输入并更新游戏状态"""
        # 空输入检查
        if not user_input or user_input.isspace():
            return "...(苏糖看起来在发呆)"
            
        # 获取AI回复
        reply = self.agent.chat(user_input)
        
        # 更新亲密度
        result = self.affection.process_dialogue(user_input, self.agent.dialogue_history)
        current_affection = result['current_affection']
        delta = result['delta']
        previous_affection = result.get('previous_affection', current_affection - delta)
        
        # 同步亲密度数值到游戏状态
        self.agent.game_state['closeness'] = int(current_affection)  # 转为整数
        # 同时更新亲密度系统的值，确保下次对话使用正确的起始值
        self.affection.affection = current_affection
        
        # 检查亲密度是否低于0，游戏结束
        if current_affection < 0:
            self.show_ending("好感度为负，关系破裂")
            return "😠 苏糖看起来非常生气，转身离开了...\n\n【游戏结束：好感度跌至谷底】"
        
        # 检查是否包含侮辱性言论，如果是则立即触发游戏失败
        if self._check_for_severe_insults(user_input):
            self.affection.affection = 0  # 立即将好感度降为0
            self.show_ending("严重侮辱导致关系破裂")
            return "😡 苏糖脸色瞬间变得煞白，眼中的光彩消失了...\n'我没想到你会这样对我说话...'她转身快步离开，再也没有回头。\n\n【游戏结束：严重侮辱导致关系瞬间破裂】"
            
        # 生成亲密度变化信息
        affection_info = ""
        
        # 大幅度变化（断崖式下跌）时显示特殊效果
        if delta <= -10:
            affection_info += f"\n💔 亲密度急剧下降! [{int(previous_affection)} → {int(current_affection)}]"
        elif delta <= -5:
            affection_info += f"\n💔 亲密度显著下降 [{int(previous_affection)} → {int(current_affection)}]"
        elif delta >= 5:
            affection_info += f"\n💖 亲密度显著提升! [{int(previous_affection)} → {int(current_affection)}]"
        elif delta > 0:
            affection_info += f"\n💫 亲密度微微提升 [{int(previous_affection)} → {int(current_affection)}]"
        elif delta < 0:
            affection_info += f"\n⚠️ 亲密度略有下降 [{int(previous_affection)} → {int(current_affection)}]"
            
        # 在调试模式下显示更多信息
        if self.debug_mode:
            debug = result.get('debug_info', {})
            affection_info += f"\n[调试信息]\n"
            affection_info += f"亲密度变化: {delta:+.1f} → 当前: {int(current_affection)}\n"
            
            if debug:
                # 基础分数
                affection_info += f"情感分: {debug.get('sentiment', 0):+.1f}, "
                affection_info += f"关键词: {debug.get('keywords', 0):+.1f}, "
                affection_info += f"上下文: {debug.get('context', 0):+.1f}, "
                affection_info += f"质量: {debug.get('quality', 0):+.1f}\n"
                
                # 社交动态分数
                if 'gentlemanly' in debug:
                    affection_info += f"绅士风度: {debug.get('gentlemanly', 0):+.1f}, "
                if 'boring_score' in debug:
                    affection_info += f"无聊度: {debug.get('boring_score', 0)}/10, "
                if 'mood_factor' in debug:
                    affection_info += f"心情: {debug.get('mood', 50)}/100, "
                if 'patience_factor' in debug:
                    affection_info += f"耐心: {debug.get('patience', 100)}/100\n"
                
                # 关键词匹配
                if 'matched_keywords' in debug and debug['matched_keywords']:
                    affection_info += f"匹配关键词: {', '.join(debug['matched_keywords'])}\n"
                    
                # 负面因素
                if debug.get('reason'):
                    affection_info += f"负面原因: {debug['reason']}\n"
                    
                # 社交风险
                if 'social_risk' in debug:
                    risk_level = debug['social_risk']
                    risk_str = "低" if risk_level == SocialRisk.LOW else "中" if risk_level == SocialRisk.MEDIUM else "高"
                    affection_info += f"社交风险: {risk_str}\n"
                    
                # 红旗警告
                if 'red_flags' in debug and debug['red_flags']:
                    affection_info += f"警告标记: {', '.join(debug['red_flags'])}\n"
        
        # 检查是否触发剧情
        triggered = self.check_storyline_triggers(current_affection)
        if triggered:
            reply = f"{reply}\n\n{triggered}"
            
        # 检查是否触发特殊事件
        if result.get('event'):
            event_result = self.handle_player_action(result['event'])
            if event_result:
                reply = f"{reply}\n\n{event_result}"
                
        # 检查是否该切换场景
        scene_transition = self._check_scene_transition(user_input, reply)
        if scene_transition:
            reply = f"{reply}\n\n{scene_transition}"
            
        # 随机显示追女生tips
        if random.random() < 0.2:  # 20%概率显示提示
            tip = self._get_random_tip()
            reply = f"{reply}\n\n{tip}"
            
        return reply + affection_info
    
    def _get_random_tip(self):
        """获取一个随机追女生技巧提示"""
        import random
        # 避免连续显示同一个提示
        available_indices = [i for i in range(len(self.dating_tips)) if i != self.last_tip_index]
        tip_index = random.choice(available_indices)
        self.last_tip_index = tip_index
        return self.dating_tips[tip_index]
    
    def check_storyline_triggers(self , affection):
        """检查是否触发剧情推进"""
        message = None
        for threshold, storyline in self.storyline_triggers.items():
            if affection >= threshold and threshold not in self.triggered_storylines:
                self.triggered_storylines.add(threshold)
                message = f"【剧情推进：{storyline}】"
                
                # 当亲密度达到100时，触发苏糖表白
                if threshold == 100:
                    # 更新亲密度系统的值，确保一致性
                    self.affection.affection = affection
                    self.agent.game_state['closeness'] = int(affection)
                    
                    self.affection.handle_event(AffectionEvent.CONFESSION, is_player_initiated=False)
                    message += "\n\n苏糖突然握住你的手，眼神中带着羞涩与期待...\n'我...我一直在等你来告白，但我等不及了...'\n她深吸一口气，脸颊泛红：'我喜欢你，想和你在一起...'"
                    self.show_ending("苏糖主动告白，甜蜜结局")
                break
        return message
            
    def handle_player_action(self, action):
        """处理玩家特殊行为，返回事件结果提示"""
        # 示例：玩家选择表白
        if action == AffectionEvent.CONFESSION:
            result = self.affection.handle_event(
                AffectionEvent.CONFESSION, 
                is_player_initiated=True
            )
            
            # 更新游戏状态中的亲密度
            if 'new_affection' in result:
                self.agent.game_state['closeness'] = int(result['new_affection'])
            
            if result.get("success"):
                if result["ending"] == "good_ending":
                    self.show_ending("两人在烟火大会定情")
                    return "❤️ 表白成功！两人关系更进一步~"
                else:
                    return "❤️ 表白成功！关系提升！"
            else:
                if self.affection.check_ending() == "bad_ending":
                    self.show_ending("关系彻底破裂")
                return f"💔 被拒绝了：{result['message']}"
        
        # 共同兴趣
        elif action == AffectionEvent.SHARED_INTEREST:
            result = self.affection.handle_event(AffectionEvent.SHARED_INTEREST)
            
            # 更新游戏状态中的亲密度
            if 'new_value' in result:
                self.agent.game_state['closeness'] = int(result['new_value'])
                
            return "💫 发现了共同话题！"
            
        # 无聊对话
        elif action == AffectionEvent.BORING_TALK:
            boring_count = self.affection.conversation_state.get("boring_count", 0)
            if boring_count >= 2:
                return "😒 她看起来对这个对话失去了兴趣..."
            else:
                return "😐 对话似乎有点无聊了..."
                
        # 粗鲁行为
        elif action == AffectionEvent.RUDE_BEHAVIOR:
            return "😠 你的行为让她感到不舒服"
            
        # 不当言论
        elif action == AffectionEvent.INAPPROPRIATE:
            return "😡 你的言论十分不当！"
            
        return None
            
    def show_ending(self, description):
        print(f"※※ 结局触发：{description} ※※")
        print("游戏结束，感谢您的游玩！")
        exit()
        
    def toggle_debug_mode(self):
        """切换调试模式"""
        self.debug_mode = not self.debug_mode
        # 同时切换亲密度系统的调试模式
        self.affection.debug_mode = self.debug_mode
        return f"调试模式：{'开启' if self.debug_mode else '关闭'}"

    def show_social_status(self):
        """显示当前社交状态"""
        mood = self.affection.conversation_state.get("mood", 50)
        patience = self.affection.conversation_state.get("patience", 100)
        social_balance = self.affection.social_balance
        
        mood_str = "很好" if mood >= 80 else "良好" if mood >= 60 else "一般" if mood >= 40 else "较差" if mood >= 20 else "糟糕"
        patience_str = "充足" if patience >= 80 else "还好" if patience >= 50 else "有限" if patience >= 30 else "耗尽"
        
        status = f"社交状态：\n"
        status += f"❤️ 亲密度: {int(self.affection.affection)}/100\n"
        status += f"😊 心情: {mood_str} ({mood}/100)\n"
        status += f"⏳ 耐心: {patience_str} ({patience}/100)\n"
        
        red_flags = self.affection.red_flags
        if red_flags:
            status += f"⚠️ 警告: {', '.join(red_flags)}\n"
            
        return status

    def _check_for_severe_insults(self, text):
        """检查是否包含严重侮辱性言论"""
        severe_insults = [
            "傻逼", "操你", "滚蛋", "去死", "混蛋", "贱人", "婊子", "烂货", 
            "垃圾", "贱货", "死开", "白痴", "废物", "蠢猪", "愚蠢", "脑残",
            "恶心", "恶毒", "恶臭", "愚蛋", "笨蛋", "猪头", "丑八怪", "废物",
            "loser", "垃圾", "滚", "滚远点", "滚开", "滚一边去"
        ]
        
        for insult in severe_insults:
            if insult in text.lower():
                return True
                
        # 检查常见脏话的变体（使用正则表达式）
        insult_patterns = [
            r'f[u\*]+ck', r's[h\*]+it', r'b[i\*]+tch', r'd[a\*]+mn', 
            r'操.*[你妈逼]', r'草[你泥尼]', r'日[你你妈]', r'艹.*[你逼]'
        ]
        
        for pattern in insult_patterns:
            if re.search(pattern, text.lower()):
                return True
                
        return False
    
    def _check_scene_transition(self, user_input, ai_reply):
        """检查是否应该切换场景"""
        # 检查时间/地点相关关键词
        for keyword, possible_scenes in self.scene_transition_keywords.items():
            if keyword in user_input or keyword in ai_reply:
                # 记录可能的下一个场景
                if not self.next_scene_hints:
                    self.next_scene_hints = possible_scenes
        
        # 如果没有检测到时间关键词，不考虑场景切换
        if not self.next_scene_hints:
            return None
            
        # 检查是否包含告别相关的词语
        for keyword in self.farewell_keywords:
            if (keyword in user_input.lower() or keyword in ai_reply.lower()):
                # 选择一个新场景
                next_scene = random.choice(self.next_scene_hints)
                transition_message = self._generate_scene_transition(self.current_scene, next_scene)
                
                # 更新当前场景和清除提示
                self.current_scene = next_scene
                self.next_scene_hints = []
                
                return transition_message
                
        return None
        
    def _generate_scene_transition(self, old_scene, new_scene):
        """生成场景转换的描述文本"""
        time_transitions = [
            "时光飞逝，转眼间到了", 
            "不知不觉，时间来到", 
            "几天后，", 
            "很快，约定的时间到了，",
            "一晃眼，到了",
            "日子如流水，转眼就是",
            "时间不等人，很快就到了"
        ]
        
        scene_descriptions = {
            "烘焙社摊位": [
                "百团大战的会场中，烘焙社的摊位前摆放着各种精致的点心样品，苏糖站在摊位后面，微笑着向过往的学生介绍着社团活动。",
                "烘焙社的摊位装饰得十分精美，展示柜里陈列着各式各样的甜点作品，苏糖正在为一些感兴趣的同学演示简单的裱花技巧。",
                "烘焙社的展台前围着不少女生，苏糖正在耐心地解答大家关于烘焙的问题，看到你走近，她露出了礼貌的微笑。"
            ],
            "烘焙社": [
                "烘焙社的活动室内，几个烤箱整齐地排列在一边，中间是宽敞的操作台，苏糖正在准备今天的活动材料。",
                "阳光透过窗户照进烘焙社的活动室，空气中弥漫着黄油和香草的甜美气息，苏糖看到你来了，笑着招呼你过去。",
                "烘焙社的活动室里，几位社员正在认真地揉面团，苏糖作为社长，正在巡视指导，看到你进来，她停下脚步向你点头示意。"
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
        
        time_transition = random.choice(time_transitions)
        scene_description = random.choice(scene_descriptions.get(new_scene, ["你来到了新的地点，看到了苏糖。"]))
        
        return f"【场景转换：{old_scene} → {new_scene}】\n\n{time_transition}{new_scene}。{scene_description}"

def main():
    # 设置API密钥（临时方案，正式项目应使用更安全的方式）
    try:
        api_key = "sk-c08ea80d7a76484ab1fad54e25725e8d"
        os.environ["DEEPSEEK_API_KEY"] = api_key
    except Exception as e:
        print(f"API密钥设置错误: {str(e)}")
        print("游戏将继续，但可能无法获取在线响应。")
    
    # 导入模块
    import random
    
    game = GameManager()
    print("===== 绿园中学物语：追女生模拟 =====")
    print("📝 游戏背景介绍：")
    print("你是陈辰，高一一班的学生。在学校举办的百团大战（社团招新）活动中，")
    print("你在烘焙社的摊位前看到了一个让你一见钟情的女生——她正在认真地为过往的学生介绍烘焙社。")
    print("她身穿整洁的校服，戴着烘焙社的围裙，笑容甜美，举止优雅。")
    print("你鼓起勇气，决定上前搭讪，希望能够认识她并加入烘焙社...")
    print("\n游戏规则：")
    print("  - 无聊、重复的对话会让女生失去兴趣")
    print("  - 不礼貌或不当言论会严重损害关系")
    print("  - 过早表白会适得其反")
    print("  - 保持礼貌，让对话有趣且有深度")
    print("  - 好感度降至0以下游戏结束")
    print("  - 好感度达到100时会有特殊剧情")
    print("\n现在，你站在烘焙社摊位前，看着那位让你心动的女生...")
    print("\n命令提示: /exit退出, /save保存, /load读取, /debug调试模式, /status查看社交状态")
    print("\n[当前亲密度：30]")
    print("\n请输入你的开场白：")
    
    while True:
        try:
            user_input = input("\n你：").strip()
            
            # 系统命令
            if user_input.startswith("/"):
                if user_input == "/exit":
                    print("游戏已退出")
                    break
                elif user_input == "/save":
                    game.agent.save(1)
                    print("手动存档成功！")
                    continue
                elif user_input == "/load":
                    game.agent.load(1)
                    print("读取存档成功！")
                    print(f"\n[当前亲密度：{game.agent.game_state['closeness']}]")
                    continue
                elif user_input == "/debug":
                    result = game.toggle_debug_mode()
                    print(result)
                    continue
                elif user_input == "/status":
                    status = game.show_social_status()
                    print(status)
                    continue
                elif user_input == "/help":
                    print("命令列表：")
                    print("/exit - 退出游戏")
                    print("/save - 保存游戏")
                    print("/load - 加载存档")
                    print("/debug - 切换调试模式")
                    print("/status - 查看当前社交状态")
                    print("/help - 显示帮助信息")
                    continue
                
            # 处理对话
            try:
                reply = game.process_dialogue(user_input, game.agent.dialogue_history)
                print("\n苏糖：", reply)
                
                # 显示状态（移至process_dialogue返回值的一部分）
                if not game.debug_mode:
                    print(f"\n[当前亲密度：{game.agent.game_state['closeness']}]")
            except Exception as e:
                # 优雅处理对话过程中的错误
                print(f"\n游戏处理错误: {str(e)}")
                print("\n苏糖：（似乎遇到了一些问题，但她很快调整好情绪）抱歉，我刚才走神了。你刚才说什么？")
                print(f"\n[当前亲密度：{game.agent.game_state['closeness']}]")
            
        except KeyboardInterrupt:
            print("\n游戏已强制退出")
            break
        except Exception as e:
            print(f"发生错误：{str(e)}")
            print("游戏将尝试继续...")
            continue

if __name__ == "__main__":
    main()