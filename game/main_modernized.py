"""
绿园中学物语：追女生模拟
现代化入口文件 - 使用模块化管理器
"""

import os
import random
import logging
import json
from datetime import datetime
from game.managers import GameManager

# 设置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Main")

def print_game_introduction():
    """打印游戏介绍"""
    print("===== 绿园中学物语：追女生模拟 =====")
    print("📝 游戏背景介绍：")
    print("你是陈辰，2021级高一一班的学生。在学校举办的百团大战（社团招新）活动中，")
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
    print("\n命令提示: /exit退出, /save保存, /load读取, /debug调试模式, /status查看社交状态")

def handle_command(command, game):
    """处理用户命令"""
    if command == "/exit":
        print("游戏已退出")
        return True
    elif command == "/save":
        # 同步其他游戏状态到agent
        game.agent.game_state["scene"] = game.scene_manager.current_scene
        game.agent.game_state["date"] = datetime.now().strftime("%Y年%m月%d日")
        game.agent.game_state["time_period"] = "上午"
        
        game.agent.save(1)
        print("手动存档成功！")
    elif command == "/load":
        # 先尝试加载存档
        if game.agent.load(1):
            # 获取加载的数据
            loaded_state = game.agent.game_state
            
            # 更新好感度
            if "closeness" in loaded_state:
                game.affection.update_value(loaded_state["closeness"])
            
            # 更新游戏状态
            if "scene" in loaded_state:
                game.scene_manager.current_scene = loaded_state["scene"]
                
            print("读取存档成功！")
            
            # 显示当前状态
            affection = int(game.game_state["closeness"])
            print(f"\n[当前亲密度：{affection}]")
        else:
            print("没有找到存档或存档损坏！")
    elif command == "/debug":
        result = game.storyline_manager.toggle_debug_mode()
        print(result)
    elif command == "/status":
        status = game.show_social_status()
        print(status)
    elif command == "/help":
        print("命令列表：")
        print("/exit - 退出游戏")
        print("/save - 保存游戏")
        print("/load - 加载存档")
        print("/debug - 切换调试模式")
        print("/status - 查看当前社交状态")
        print("/help - 显示帮助信息")
    else:
        print(f"未知命令: {command}，输入 /help 查看可用命令")
    
    return False

def game_loop(game):
    """游戏主循环"""
    try:
        while True:
            try:
                user_input = input("\n你：").strip()
                
                # 处理系统命令
                if user_input.startswith("/"):
                    should_exit = handle_command(user_input, game)
                    if should_exit:
                        break
                    continue
                
                # 处理对话
                try:
                    reply = game.process_dialogue(user_input, game.agent.dialogue_history)
                    print("\n苏糖：", reply)
                    
                    # 自动保存功能
                    if random.random() < 0.2:  # 20%概率自动保存
                        game.agent.game_state["scene"] = game.scene_manager.current_scene
                        game.agent.game_state["date"] = datetime.now().strftime("%Y年%m月%d日")
                        game.agent.game_state["time_period"] = "上午"
                        game.agent.save(0)  # 自动保存到槽位0
                    
                    # 显示状态
                    if not game.storyline_manager.is_debug_mode():
                        affection = int(game.game_state["closeness"])
                        print(f"\n[当前亲密度：{affection}]")
                except Exception as e:
                    # 优雅处理对话过程中的错误
                    logger.error(f"对话处理错误: {str(e)}", exc_info=True)
                    print(f"\n游戏处理错误: {str(e)}")
                    print("\n苏糖：（似乎遇到了一些问题，但她很快调整好情绪）抱歉，我刚才走神了。你刚才说什么？")
                    
                    # 显示状态
                    affection = int(game.game_state["closeness"])
                    print(f"\n[当前亲密度：{affection}]")
                
            except KeyboardInterrupt:
                print("\n游戏已强制退出")
                break
            except Exception as e:
                logger.error(f"未捕获的异常: {str(e)}", exc_info=True)
                print(f"发生错误：{str(e)}")
                print("游戏将尝试继续...")
                continue
    except Exception as e:
        logger.critical(f"游戏主循环崩溃: {str(e)}", exc_info=True)
        print(f"游戏发生严重错误，请查看日志: {str(e)}")

