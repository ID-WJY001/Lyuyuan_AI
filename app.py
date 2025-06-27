"""
绿园中学物语：追女生模拟
Web版本后端 (带输入校验机制)
"""

# 导入所有必要的库
from flask import Flask, render_template, request, jsonify, session
import os
import sys
# --- 新增导入 ---
from jsonschema import validate, ValidationError

# 设置项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

# 确保工作目录正确
os.chdir(ROOT_DIR)

# 导入工具函数
try:
    from utils.common import load_env_file, ensure_directories
    # 读取.env文件中的环境变量
    load_env_file()
except ImportError:
    print("警告：无法导入 'utils.common'，请确保环境变量已配置。")


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
    raise  # 保持原有行为，如果失败则抛出异常

# --------------------------------------------------------------------------
# --- 新增：定义明确的输入规范 (JSON Schema) ---
# 这份“合同”规定了 /api/chat 接口的输入要求
CHAT_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {
            "type": "string",
            "minLength": 1,
            "description": "用户的聊天内容，必须是非空字符串。"
        }
    },
    "required": ["message"],
    "additionalProperties": False # 不允许有除 message 之外的其他字段
}
# --------------------------------------------------------------------------


@app.route('/')
def index():
    """渲染主页 (保持不变)"""
    if 'initialized' not in session:
        session['initialized'] = True
        session['game_started'] = False
    return render_template('index.html')

@app.route('/api/start_game', methods=['POST'])
def start_game():
    """开始游戏 (保持不变)"""
    session['game_started'] = True
    
    if hasattr(game_agent, 'reset_game'):
        game_agent.reset_game()
    else:
        game_agent.game_state["closeness"] = 30
        if hasattr(game_agent, 'agent') and hasattr(game_agent.agent, 'game_state'):
            game_agent.agent.game_state["closeness"] = 30
            game_agent.agent.game_state["relationship_state"] = "初始阶段"
        if hasattr(game_agent, 'sync_affection_values'):
             game_agent.sync_affection_values()
    
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
    """处理聊天请求 (增加了校验机制，核心逻辑不变)"""
    try:
        # --- 这是新增的校验代码块 ---
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': '无效的请求',
                'message': '请求体必须是JSON格式。'
            }), 400

        try:
            # 使用我们定义的 Schema 来校验接收到的数据
            validate(instance=json_data, schema=CHAT_INPUT_SCHEMA)
        except ValidationError as e:
            # 如果校验失败，返回一个清晰的、对开发者友好的错误信息
            return jsonify({
                'error': '输入数据不符合规范',
                'message': e.message
            }), 400
        # --- 校验结束，如果代码能走到这里，说明输入数据是100%合规的 ---

        # 获取用户输入 (现在可以放心获取，因为已经校验过了)
        user_input = json_data.get('message')
        
        # --- 以下是你原有的核心逻辑，一个字都没改 ---
        try:
            response = game_agent.chat(user_input)
            
            # 你的原有逻辑：确保返回的是字符串
            if not isinstance(response, str):
                # 如果是生成器，消费它 (这是为了兼容你可能在Agent里做的修改)
                response = "".join(list(response)) if not isinstance(response, str) else str(response)
                
            return jsonify({
                'response': response,
                'game_state': game_agent.game_state
            })
        except AttributeError as e:
            app.logger.error(f"聊天方法调用错误: {str(e)}")
            return jsonify({
                'error': '游戏代理错误',
                'message': '聊天系统处理失败，可能需要重新启动游戏',
                'details': str(e)
            }), 500
            
    except Exception as e:
        app.logger.error(f"处理聊天请求时发生错误: {str(e)}")
        return jsonify({
            'error': '服务器错误',
            'message': '处理消息时发生错误，请重试',
            'details': str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")