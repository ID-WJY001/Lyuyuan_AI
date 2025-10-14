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
    # 为前端提供角色键与角色名称
    initial_data['character_key'] = role
    try:
        agent = getattr(getattr(game_service, '_core', None), 'agent', None)
        if agent and getattr(agent, 'name', None):
            initial_data['character_name'] = str(agent.name)
    except Exception:
        pass
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

        payload = {
            'response': str(response_text), # 强制转字符串，更安全
            'game_state': current_state,
            'character_key': session.get('character_key', 'su_tang')
        }
        try:
            agent = getattr(getattr(game_service, '_core', None), 'agent', None)
            if agent and getattr(agent, 'name', None):
                payload['character_name'] = str(agent.name)
        except Exception:
            pass
        return jsonify(payload)
    except Exception as e:
        import traceback
        print(f"!!! UNEXPECTED ERROR IN CHAT API !!!\n{traceback.format_exc()}")
        return jsonify({'error': '服务器发生未知错误', 'details': str(e)}), 500

@app.route('/api/save', methods=['POST'])
def save_game_api():
    print("[API] Request to /api/save")
    payload = request.get_json(silent=True) or {}
    slot = payload.get('slot', 1)
    # 可选命名：label 或 name（写入 meta.label）
    label = payload.get('label') or payload.get('name')
    if label:
        try:
            # 将 label 写到当前 agent 的 state，BaseCharacter.save 会自动带入 meta
            agent = getattr(getattr(game_service, '_core', None), 'agent', None)
            if agent and hasattr(agent, 'game_state') and isinstance(agent.game_state, dict):
                agent.game_state['label'] = str(label)
        except Exception:
            pass
    success = game_service.save(slot)
    return jsonify({'success': success})

@app.route('/api/load', methods=['POST'])
def load_game_api():
    print("[API] Request to /api/load")
    payload = request.get_json(silent=True) or {}
    slot = payload.get('slot', 1)
    # 先读取一次存档 meta，用于判断角色
    from backend.game_storage import GameStorage
    storage = GameStorage()
    raw = storage.load_game(slot)
    target_role = None
    if raw and isinstance(raw, dict):
        meta = raw.get('meta') or {}
        target_role = meta.get('role')
    # 若存档包含 role，尝试在开始新游戏时切换到对应角色
    if target_role:
        try:
            game_service.start_game(target_role)
            session['character_key'] = str(target_role)
            # 用加载覆盖状态
            success = game_service.load(slot)
        except Exception:
            success = game_service.load(slot)
    else:
        success = game_service.load(slot)
    if success:
        raw_history = getattr(getattr(game_service, '_core', None), 'agent', None)
        raw_history = raw_history.dialogue_history if raw_history else []
        payload = {
            'success': True,
            'game_state': game_service.get_state(),
            'history': _filter_history_for_client(raw_history),
            'character_key': session.get('character_key', 'su_tang')
        }
        try:
            agent = getattr(getattr(game_service, '_core', None), 'agent', None)
            if agent and getattr(agent, 'name', None):
                payload['character_name'] = str(agent.name)
        except Exception:
            pass
        return jsonify(payload)
    return jsonify({'success': False})


@app.route('/api/saves', methods=['GET'])
def list_saves_api():
    """列出存档（包含 meta），便于前端展示角色与保存时间。"""
    print("[API] Request to /api/saves")
    from backend.game_storage import GameStorage
    storage = GameStorage()
    items = storage.list_saves_detailed()
    return jsonify({'saves': items})

# web_start.py 调用
if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0")