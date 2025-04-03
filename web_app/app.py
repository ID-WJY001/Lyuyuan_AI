"""
绿园中学物语：追女生模拟
Web版本后端
"""

from flask import Flask, render_template, request, jsonify, session
import os
import json
import random
from datetime import datetime
import sys
from openai import OpenAI

# 导入游戏核心逻辑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from game.managers import GameManager
except ImportError:
    # 如果不能导入新结构，使用简化版游戏代理
    class SimpleGameAgent:
        """简化版游戏智能体"""
        def __init__(self):
            self.dialogue_history = []
            self.game_state = {
                "closeness": 30,  # 初始好感度
                "discovered": [],
                "last_topics": [],
                "relationship_state": "初始阶段",
                "scene": "学校 - 百团大战",
                "date": datetime.now().strftime("%Y年%m月%d日"),
                "time_period": "上午"
            }
            
            # 初始化对话历史
            self._init_dialogue()
        
        def _init_dialogue(self):
            """初始化对话历史"""
            self.dialogue_history = [
                {"role": "system", "content": "你是苏糖，绿园中学高一二班的学生，烘焙社社长。你性格温柔甜美，做事认真负责，对烘焙充满热情。"},
                {"role": "system", "content": "你现在正在百团大战活动中为烘焙社招新。你是个温柔、甜美的女生，但也有自己的原则和底线。"},
                {"role": "assistant", "content": "（正在整理烘焙社的宣传材料）有什么我可以帮你的吗？"}
            ]
        
        def chat(self, user_input):
            """处理用户输入，返回回复"""
            # 添加用户输入
            self.dialogue_history.append({"role": "user", "content": user_input})
            
            # 简单的预设回复系统
            responses = [
                "（微笑）是的，我们烘焙社本学期会有很多有趣的活动，包括蛋糕制作、面包烘焙和甜点装饰课程。你有烘焙经验吗？",
                "（认真地看着你）烘焙其实是一门需要耐心和专注的艺术，我从小就很喜欢看妈妈做点心，慢慢就爱上了这个过程。",
                "（轻轻歪头）其实每个人都可以学会烘焙的，只要有热情就好。我们社团也会从最基础的教起，不用担心跟不上。",
                "（笑着）你知道吗？我最拿手的是提拉米苏和草莓慕斯蛋糕。如果你加入我们社团，以后有机会可以尝尝我做的。",
                "（温和地）嗯，我们社团每周五下午都有活动，如果你感兴趣的话，可以留下你的联系方式。",
                "（好奇地）你平时有什么兴趣爱好吗？除了烘焙，我也很喜欢听音乐和阅读。",
                "（眼睛亮起来）真的吗？我也很喜欢这个！看来我们有共同的兴趣呢。",
                "（认真思考）这个问题很有趣，我之前没想过...让我想想...",
                "（微微脸红）谢谢你的夸奖，能遇到理解烘焙魅力的人真的很开心。",
                "（轻声笑）你说话真有意思，我们班上可没几个男生会这么聊天。"
            ]
            
            # 根据好感度选择不同风格的回复
            closeness = self.game_state["closeness"]
            if closeness >= 80:
                high_closeness_responses = [
                    "（脸颊微红，视线略显害羞）你真的很特别，陈辰...我从没遇过像你这样的人。（轻轻碰了一下你的手臂）下次我做点心一定要第一个给你尝尝。",
                    "（靠近一些，小声说）其实...我昨天做了一批曲奇饼，还特意多做了一些...（眼睛亮亮的看着你）明天想尝尝吗？我可以单独给你带一盒。",
                    "（开心地整理你的衣领）你今天这件衣服很适合你呢！（微微脸红，小声说）我总是能在人群中一眼就找到你...",
                    "（笑容特别明亮）陈辰，放学后有空吗？我想去那家新开的咖啡厅，但一个人去有点...（期待地看着你）你愿意陪我去吗？"
                ]
                responses.extend(high_closeness_responses)
                
            # 随机选择一个回复
            reply = random.choice(responses)
            
            # 更新好感度（根据用户输入长度和随机因素）
            if len(user_input) > 20:
                # 较长的回答增加好感度
                self.game_state["closeness"] += random.randint(1, 3)
            elif "烘焙" in user_input or "蛋糕" in user_input or "甜点" in user_input:
                # 谈论烘焙相关话题增加好感度
                self.game_state["closeness"] += random.randint(2, 4)
            else:
                # 普通对话随机变化
                self.game_state["closeness"] += random.randint(-1, 2)
                
            # 确保好感度在合理范围内
            self.game_state["closeness"] = max(0, min(100, self.game_state["closeness"]))
            
            # 更新关系状态
            self._update_relationship_state()
            
            # 添加AI回复到历史
            self.dialogue_history.append({"role": "assistant", "content": reply})
            
            return reply
        
        def _update_relationship_state(self):
            """根据好感度更新关系状态"""
            closeness = self.game_state["closeness"]
            if closeness >= 80:
                self.game_state["relationship_state"] = "亲密关系"
            elif closeness >= 60:
                self.game_state["relationship_state"] = "好朋友"
            elif closeness >= 40:
                self.game_state["relationship_state"] = "朋友"
            else:
                self.game_state["relationship_state"] = "初始阶段"
        
        def save(self, slot=1):
            """保存游戏状态"""
            save_dir = "saves"
            os.makedirs(save_dir, exist_ok=True)
            
            save_data = {
                "dialogue_history": self.dialogue_history,
                "game_state": self.game_state
            }
            
            with open(f"{save_dir}/save_{slot}.json", "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            return True
        
        def load(self, slot=1):
            """加载游戏状态"""
            save_path = f"saves/save_{slot}.json"
            if not os.path.exists(save_path):
                return False
            
            try:
                with open(save_path, "r", encoding="utf-8") as f:
                    save_data = json.load(f)
                
                self.dialogue_history = save_data["dialogue_history"]
                self.game_state = save_data["game_state"]
                return True
            except Exception as e:
                print(f"加载存档失败: {e}")
                return False

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'green_garden_high_school_romance'  # 用于session

# 确保保存目录存在
os.makedirs("saves", exist_ok=True)

# 创建全局游戏代理
try:
    game_agent = GameManager()
except:
    print("无法加载完整GameManager，使用简化版游戏代理")
    game_agent = SimpleGameAgent()
    
    # 确保简化版游戏代理在对话方法中使用正确的API调用
    original_chat = game_agent.chat
    
    def new_chat(user_input):
        """修改后的聊天函数，尝试使用API进行对话"""
        # 添加用户输入
        game_agent.dialogue_history.append({"role": "user", "content": user_input})
        
        try:
            # 尝试使用API
            client = OpenAI(
                api_key=os.environ.get("DEEPSEEK_API_KEY", "your-deepseek-api-key"),  # 替换为实际API密钥
                base_url="https://api.deepseek.com/v1"  # DeepSeek的API基础URL
            )
            response = client.chat.completions.create(
                model="deepseek-chat", 
                messages=game_agent.dialogue_history,
                temperature=0.7,
                max_tokens=800
            )
            
            # 获取回复
            reply = response.choices[0].message.content
            
        except Exception as e:
            # 连接错误处理：使用预设回复
            print(f"API连接错误: {str(e)}")
            # 使用原始方法的备用回复
            reply = original_chat(user_input)
            # 这里不需要更新好感度，因为original_chat已经处理了
            return reply
        
        # 添加AI回复到历史
        game_agent.dialogue_history.append({"role": "assistant", "content": reply})
        
        # 更新好感度（类似于original_chat中的逻辑）
        if len(user_input) > 20:
            # 较长的回答增加好感度
            game_agent.game_state["closeness"] += random.randint(1, 3)
        elif "烘焙" in user_input or "蛋糕" in user_input or "甜点" in user_input:
            # 谈论烘焙相关话题增加好感度
            game_agent.game_state["closeness"] += random.randint(2, 4)
        else:
            # 普通对话随机变化
            game_agent.game_state["closeness"] += random.randint(-1, 2)
            
        # 确保好感度在合理范围内
        game_agent.game_state["closeness"] = max(0, min(100, game_agent.game_state["closeness"]))
        
        # 更新关系状态
        game_agent._update_relationship_state()
        
        return reply
    
    # 替换chat方法
    game_agent.chat = new_chat

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
    user_input = request.json.get('message', '')
    
    # 使用游戏代理处理消息
    response = game_agent.chat(user_input)
    
    return jsonify({
        'response': response,
        'game_state': game_agent.game_state
    })

@app.route('/api/save', methods=['POST'])
def save_game():
    """保存游戏"""
    slot = request.json.get('slot', 1)
    success = game_agent.save(slot)
    
    return jsonify({
        'success': success,
        'message': f"游戏已保存到存档 {slot}" if success else "保存游戏失败"
    })

@app.route('/api/load', methods=['POST'])
def load_game():
    """加载游戏"""
    slot = request.json.get('slot', 1)
    success = game_agent.load(slot)
    
    return jsonify({
        'success': success,
        'message': f"已加载存档 {slot}" if success else "加载游戏失败",
        'game_state': game_agent.game_state if success else None
    })

@app.route('/api/get_saves', methods=['GET'])
def get_saves():
    """获取所有存档"""
    saves = []
    save_dir = "saves"
    
    if os.path.exists(save_dir):
        for file in os.listdir(save_dir):
            if file.startswith("save_") and file.endswith(".json"):
                slot = file[5:-5]  # 提取slot编号
                try:
                    slot = int(slot)
                    with open(os.path.join(save_dir, file), "r", encoding="utf-8") as f:
                        save_data = json.load(f)
                    
                    saves.append({
                        'slot': slot,
                        'date': save_data.get('game_state', {}).get('date', '未知日期'),
                        'closeness': save_data.get('game_state', {}).get('closeness', 0),
                        'relationship': save_data.get('game_state', {}).get('relationship_state', '未知状态')
                    })
                except:
                    pass
    
    return jsonify({
        'saves': saves
    })

if __name__ == '__main__':
    # 确保工作目录正确
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 运行Flask应用
    app.run(debug=True) 