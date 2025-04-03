"""
对话处理系统模块
负责处理玩家输入、生成回复和计算亲密度变化
"""

import random
import re
from core.affection import AffectionEvent, SocialRisk

class DialogueSystem:
    def __init__(self, game_manager):
        """
        初始化对话系统
        
        Args:
            game_manager: 游戏管理器实例
        """
        self.game_manager = game_manager
        
    def process_dialogue(self, user_input, dialogue_history):
        """
        处理玩家输入并更新游戏状态
        
        Args:
            user_input: 玩家输入的文本
            dialogue_history: 对话历史
            
        Returns:
            AI角色的回复文本
        """
        # 空输入检查
        if not user_input or user_input.isspace():
            return "...(苏糖看起来在发呆)"
            
        # 获取AI回复
        reply = self.game_manager.agent.chat(user_input)
        
        # 在获取回复前，确保所有系统的亲密度值是一致的
        self.game_manager.affection_manager.force_sync()
        
        # 更新亲密度
        result = self.game_manager.affection.process_dialogue(user_input, self.game_manager.agent.dialogue_history)
        current_affection = result['current_affection']
        delta = result['delta']
        previous_affection = result['previous_affection']
        
        # 使用亲密度管理器更新所有系统中的亲密度值
        update_result = self.game_manager.affection_manager.update_value(current_affection, source="dialogue_process")
        
        # 更新游戏状态中的好感度相关数据（这些只是记录，实际值已通过管理器同步）
        self.game_manager.game_state["last_affection"] = previous_affection
        
        # 更新连续对话计数
        if delta > 0:
            self.game_manager.game_state["consecutive_positive"] += 1
            self.game_manager.game_state["consecutive_negative"] = 0
        elif delta < 0:
            self.game_manager.game_state["consecutive_negative"] += 1
            self.game_manager.game_state["consecutive_positive"] = 0
            
        # 检查亲密度是否低于0，游戏结束
        final_affection = self.game_manager.affection_manager.get_value()
        if final_affection <= 0:
            # 好感度已降至0，游戏结束
            self.game_manager.show_ending("好感度为负，关系破裂")
            return "😠 苏糖看起来非常生气，转身离开了...\n\n【游戏结束：好感度跌至谷底】"
        
        # 检查是否包含侮辱性言论
        if self._check_for_severe_insults(user_input):
            # 严重侮辱，好感度直接归零
            self.game_manager.affection_manager.update_value(0, source="severe_insult")
            self.game_manager.show_ending("严重侮辱导致关系破裂")
            return "😡 苏糖脸色瞬间变得煞白，眼中的光彩消失了...\n'我没想到你会这样对我说话...'她转身快步离开，再也没有回头。\n\n【游戏结束：严重侮辱导致关系瞬间破裂】"
            
        # 生成亲密度变化信息
        affection_info = self._generate_affection_info(delta, previous_affection, final_affection, result)
        
        # 如果有亲密度变化信息，添加到回复中
        if affection_info:
            reply += affection_info

        # 检查是否触发剧情
        triggered = self.game_manager.check_storyline_triggers(final_affection)
        if triggered:
            reply = f"{reply}\n\n{triggered}"
            
        # 分析对话并检查是否需要场景切换
        scene_change = self.game_manager.scene_manager.analyze_conversation(
            user_input, reply, self.game_manager.current_scene, 
            self.game_manager.current_date, self.game_manager.current_time
        )
        
        if scene_change and scene_change["should_change"]:
            # 更新场景和时间
            old_scene = self.game_manager.current_scene
            self.game_manager.current_scene = scene_change["new_scene"]
            
            # 处理时间推进，根据场景转换生成描述文本
            scene_transition = self.game_manager._generate_scene_transition(scene_change)
            
            if scene_transition:
                reply = f"{reply}\n\n{scene_transition}"
        
        # 游戏进度增加，对话次数+1
        self.game_manager.game_state["conversation_count"] += 1
        
        # 检查是否有新的成就解锁
        unlocked_achievements = self.game_manager.achievement_system.check_achievements(self.game_manager)
        for achievement in unlocked_achievements:
            # 处理成就奖励
            if achievement.reward:
                if "好感度+" in achievement.reward:
                    try:
                        bonus = int(achievement.reward.split("+")[1])
                        # 使用亲密度管理器增加好感度值
                        current = self.game_manager.affection_manager.get_value()
                        self.game_manager.affection_manager.update_value(current + bonus, source="achievement")
                    except (ValueError, IndexError):
                        pass
            
            # 添加成就通知
            notification = self.game_manager.achievement_system.get_achievement_notification(achievement)
            reply = f"{reply}\n\n{notification}"
        
        # 记录对话历史到数据库
        self.game_manager.agent.storage.log_dialogue(
            save_slot="auto",  # 自动保存槽
            player_input=user_input,
            character_response=reply,
            affection_change=delta,
            current_affection=self.game_manager.affection_manager.get_value(),
            scene=self.game_manager.current_scene
        )
        
        # 随机添加温馨提示
        if random.random() < 0.2:  # 20%概率
            tip = self._get_random_tip()
            reply = f"{reply}\n\n{tip}"
                
        # 确保在对话结束前，所有系统的亲密度是一致的
        self.game_manager.affection_manager.verify_consistency()
        
        # 自动保存功能
        if random.random() < 0.2:  # 20%概率自动保存
            # 确保所有状态都已同步
            self.game_manager.agent.game_state["date"] = self.game_manager.current_date
            self.game_manager.agent.game_state["time_period"] = self.game_manager.current_time
            self.game_manager.agent.game_state["scene"] = self.game_manager.current_scene
            self.game_manager.agent.save(0)  # 自动保存到槽位0
        
        return reply
        
    def _generate_affection_info(self, delta, previous_affection, final_affection, result):
        """
        生成亲密度变化信息
        
        Args:
            delta: 亲密度变化值
            previous_affection: 之前的亲密度
            final_affection: 当前亲密度
            result: 亲密度处理结果
            
        Returns:
            亲密度变化信息文本
        """
        affection_info = ""
        
        # 大幅度变化（断崖式下跌）时显示特殊效果
        if delta <= -10:
            affection_info += f"\n💔 亲密度急剧下降! [{int(previous_affection)} → {int(final_affection)}]"
        elif delta <= -5:
            affection_info += f"\n💔 亲密度显著下降 [{int(previous_affection)} → {int(final_affection)}]"
        elif delta >= 5:
            affection_info += f"\n💖 亲密度显著提升! [{int(previous_affection)} → {int(final_affection)}]"
        elif delta > 0:
            affection_info += f"\n💫 亲密度微微提升 [{int(previous_affection)} → {int(final_affection)}]"
        elif delta < 0:
            affection_info += f"\n⚠️ 亲密度略有下降 [{int(previous_affection)} → {int(final_affection)}]"
            
        # 在调试模式下显示更多信息
        if self.game_manager.debug_mode:
            debug = result.get('debug_info', {})
            affection_info += f"\n[调试信息]\n"
            affection_info += f"亲密度变化: {delta:+.1f} → 当前: {int(final_affection)}\n"
            
            # 显示亲密度管理器的一致性检查结果
            consistency = self.game_manager.affection_manager.verify_consistency()
            if consistency["consistent"]:
                affection_info += f"亲密度同步状态: ✓ 一致\n"
            else:
                affection_info += f"亲密度同步状态: ✗ 不一致 {consistency['system_values']}\n"
            
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
                    
        return affection_info
    
    def _get_random_tip(self):
        """获取一个随机追女生技巧提示"""
        # 避免连续显示同一个提示
        available_indices = [i for i in range(len(self.game_manager.dating_tips)) 
                             if i != self.game_manager.last_tip_index]
        tip_index = random.choice(available_indices)
        self.game_manager.last_tip_index = tip_index
        return self.game_manager.dating_tips[tip_index]
    
    def _check_for_severe_insults(self, text):
        """
        检查是否包含严重侮辱性言论
        
        Args:
            text: 要检查的文本
        
        Returns:
            bool: 是否包含侮辱性言论
        """
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