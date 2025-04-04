"""
绿园中学物语：追女生模拟
主入口文件
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
    print("\n命令提示: /exit退出, /save保存, /load读取, /debug调试模式, /status查看社交状态, /help查看帮助")

def handle_command(command, game):
    """处理用户命令"""
    if command == "/exit":
        print("游戏已退出")
        return True
    elif command == "/save":
        # 同步其他游戏状态到agent
        game.agent.game_state["scene"] = game.scene_manager.current_scene
        game.agent.game_state["date"] = datetime.now().strftime("%Y年%m月%d日")
        game.agent.game_state["time_period"] = game.current_time
        
        game.agent.save(1)
        print("手动存档成功！")
    elif command == "/load":
        # 先尝试加载存档
        if game.agent.load(1):
            # 获取加载的数据
            loaded_state = game.agent.game_state
            
            # 更新好感度
            if "closeness" in loaded_state:
                game.affection_manager.update_value(loaded_state["closeness"], source="load")
            
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
        result = game.toggle_debug_mode()
        print(result)
    elif command == "/status":
        status = game.show_social_status()
        print(status)
    elif command == "/time":
        print(f"当前时间：{game.current_date.strftime('%Y年%m月%d日')} {game.current_time}")
    elif command == "/help":
        print("命令列表：")
        print("/exit - 退出游戏")
        print("/save - 保存游戏")
        print("/load - 加载存档")
        print("/debug - 切换调试模式")
        print("/status - 查看当前社交状态")
        print("/time - 查看当前时间")
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
                        game.agent.game_state["time_period"] = game.current_time
                        game.agent.save(0)  # 自动保存到槽位0
                    
                    # 显示状态
                    if not game.debug_mode:
                        print(f"\n[当前时间：{game.current_date.strftime('%Y年%m月%d日')} {game.current_time}]")
                        affection = int(game.affection_manager.get_value())
                        print(f"\n[当前亲密度：{affection}]")
                except Exception as e:
                    # 优雅处理对话过程中的错误
                    logger.error(f"对话处理错误: {str(e)}", exc_info=True)
                    print(f"\n游戏处理错误: {str(e)}")
                    print("\n苏糖：（似乎遇到了一些问题，但她很快调整好情绪）抱歉，我刚才走神了。你刚才说什么？")
                    
                    # 显示状态
                    print(f"\n[当前时间：{game.current_date.strftime('%Y年%m月%d日')} {game.current_time}]")
                    affection = int(game.affection_manager.get_value())
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

def setup_environment():
    """设置环境变量和API密钥"""
    try:
        # 加载环境变量
        from utils.common import load_env_file
        load_env_file()
        logger.info("环境变量加载成功")
    except Exception as e:
        logger.warning(f"环境变量加载错误: {str(e)}")
        print(f"环境变量加载错误: {str(e)}")
        print("游戏将继续，但可能需要手动设置环境变量。")

def ensure_save_directory():
    """确保存档目录存在"""
    try:
        os.makedirs("saves", exist_ok=True)
        logger.info("存档目录准备完成")
    except Exception as e:
        logger.warning(f"创建存档目录失败: {str(e)}")
        print(f"创建存档目录失败: {str(e)}")
        print("游戏将继续，但可能无法保存游戏进度。")

def main():
    """游戏主函数"""
    try:
        # 设置环境变量
        setup_environment()
        
        # 确保存档目录
        ensure_save_directory()
        
        # 初始化游戏管理器
        logger.info("初始化游戏...")
        game = GameManager()
        
        # 显示游戏介绍
        print_game_introduction()
        
        # 显示初始状态
        print(f"\n[当前时间：{game.current_date.strftime('%Y年%m月%d日')} {game.current_time}]")
        affection = int(game.affection_manager.get_value())
        print(f"\n[当前亲密度：{affection}]")
        print("\n请输入你的开场白：")
        
        # 进入游戏主循环
        game_loop(game)
        
        print("感谢游玩！")
    except Exception as e:
        logger.critical(f"游戏启动失败: {str(e)}", exc_info=True)
        print(f"游戏启动失败: {str(e)}")
        print("请检查日志获取更多信息。")

if __name__ == "__main__":
    main() 