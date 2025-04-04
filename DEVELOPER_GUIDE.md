# 绿园中学物语 - 开发者文档

## 1. 项目概述

**绿园中学物语** 是一款基于 Python 开发的恋爱模拟游戏 (Dating Sim)。玩家扮演高中男生"陈辰"，通过与女主角"苏糖"进行对话互动，提升好感度，最终达成不同结局。

游戏的核心机制包括：

*   **对话驱动:** 通过自然语言输入与 AI 控制的角色进行交流。
*   **好感度系统:** 玩家的选择和对话质量会影响角色好感度。
*   **关系阶段:** 好感度决定了玩家与角色关系的不同阶段。
*   **多结局:** 最终关系状态导向不同的游戏结局。
*   **成就系统:** 记录并奖励玩家在游戏中的特定行为或里程碑。

项目同时提供了**命令行界面**和**Web图形用户界面 (GUI)** 两种体验方式。

**技术栈:**

*   **后端:** Python 3
*   **Web框架 (Web版):** Flask
*   **AI对话:** 可能使用 OpenAI API 或类似的大型语言模型 (基于 `openai` 库的导入和 `.env` 文件中的 API 密钥推断)。
*   **数据存储:** JSON 文件 (存档), SQLite (成就, 对话记录)
*   **配置:** YAML 文件

## 2. 高层架构

项目大致可以分为以下几个主要模块：

1.  **游戏管理器 (`GameManager`):** 作为游戏的核心协调者，负责初始化和管理所有子系统（如角色、场景、好感度、对话、成就等），控制游戏流程和状态。
2.  **角色AI (`GalGameAgent` / `Su_Tang.py`):** 负责单个角色的行为逻辑，包括处理玩家输入、生成对话响应（可能调用外部API）、管理角色内部状态（好感度、情绪、记忆等）。`CharacterFactory` 用于创建和管理不同的角色实例。
3.  **核心系统 (`core/`):** 包含游戏的基础机制模块，如更通用的好感度计算逻辑 (`affection_system.py`)、自然语言处理引擎 (`nlp_engine.py`) 和场景管理 (`scene_manager.py`)。
4.  **游戏逻辑 (`game/`):** 包含更具体的游戏玩法实现，如对话处理流程 (`dialogue_system.py`) 和好感度在游戏层面的应用 (`affection_manager.py`)。
5.  **Web应用 (`web_app/`):** 提供基于 Flask 的 Web GUI，处理 HTTP 请求，渲染前端页面，并通过 API 与后端游戏逻辑交互。
6.  **数据持久化 (`Game_Storage.py`, `achievement_system.py`):** 负责将游戏状态（存档）和成就进度保存到文件或数据库，并从中加载。
7.  **配置与资源:** 包含角色设定、游戏配置、提示文本、静态资源（图片等）。

```mermaid
graph TD
    subgraph User Interface
        CLI[命令行界面]
        WebApp[Web界面 (Flask)]
    end

    subgraph Backend Core
        GM[GameManager (game/game_manager.py)]
        CF[CharacterFactory (Character_Factory.py)]
        Agent[角色AI (Su_Tang.py / GalGameAgent)]
        DS[DialogueSystem (game/dialogue_system.py)]
        AM[AffectionManager (game/affection_manager.py)]
        SM[SceneManager (core/scene_manager.py)]
        AS[AchievementSystem (achievement_system.py)]
        NLP[NLPEngine (core/nlp_engine.py)]
        AffSys[AffectionSystem (core/affection_system.py)]
        Storage[GameStorage (Game_Storage.py)]
    end

    subgraph Data & Config
        ConfigYAML[配置 (config/*.yaml)]
        Prompts[提示 (prompts/*.txt, sutang_prompt.txt)]
        Saves[存档 (saves/*.json)]
        DB[数据库 (data/*.db)]
        Assets[资源 (assets/*)]
        Env[.env]
    end

    subgraph External Services
        LLM[大语言模型 API (e.g., OpenAI)]
    end

    CLI --> GM
    WebApp -- HTTP API --> FlaskApp[web_app/app.py]
    FlaskApp --> GM

    GM --> CF
    GM --> DS
    GM --> AM
    GM --> SM
    GM --> AS
    GM --> Storage
    GM --> Agent  # GameManager可能直接或间接与Agent交互

    CF --> Agent
    Agent -- 调用 --> LLM
    Agent --> Storage # Agent内部也可能调用存档
    Agent <-- Prompts
    Agent <-- ConfigYAML # 角色配置

    DS --> Agent
    DS --> NLP
    AM --> AffSys
    AM --> GM # 更新全局状态
    AS --> DB # 读写成就数据
    AS --> GM # 检查成就条件

    Storage --> Saves

    GM <-- ConfigYAML # 加载游戏配置
    FlaskApp <-- Env # 加载API Key

```

