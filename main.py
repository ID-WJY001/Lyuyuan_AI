import yaml
from Su_Tang import GalGameAgent
import os
import random
from core.affection_system import AffectionSystem, AffectionEvent, SocialRisk
from core.nlp_engine import NaturalLanguageProcessor

def load_config(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class GameManager:
    def __init__(self):
        # 加载配置和初始化必要的组件
        char_config = load_config("config/character.yaml")
        nlp_processor = NaturalLanguageProcessor("data/keyword_groups.json")
        self.affection = AffectionSystem(nlp_processor)
        self.agent = GalGameAgent()
        self.storyline_triggers = {
            30: "初始阶段",
            45: "渐渐熟悉",
            60: "成为朋友",
            75: "关系深入",
            90: "亲密关系",
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
            "温馨提示: 不当言论会严重损害关系，请保持绅士风度"
        ]
        self.last_tip_index = -1
        
    def process_dialogue(self, user_input):
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
        self.agent.game_state['closeness'] = int(current_affection)  # 转为整数
        
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
    
    def check_storyline_triggers(self, affection):
        """检查是否触发剧情推进"""
        message = None
        for threshold, storyline in self.storyline_triggers.items():
            if affection >= threshold and threshold not in self.triggered_storylines:
                self.triggered_storylines.add(threshold)
                message = f"【剧情推进：{storyline}】"
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
            self.affection.handle_event(AffectionEvent.SHARED_INTEREST)
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
        exit()
        
    def toggle_debug_mode(self):
        """切换调试模式"""
        self.debug_mode = not self.debug_mode
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

def main():
    # 设置API密钥（临时方案，正式项目应使用更安全的方式）
    os.environ["DEEPSEEK_API_KEY"] = "sk-5e582133cbeb47e5b21d807f7242d03e"
    
    # 导入模块
    import random
    
    game = GameManager()
    print("===== 绿园中学物语：追女生模拟 =====")
    print("📝 游戏难度增加！现在游戏将更真实地模拟现实中的社交互动：")
    print("  - 无聊、重复的对话会让苏糖失去兴趣")
    print("  - 不礼貌或不当言论会严重损害关系")
    print("  - 过早表白会适得其反")
    print("  - 保持绅士风度，但也要让对话有趣")
    print("\n苏糖：", game.agent.dialogue_history[-1]['content'])
    print(f"\n[当前亲密度：{game.agent.game_state['closeness']}]")
    print("\n命令提示: /exit退出, /save保存, /load读取, /debug调试模式, /status查看社交状态")
    
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
            reply = game.process_dialogue(user_input)
            print("\n苏糖：", reply)
            
            # 显示状态（移至process_dialogue返回值的一部分）
            if not game.debug_mode:
                print(f"\n[当前亲密度：{game.agent.game_state['closeness']}]")
            
        except KeyboardInterrupt:
            print("\n游戏已强制退出")
            break
        except Exception as e:
            print(f"发生错误：{str(e)}")
            break

if __name__ == "__main__":
    main()