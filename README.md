# 绿园中学物语 (Green Garden High School Story)

> v1.0.0 — 多角色首发版：五名可选角色、统一分析模板、人设去标签化、首页简介含初始好感度、首帧动画优化。

**绿园中学物语**是一款由 LLM 驱动的轻叙事 RPG。你将扮演主角，与多个有“温度”的 AI 角色在绿园中学游逛、搭话与靠近。

本版起，支持五名角色与更稳定的人设表达；从前端 UI 到后端状态与 Prompt 均做了结构化升级。

---

## 🆕 v1.0.0 有哪些变化

- 多角色可选（5 人）：苏糖、林雨含、罗一莫、顾盼、夏星晚（欢迎页下拉选择）
- 角色简介更清晰：首页显示每个角色简述与“初始好感度”
- 人设去标签化：去除“模板腔”（如过度招新/教练口吻/清单式建议），加入“场景任务克制”规则，优先跟随玩家话题
- 统一分析模板：所有角色遵循同一 <analysis>/<response> 输出规范，稳定产出 JSON 分析并驱动好感/无聊变更
- 首帧动画优化：进入游戏时好感度条直接定位到初始值，不再从 30 动画到初始值
- 存档槽位扩展：页面底部存档槽位 1→5
- 前端显示角色名：聊天界面立绘下方实时显示当前角色名称
- 图像与占位：立绘统一为 `.png`；加载失败回退为 `favicon.ico`

---

## ✨ 玩法亮点

- 🧠 一次请求，双通道产出：角色回复 + 内心分析（JSON），保证“说/想/改状态”一致
- 💖 情绪与关系：根据分析调整好感度、无聊度、关系阶段，并触发事件（例如表白）
- 🗂️ Prompt 驱动人格：角色 Persona + Analysis 模板可快速迭代，支持“风格与人情味”约束
- 💾 轻量存档：JSON 文件存档，前端一键保存/读取，槽位 1-5

---

## 🧩 可选角色（初始好感度）

- 苏糖（30）：烘焙社摊位附近的温柔女孩；甜点与音乐是她的安全感
- 林雨含（50）：舞蹈社附近的气氛担当；元气直给，也会认真安慰
- 罗一莫（35）：科技协会附近的慢热同学；话不多但认真听，细节里有温度
- 顾盼（40）：桌游社附近常能遇到他；会接梗也会收住，让人不尴尬
- 夏星晚（38）：操场与网球社之间的身影；自律里有温柔，很会照顾人

> 备注：招新仅是“壳子”背景，不会反复打断话题。除非玩家主动提及或自然衔接，系统会克制把话题拉回“招新/报名/流程”。

---

## 🏗️ 技术栈与结构

- 后端：Python 3 + Flask（`app.py` 路由，`backend/` 领域与服务）
- LLM：DeepSeek Chat API（可替换），以 system+user 组合发起推理
- Agent：`BaseCharacter` 通用基类 + 角色类（`backend/domain/characters/`）
- 存档：`GameStorage`（JSON 到 `saves/`）
- 前端：原生 HTML/Bootstrap/jQuery（伪打字机、进度条动画、选择器、AJAX）
- 立绘：`frontend/static/images/*.png`，错误回退到 `favicon.ico`

```
.
├── web_start.py                 # 统一入口：加载 .env、检查目录、启动 Flask
├── app.py                       # 路由：/api/start_game /api/chat /api/save /api/load
├── backend/
│   ├── domain/
│   │   ├── characters/          # BaseCharacter + 各角色类（SuTang / LinYuhan / LuoYimo / GuPan / XiaXingwan）
│   │   └── game_core.py         # 角色工厂与聊天/状态分发
│   ├── services/                # Service 包装（game_service）
│   ├── game_storage.py          # JSON 存档
│   └── config.py                # PROMPTS_DIR 等
├── frontend/
│   ├── templates/               # index.html / layout.html
│   └── static/
│       ├── js/main.js           # UI 交互与 AJAX、预览与头像切换
│       └── css/style.css
├── prompts/                     # 各角色 persona 与 analysis 模板
└── saves/                       # 存档输出目录（save_1.json ...）
```

---

## 🔧 快速开始（Windows/Powershell）

在开始之前，请确保：

- 已安装 Python 3.10+（建议 3.11/3.12）。检查：

```powershell
python --version; pip --version
# 若提示未找到 python，可尝试：
py --version; py -m pip --version
```

- 你正在 Windows PowerShell 中操作（不是 CMD）。
- 本项目根目录下将创建 `.venv/` 虚拟环境；无需使用仓库里的 `web_venv/`（那是本地环境，不可移植）。

1) 克隆与进入目录

```powershell
git clone https://github.com/你的用户名/Lyuyuan_AI.git
cd Lyuyuan_AI
```

2) 创建与激活环境