## 3. 目录结构

```
Su_Tang/
├── assets/               # 资产文件夹
│   ├── images/           # 图片资源
│   └── audio/            # 音频资源
├── config/               # 配置文件
│   ├── characters/       # 角色配置
│   └── affection_config.json  # 好感度系统配置
├── core/                 # 核心功能模块
│   ├── affection/        # 好感度系统
│   ├── dialogue/         # 对话系统
│   ├── nlp/              # 自然语言处理
│   └── storage/          # 存储系统
├── data/                 # 数据文件
│   ├── memories/         # 记忆数据
│   └── profiles/         # 角色资料
├── game/                 # 游戏逻辑
│   ├── managers/         # 游戏管理器
│   ├── game_manager.py   # 游戏管理主类
│   └── main.py           # 游戏主入口
├── prompts/              # 提示词文件
│   ├── system_prompt.txt     # 系统提示词
│   └── character_prompt.txt  # 角色提示词
├── utils/                # 工具函数
│   ├── common.py         # 通用工具函数
│   └── config/           # 配置管理模块
├── web_app/              # Web应用
│   ├── static/           # 静态资源
│   ├── templates/        # HTML模板
│   └── app.py            # Flask应用
├── web_venv/             # Python虚拟环境 (唯一的虚拟环境)
├── .env                  # 环境变量
├── .gitignore            # Git忽略文件
├── install.py            # 安装脚本
├── install_deps.py       # 依赖安装脚本
├── install_windows.bat   # Windows安装批处理
├── main.py               # 游戏启动入口
├── start_web.bat         # Web版启动批处理
├── web_start.py          # Web版启动脚本
└── README.md             # 项目说明
```

## 4. 关键文件详解

### 4.1 根目录文件

*   **`Su_Tang.py` (`GalGameAgent` 类):**
    *   定义了苏糖 (以及通用角色) 的 AI 代理。
    *   负责加载角色 Prompt (`sutang_prompt.txt`, `CHARACTER_DETAILS`)。
    *   维护 `dialogue_history` 用于与 LLM API 交互。
    *   管理角色的内部状态 (`game_state`)，包括好感度 (`closeness`)、关系阶段 (`relationship_state`)、情绪 (`mood_today`)、无聊度 (`boredom_level`) 等。
    *   `chat()` 方法: 处理用户输入，调用 LLM API 获取回复，并根据输入和回复更新内部状态和好感度 (`_update_closeness_based_on_input`)。
    *   `_get_contextual_guideline()`: 动态生成指导性 Prompt，根据当前好感度、情绪等调整 AI 的行为。
    *   包含调试命令 (`/debug closeness`) 和特殊剧情触发逻辑 (如好感度100的告白)。
    *   内部调用 `GameStorage` 进行存档和读档。
*   **`Character_Factory.py` (`CharacterFactory` 类):**
    *   负责根据 `config/characters/` 下的 YAML 配置文件创建和管理不同的角色对象 (`GalGameAgent` 实例)。
    *   `load_character_configs()`: 加载所有角色配置。
    *   `get_character()`: 获取指定 ID 的角色实例，如果不存在则创建。
    *   `_create_generic_character()`: 创建通用角色（如果非苏糖）。
    *   `_generate_prompt_from_config()`: 如果角色没有专门的 prompt 文件，则根据配置生成。
*   **`Game_Storage.py` (`GameStorage` 类):**
    *   提供简单的游戏存档和读档功能。
    *   `save_game()`: 将包含 `dialogue_history` 和 `game_state` 的字典保存为 JSON 文件到 `saves/` 目录。
    *   `load_game()`: 从 `saves/` 目录加载 JSON 存档文件。
*   **`achievement_system.py` (`AchievementSystem`, `Achievement` 类):**
    *   定义 `Achievement` 类来表示单个成就的结构（ID, 名称, 描述, 条件, 奖励等）。
    *   `AchievementSystem` 类管理所有成就：
        *   `_setup_db()`: 在 `data/dialogues.db` 中创建 `achievements` (成就定义) 和 `player_achievements` (玩家进度) 表。
        *   `_load_achievements()`: 从数据库加载成就定义和玩家进度。如果数据库为空，则调用 `_initialize_default_achievements()` 初始化预设成就。
        *   `check_achievements()`: **核心方法**，根据传入的 `game_manager` 状态检查是否有成就达成。
        *   `_save_unlocked_achievements()`: 将新解锁的成就状态更新回数据库。
        *   提供获取成就列表、通知等辅助方法。
