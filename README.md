# 绿园中学物语 (Green Garden High School Story)

**绿园中学物语**是一款由大型语言模型驱动的RPG模拟游戏。你将扮演主角，与多个可扩展的 AI 角色在绿园中学开启一段充满变量的校园故事。

目前项目以单角色 Demo 形式运行，核心功能已串联：从前端对话框到后端状态机再到 LLM 调用均可完整走通。以下内容总结了现阶段的实现情况，并指导你如何快速启动体验。

---

## 📌 当前项目状态

* ✅ **基础流程完成**：使用 Flask 提供 Web 接口，前端原生 HTML/CSS/JS，实现对话、好感度展示、存档与读档。
* ✅ **AI 角色架构已成型**：以 `BaseCharacter` 为通用基类，角色以独立类扩展（当前示例为 `SuTangCharacter`）。完成 Prompt 渲染、DeepSeek Chat API 调用、分析 JSON 解析、状态回写等核心链路。
* ✅ **存档系统可用**：`GameStorage` 以 JSON 文件形式管理存档。
* ✅ **人物设定更稳**：系统提示词作为 system 消息随每轮请求注入，显著减少设定漂移（如“烘焙社摊位负责招新”）。
* ✅ **目录已瘦身**：移除根级 legacy 目录与文件（`characters/`、`game_core.py`、`services/`），统一使用 `backend/` 路径。
* ⚠️ **依赖外部 API**：默认使用 DeepSeek Chat，需要在环境变量或 `.env` 中提供 `DEEPSEEK_API_KEY`。
* 🚧 **待办方向**：尚未接入长期记忆/向量库，也未实现多角色、多场景或复杂 UI 效果；README 中列出的未来计划仍未启动。

---

## ✨ 核心玩法亮点

* 🧠 **统一心智 AI**：一次 LLM 请求同时输出角色回复与内心分析，确保情感与行为一致。
* 💖 **可调情绪系统**：分析结果会调整好感度、无聊度、关系阶段，并驱动特殊事件（如表白剧情）。
* 🗂️ **Prompt 驱动人格**：每个角色拥有独立的 Prompt 目录（示例：`prompts/su_tang/`），便于快速修改与扩展。
* 💾 **轻量存档**：每次关键事件可自动保存，方便重复体验不同结局。

---

## 🚀 技术栈

* **后端**：Python 3 + Flask（`app.py`，静态与模板来自 `frontend/`）
* **AI 调用**：DeepSeek Chat API（默认），可自行替换其他兼容的 Chat Completion 服务
* **Agent 核心**：`BaseCharacter`（`backend/domain/characters/base_character.py`） + 各角色类（如 `SuTangCharacter`）
* **存档**：JSON 文件（`saves/`，已在 `.gitignore` 忽略）
* **前端**：原生 HTML / Bootstrap / jQuery（伪打字机效果、好感度动画等）

---

## 🔧 如何运行

1. **克隆仓库**
   ```bash
   git clone https://github.com/你的用户名/Lyuyuan_AI.git
   cd Lyuyuan_AI
   ```

2. **创建并激活虚拟环境**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置 API 密钥**
   * 复制 `.env.example`（若不存在，可新建 `.env` 文件）。
   * 在 `.env` 中写入：
     ```
     DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxx"
     ```
   * 也可以直接在系统环境变量中设置同名变量。

5. **启动 Web 应用**
   ```bash
   python web_start.py
   ```

   说明：若未设置 `DEEPSEEK_API_KEY`，服务仍可启动以调试前端，但首次调用聊天接口会失败（控制台会有提示）。

6. 在浏览器访问 `http://127.0.0.1:5000`，点击「开始游戏」按钮即可开始体验（默认示例为苏糖）。

---

## 🏛️ 当前架构速览

```
.
├── web_start.py          # 统一入口：加载 .env、校验目录并启动 Flask
├── backend/
│   ├── services/         # 应用服务层（对接路由与领域）
│   ├── domain/           # 领域层（角色与核心逻辑）
│   ├── game_storage.py   # JSON 存档管理（唯一权威实现）
│   └── config.py         # 配置（例如 PROMPTS_DIR）
├── frontend/
│   ├── templates/        # 页面模板（index.html 等）
│   └── static/           # 前端资源（CSS、JS、图片）
├── prompts/su_tang/      # 示例角色的 Prompt 模板与角色设定
└── saves/                # 存档输出目录
```