```powershell
# 任意一种可用命令创建虚拟环境
python -m venv .venv  # 或者
py -3.11 -m venv .venv

# 激活（PowerShell）
.\.venv\Scripts\Activate.ps1

# 如遇“运行脚本被禁用”(Execution Policy) 报错，可临时放开本会话：
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

3) 安装依赖

```powershell
python -m pip install -U pip
pip install -r requirements.txt
```

4) 配置 LLM 密钥（以Deepseek API为例）

- 打开Deepseek官网，进入右上角的 API 开放平台，充值（几块钱就够了可以用好久好久）后创建API Key后复制。

- 新建 `.env`（或复制 `.env.example`）并写入：
```
DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxx"
```
- 未配置密钥时，服务仍可启动以调试前端；首次调用聊天会失败（控制台有提示）。
  - `.env` 文件放在项目根目录（与 `web_start.py` 同级）。

5) 启动服务

```powershell
python web_start.py
```

提示：
- 首次启动可能弹出 Windows 防火墙提示，选择“允许访问”。
- 终止服务：在该终端按 Ctrl+C。

浏览器访问 http://127.0.0.1:5000，选择角色后“开始游戏”。

---

## 🔧 快速开始（macOS / zsh 或 bash）

1) 克隆与进入目录

```bash
git clone https://github.com/你的用户名/Lyuyuan_AI.git
cd Lyuyuan_AI
```

2) 创建与激活环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3) 安装依赖

```bash
python3 -m pip install -U pip
pip3 install -r requirements.txt
```

4) 配置 LLM 密钥（以Deepseek API为例）

- 打开Deepseek官网，进入右上角的 API 开放平台，充值（几块钱就够了可以用好久好久）后创建API Key后复制。

- 新建 `.env`（或复制 `.env.example`）并写入：
```
DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxx"
```
- 未配置密钥时，服务仍可启动以调试前端；首次调用聊天会失败（控制台有提示）。
  - `.env` 文件放在项目根目录（与 `web_start.py` 同级）。

5) 启动服务

```bash
python3 web_start.py
```

在浏览器访问 http://127.0.0.1:5000。停止服务按 Ctrl+C。

---

## ❓常见问题排查（Windows/macOS）

- python/pip 命令找不到：
  - Windows 用 `py` 和 `py -m pip`；macOS 用 `python3` 和 `pip3`。
- 激活虚拟环境时报“运行脚本被禁用”：
  - PowerShell 执行：`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` 后再激活。
- 启动后立刻退出（Exit Code: 1）或报模块缺失（如 Flask）：
  - 确认已激活虚拟环境，并重新执行 `pip install -r requirements.txt`。
- 5000 端口被占用：
  - 关闭占用该端口的程序，或暂时改端口（编辑 `web_start.py`/`app.py` 中的 `port=5000` 为其他未占用端口）。
- 未配置 DEEPSEEK_API_KEY：
  - 前端可正常打开和操作，首次聊天请求会失败；配置 `.env` 后重启服务即可。

---

## 🔌 API 概览

- POST `/api/start_game`
  - 请求：`{ "role": "su_tang" | "lin_yuhan" | "luo_yimo" | "gu_pan" | "xia_xingwan" }`
  - 响应：`{ intro_text, game_state, history, character_key, character_name }`
  - 说明：`history` 仅返回 user/assistant（过滤 system）；用于前端重建可见聊天。

- POST `/api/chat`
  - 请求：`{ "message": "..." }`
  - 响应：`{ response, game_state, character_key, character_name }`
  - 说明：后端会调用 LLM 产出 `<analysis>` JSON 与 `<response>`，并据此更新好感/无聊/关系等状态。

- POST `/api/save`
  - 请求：`{ "slot": 1, "label"?: "可选名称" }`
  - 响应：`{ success: true|false }`

- POST `/api/load`
  - 请求：`{ "slot": 1 }`
  - 响应：`{ success, game_state, history, character_key, character_name }`
  - 说明：若存档含 `meta.role`，会自动切到对应角色再加载。

- GET `/api/saves`
  - 响应：`{ saves: [...] }`（包含 `slot`、`meta`、`mtime` 等，便于在前端列表展示）

---

## 🧠 Prompt 与分析规范（统一）

- 所有角色使用统一的分析输出结构，LLM 必须在 `<analysis>` 中给出严格 JSON：
  - `thought_process`, `player_emotion_guess`, `player_intent_guess`, `response_strategy`,
    `affection_delta_reason`, `affection_delta (-5..+5)`, `boredom_delta (-3..+3)`,
    `mood_change`, `triggered_topics`
- `<response>` 为最终对话文本；服务端解析后更新状态并入历史
- “场景任务克制”：招新/拉场等为背景，只在自然需要时点到；优先跟随玩家的当下话题与情绪
- 风格规则（示例）：短句优先、一次一个小建议、允许自然停顿、可点到轻量生活细节、避免“清单/教程/教练腔”

---

## 💾 存档与资源

- 存档：`saves/save_{slot}.json`（槽位 1-5，或更多）
- 立绘：`frontend/static/images/{role_key}.png`；失败回退 `favicon.ico`
- 角色名：接口返回 `character_name`，前端立绘下方展示
- 初始好感：欢迎页简介显示；进入游戏首帧直接按初始值渲染进度条（无 30→初始动画）

---

## 🛠️ 开发与协作

- 依赖（最小集）：Flask、requests、python-dotenv、jieba
- 本地虚拟环境不提交：`.venv/`、`venv/`、`web_venv/` 已在 `.gitignore`
- 若曾误提交本地环境，可用：
  ```powershell
  git rm -r --cached web_venv
  git commit -m "chore: stop tracking local virtual env web_venv"
  ```
- 立绘命名规范：与角色键一致（`su_tang.png` 等）

---

## 🔭 路线图

- [ ] 更丰富的事件流与分支
- [ ] 记忆系统（向量库）与长期关系演化
- [ ] 多场景与章节推进
- [ ] UI 提示与状态小组件（心情、触发事件）
- [ ] 更多角色与差异化互动机制

---

一起把角色们打磨得更有灵魂 💡