*   **`web_start.py` / `start_web.bat`:** 用于启动 Flask Web 应用 (`web_app/app.py`)。
*   **`main.py` / `game/main.py` / `game/main_modernized.py`:** 命令行版本游戏的入口点。通常会实例化 `GameManager` 并启动游戏循环。
*   **`.env` / `.env.example`:** 存储环境变量，特别是 OpenAI API Key (`DEEPSEEK_API_KEY` 在代码中被查找，说明可能使用 DeepSeek 或兼容 OpenAI 接口的模型)。
*   **`sutang_prompt.txt` / `prompts/*.txt`:** 定义 AI 角色的核心设定、背景故事和行为准则，供 `GalGameAgent` 加载。

### 4.2 `game/` 目录

*   **`game_manager.py` (`GameManager` 类):**
    *   **项目核心协调器。**
    *   `__init__()`: 初始化所有子系统，包括 `AffectionManager`, `AffectionSystem`, `CharacterFactory`, `SceneManager`, `AchievementSystem`, `DialogueSystem`, NLP 引擎，加载配置，设置初始游戏状态、时间和场景。
    *   `_init_*()` 方法: 初始化场景数据、剧情触发点、游戏状态、角色状态。
    *   `_register_affection_systems()`: 将需要同步好感度的模块注册到 `AffectionManager`。
    *   `sync_affection_values()`: 调用 `AffectionManager` 来同步所有注册系统的好感度值。
    *   `process_dialogue()`: (可能由 `DialogueSystem` 调用或内部处理) 处理对话逻辑的核心流程，可能包括调用角色 AI、更新好感度、检查成就、推进时间等。
    *   `check_storyline_triggers()`: 根据好感度等条件检查是否触发关键剧情点。
    *   `handle_player_action()`: 处理玩家的非对话动作（如移动、查看状态等）。
    *   管理游戏时间 (`current_date`, `current_time`, 时间段推进)。
    *   管理当前场景 (`current_scene`) 和场景切换逻辑。
    *   包含好感度 (`closeness`)、红牌警告 (`red_flags`)、连续正负反馈计数等游戏状态变量。
*   **`dialogue_system.py` (`DialogueSystem` 类):**
    *   负责处理用户输入的对话，并将其传递给当前激活的角色 AI (`GalGameAgent`)。
    *   可能包含解析特殊命令（如 `/save`, `/load`）的逻辑。
    *   与 `GameManager` 交互以获取当前状态（如角色、场景）并更新状态（如对话计数）。
*   **`affection_manager.py` (`AffectionManager` 类):**
    *   用于**统一管理和同步**不同模块中的好感度值。
    *   `register_system()`: 允许其他模块 (如 `GameManager` 的 `game_state`, `agent` 的 `game_state`, `AffectionSystem` 等) 注册其好感度相关的 getter 和 setter 方法。
    *   `set_affection()`: 设置一个新的好感度值，并自动更新所有已注册系统的对应值。
    *   `get_affection()`: 获取当前统一的好感度值。

### 4.3 `core/` 目录

*   **`affection_system.py` (`AffectionSystem` 类):**
    *   可能包含更底层的、通用的好感度计算规则和逻辑。
    *   可能与 `core/nlp_engine.py` 结合，根据对话内容分析情感倾向来调整好感度。
    *   (注意：`game/affection_manager.py` 负责同步，`core/affection_system.py` 可能负责计算细节)
*   **`nlp_engine.py` (`NaturalLanguageProcessor` 类):**
    *   提供自然语言处理功能。
    *   `__init__()`: 加载 `data/keyword_groups.json` 用于关键词分析。
    *   可能包含意图识别、情感分析、关键词提取等功能，供 `AffectionSystem` 或 `DialogueSystem` 使用。
*   **`scene_manager.py` (`SceneManager` 类):**
    *   管理游戏中的场景（地点）。
    *   可能包含场景列表、场景间的连接关系、进入特定场景的条件（如时间、好感度）。
    *   处理场景切换逻辑。

### 4.4 `web_app/` 目录

