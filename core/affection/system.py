"""
核心情感与亲密度系统模块。

该模块定义了 `AffectionSystem` 类，它是游戏情感和亲密度管理的核心。
它负责处理玩家的对话输入，评估多种社交因素（如言辞、话题、情绪、重复度等），
并基于这些评估动态调整与角色之间的亲密度值。系统还管理特殊事件的处理、
结局的判断，并能与其他游戏子系统（如话题、剧情管理器）同步亲密度状态。

它依赖于外部的自然语言处理器 (NLP) 以及内部的关键词分析器 (`KeywordAnalyzer`)
和对话评估器 (`DialogueEvaluator`) 来实现复杂的逻辑。
"""
import random
import json
import re
from collections import Counter
from .events import AffectionEvent, SocialRisk, Phase
from .keyword_analyzer import KeywordAnalyzer
from .dialogue_evaluator import DialogueEvaluator

class AffectionSystem:
    def __init__(self, nlp_processor):
        """
        初始化情感与亲密度系统。

        Args:
            nlp_processor: 一个外部传入的自然语言处理器实例，用于文本分析。
        
        初始化内容包括：
        - 设置初始亲密度值。
        - 加载情感系统相关的配置文件 (例如 `config/affection_config.json`)。
        - 初始化子模块，如 `KeywordAnalyzer` 和 `DialogueEvaluator`。
        - 初始化各种内部状态，包括最近输入历史、负面行为标记、对话状态
          (如无聊计数、粗鲁计数、心情、耐心值等)、社交平衡度、难度系数和调试模式。
        - 初始化用于存储已注册其他游戏子系统的列表。
        """
        self.nlp = nlp_processor
        self.affection = 30  # 初始值设为30
        self.phase_history = []
        
        # 加载配置
        self.config = self.load_config("config/affection_config.json")
        
        # 初始化子模块
        self.keyword_analyzer = KeywordAnalyzer(self.config)
        self.dialogue_evaluator = DialogueEvaluator(self.keyword_analyzer)
        
        # 状态管理
        self.last_inputs = []  # 记录最近的输入，用于检测重复
        self.red_flags = []    # 记录严重负面行为
        self.conversation_state = {
            "last_topic": None,
            "topic_continuity": 0,
            "dialogue_quality": 0,
            "boring_count": 0,     # 无聊对话计数
            "rude_count": 0,       # 粗鲁行为计数
            "mood": 50,            # 当前心情(0-100)
            "patience": 100,       # 耐心值(0-100)
            "recent_topics": []    # 最近的话题，用于检测话题重复
        }
        
        self.social_balance = 50   # 社交平衡度(0-100)，影响整体评价
        self.difficulty_factor = 1.2  # 难度系数，降低为1.2（原来是1.8）
        self.debug_mode = False  # 调试模式开关
        
        # 注册的系统列表
        self.registered_systems = []

    def register_system(self, system):
        """
        将一个外部游戏子系统注册到情感系统中。

        注册后的系统可以在情感系统的亲密度值发生变化时，
        通过其 `update_affection` 方法接收到更新。

        Args:
            system: 需要注册的游戏子系统实例。

        Returns:
            bool: 如果系统成功注册（之前未注册过），则返回 True；否则返回 False。
        """
        if system not in self.registered_systems:
            self.registered_systems.append(system)
            return True
        return False
            
    def update_value(self, new_value):
        """
        直接更新情感系统的核心亲密度值，并同步到所有已注册的子系统。

        亲密度值会被限制在 0 到 100 之间。

        Args:
            new_value (int or float): 新的亲密度值。

        Returns:
            float: 更新并限制范围后的当前亲密度值。
        """
        if new_value != self.affection:
            self.affection = max(0, min(100, new_value))
            # 同步到注册的系统
            for system in self.registered_systems:
                if hasattr(system, 'update_affection'):
                    system.update_affection(self.affection)
        return self.affection

    def process_dialogue(self, user_input, dialogue_history):
        """
        处理用户的对话输入，并据此更新亲密度及相关游戏状态。

        这是情感系统中最核心和复杂的方法。它按顺序执行以下操作：
        1.  记录处理前的亲密度值。
        2.  检查输入有效性：处理空输入或过短输入（减少耐心）。
        3.  检测重复输入：如果与最近几次输入完全相同，则视为无聊，减少耐心和亲密度。
        4.  更新最近输入历史记录。
        5.  调用NLP模块分析用户输入，获取情感、关键词等信息。
        6.  检测输入中是否有单个词汇被过度重复，若是则视为无聊。
        7.  检测是否短时间内进行了过于频繁的短对话，若是则减少耐心和社交平衡。
        (后续步骤见方法内其他注释块)

        Args:
            user_input (str): 用户的最新对话输入文本。
            dialogue_history (list): （通常是字符串列表）包含此前的对话历史。

        Returns:
            dict: 一个包含亲密度变化详情、当前亲密度、事件类型、消息以及
                  大量调试信息的字典。 (具体结构见方法末尾注释)
        """
        previous_affection = self.affection  # 记录修改前的亲密度
        
        # --- 1. 输入有效性与重复性检查 ---
        # 空输入或过短输入检测
        if not user_input or user_input.isspace() or len(user_input) < 2:
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 5)
            return {
                "delta": 0,
                "current_affection": self.affection,
                "previous_affection": previous_affection,
                "event": None, # 通常可以定义一个 AffectionEvent.INVALID_INPUT
                "message": "输入内容过短，苏糖似乎没有理解。",
                "debug_info": {"reason": "输入过短或无效", "social_risk": SocialRisk.LOW}
            }
            
        # 完全重复输入检测
        if user_input in self.last_inputs:
            self.conversation_state["boring_count"] += 1
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 10)
            penalty = 3 * self.difficulty_factor
            current_affection = max(0, self.affection - penalty) # 预计算当前好感度
            delta = current_affection - self.affection # 计算实际变化值
            self.affection = current_affection # 更新好感度
            return {
                "delta": delta,
                "current_affection": self.affection,
                "previous_affection": previous_affection,
                "event": AffectionEvent.BORING_TALK,
                "message": "同样的话说第二遍就没意思了呢。",
                "debug_info": {"reason": "完全重复的输入", "social_risk": SocialRisk.MEDIUM}
            }
            
        # 更新最近输入记录 (用于重复检测)
        self.last_inputs.append(user_input)
        if len(self.last_inputs) > 5: # 保留最近5条输入
            self.last_inputs.pop(0)
        
        # --- 2. NLP分析与初步内容检查 ---
        analysis = self.nlp.analyze(user_input) # 调用NLP进行分析
        
        # 检测单个词汇的过度重复 (例如"猫咪猫咪猫咪")
        word_counter = Counter(re.findall(r'\w+', user_input))
        repetitive_words = [word for word, count in word_counter.items() if count > 2 and len(word) > 1]
        
        if repetitive_words:
            self.conversation_state["boring_count"] += 1
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 8)
            # 此处惩罚较小，因为可能只是口吃或强调，但也可能令人厌烦
            penalty = 3.0 # 固定惩罚值，不受难度系数影响
            current_affection = max(0, self.affection - penalty)
            delta = current_affection - self.affection
            self.affection = current_affection
            return {
                "delta": delta,
                "current_affection": self.affection,
                "previous_affection": previous_affection,
                "event": AffectionEvent.BORING_TALK,
                "message": "一直说同一个词，是卡住了吗？",
                "debug_info": {"reason": f"单个词汇重复多次: {repetitive_words}", "social_risk": SocialRisk.MEDIUM}
            }
            
        # 过于频繁的短对话检测 (例如，连续追问)
        if len(self.last_inputs) >= 3 and all(len(inp) < 15 for inp in self.last_inputs[-3:]):
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 5)
            self.social_balance = max(0, self.social_balance - 3)
            # 此处不直接扣分，但会影响后续的心情和耐心恢复，以及社交平衡
        
        # --- 3. 不得体言论检测 (续) ---
        inappropriate_words = self.keyword_analyzer.check_inappropriate(user_input)
        if inappropriate_words:
            # 根据检测到的不当言论类型和数量确定惩罚力度
            has_severe_insult = "侮辱性言论" in inappropriate_words
            has_sexual_hint = "不适当的性暗示" in inappropriate_words
            penalty = 0
            
            # 侮辱性言论可能导致好感度大幅下降甚至直接归零
            if has_severe_insult:
                # 有10%的概率或检测到多种侮辱性言论时，直接归零
                if random.random() < 0.1 or len(inappropriate_words) >= 2:
                    penalty = self.affection # 惩罚值为当前全部好感度
                    message = "你的言论让苏糖感到受到了严重的冒犯！好感度降至冰点。"
                else:
                    # 大幅降分，但不至于直接归零
                    penalty = min(80, 20 * len(inappropriate_words) * self.difficulty_factor)
                    message = "这种话非常伤人，苏糖看起来很难过。"
            # 性暗示言论，尤其在好感度不高时，也可能导致好感度大幅下降甚至归零
            elif has_sexual_hint:
                # 好感度低于60时，有30%概率或检测到多种性暗示时，直接归零
                if (random.random() < 0.3 and self.affection < 60) or len(inappropriate_words) >= 3:
                    penalty = self.affection
                    message = "苏糖被你的话吓到了，好感度降至冰点！"
                else:
                    # 大幅降分
                    penalty = min(60, 15 * len(inappropriate_words) * self.difficulty_factor)
                    message = "这样的话题对苏糖来说似乎太早了，她看起来很不自在。"
            else:
                # 其他一般性的不得体言论
                penalty = min(40, 10 * len(inappropriate_words) * self.difficulty_factor)
                message = "这样说话不太礼貌，苏糖皱起了眉头。"
            
            self.conversation_state["rude_count"] += 1
            self.social_balance = max(0, self.social_balance - 20) # 社交平衡大幅下降
            
            current_affection = max(0, self.affection - penalty)
            delta = current_affection - self.affection
            self.affection = current_affection
            return {
                "delta": delta,
                "current_affection": self.affection,
                "previous_affection": previous_affection,
                "event": AffectionEvent.INAPPROPRIATE,
                "message": message,
                "debug_info": {"reason": f"不得体言论: {inappropriate_words}", "social_risk": SocialRisk.HIGH}
            }
        
        # --- 4. 对话质量评估 (绅士风度与无聊度) ---
        # 计算对话的"绅士风度"分数
        gentlemanly_score, gentlemanly_factors = self.dialogue_evaluator.evaluate_gentlemanly(user_input, dialogue_history)
        
        # 计算对话的"无聊度"
        boring_score, boring_factors = self.dialogue_evaluator.evaluate_boringness(user_input, dialogue_history, self.affection)
        
        # 无聊度过高，触发无聊事件
        if boring_score > 7: # 无聊度阈值，可配置
            self.conversation_state["boring_count"] += 1
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 10)
            self.conversation_state["mood"] = max(0, self.conversation_state["mood"] - 10)
            
            # 连续多次无聊对话，导致更严重的惩罚
            if self.conversation_state["boring_count"] >= 3:
                penalty = 15 * self.difficulty_factor
                self.social_balance = max(0, self.social_balance - 15)
                message = "和你的对话越来越没意思了，苏糖已经不想再继续了。"
                current_affection = max(0, self.affection - penalty)
                delta = current_affection - self.affection
                self.affection = current_affection
                return {
                    "delta": delta,
                    "current_affection": self.affection,
                    "previous_affection": previous_affection,
                    "event": AffectionEvent.BORING_TALK,
                    "message": message,
                    "debug_info": {
                        "reason": "连续多次无聊对话", 
                        "boring_factors": boring_factors,
                        "social_risk": SocialRisk.HIGH
                    }
                }
            else:
                # 单次无聊对话的惩罚
                penalty = boring_score * 0.6 * self.difficulty_factor
                message = "刚才的话题有点干巴巴的呢...苏糖看起来没什么精神。"
                current_affection = max(0, self.affection - penalty)
                delta = current_affection - self.affection
                self.affection = current_affection
                return {
                    "delta": delta,
                    "current_affection": self.affection,
                    "previous_affection": previous_affection,
                    "event": AffectionEvent.BORING_TALK,
                    "message": message,
                    "debug_info": {
                        "reason": "单次无聊对话", 
                        "boring_factors": boring_factors,
                        "social_risk": SocialRisk.MEDIUM
                    }
                }
        
        # --- 5. 计算各项正面及负面影响的 delta 值 (续) ---
        # 计算情感影响 (来自NLP分析结果)
        sentiment_delta = analysis["sentiment"] * 2.5  # 情感得分的权重设为2.5
        
        # 检查关键词匹配 (来自NLP分析结果和KeywordAnalyzer)
        keywords = analysis["keywords"]
        keyword_analysis = self.keyword_analyzer.analyze_keywords(keywords)
        keyword_delta = keyword_analysis["delta"] # 关键词带来的好感度变化
        matched_keywords = keyword_analysis["matched_keywords"] # 匹配到的具体关键词
        
        # 计算上下文连贯性影响 (来自NLP分析和DialogueEvaluator)
        coherence_score = analysis["coherence"] # NLP评估的文本自身连贯性
        context_bonus = self.dialogue_evaluator.evaluate_context_relevance(user_input, dialogue_history) # 与对话历史的关联度
        context_delta = coherence_score * 2 + context_bonus # 综合上下文影响
        
        # 计算输入长度和内容质量影响 (来自DialogueEvaluator)
        quality_delta = self.dialogue_evaluator.evaluate_input_quality(user_input)
        
        # 风度评分影响 (来自之前计算的gentlemanly_score)
        gentleman_delta = gentlemanly_score / 2.0
        
        # --- 6. 汇总 delta，应用调整并更新状态 ---
        total_delta = sentiment_delta + keyword_delta + context_delta + quality_delta + gentleman_delta
        
        # 添加随机波动，增加一些不确定性
        random_factor = random.uniform(-0.5, 1.0) # 波动范围可调整
        total_delta += random_factor
        
        # 应用心情和耐心对 delta 的调整
        mood_factor = self.conversation_state["mood"] / 50.0  # 心情因子 (1.0为标准)
        patience_factor = self.conversation_state["patience"] / 100.0  # 耐心因子 (1.0为满耐心)
        
        # 心情差时，负面影响加剧；心情好时，正面影响增强
        if total_delta < 0:
            total_delta *= (2.0 - mood_factor) * self.difficulty_factor
        else:
            total_delta *= mood_factor * 0.85
        
        # 耐心值整体上调整 delta 的幅度
        total_delta *= patience_factor
        
        # 限制单次对话中亲密度的最大变化幅度
        if total_delta > 0:
            total_delta = min(6, total_delta)  # 单次最大加分
        else:
            total_delta = max(-6 * self.difficulty_factor, total_delta)  # 单次最大扣分 (受难度系数影响)
            
        # 以小概率触发随机降分事件，增加游戏挑战性
        if random.random() < 0.1: # 10%的概率触发
            random_penalty = random.uniform(0.3, 1.0) * self.difficulty_factor
            total_delta -= random_penalty
            if self.debug_mode:
                print(f"[AffectionSystem DEBUG] 随机降分触发: -{random_penalty:.2f}")
                
        # --- 7. 更新最终亲密度、心情、耐心，并确定事件类型 ---
        self.affection = max(0, min(100, self.affection + total_delta)) # 更新亲密度，并确保在0-100范围
        
        # 根据本次亲密度变化，回顾性地调整心情和耐心
        if total_delta > 0.5: # 稍微积极的变化就可能改善心情和耐心
            self.conversation_state["mood"] = min(100, self.conversation_state["mood"] + total_delta * 2)
            if self.conversation_state["patience"] < 80: # 耐心值较低时更容易恢复
                self.conversation_state["patience"] = min(100, self.conversation_state["patience"] + 2)
        elif total_delta < -0.5: # 稍微负面的变化就可能降低心情和耐心
            self.conversation_state["mood"] = max(0, self.conversation_state["mood"] + total_delta) # total_delta是负值
            self.conversation_state["patience"] = max(0, self.conversation_state["patience"] - 3)
            
        # 根据亲密度变化的剧烈程度，确定一个概括性的事件类型
        event_for_return = AffectionEvent.NORMAL_DIALOGUE # 默认为普通对话
        if total_delta > 4: # 大幅正面变化
            event_for_return = AffectionEvent.SHARED_INTEREST # 可视为发现共同兴趣或愉快交流
        elif total_delta < -4: # 大幅负面变化
            event_for_return = AffectionEvent.RUDE_BEHAVIOR # 可视为粗鲁行为或不愉快交流
            
        # --- 8. 构建并返回结果 --- 
        # 此处返回的 event (event_for_return) 是对本次对话整体效果的概括总结，
        # 而在方法前面部分因特定原因（如重复、不得体言论）提前返回时，
        # 使用的是更具体的事件类型。
        result = {
            "delta": total_delta,
            "current_affection": self.affection,
            "previous_affection": previous_affection,
            "event": event_for_return,
            "message": "", # 通常由调用方根据event和delta填充具体消息
            "debug_info": {
                "sentiment_delta": sentiment_delta,
                "keyword_delta": keyword_delta,
                "matched_keywords": matched_keywords,
                "context_delta": context_delta,
                "quality_delta": quality_delta,
                "gentleman_delta": gentleman_delta,
                "boringness_score": boring_score,
                "boring_factors": boring_factors,
                "gentlemanly_score": gentlemanly_score,
                "gentlemanly_factors": gentlemanly_factors,
                "mood_factor": mood_factor,
                "patience_factor": patience_factor,
                "final_total_delta_before_clamping": total_delta, # 用于调试，看限制前的delta
                "social_risk": self._evaluate_social_risk()
            }
        }
        # 同步好感度到其他注册系统
        self.update_value(self.affection)
            
        return result
    
    def _evaluate_social_risk(self):
        """
        内部辅助方法，用于评估当前对话的整体社交风险等级。

        社交风险基于以下因素：
        - `boring_count`: 无聊对话的累计次数。
        - `rude_count`: 粗鲁或不得体行为的累计次数。
        - `patience`: 角色的当前耐心值。

        Returns:
            SocialRisk: 一个 `SocialRisk` 枚举成员 (HIGH, MEDIUM, LOW)，
                        表示当前评估的社交风险等级。
        """
        if self.conversation_state["boring_count"] > 3 or self.conversation_state["rude_count"] > 1:
            return SocialRisk.HIGH
        elif self.conversation_state["boring_count"] > 1 or self.conversation_state["patience"] < 50:
            return SocialRisk.MEDIUM
        else:
            return SocialRisk.LOW
    
    def load_config(self, path):
        """
        从指定的JSON文件路径加载情感系统的配置文件。

        配置文件通常包含：
        - `event_effects`: 定义了不同 `AffectionEvent` 对亲密度的基础影响值。
        - `confession_probability` (在代码中被转换为 `confession_prob`): 
          定义了在不同亲密度阈值下，玩家发起告白的成功概率。
        
        此方法会尝试加载文件，如果文件不存在或格式错误，则会打印错误信息并返回一套
        硬编码的默认配置，以确保系统能够继续运行。
        它还会确保一些关键的事件效果（如BORING_TALK, RUDE_BEHAVIOR, INAPPROPRIATE）
        在配置中存在，如果不存在则添加默认值。

        Args:
            path (str): 配置文件的路径 (通常是 `config/affection_config.json`)。

        Returns:
            dict: 加载或生成的配置字典。
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 确保配置中包含所有必要字段
            if "event_effects" not in config:
                config["event_effects"] = {}
                
            # 添加新事件效果
            if "6" not in config["event_effects"]:  # BORING_TALK
                config["event_effects"]["6"] = -5
            if "7" not in config["event_effects"]:  # RUDE_BEHAVIOR
                config["event_effects"]["7"] = -10
            if "8" not in config["event_effects"]:  # INAPPROPRIATE
                config["event_effects"]["8"] = -15
                
            # 转换概率配置为枚举键
            config["confession_prob"] = {
                int(k): v for k, v in config.get("confession_probability", {}).items()
            }
            
            return config
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            # 返回默认配置
            return {
                "event_effects": {
                    "1": 1,    # NORMAL_DIALOGUE
                    "2": 5,    # SHARED_INTEREST
                    "3": 10,   # DATE_ACCEPTED
                    "4": 0,    # CONFESSION (特殊处理)
                    "5": -10,  # TABOO_TOPIC
                    "6": -5,   # BORING_TALK
                    "7": -10,  # RUDE_BEHAVIOR
                    "8": -15   # INAPPROPRIATE
                },
                "confession_prob": {
                    30: 0.01,  # 好感度30时，成功率1%
                    50: 0.1,   # 好感度50时，成功率10%
                    70: 0.5,   # 好感度70时，成功率50%
                    90: 0.9    # 好感度90时，成功率90%
                }
            }

    def handle_event(self, event, is_player_initiated=True, **kwargs):
        """
        处理特定的情感相关事件，并更新亲密度。

        不同的事件类型对亲密度的影响不同，有些事件（如告白）有复杂的判断逻辑。

        Args:
            event (AffectionEvent): 需要处理的事件类型，是一个 `AffectionEvent` 枚举成员。
            is_player_initiated (bool, optional): 指示事件是否由玩家主动发起。
                                                主要用于区分玩家告白和AI(角色)告白。
                                                默认为 True。
            **kwargs: 其他可能的参数，当前未使用。

        Returns:
            dict: 一个包含事件处理结果的字典。其结构根据事件类型而有所不同：
                  - 对于告白事件 (AffectionEvent.CONFESSION):
                    {
                        "success": bool,       // 告白是否成功
                        "message": str,        // 给玩家的反馈消息
                        "ending": str,         // 触发的结局类型 (例如 "good_ending", "bad_ending")
                        "old_affection": float, // 事件处理前亲密度
                        "new_affection": float  // 事件处理后亲密度
                    }
                  - 对于发现共同兴趣事件 (AffectionEvent.SHARED_INTEREST):
                    {
                        "delta": float,       // 亲密度变化量
                        "old_value": float,   // 旧亲密度
                        "new_value": float    // 新亲密度
                    }
                  - 对于其他多数事件:
                    {
                        "delta": float,       // 亲密度变化量 (通常来自配置)
                        "old_value": float,   // 旧亲密度
                        "new_value": float    // 新亲密度
                    }
        """
        event_type_str = str(event.value) # 将枚举值转为字符串以匹配配置文件中的键
        effect = self.config.get("event_effects", {}).get(event_type_str, 0)
        old_affection_before_event = self.affection # 记录事件处理前的亲密度
        
        if event == AffectionEvent.CONFESSION:
            # --- 告白事件的特殊处理逻辑 ---
            current_phase_str = self._get_current_phase() # 获取当前关系阶段
            
            if is_player_initiated:
                # --- 玩家主动发起的告白 ---
                success_confession = False
                message_confession = ""
                ending_type_confession = "continue" # 默认游戏继续
                affection_change_confession = 0

                # 判断告白成功的核心条件：亲密度足够高 (>=75) 且没有太多负面记录 (red_flags <= 1)
                if self.affection >= 75 and len(self.red_flags) <= 1:
                    success_confession = True
                    if self.affection >= 90: # 极高好感度下的告白 -> 特别好的结局
                        ending_type_confession = "good_ending" # 或更具体的如 "perfect_ending"
                        affection_change_confession = 15 # 成功后大幅提升亲密度
                        message_confession = self.config.get("confession_messages", {}).get("perfect_success", 
                                                      "苏糖的脸颊泛起红晕，眼中闪烁着难以置信的幸福光芒... '我...我也是！从很久以前开始！'")
                    else: # 较高好感度下的告白 -> 普通成功结局
                        ending_type_confession = "normal_ending" # 或更具体的如 "good_success"
                        affection_change_confession = 10
                        message_confession = self.config.get("confession_messages", {}).get("good_success", 
                                                      "苏糖害羞地低下了头，嘴角却忍不住上扬，'嗯... 我愿意...'")
                else:
                    # --- 告白失败的逻辑 ---
                    success_confession = False
                    if self.affection < 40: # 亲密度过低时告白 -> 直接坏结局
                        ending_type_confession = "bad_ending"
                        affection_change_confession = -self.affection # 好感度直接清零
                        message_confession = self.config.get("confession_messages", {}).get("critical_failure", 
                                                      "苏糖看起来非常困扰和尴尬，'对不起...我一直只把你当普通同学...我们以后还是别这样了。'")
                    elif self.affection < 60: # 亲密度不足时告白 -> 较大惩罚，游戏继续
                        affection_change_confession = -15 
                        message_confession = self.config.get("confession_messages", {}).get("normal_failure", 
                                                      "苏糖愣了一下，有些为难地说：'这太突然了... 我想我还需要一些时间考虑...对不起。'")
                    else: # 亲密度尚可但未达标时告白 -> 一般惩罚，游戏继续
                        affection_change_confession = -8
                        message_confession = self.config.get("confession_messages", {}).get("slight_failure", 
                                                      "苏糖的表情有些复杂，'谢谢你...但我现在可能还没准备好...我们能先从朋友开始吗？'")
                
                self.affection = max(0, min(100, self.affection + affection_change_confession))
                self.update_value(self.affection) # 同步好感度
                return {
                    "success": success_confession, 
                    "message": message_confession, 
                    "ending": ending_type_confession,
                    "old_affection": old_affection_before_event,
                    "new_affection": self.affection
                }
            else:
                # AI (角色) 主动告白 - 这种情况在此代码中似乎未被充分实现或触发
                # 简单返回一个成功状态，实际应用中需要更复杂的逻辑
                # 例如，AI告白通常只应在极高好感度且满足特定剧情条件下发生
                self.affection = min(100, self.affection + 10) # 象征性增加好感度
                self.update_value(self.affection)
                return {
                    "success": True, 
                    "message": self.config.get("confession_messages", {}).get("ai_confession", 
                                                   "(苏糖主动向你表白了！这是一个非常特殊的时刻！)"), 
                    "ending": "special_ai_ending", # 特殊的AI告白结局
                    "old_affection": old_affection_before_event,
                    "new_affection": self.affection
                }
                
        elif event == AffectionEvent.SHARED_INTEREST:
            # 发现共同兴趣事件，给予固定奖励
            boost = self.config.get("event_effects", {}).get(str(AffectionEvent.SHARED_INTEREST.value), 5) # 从配置或默认值获取
            self.affection = min(100, self.affection + boost)
            delta = self.affection - old_affection_before_event
            self.update_value(self.affection)
            return {"delta": delta, "old_value": old_affection_before_event, "new_value": self.affection, "message": "和苏糖聊到了共同的爱好，感觉更亲近了！"}
            
        else:
            # 其他类型事件的通用处理逻辑，效果值来自配置文件
            self.affection = max(0, min(100, self.affection + effect))
            delta = self.affection - old_affection_before_event
            self.update_value(self.affection)
            # 对于其他事件，message可以由调用方根据event类型来生成
            return {"delta": delta, "old_value": old_affection_before_event, "new_value": self.affection, "message": ""}

    def check_ending(self):
        """
        根据当前的亲密度值检查是否应触发某种游戏结局。

        Returns:
            str or None: 
                - 如果亲密度小于等于0，返回 "bad_ending" (坏结局)。
                - 如果亲密度大于等于100，返回 "good_ending" (好结局)。
                - 否则，返回 None (无结局触发)。
        """
        if self.affection <= 0:
            return "bad_ending"
        elif self.affection >= 100:
            return "good_ending"
        else:
            return None

    def _get_current_phase(self):
        """
        内部辅助方法，根据当前的亲密度值获取对应的关系阶段描述。

        这些阶段可以用于游戏逻辑判断、对话内容调整或剧情触发等。
        注意：此方法返回的是阶段的字符串描述，可能与 `Phase` 枚举类型对应。

        Returns:
            str: 表示当前关系阶段的字符串，例如:
                 - "stranger" (陌生人): 亲密度 < 30
                 - "acquaintance" (相识): 30 <= 亲密度 < 50
                 - "friend" (朋友): 50 <= 亲密度 < 75
                 - "close_friend" (密友): 75 <= 亲密度 < 90
                 - "romantic" (恋人/暧昧): 亲密度 >= 90
        """
        if self.affection < 30:
            return "stranger"
        elif self.affection < 50:
            return "acquaintance"
        elif self.affection < 75:
            return "friend"
        elif self.affection < 90:
            return "close_friend"
        else:
            return "romantic" 