---

---

## 🧩 如何新增一个角色（多角色指引）

1) 新建角色类文件
   - 在 `backend/domain/characters/` 下创建 `your_role_character.py`，继承 `BaseCharacter`。
   - 可参考现有示例：`backend/domain/characters/su_tang_character.py`
     - 指定角色名、欢迎语、默认状态（如 closeness、mood_today、last_topics 等）。
     - 提供 `prompt_template_path` 与 `system_prompts`（角色设定与场景）。
     - 可覆写钩子：`handle_special_commands`、`handle_pre_chat_events`、`handle_post_chat_events`、`get_backup_reply`。

2) 准备 Prompt 目录
   - 在 `prompts/` 下创建 `your_role/` 文件夹，至少包含：
     - `analysis_prompt.txt`：指导 LLM 产出 <analysis> JSON 与 <response>。
     - `your_role_prompt.txt`：角色世界观/说话风格等系统设定。

3) 挂载到游戏核心（backend 架构）
    - 在 `backend/domain/characters/` 下新增你的角色类文件，并在 `backend/domain/game_core.py` 中替换默认角色：
       ```python
       from backend.domain.characters.your_role_character import YourRoleCharacter
       # ...
       self.agent = YourRoleCharacter(is_new_game=True)
       ```
    - 如需运行时切换角色，可在 `backend/services/game_service.py` 与路由层中读取 `role` 参数，选择不同的角色实例或工厂创建。

4) 资源与前端
   - 如有角色立绘，请放到 `frontend/static/images/`，并在前端按需切换显示逻辑。

5) 存档兼容
   - `GameStorage` 使用 JSON 存档；不同角色建议在存档中写入 `meta.role` 或以不同槽位/文件名区分，以避免混用状态。

---

## 🔭 下一步计划

* [ ] UI 提示强化：在界面实时展示心情、事件提醒等
* [ ] 记忆系统：引入向量数据库，支持长期记忆召回
* [ ] 多角色选择：在启动页/菜单选择不同角色并热切换
* [ ] 多场景扩展：让场景描述与剧情章节动态切换
* [ ] 事件编排：基于分析结果触发更多分支剧情

欢迎提出 Issues / PR，一起让角色们更有灵魂 💡

---

## 🔌 API 概览（后端）

- POST `/api/start_game`
   - 请求体：`{ "role": "su_tang" }`（当前仅示例角色，参数为预留）
   - 响应：`{ intro_text, game_state, history, character_key }`
   - 说明：返回对话开场文本与初始状态。history 已过滤掉 system 消息。

- POST `/api/chat`
   - 请求体：`{ "message": "..." }`
   - 响应：`{ response, game_state, character_key }`
   - 说明：服务端会注入 system prompts 并与历史一同推理，更新好感度等状态。

- POST `/api/save`
   - 请求体：`{ "slot": 1 }`
   - 响应：`{ success: true/false }`

- POST `/api/load`
   - 请求体：`{ "slot": 1 }`
   - 响应：`{ success, game_state, history, character_key }`
   - 说明：history 为仅包含 user/assistant 的可展示对话。

---

## 🖥️ 前端要点

- 欢迎页选择角色（当前仅苏糖），开始游戏后切换到对话界面。
- 对话区支持伪打字机效果；状态区展示“好感度/关系/场景”，好感度变更有动画。
- 保存/读档在页脚，支持槽位 1-3；读档后可直接恢复历史并进入游戏界面。
- 头像会根据 `character_key` 动态加载，失败时回退到 `su_tang.jpg`。
- 界面使用固定 60vh 聊天高度，避免滚动跳动。

## 🛠️ 开发提示（Git 与环境）

- 虚拟环境不应提交到仓库：`.venv/`、`venv/`、`web_venv/` 已加入 `.gitignore`。
- 如果你的本地虚拟环境之前被提交过，可“取消跟踪”（不删本地，只从 Git 移除）：
   ```powershell
   git rm -r --cached web_venv
   git commit -m "chore: stop tracking local virtual env web_venv"
   ```
   如有需要，替换为 `.venv` 或 `venv` 执行同样操作。
- `__pycache__` 属于正常的 Python 缓存目录，已被忽略；无需手动清理。
- 依赖精简：`requirements.txt` 保持与代码一致（Flask、requests、python-dotenv、jieba），尽量避免未使用库。