*   **`app.py`:**
    *   基于 Flask 的 Web 应用后端。
    *   `load_env_file()`: 从 `.env` 加载环境变量 (API Key)。
    *   创建 Flask app 实例，设置 `secret_key` 用于 session。
    *   **全局实例化 `GameManager` (`game_agent`)** 来处理游戏逻辑。
    *   定义路由 (Routes) 和视图函数 (View Functions):
        *   `/`: 渲染主页 (`index.html`)。
        *   `/api/start_game` (POST): 初始化或重置游戏状态，返回初始介绍文本和状态。
        *   `/api/chat` (POST): 接收用户聊天消息，调用 `game_agent.chat()` 处理，返回 AI 回复和更新后的游戏状态。包含详细的错误处理。
        *   `/api/save` (POST): 调用 `game_agent.save()` 保存游戏。
        *   `/api/load` (POST): 调用 `game_agent.load()` 加载游戏。
        *   `/api/get_saves` (GET): 列出 `saves/` 目录下的存档信息。
    *   使用 Flask session 来跟踪用户会话状态 (如 `game_started`)。
*   **`static/`:** 存放 CSS, JavaScript, 图片等前端静态资源。
*   **`templates/index.html`:** Web 界面的 HTML 结构，使用 Jinja2 模板引擎渲染动态内容（如对话历史、游戏状态）。

## 5. 核心系统详解

### 5.1 游戏流程 (推测)

**命令行版本:**

1.  `main.py` (或类似入口) 启动。
2.  实例化 `GameManager`。
3.  `GameManager` 初始化所有子系统 (角色、场景、状态等)。
4.  进入主游戏循环：
    *   显示当前场景和角色信息。
    *   提示用户输入。
    *   `DialogueSystem` 或 `GameManager` 接收用户输入。
    *   如果是特殊命令 (`/save`, `/load`, `/status`)，执行相应操作。
    *   如果是对话，调用 `GameManager` 的处理逻辑 (可能委托给 `DialogueSystem`)。
    *   调用当前角色 (`GalGameAgent`) 的 `chat()` 方法。
    *   `GalGameAgent.chat()`:
        *   更新对话历史。
        *   调用 LLM API 获取回复。
        *   根据用户输入和 AI 回复，更新内部状态和好感度。
    *   `GameManager` 获取 AI 回复和更新后的状态。
    *   `GameManager` 调用 `AffectionManager.sync_affection_values()` 同步好感度。
    *   `GameManager` 调用 `AchievementSystem.check_achievements()` 检查成就。
    *   `GameManager` 更新游戏时间、场景等状态。
    *   显示 AI 回复和游戏状态更新。
    *   检查游戏结束条件 (好感度 <= 0 或 >= 100 触发结局)。
    *   重复循环。

**Web 版本:**

1.  `web_start.py` 或 `start_web.bat` 启动 `web_app/app.py`。
2.  Flask 应用运行，全局实例化 `GameManager`。
3.  用户访问 `/`，加载 `index.html`。
4.  前端 JS 发送 POST 请求到 `/api/start_game`。
5.  `start_game` 视图函数调用 `game_agent.reset_game()` (或类似方法)，返回初始信息。
6.  前端显示初始界面和苏糖的第一句话。
7.  用户在输入框输入消息，点击发送。
8.  前端 JS 发送 POST 请求到 `/api/chat`，包含用户消息。
9.  `chat` 视图函数调用 `game_agent.chat()` (这里 `GameManager` 可能需要一个 `chat` 接口，或者直接调用 `DialogueSystem` 或 `GalGameAgent` 的方法)。
10. 后端处理逻辑类似命令行版本中的对话处理步骤 (调用 AI, 更新状态, 同步好感度, 检查成就)。
11. `chat` 视图函数将 AI 回复和更新后的 `game_state` 以 JSON 格式返回给前端。
12. 前端 JS 接收响应，更新对话框、状态显示区域。
13. 用户进行保存/加载操作时，前端 JS 调用 `/api/save`, `/api/load`, `/api/get_saves` 接口。

### 5.2 好感度与关系

*   好感度 (`closeness`) 是核心数值，范围 0-100，初始为 30。
*   存储在多个地方 (`GameManager.game_state`, `GalGameAgent.game_state`, `AffectionSystem`)，通过 `AffectionManager` 同步。
*   `GalGameAgent._update_closeness_based_on_input()`: 根据用户输入的长度、是否包含特定关键词 (如烘焙)、是否重复、是否礼貌等因素调整好感度。使用了 `nlp_processor` 进行分析。
*   `GalGameAgent._update_relationship_state()`: 根据好感度阈值更新关系状态 (`stranger`, `acquaintance`, `friend`, `close_friend`, `crush`)。
*   关系状态会影响 `GalGameAgent._get_contextual_guideline()` 生成的 Prompt，进而影响 AI 的行为和语气。
*   好感度也直接影响成就 (`AchievementSystem`) 和剧情触发 (`GameManager.check_storyline_triggers`)。

### 5.3 对话生成 (AI 交互)