def setup_api_key():
    """设置API密钥"""
    try:
        # 在实际应用中，应该从环境变量或配置文件中加载API密钥
        api_key = "YOUR_API_KEY_HERE"  # 替换为实际的API密钥
        os.environ["DEEPSEEK_API_KEY"] = api_key
        logger.info("API密钥设置成功")
    except Exception as e:
        logger.warning(f"API密钥设置错误: {str(e)}")
        print(f"API密钥设置错误: {str(e)}")
        print("游戏将继续，但可能无法获取在线响应。")

def sync_state_to_agent(game):
    """同步游戏状态到代理"""
    # 更新状态
    game.agent.game_state["closeness"] = game.game_state["closeness"]
    game.agent.game_state["scene"] = game.scene_manager.current_scene
    game.agent.game_state["relationship_state"] = game.character_states["su_tang"]["relationship_stage"]
    game.agent.game_state["date"] = datetime.now().strftime("%Y年%m月%d日")
    game.agent.game_state["time_period"] = "上午"

def load_game(game, slot=1):
    """加载游戏存档"""
    save_path = f"saves/save_{slot}.json"
    if not os.path.exists(save_path):
        print("存档不存在！")
        return False
    
    try:
        with open(save_path, "r", encoding="utf-8") as f:
            save_data = json.load(f)
        
        # 加载基本状态
        loaded_state = save_data.get("game_state", {})
        
        # 加载日期和时间（保持简单设置）
        game.agent.game_state["date"] = datetime.now().strftime("%Y年%m月%d日")
        game.agent.game_state["time_period"] = "上午"
        
        # 加载对话历史
        game.agent.dialogue_history = save_data.get("dialogue_history", [])
        
        # 加载好感度
        game.game_state["closeness"] = loaded_state.get("closeness", 30)
        
        # 同步状态
        sync_state_to_agent(game)
        
        print("游戏加载成功！")
        return True
    except Exception as e:
        print(f"加载存档失败: {e}")
        return False

def show_game_status(game):
    """显示游戏状态"""
    closeness = game.game_state["closeness"]
    print("\n" + "="*50)
    print(f"当前状态：好感度 {int(closeness)} | 场景: {game.scene_manager.current_scene}")
    print(f"当前日期：{game.agent.game_state.get('date', '未知')} {game.agent.game_state.get('time_period', '未知')}")
    relationship = game.character_states["su_tang"]["relationship_stage"]
    print(f"当前关系：{relationship}")
    print("="*50)

def advance_scene(game):
    """推进场景"""
    print("\n---场景切换---")
    scenes = game.scene_manager.available_scenes
    for i, scene in enumerate(scenes, 1):
        print(f"{i}. {scene}")
    
    while True:
        choice = input("\n请选择要去的场景（输入数字）: ")
        try:
            index = int(choice) - 1
            if 0 <= index < len(scenes):
                scene = scenes[index]
                game.scene_manager.change_scene(scene)
                
                # 更新场景
                print(f"\n[场景已切换到：{scene}]")
                
                # 同步状态
                game.agent.game_state["scene"] = scene
                
                return
            else:
                print("无效的选择，请重试")
        except ValueError:
            print("请输入有效的数字")

def main():
    """游戏主函数"""
    try:
        # 打印游戏介绍
        print_game_introduction()
        
        # 设置API密钥
        setup_api_key()
        
        # 初始化游戏对象
        game = GameManager()
        
        # 显示初始对话
        print("\n（苏糖正在整理烘焙社的宣传材料）")
        print("苏糖：有什么我可以帮你的吗？")
        
        # 进入游戏主循环
        game_loop(game)
        
    except Exception as e:
        logger.critical(f"游戏初始化错误: {str(e)}", exc_info=True)
        print(f"游戏无法启动: {str(e)}")
        input("按任意键退出...")

if __name__ == "__main__":
    main() 