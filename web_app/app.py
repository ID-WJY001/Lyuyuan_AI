"""
绿园中学物语：追女生模拟
Web版本后端 - [终极调试版]
"""

from flask import Flask, render_template, request, jsonify, session
import os
import sys
import traceback # [新] 导入traceback模块

# 设置项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

# 确保工作目录正确
os.chdir(ROOT_DIR)

# 导入工具函数
# 假设你的utils目录在根目录
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
    game_manager = GameManager() # [改] 变量名改为更通用的 game_manager
except Exception as e:
    print(f"导入GameManager模块失败: {e}")
    raise

@app.route('/')
def index():
    """渲染主页"""
    if 'initialized' not in session:
        session['initialized'] = True
        session['game_started'] = False
    return render_template('index.html')

@app.route('/api/start_game', methods=['POST'])
def start_game():
    """开始游戏"""
    session['game_started'] = True
    
    # [改] 使用新的 game_manager 变量
    if hasattr(game_manager, 'reset_game'):
        game_manager.reset_game()
    else:
        # 你的备用逻辑保持不变
        game_manager.game_state["closeness"] = 30
        if hasattr(game_manager, 'agent') and hasattr(game_manager.agent, 'game_state'):
            game_manager.agent.game_state["closeness"] = 30
            game_manager.agent.game_state["relationship_state"] = "初始阶段"
        if hasattr(game_manager, 'sync_affection_values'):
            game_manager.sync_affection_values()
    
    intro_text = """...（你的游戏介绍文本，此处省略）..."""
    
    # [改] 确保从正确的地方获取 game_state
    current_state = {}
    if hasattr(game_manager, 'game_state'):
        current_state = game_manager.game_state
    elif hasattr(game_manager, 'agent'):
        current_state = game_manager.agent.game_state

    return jsonify({
        'intro_text': intro_text,
        'game_state': current_state
    })

# ====================================================================
# [!!! 核心修改区域 !!!]
# 用下面这个全新的、带有详细调试日志的chat函数，替换你原来的版本
# ====================================================================
@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求 - [终极调试版]"""
    print("\n" + "*"*20 + " WEB APP /api/chat RECEIVED " + "*"*20)
    try:
        # 1. 获取请求数据
        if not request.json:
            print("[WEB_APP_ERROR] Request has no JSON body.")
            return jsonify({'error': '无效的请求数据'}), 400
            
        user_input = request.json.get('message', '')
        print(f"[WEB_APP] Received user_input: '{user_input}'")
        
        if not user_input or not isinstance(user_input, str):
            print(f"[WEB_APP_ERROR] Invalid user_input: type={type(user_input)}, value='{user_input}'")
            return jsonify({'error': '无效的消息内容'}), 400
        
        # 2. 调用游戏核心逻辑
        print("[WEB_APP] Calling game_manager.chat()...")
        response_text = game_manager.chat(user_input)
        print(f"[WEB_APP] game_manager.chat() returned.")
        
        # 3. [关键调试点] 在 jsonify 之前，彻底检查 response_text
        print(f"[WEB_APP] Type of response_text: {type(response_text)}")
        print(f"[WEB_APP] repr(response_text): {repr(response_text)}") # repr() 会显示所有特殊字符

        # 4. 获取更新后的游戏状态
        current_state = {}
        if hasattr(game_manager, 'game_state'):
            current_state = game_manager.game_state
        elif hasattr(game_manager, 'agent') and hasattr(game_manager.agent, 'game_state'):
            current_state = game_manager.agent.game_state
        print(f"[WEB_APP] Fetched current_state: {current_state}")

        # 5. 准备返回给前端的最终数据
        # [改] 强制将 response_text 转为字符串，增加健壮性
        response_data = {
            'response': str(response_text),
            'game_state': current_state
        }
        print(f"[WEB_APP] Preparing to jsonify: {response_data}")

        # 6. 返回JSON响应
        json_response = jsonify(response_data)
        print("[WEB_APP] jsonify() successful. Returning response to client.")
        return json_response

    except Exception as e:
        # [改] 打印最详细的错误堆栈信息
        error_traceback = traceback.format_exc()
        print("!!!!!! AN EXCEPTION OCCURRED IN CHAT API !!!!!!")
        print(error_traceback)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        
        # 返回一个更明确的错误信息给前端
        return jsonify({
            'error': '服务器内部发生未知错误',
            'details': str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0")