*   `GalGameAgent.chat()` 是核心交互方法。
*   维护一个 `dialogue_history` 列表，包含 `system` (Prompt), `user`, `assistant` 角色的消息。
*   在调用 API 前，会更新 `system` Prompt (`_get_contextual_guideline()`) 以反映当前状态。
*   使用 `openai.OpenAI()` 客户端 (或兼容客户端) 与 LLM API 通信，发送 `dialogue_history`。
*   从 API 获取 `assistant` 的回复。
*   对回复进行处理，更新 `dialogue_history`。
*   包含对无聊度 (`boredom_level`) 和尊重度 (`respect_level`) 的管理，这些状态会影响 Prompt 和 AI 反应。
*   包含预设的告白剧情逻辑 (好感度 >= 100)。

### 5.4 成就系统

*   成就定义存储在数据库 `achievements` 表中，包含 ID, 名称, 描述, 条件 (JSON格式), 奖励等。
*   玩家进度存储在 `player_achievements` 表中，记录是否解锁、解锁时间等。
*   `AchievementSystem.check_achievements()` 在每次交互后被 `GameManager` 调用。
*   该方法遍历所有未解锁的成就，根据 `game_manager` 提供的当前游戏状态 (好感度、对话次数、当前场景、触发的事件等) 检查其 `requirements` 是否满足。
*   如果满足，则将成就标记为已解锁，并调用 `_save_unlocked_achievements()` 更新数据库。
*   可能会返回解锁通知给 `GameManager` 显示。

## 6. 安装与运行

### 6.1 环境设置

1.  **安装 Python:** 确保安装了 Python 3 (推荐 3.8+)。
2.  **创建虚拟环境:**
    ```bash
    python -m venv web_venv
    ```
3.  **激活虚拟环境:**
    *   Windows: `web_venv\Scripts\activate`
    *   macOS/Linux: `source web_venv/bin/activate`
4.  **安装依赖:**
    *   **基础依赖:** (可能需要查看 `install_deps.py` 或手动整理)
        ```bash
        pip install pyyaml openai python-dotenv flask jieba
        ```
    *   **Web 应用依赖:**
        ```bash
        pip install -r web_app/requirements.txt # 通常包含 Flask
        ```
    *   **或者使用提供的安装脚本:**
        *   Windows: 运行 `install_windows.bat` 或 `python install_and_run.py`。
        *   其他系统: 可能需要适配脚本或手动安装。
5.  **配置 API Key:**
    *   复制 `.env.example` 为 `.env`。
    *   在 `.env` 文件中填入你的 OpenAI API Key 或 DeepSeek API Key 到 `DEEPSEEK_API_KEY=` 后面。

### 6.2 运行游戏

*   **命令行版本:**
    ```bash
    python main.py # 或者 python game/main.py
    ```
*   **Web 版本:**
    ```bash
    python web_start.py
    # 或者直接运行 Flask 开发服务器 (确保在 web_app 目录下或配置好 Python 路径)
    # flask --app web_app.app run --host=0.0.0.0 --port=5000
    # 或者运行 start_web.bat (Windows)
    ```
    然后在浏览器中打开 `http://localhost:5000` (或对应的 IP 和端口)。

## 7. 开发者建议

*   **理解 GameManager:** 这是协调中心，大部分游戏流程和状态变化都与之相关。
*   **理解 GalGameAgent:** 这是角色 AI 的核心，理解其状态管理、Prompt 生成和好感度更新逻辑至关重要。
*   **好感度同步:** 注意 `AffectionManager` 的作用，确保好感度在各模块间正确同步。
*   **配置驱动:** 许多行为 (角色设定、成就条件、NLP关键词) 是通过配置文件 (YAML, JSON, TXT) 控制的，修改配置可以快速调整游戏内容。
*   **日志:** 利用代码中已有的 `logging` 来跟踪调试。
*   **测试:** `api_test.py`, `simple_test.py` 可作为编写新测试的起点。
*   **版本控制:** 遵循良好的 Git 实践。

## 8. 未来可扩展方向

*   **多角色支持:** `CharacterFactory` 已奠定基础，可以方便地添加更多可攻略角色。
*   **更复杂的场景交互:** 增加场景中的对象、事件和更丰富的非对话交互。
*   **道具系统:** 引入可以影响对话或好感度的道具。
*   **UI/UX 改进:** 优化 Web 界面的视觉效果和用户体验。
*   **更精细的 NLP:** 使用更强大的 NLP 技术进行意图识别、情感分析，使 AI 反应更智能。
*   **剧情编辑器:** 开发工具让非程序员也能方便地编辑剧情、对话和成就。

---

希望这份文档能帮助您和其他开发者更好地理解和维护 "绿园中学物语" 项目！ 