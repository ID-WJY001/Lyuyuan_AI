"""
绿园中学物语：追女生模拟
Web版本后端
"""

from flask import Flask, render_template, request, jsonify, session
import os
import json
import sys
from openai import OpenAI

# 设置项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

# 确保工作目录正确
os.chdir(ROOT_DIR)

# 导入工具函数
from utils.common import load_env_file, ensure_directories

# 读取.env文件中的环境变量
load_env_file()

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'green_garden_high_school_romance'  # 用于session

# 导入游戏核心逻辑
try:
    from game.managers import GameManager
    print("成功导入GameManager模块")
    # 创建全局游戏代理
    game_agent = GameManager()
except Exception as e:
    print(f"导入GameManager模块失败: {e}")
    raise  # 抛出异常，不再使用简化版游戏代理

@app.route('/')
def index():
    """渲染主页"""
    # 初始化session
    if 'initialized' not in session:
        session['initialized'] = True
        session['game_started'] = False
    return render_template('index.html')

@app.route('/api/start_game', methods=['POST'])
def start_game():
    """开始游戏"""
    session['game_started'] = True
    
    # 完全重置游戏状态
    if hasattr(game_agent, 'reset_game'):
        game_agent.reset_game()
    else:
        # 备用方案：手动设置好感度
        game_agent.game_state["closeness"] = 30
        
        # 如果角色智能体中也有游戏状态，确保其好感度也为30
        if hasattr(game_agent, 'agent') and hasattr(game_agent.agent, 'game_state'):
            game_agent.agent.game_state["closeness"] = 30
            # 同时更新关系状态为初始阶段
            game_agent.agent.game_state["relationship_state"] = "初始阶段"
        
        # 同步好感度到所有系统
        game_agent.sync_affection_values()
    
    # 返回游戏初始状态
    intro_text = """===== 绿园中学物语：追女生模拟 =====

📝 游戏背景介绍：
你是陈辰，2021级高一一班的学生。在学校举办的百团大战（社团招新）活动中，
你在烘焙社的摊位前看到了一个让你一见钟情的女生——她正在认真地为过往的学生介绍烘焙社。
她身穿整洁的校服，戴着烘焙社的围裙，笑容甜美，举止优雅。
你鼓起勇气，决定上前搭讪，希望能够认识她并加入烘焙社...

游戏规则：
  - 无聊、重复的对话会让女生失去兴趣
  - 不礼貌或不当言论会严重损害关系
  - 过早表白会适得其反
  - 保持礼貌，让对话有趣且有深度
  - 好感度降至0以下游戏结束
  - 好感度达到100时会有特殊剧情

（苏糖正在整理烘焙社的宣传材料）
苏糖：有什么我可以帮你的吗？
"""
    
    return jsonify({
        'intro_text': intro_text,
        'game_state': game_agent.game_state
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        # 获取用户输入
        if not request.json:
            return jsonify({
                'error': '无效的请求数据',
                'message': '请求必须包含JSON数据'
            }), 400
            
        user_input = request.json.get('message', '')
        
        if not user_input or not isinstance(user_input, str):
            return jsonify({
                'error': '无效的消息内容',
                'message': '消息内容必须是非空字符串'
            }), 400
        
        # 使用游戏代理处理消息
        try:
            response = game_agent.chat(user_input)
            
            # 确保返回的是字符串
            if not isinstance(response, str):
                response = str(response)
                
            return jsonify({
                'response': response,
                'game_state': game_agent.game_state
            })
        except AttributeError as e:
            # 处理游戏代理方法调用错误
            app.logger.error(f"聊天方法调用错误: {str(e)}")
            return jsonify({
                'error': '游戏代理错误',
                'message': '聊天系统处理失败，可能需要重新启动游戏',
                'details': str(e)
            }), 500
            
    except Exception as e:
        # 处理所有其他类型的错误
        app.logger.error(f"处理聊天请求时发生错误: {str(e)}")
        return jsonify({
            'error': '服务器错误',
            'message': '处理消息时发生错误，请重试',
            'details': str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0") 