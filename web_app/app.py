# web_app/app.py
# 最终的、简化的Web应用入口
# 这个版本只依赖我们新建的 game_core.py，与其他旧模块完全解耦。

from flask import Flask, render_template, request, jsonify, session
import os
import sys

# 设置路径以便导入根目录模块
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# [核心改动] 我们不再导入任何旧的管理器或工具函数
# 而是直接导入我们新建的、干净的 game_core
from web_app.game_core import game_core

# 你可以保留你原来的load_env_file逻辑，如果它在一个你没删除的文件里
# 否则，简单的os.environ.get就足够了
if not os.environ.get("DEEPSEEK_API_KEY"):
    from dotenv import load_dotenv
    print("Loading .env file...")
    load_dotenv()
    if not os.environ.get("DEEPSEEK_API_KEY"):
         print("FATAL ERROR: DEEPSEEK_API_KEY not found in .env or environment variables.")


app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'a_very_secret_key_for_sutang_reborn'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start_game', methods=['POST'])
def start_game():
    """开始新游戏，完全由SimpleGameCore驱动"""
    print("[WEB_APP] Request to /api/start_game")
    initial_data = game_core.start_new_game()
    return jsonify(initial_data)

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求，完全由SimpleGameCore驱动"""
    print("[WEB_APP] Request to /api/chat")
    try:
        user_input = request.json.get('message', '')
        if not user_input:
            return jsonify({'error': 'Message is empty'}), 400

        # 直接调用 SimpleGameCore 的方法
        response_text = game_core.chat(user_input)
        current_state = game_core.get_current_state()

        return jsonify({
            'response': str(response_text), # 强制转字符串，更安全
            'game_state': current_state
        })
    except Exception as e:
        import traceback
        print(f"!!! UNEXPECTED ERROR IN CHAT API !!!\n{traceback.format_exc()}")
        return jsonify({'error': '服务器发生未知错误', 'details': str(e)}), 500


# [新] 重新启用存档/读档API，并连接到SimpleGameCore
@app.route('/api/save', methods=['POST'])
def save_game_api():
    print("[WEB_APP] Request to /api/save")
    slot = request.json.get('slot', 1)
    success = game_core.save_game(slot)
    return jsonify({'success': success})

@app.route('/api/load', methods=['POST'])
def load_game_api():
    print("[WEB_APP] Request to /api/load")
    slot = request.json.get('slot', 1)
    success = game_core.load_game(slot)
    if success:
        return jsonify({
            'success': True,
            'game_state': game_core.get_current_state()
        })
    return jsonify({'success': False})

# web_start.py 应该调用这个
if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0")