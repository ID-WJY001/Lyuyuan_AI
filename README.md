# 绿园中学物语 (Green Garden High School Story)

**绿园中学物语**是一款由大型语言模型驱动的恋爱模拟游戏。你将扮演主角，与多个可扩展的 AI 角色在绿园中学开启一段充满变量的校园故事。

目前项目以单角色 Demo 形式运行，核心功能已串联：从前端对话框到后端状态机再到 LLM 调用均可完整走通。以下内容总结了现阶段的实现情况，并指导你如何快速启动体验。

---

## 📌 当前项目状态

* ✅ **基础流程完成**：使用 Flask 提供 Web 接口，前端原生 HTML/CSS/JS，实现对话、好感度展示、存档与读档。
* ✅ **AI 角色架构已成型**：以 `BaseCharacter` 为通用基类，角色以独立类扩展（当前示例为 `SuTangCharacter`）。完成 Prompt 渲染、DeepSeek Chat API 调用、分析 JSON 解析、状态回写等核心链路。
* ✅ **存档系统可用**：`GameStorage` 以 JSON 文件形式管理存档，并带有简单版本信息与自动保存结局的能力。
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

* **后端**：Python 3 + Flask（`web_app/app.py`）
* **AI 调用**：DeepSeek Chat API（默认），可自行替换其他兼容的 Chat Completion 服务
* **Agent 核心**：`BaseCharacter`（通用逻辑） + 各角色类（如 `SuTangCharacter`）
* **存档**：JSON 文件（`saves/`）
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

6. 在浏览器访问 `http://127.0.0.1:5000`，点击「开始游戏」按钮即可开始体验（默认示例为苏糖）。

---

## 🏛️ 当前架构速览

```
.
├── web_start.py          # 统一入口：加载 .env、校验目录并启动 Flask
├── base_character.py     # 可复用的 LLM 角色基类
├── su_tang_character.py  # 示例角色：苏糖（实现与事件脚本）
├── Game_Storage.py       # JSON 存档管理
├── web_app/
│   ├── app.py            # Flask 路由与 API
│   ├── game_core.py      # SimpleGameCore，封装角色实例
│   ├── templates/        # 页面模板（index.html 等）
│   └── static/           # 前端资源（CSS、JS、图片）
├── prompts/su_tang/      # 示例角色的 Prompt 模板与角色设定
└── saves/                # 存档输出目录
```

---

---

## 🧩 如何新增一个角色（多角色指引）

1) 新建角色类文件
   - 在项目根目录创建 `your_role_character.py`，继承 `BaseCharacter`。
   - 参考 `su_tang_character.py`：
     - 指定角色名、欢迎语、默认状态（如 closeness、mood_today、last_topics 等）。
     - 提供 `prompt_template_path` 与 `system_prompts`（角色设定与场景）。
     - 可覆写钩子：`handle_special_commands`、`handle_pre_chat_events`、`handle_post_chat_events`、`get_backup_reply`。

2) 准备 Prompt 目录
   - 在 `prompts/` 下创建 `your_role/` 文件夹，至少包含：
     - `analysis_prompt.txt`：指导 LLM 产出 <analysis> JSON 与 <response>。
     - `your_role_prompt.txt`：角色世界观/说话风格等系统设定。

3) 挂载到游戏核心
   - 在 `web_app/game_core.py` 中把默认角色替换为你的角色：
     ```python
     from your_role_character import YourRoleCharacter
     # ...
     self.agent = YourRoleCharacter(is_new_game=True)
     ```
   - 如需运行时切换角色，可扩展为：根据 URL 参数/会话状态选择不同角色实例。

4) 资源与前端
   - 如有角色立绘，请放到 `web_app/static/images/`，并在前端按需切换显示逻辑。

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