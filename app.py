# app.py

from flask import Flask, render_template, request, jsonify, session
import os
import sys

# 设置路径以便导入根目录模块
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from backend.services.game_service import game_service

if not os.environ.get("DEEPSEEK_API_KEY"):
    from dotenv import load_dotenv
    print("Loading .env file...")
    load_dotenv()
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("FATAL ERROR: DEEPSEEK_API_KEY not found in .env or environment variables.")


app = Flask(
    __name__,
    static_folder='frontend/static',
    template_folder='frontend/templates',
    static_url_path='/static'
)
app.secret_key = 'a_very_secret_key_for_sutang_reborn'


def _filter_history_for_client(history):
    try:
        return [
            {"role": msg.get("role"), "content": msg.get("content", "")}
            for msg in (history or [])
            if msg.get("role") in ("user", "assistant")
        ]
    except Exception:
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start_game', methods=['POST'])
def start_game():
    """开始新游戏，完全由SimpleGameCore驱动"""
    print("[API] Request to /api/start_game")
    payload = request.get_json(silent=True) or {}
    role = (payload.get('role') or 'su_tang').strip().lower()
    # 暂存所选角色到会话，便于后续 /api/chat 返回给前端
    session['character_key'] = role

    initial_data = game_service.start_game(role)
    # 为前端提供角色键，默认 'su_tang'
    initial_data['character_key'] = role
    # 不向前端暴露 system 提示词；如果历史里只有 system，则让前端显示 intro_text
    if 'history' in initial_data:
        initial_data['history'] = _filter_history_for_client(initial_data.get('history'))
    return jsonify(initial_data)

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求，完全由SimpleGameCore驱动"""
    print("[API] Request to /api/chat")
    try:
        user_input = request.json.get('message', '')
        if not user_input:
            return jsonify({'error': 'Message is empty'}), 400

        # 直接调用 SimpleGameCore 的方法
        response_text = game_service.chat(user_input)
        current_state = game_service.get_state()

        return jsonify({
            'response': str(response_text), # 强制转字符串，更安全
            'game_state': current_state,
            'character_key': session.get('character_key', 'su_tang')
        })
    except Exception as e:
        import traceback
        print(f"!!! UNEXPECTED ERROR IN CHAT API !!!\n{traceback.format_exc()}")
        return jsonify({'error': '服务器发生未知错误', 'details': str(e)}), 500

@app.route('/api/save', methods=['POST'])
def save_game_api():
    print("[API] Request to /api/save")
    slot = request.json.get('slot', 1)
    success = game_service.save(slot)
    return jsonify({'success': success})

@app.route('/api/load', methods=['POST'])
def load_game_api():
    print("[API] Request to /api/load")
    slot = request.json.get('slot', 1)
    success = game_service.load(slot)
    if success:
        raw_history = getattr(getattr(game_service, '_core', None), 'agent', None)
        raw_history = raw_history.dialogue_history if raw_history else []
        return jsonify({
            'success': True,
            'game_state': game_service.get_state(),
            'history': _filter_history_for_client(raw_history),
            'character_key': session.get('character_key', 'su_tang')
        })
    return jsonify({'success': False})

# web_start.py 调用
if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0")