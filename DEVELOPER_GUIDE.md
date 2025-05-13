# 绿园中学物语 - 开发者文档

## 1. 项目概述

**绿园中学物语** 是一款基于 Python 开发的恋爱模拟游戏 (Dating Sim)。玩家通过与AI控制的角色（主要是"苏糖"）进行对话互动，培养感情，解锁剧情，并最终达成不同的游戏结局。

游戏的核心机制包括：

*   **自然语言对话驱动:** 玩家通过输入自然语言与 AI 控制的角色进行交流。
*   **动态好感度系统:** 玩家的对话选择、内容质量、行为方式都会影响与角色的好感度。
*   **多维度情感状态:** AI角色不仅有好感度，还有情绪、耐心等内部状态，影响其行为和反应。
*   **关系阶段与剧情:** 好感度累积会推动关系进入不同阶段，并触发特定剧情事件。
*   **场景与时间流逝:** 游戏包含多个场景，对话和行动会推进游戏内的时间。
*   **主题系统:** 对话围绕特定主题展开，主题的可用性受好感度等因素影响。
*   **成就系统:** 记录并奖励玩家在游戏中达成的特定里程碑或特殊行为。
*   **多结局:** 基于玩家与角色的最终关系状态和关键选择，导向不同的游戏结局。

项目提供了**命令行界面 (CLI)** 和 **Web 图形用户界面 (GUI)** 两种体验方式。

**技术栈:**

*   **后端:** Python 3
*   **AI对话核心:** `Su_Tang.py` 中的 `GalGameAgent` 类，可能依赖外部大语言模型 (LLM) API (如 DeepSeek 或 OpenAI 兼容接口)。
*   **Web框架 (Web版):** Flask
*   **自然语言处理 (NLP):** `jieba` (分词), `SnowNLP` (情感分析), 自定义关键词提取。
*   **数据存储:**
    *   游戏存档: JSON 文件 (`saves/`)，通过 `Game_Storage.py` 管理。
    *   成就与对话记录: SQLite 数据库 (`data/dialogues.db`)，通过 `achievement_system.py` 和 `Game_Storage.py` (间接) 管理。
*   **配置:** YAML 文件 (`config/`)，用于角色、场景、剧情等配置。
*   **核心依赖库:** `openai` (或兼容库), `pyyaml`, `flask`, `jieba`, `SnowNLP`, `colorama`, `logging`.

## 2. 高层架构

项目采用模块化设计，主要组件协同工作以实现完整的游戏体验：

1.  **游戏管理器 (`game.managers.game_manager_new.GameManager`):** 游戏的中央协调器。负责初始化和管理所有核心子系统，处理游戏主循环，响应玩家输入，更新游戏状态，并协调各模块间的数据同步。
2.  **角色AI代理 (`Su_Tang.GalGameAgent`):** 代表游戏中的AI角色（如苏糖）。负责处理具体角色的对话逻辑（调用LLM）、管理角色内部状态（好感度、话题、情绪等）、根据玩家输入和自身状态生成回应。
3.  **角色工厂 (`Character_Factory.CharacterFactory`):** 负责根据配置文件创建和管理角色实例 (`GalGameAgent`)。
4.  **对话系统 (`game.dialogue_system.DialogueSystem`):** 处理玩家输入到AI回复的完整对话流程，包括调用AI代理、更新好感度、检查成就、触发剧情、处理场景转换等。
5.  **核心情感系统 (`core.affection.system.AffectionSystem`):** 底层好感度计算引擎。评估对话内容（基于NLP分析结果、社交风险、角色情绪等），计算好感度变化。
    *   **关键词分析器 (`core.affection.keyword_analyzer.KeywordAnalyzer`):** 从对话中提取关键词，识别敏感内容。
    *   **对话评估器 (`core.affection.dialogue_evaluator.DialogueEvaluator`):** 从多个维度评估对话质量（如礼貌、趣味性、上下文关联性）。
6.  **自然语言处理器 (`core.nlp.processor.NaturalLanguageProcessor`):** 提供文本分析功能，包括分词、关键词提取、情感分析。
7.  **场景管理器 (`core.scene.manager.SceneManager`):** 管理游戏中的场景数据、场景转换逻辑和游戏内时间的推进。
8.  **主题管理器 (`game.managers.topic_manager.TopicManager`):** 管理对话主题，包括主题的解锁、持续时间、特殊主题（如糖豆）等。
9.  **剧情管理器 (`game.managers.storyline_manager.StorylineManager`):** 管理游戏中的主线和支线剧情，根据条件（如好感度）触发剧情事件。
10. **成就系统 (`achievement_system.AchievementSystem`):** 管理游戏成就的定义、解锁条件的检查、玩家成就数据的存储和读取。
11. **存档系统 (`Game_Storage.GameStorage`):** 负责将游戏进度（包括角色状态、对话历史等）保存到JSON文件，并从中加载。也负责对话日志的数据库记录。
12. **Web应用 (Flask):** (`web_app/app.py`) 提供Web GUI，通过API与后端游戏逻辑交互。
13. **配置加载与管理:** 各模块从YAML或JSON配置文件中读取设定。

```mermaid
graph TD
    subgraph "用户接口 (User Interface)"
        CLI["命令行界面 (game/main.py)"]
        WebApp["Web界面 (web_app/app.py)"]
    end

    subgraph "游戏核心逻辑 (Game Core Logic)"
        GM["GameManager (game.managers.game_manager_new)"]
        DS["DialogueSystem (game.dialogue_system)"]
        Agent["GalGameAgent (Su_Tang.GalGameAgent)"]
        CF["CharacterFactory (Character_Factory)"]
    end

    subgraph "核心子系统 (Core Subsystems)"
        AffSys["AffectionSystem (core.affection.system)"]
        NLP["NLP Processor (core.nlp.processor)"]
        SceneMgr["SceneManager (core.scene.manager)"]
        TopicMgr["TopicManager (game.managers.topic_manager)"]
        StoryMgr["StorylineManager (game.managers.storyline_manager)"]
        AchSys["AchievementSystem (achievement_system)"]
        GS["GameStorage (Game_Storage)"]
    end
    
    subgraph "情感计算辅助模块"
        KA["KeywordAnalyzer (core.affection.keyword_analyzer)"]
        DE["DialogueEvaluator (core.affection.dialogue_evaluator)"]
    end

    subgraph "数据与配置 (Data & Config)"
        CharCfg["角色配置 (config/characters/*.yaml)"]
        GameCfg["游戏配置 (config/*.yaml/json)"]
        Prompts["角色提示 (prompts/*.txt, sutang_prompt.txt)"]
        Saves["存档 (saves/*.json)"]
        DB["数据库 (data/dialogues.db)"]
        Env[".env (API Keys)"]
    end

    subgraph "外部服务 (External Services)"
        LLM["大语言模型 API (e.g., DeepSeek)"]
    end

    CLI --> GM
    WebApp -- HTTP API --> GM

    GM --> DS
    GM --> CF
    GM --> SceneMgr
    GM --> TopicMgr
    GM --> StoryMgr
    GM --> AchSys
    GM --> AffSys # GameManager 可能直接初始化 AffectionSystem
    GM --> GS # GameManager 可能直接进行存取档操作或委托

    DS --> Agent
    DS --> AffSys # DialogueSystem 调用 AffectionSystem 进行评估
    DS --> AchSys # 检查成就
    DS --> SceneMgr # 请求场景分析
    DS --> StoryMgr # 检查剧情触发
    
    CF --> Agent
    Agent -- 调用 --> LLM
    Agent --> GS # Agent 内部的存读档
    Agent <-- Prompts
    Agent <-- CharCfg
    Agent --> TopicMgr # Agent 可能更新话题状态

    AffSys --> KA
    AffSys --> DE
    AffSys --> NLP # AffectionSystem 使用 NLP 结果

    AchSys --> DB
    GS --> Saves
    GS --> DB # GameStorage 也负责对话日志

    GM <-- GameCfg
    Agent <-- Env # Agent 加载 API Key
```

## 3. 目录结构 (校正后)

```
Su_Tang/
├── .vscode/                # VSCode 编辑器配置
├── assets/                 # 静态资源 (Web版使用)
│   └── images/
├── config/                 # 配置文件
│   ├── characters/         # 角色YAML配置 (e.g., Su_Tang.yaml)
│   ├── affection_config.json # 情感系统配置
│   ├── game_config.yaml    # 游戏全局配置
│   └── scene_config.yaml   # 场景配置
├── core/                   # 核心引擎模块
│   ├── affection/
│   │   ├── dialogue_evaluator.py # 对话质量评估器
│   │   ├── __init__.py
│   │   ├── keyword_analyzer.py   # 关键词分析器
│   │   └── system.py             # 核心情感计算系统 (AffectionSystem)
│   ├── nlp/
│   │   ├── __init__.py
│   │   └── processor.py          # 自然语言处理器 (NaturalLanguageProcessor)
│   ├── scene/
│   │   ├── __init__.py
│   │   └── manager.py            # 场景管理器 (SceneManager)
│   └── __init__.py
├── data/                   # 游戏数据
│   ├── dialogues.db        # SQLite数据库 (成就, 对话日志)
│   └── keyword_groups.json # NLP关键词分组
├── game/                   # 游戏逻辑实现
│   ├── managers/
│   │   ├── game_manager_new.py # 新版游戏管理器 (GameManager)
│   │   ├── __init__.py
│   │   ├── scene_manager.py    # (实际是 core.scene.manager 的引用)
│   │   ├── storyline_manager.py# 剧情管理器
│   │   └── topic_manager.py      # 主题管理器
│   ├── dialogue_system.py  # 对话流程系统
│   └── main.py             # 命令行游戏主入口
├── prompts/                # AI 角色提示文件
│   ├── Su_Tang/            # 苏糖特定提示 (如果更复杂)
│   └── sutang_prompt.txt     # 苏糖主提示
├── saves/                  # 游戏存档 (JSON格式)
│   └── metadata.json       # 存档元数据
├── web_app/                # Web应用 (Flask)
│   ├── static/             # Web静态资源 (CSS, JS, images)
│   ├── templates/          # HTML模板 (index.html)
│   ├── __init__.py
│   └── app.py              # Flask应用主文件
├── web_venv/               # Python虚拟环境 (建议)
├── .env                    # 环境变量 (API Key等)
├── .env.example            # 环境变量模板
├── .gitignore
├── achievement_system.py   # 成就系统
├── api_test.py             # API测试脚本
├── Character_Factory.py    # 角色工厂
├── Game_Storage.py         # 游戏存档/读档及日志记录
├── install.py              # (旧) 安装脚本
├── install_and_run.py      # (旧) 安装并运行脚本
├── install_deps.py         # 依赖安装脚本
├── install_windows.bat     # Windows安装批处理
├── LICENSE
├── main.py                 # 项目根目录的游戏启动入口 (通常调用 game.main)
├── README.md               # 项目说明
├── requirements.txt        # Python依赖列表
├── Su_Tang.py              # 苏糖AI代理 (GalGameAgent 类)
├── web_start.py            # Web应用启动脚本
└── start_web.bat           # Windows下Web应用启动批处理
```

## 4. 关键文件与模块详解

### 4.1 根目录及主要Python文件

*   **`Su_Tang.py` (`GalGameAgent` 类):**
    *   **核心AI角色代理实现。**
    *   `__init__()`: 初始化角色，加载角色配置 (`CHARACTER_DETAILS`，通常来自`Character_Factory`)，设置初始状态 (好感度 `closeness`, 对话主题 `topics`, 情绪 `mood_today` 等)，加载对话历史，设置LLM API密钥。
    *   `_init_new_game()`: 用于新游戏开始时或重置角色状态。
    *   `chat()`: **核心对话方法。** 接收用户输入，构建包含历史和当前上下文的prompt，调用LLM API (`self.client.chat.completions.create`) 获取AI回复。之后更新内部状态，如对话历史、无聊度、尊重等级。
    *   `_get_contextual_guideline()`: 动态生成或选择指导性上下文信息，根据当前好感度、情绪、话题等调整AI的行为和回复风格。这是实现角色动态性的关键。
    *   `_update_closeness_based_on_input()`: (此方法在 `AffectionSystem` 中被更复杂逻辑取代) 原用于根据简单规则（如输入长度、关键词）调整好感度。
    *   `_update_relationship_state()`: 根据好感度阈值更新关系阶段 (`stranger`, `acquaintance`, `friend`, `close_friend`, `crush`, `love`, `soulmate`)。
    *   `save()` / `load()`: 调用 `GameStorage` 实例进行角色状态的存档和读档。
    *   管理与特定角色相关的数据，如已谈论话题、好感度阶段等。

*   **`Character_Factory.py` (`CharacterFactory` 类):**
    *   负责从 `config/characters/*.yaml` 配置文件中加载角色定义，并创建相应的 `GalGameAgent` 实例。
    *   `load_character_configs()`: 加载所有角色配置。
    *   `get_character()`: 按角色ID获取角色实例，如果尚不存在则创建。
    *   `_create_generic_character()`: 创建通用角色（非默认的苏糖时）。
    *   `_generate_prompt_from_config()`: 若角色无独立prompt文件，则根据配置信息生成基础prompt。

*   **`Game_Storage.py` (`GameStorage` 类):**
    *   提供游戏存档和读档功能，支持多个存档槽位。
    *   `save_game()`: 将游戏状态 (通常是 `GalGameAgent` 的状态和对话历史) 保存为JSON文件到 `saves/` 目录。包含版本号和时间戳。
    *   `load_game()`: 从 `saves/` 目录加载JSON存档文件。
    *   `get_save_slots()`: 列出所有可用的存档槽位及其元数据。
    *   `log_dialogue()`: 将每一轮对话（玩家输入、AI回复、好感度变化、场景等）记录到 `data/dialogues.db` 数据库的 `dialogue_history` 表。

*   **`achievement_system.py` (`Achievement` 类, `AchievementSystem` 类):**
    *   `Achievement`: 数据类，表示单个成就的结构 (ID, 名称, 描述, 解锁条件-JSON, 奖励, 图标, 是否隐藏等)。
    *   `AchievementSystem`:
        *   `__init__()`: 初始化，连接到 `data/dialogues.db` 数据库。
        *   `_setup_db()`: 创建 `achievements` (成就定义) 和 `player_achievements` (玩家已解锁成就及进度) 表。
        *   `_load_achievements()`: 从数据库加载所有成就定义和玩家的解锁状态。若数据库为空，则调用 `_initialize_default_achievements()` 添加预设成就。
        *   `_initialize_default_achievements()`: 定义并存储一组初始成就到数据库。
        *   `check_achievements()`: **核心检查逻辑。** 根据传入的 `GameManager` 提供的当前游戏状态 (好感度, 对话次数, 访问场景, 特定事件等)，遍历检查各项成就是否满足解锁条件。
        *   `_save_unlocked_achievements()`: 将新解锁的成就及其解锁时间更新到 `player_achievements` 表。
        *   提供获取成就通知文本、所有成就列表、特定成就进度等辅助方法。

*   **`main.py` (根目录):** 通常是项目的最顶层启动脚本，它会调用 `game.main.main()`。
*   **`.env`:** 存储敏感配置，如 `DEEPSEEK_API_KEY` (或其他LLM API密钥)。

### 4.2 `game/` 目录 - 游戏逻辑实现

*   **`main.py` (`game/main.py`):**
    *   命令行版本游戏的主入口和主循环。
    *   `main()` 函数实例化 `GameManager`。
    *  `GameManager` 初始化所有子系统 (NLP, 情感, 场景, 主题, 剧情, 成就, 角色, 对话系统)。
    *  打印游戏介绍。
    *  进入主循环：
        a.  显示当前场景、日期、时间、角色状态提示。
        b.  等待用户输入。
        c.  `handle_command()` 解析输入：
            *   如果是特殊命令 (`/exit`, `/save <slot>`, `/load <slot>`, `/status`, `/history`, `/tips`, `/debug affection` 等)，执行相应操作 (调用 `GameManager` 的方法)。
            *   如果是普通对话，调用 `game_manager.chat(user_input)`，实际由 `DialogueSystem.process_dialogue()` 处理。
        d.  `DialogueSystem.process_dialogue()` 执行完整流程（见 4.2 节描述），包括：
            *   调用 `GalGameAgent.chat()` 获取LLM回复。
            *   调用 `AffectionSystem.process_dialogue()` 计算好感度。
            *   检查成就、剧情、场景切换。
            *   记录日志、自动保存。
        e.  `game/main.py` 接收并显示 `DialogueSystem` 返回的最终AI回复和游戏状态更新。
        f.  检查游戏是否结束 (如好感度过低导致 `GameManager` 触发结局)。
        g.  重复循环。

*   **`managers/game_manager_new.py` (`GameManager` 类):**
    *   **游戏总指挥，协调所有游戏模块和状态。**
    *   `__init__()`:
        *   加载游戏配置 (`game_config.yaml`, `affection_config.json` 等)。
        *   初始化核心系统：`NaturalLanguageProcessor`, `AffectionSystem`, `SceneManager`, `TopicManager`, `StorylineManager`, `AchievementSystem`。
        *   初始化 `CharacterFactory` 并获取默认角色 (苏糖)。
        *   初始化 `DialogueSystem`，并将自身 (`GameManager`) 实例传入。
        *   设置初始游戏状态：当前日期、时间、场景、好感度等。
        *   注册需要同步好感度的系统到 `AffectionSystem` 的内部列表中（情感系统现在自行管理同步）。
    *   `load_config()`: 加载各类配置文件。
    *   `_initialize_systems()`: 统一初始化各个子系统。
    *   `start_new_game()`: 开始新游戏或重置游戏到初始状态。
    *   `chat()`: **核心交互接口。** 接收玩家输入，通常委托给 `DialogueSystem.process_dialogue()` 进行处理。
    *   `process_dialogue()`: (此方法主要逻辑已移至 `DialogueSystem`) 原本处理对话，调用角色AI，更新状态等。
    *   `handle_player_action()`: 处理非对话的玩家行为。
    *   `_handle_scene_change()`: 在场景变化时更新状态和显示。
    *   `show_ending()`, `show_social_status()`, `view_dialogue_history()`: 提供游戏信息展示功能。
    *   `save()` / `load()`: 调用角色代理和自身状态的保存/加载。
    *   `reset_game()`: 重置整个游戏状态。
    *   管理全局游戏状态变量，如 `current_date`, `current_time`, `current_scene`, `game_state` 字典 (包含 `closeness`, `conversation_count` 等)。

*   **`dialogue_system.py` (`DialogueSystem` 类):**
    *   `__init__()`: 持有 `GameManager` 的引用。
    *   `process_dialogue()`: **核心对话处理流程。**
        1.  获取AI回复 (`game_manager.agent.chat(user_input)`)。
        2.  调用情感系统 (`game_manager.affection.process_dialogue()`) 处理玩家输入和AI历史，计算好感度变化。
        3.  更新游戏状态中的好感度记录和连续积极/消极反馈计数。
        4.  检查游戏结束条件 (好感度 <= 0 或严重侮辱)。
        5.  生成好感度变化反馈信息 (`_generate_affection_info()`)。
        6.  检查并触发剧情 (`game_manager.storyline_manager.check_storyline_triggers()`)。
        7.  分析对话并处理场景切换 (`game_manager.scene_manager.analyze_conversation()`)。
        8.  更新对话计数。
        9.  检查并处理成就解锁 (`game_manager.achievement_system.check_achievements()`)，包括应用奖励。
        10. 记录对话到数据库 (`game_manager.agent.storage.log_dialogue()`)。
        11. 随机显示提示 (`_get_random_tip()`)。
        12. 执行自动保存。
        13. 返回最终的AI回复给上层 (通常是 `game.main` 或 `web_app.app`)。
    *   `_generate_affection_info()`: 生成详细的好感度变化反馈文本，调试模式下信息更丰富。
    *   `_get_random_tip()`: 从 `GameManager` 中获取随机提示。
    *   `_check_for_severe_insults()`: 检测输入中的严重侮辱性词汇。

*   **`managers/topic_manager.py` (`TopicManager` 类):**
    *   `__init__()`: 初始化话题数据 (通常从配置加载)。
    *   `get_available_topics()`: 根据当前好感度、已谈论话题等条件，返回当前可用的对话主题。
    *   管理特殊主题如"糖豆话题"的逻辑 (`is_sugar_bean_topic`, `should_show_sugar_bean`)。
    *   提供"约会技巧"提示 (`get_next_tip`)。
    *   管理话题持续时间。
    *   管理"兴趣话题" (`get_interest_topics`)。
    *   `update_affection()`: 接收好感度更新，可能会影响话题解锁。

*   **`managers/storyline_manager.py` (`StorylineManager` 类):**
    *   `__init__()`: 初始化剧情数据 (通常从配置加载剧情触发条件和内容)。
    *   `check_storyline_triggers()`: 根据当前好感度等游戏状态，检查是否有剧情被触发。如果触发，返回剧情文本。
    *   `is_storyline_triggered()`: 查询特定剧情是否已被触发。
    *   管理已触发剧情列表。
    *   支持调试模式 (`toggle_debug_mode`)。
    *   `update_affection()`: 接收好感度更新，用于检查新的剧情触发。

*   **`managers/__init__.py`**: 聚合导入 `GameManager`, `SceneManager`, `TopicManager`, `StorylineManager`。
*   **`managers/scene_manager.py`**: 这是一个简单的重定向，实际导入并重命名了 `core.scene.manager.SceneManager`。

### 4.3 `core/` 目录 - 核心引擎模块

*   **`affection/system.py` (`AffectionSystem` 类):**
    *   **复杂的好感度计算和关系管理引擎。**
    *   `__init__()`: 初始化，加载好感度配置 (`affection_config.json`)，实例化 `KeywordAnalyzer` 和 `DialogueEvaluator`。
    *   `register_system()`: 允许其他系统注册回调，以便在好感度更新时同步。
    *   `update_value()`: 更新好感度值，并通知所有已注册的系统。
    *   `process_dialogue()`: **核心好感度评估方法。**
        1.  接收玩家当前输入和AI的对话历史。
        2.  使用 `KeywordAnalyzer` 分析输入中的关键词、话题、不当内容。
        3.  使用 `DialogueEvaluator` 从多个维度（绅士风度、无聊度、上下文相关性、输入质量）评估玩家的输入。
        4.  综合考虑NLP分析（情感倾向）、关键词、对话评估结果、角色当前情绪 (`mood`)、耐心 (`patience`)、社交风险 (`_evaluate_social_risk`) 等多种因素，通过一套复杂的加权和调整逻辑，计算出好感度变化 (`delta`)。
        5.  更新内部好感度、情绪、耐心等状态。
        6.  处理特殊事件如"告白"。
        7.  返回包含当前好感度、变化量和详细调试信息的字典。
    *   `_evaluate_social_risk()`: 评估对话中的社交风险等级。
    *   `load_config()`: 加载情感配置文件。
    *   `handle_event()`: 处理特定情感事件（如 `AffectionEvent.CONFESSION`）。
    *   `check_ending()`: 检查是否达到特定情感结局的条件。
    *   `_get_current_phase()`: 根据好感度获取当前的关系阶段。

*   **`affection/keyword_analyzer.py` (`KeywordAnalyzer` 类):**
    *   `__init__()`: 加载关键词类别（积极、消极、兴趣等）和不当内容模式。
    *   `extract_topics()`: 从文本中提取预定义的话题。
    *   `check_inappropriate()`: 使用正则表达式检查文本中是否包含不雅词汇（侮辱、性暗示、不尊重）。
    *   `get_keyword_category()`: 判断关键词所属的类别。
    *   `analyze_keywords()`: 分析文本中的关键词，返回其类别、频率等信息，供 `AffectionSystem` 使用。

*   **`affection/dialogue_evaluator.py` (`DialogueEvaluator` 类):**
    *   `__init__()`: 初始化评估参数。
    *   `evaluate_gentlemanly()`: 评估输入的礼貌和尊重程度。
    *   `evaluate_boringness()`: 评估输入的无聊程度（基于长度、信息量、重复性等），在高好感度时容忍度更高。
    *   `evaluate_context_relevance()`: 评估输入与AI上一句话（尤其是提问）的关联性。
    *   `evaluate_input_quality()`: 评估输入的整体质量（长度、多样性、标点、句子复杂度）。
    *   这些评估结果会作为因子输入到 `AffectionSystem` 的好感度计算模型中。

*   **`nlp/processor.py` (`NaturalLanguageProcessor` 类):**
    *   `__init__()`: 初始化 `jieba` (可加载自定义词典) 和 `SnowNLP`。加载 `data/keyword_groups.json` 定义的关键词。
    *   `analyze()`: 对输入文本进行综合分析，返回一个包含分词结果、情感分数 (SnowNLP)、提取到的关键词、上下文连贯性评分的字典。
    *   `_load_keywords()`: 加载关键词及其类别。
    *   `_extract_keywords()`: 从分词结果中提取预定义的关键词。
    *   `_sentiment_analysis()`: 使用 SnowNLP 进行情感分析。
    *   `_context_coherence()`: (可能较简单) 评估与上下文的连贯性。

*   **`scene/manager.py` (`SceneManager` 类):**
    *   `__init__()`: 加载场景数据 (来自 `config/scene_config.yaml`)，包括场景描述、可转换到的场景、转换所需时间等。
    *   `analyze_conversation()`: **核心方法。** 根据当前对话内容 (玩家输入和AI回复)、当前场景、日期和时间，判断是否应该以及可以切换到哪个新场景。
        *   这可能基于对话中提及的特定地点关键词、时间段限制、或特定事件的触发。
    *   `get_scene_info()`: 获取特定场景的详细信息。
    *   `get_possible_transitions()`: 获取当前场景下所有可能的场景转换。
    *   管理游戏内日期和时间的推进，通常与场景转换相关联。例如，从"学校"到"公园"可能会消耗游戏内时间。
    *   `_advance_time()`: 根据场景转换或特定行动来推进游戏时间。

### 4.4 `web_app/` 目录 - Web 应用

*   **`app.py`:**
    *   Flask 应用的入口和核心。
    *   `load_env_file()`: 从 `.env` 加载环境变量 (如API Key)。
    *   创建 Flask app 实例，设置 `secret_key` 用于 session 管理。
    *   **全局实例化 `GameManager` (通常命名为 `game_manager` 或 `agent_manager`)**，这是Web后端与游戏核心逻辑交互的桥梁。
    *   定义 Flask 路由 (Routes) 和视图函数 (View Functions):
        *   `/` 或 `/index`: 渲染主游戏界面 (`index.html`)。
        *   `/api/start_game` (POST): 调用 `game_manager.start_new_game()` 或 `reset_game()`，初始化或重置游戏状态，返回初始介绍文本和游戏状态给前端。
        *   `/api/chat` (POST): 接收前端传来的用户聊天消息，调用 `game_manager.chat(user_input)` 处理，获取AI回复和更新后的游戏状态，以JSON格式返回给前端。包含详细的错误处理。
        *   `/api/save` (POST): 调用 `game_manager.save(slot)` 保存游戏。
        *   `/api/load` (POST): 调用 `game_manager.load(slot)` 加载游戏。
        *   `/api/get_saves` (GET): 调用 `game_manager.agent.storage.get_save_slots()` (或通过 GameManager 封装的方法) 列出存档信息。
        *   其他可能的API接口，如获取状态、成就等。
    *   使用 Flask `session` 来初步跟踪用户会话，但复杂状态主要由 `GameManager` 维护。

*   **`static/`:** 存放 CSS 文件 (`style.css`)、JavaScript 文件 (`script.js`)、图片等前端静态资源。
    *   `script.js` 会处理用户输入、与后端API交互、动态更新页面DOM元素（如对话框、状态显示）。
*   **`templates/index.html`:** Web 界面的主 HTML 结构。使用 Jinja2 模板引擎，但主要内容通常由前端 JavaScript 动态填充。

## 5. 核心系统详解

### 5.1 游戏主循环与交互流程

**命令行版本 (`game/main.py`):**

1.  启动 `game/main.py`。
2.  `main()` 函数实例化 `GameManager`。
3.  `GameManager` 初始化所有子系统 (NLP, 情感, 场景, 主题, 剧情, 成就, 角色, 对话系统)。
4.  打印游戏介绍。
5.  进入主循环：
    a.  显示当前场景、日期、时间、角色状态提示。
    b.  等待用户输入。
    c.  `handle_command()` 解析输入：
        *   如果是特殊命令 (`/exit`, `/save <slot>`, `/load <slot>`, `/status`, `/history`, `/tips`, `/debug affection` 等)，执行相应操作 (调用 `GameManager` 的方法)。
        *   如果是普通对话，调用 `game_manager.chat(user_input)`，实际由 `DialogueSystem.process_dialogue()` 处理。
    d.  `DialogueSystem.process_dialogue()` 执行完整流程（见 4.2 节描述），包括：
        *   调用 `GalGameAgent.chat()` 获取LLM回复。
        *   调用 `AffectionSystem.process_dialogue()` 计算好感度。
        *   检查成就、剧情、场景切换。
        *   记录日志、自动保存。
    e.  `game/main.py` 接收并显示 `DialogueSystem` 返回的最终AI回复和游戏状态更新。
    f.  检查游戏是否结束 (如好感度过低导致 `GameManager` 触发结局)。
    g.  重复循环。

**Web 版本 (`web_app/app.py`):**

1.  运行 `web_start.py` (或 `start_web.bat`) 启动 Flask 开发服务器。
2.  `web_app/app.py` 执行，全局实例化 `GameManager`。
3.  用户在浏览器打开应用 (e.g., `http://localhost:5000`)。
4.  前端 (`static/script.js`) 发送 POST 请求到 `/api/start_game`。
5.  Flask 路由 `/api/start_game` 对应的视图函数调用 `game_manager.start_new_game()`，并将初始游戏数据 (介绍、状态) 以 JSON 形式返回。
6.  前端JS接收数据，渲染初始界面和苏糖的第一句话。
7.  用户在输入框输入消息，点击发送。
8.  前端JS将用户消息通过 POST 请求发送到 `/api/chat`。
9.  Flask 路由 `/api/chat` 对应的视图函数调用 `game_manager.chat(user_input)` (内部委托给 `DialogueSystem`)。
10. 后端 `DialogueSystem` 完成对话处理（同命令行版 d 步骤）。
11. Flask 视图函数将AI回复和更新后的游戏状态 (来自 `GameManager`) 以JSON格式返回给前端。
12. 前端JS接收响应，动态更新对话历史、角色状态显示、好感度条等。
13. 用户点击保存/加载按钮时，前端JS调用对应的 `/api/save`, `/api/load`, `/api/get_saves` 接口，后端 `GameManager` 执行相应操作。

### 5.2 好感度与关系 (`AffectionSystem` 及周边)

*   **核心数值:** `closeness` (好感度) 是关键，通常范围较大 (如0-1000或更高)，并映射到不同的关系阶段。
*   **计算引擎:** `core.affection.system.AffectionSystem` 是好感度计算的核心。
    *   **输入:** 玩家的当前对话输入、AI的对话历史。
    *   **处理步骤 (`process_dialogue`):**
        1.  **NLP分析:** `NaturalLanguageProcessor` 分析玩家输入的情感、关键词。
        2.  **关键词检查:** `KeywordAnalyzer` 检查不当内容、提取对话主题和有特殊情感价值的关键词。
        3.  **对话质量评估:** `DialogueEvaluator` 从礼貌、趣味性、相关性、质量等维度打分。
        4.  **综合计算:** 结合上述分析结果，以及角色当前的情绪 (`mood`)、耐心 (`patience`)、历史互动、社交风险评估等，通过一套复杂的加权和调整逻辑，计算出好感度变化 (`delta`)。
        5.  更新内部好感度、情绪、耐心等状态。
    *   **输出:** 返回一个包含当前好感度、变化量、以及详细调试信息（各评估维度得分、影响因素）的字典。
*   **关系阶段:** `GalGameAgent._update_relationship_state()` (或由`AffectionSystem`管理) 根据好感度阈值更新与角色的关系阶段 (陌生人 -> 熟人 -> ... -> 挚爱)。
*   **影响:**
    *   关系阶段和情绪会影响 `GalGameAgent._get_contextual_guideline()` 生成的系统提示，进而改变AI的回复风格和行为。
    *   好感度是 `TopicManager` 解锁新话题、`StorylineManager` 触发剧情、`AchievementSystem` 解锁成就的关键条件。
*   **同步:** 虽然之前有 `AffectionManager`，但新结构中 `AffectionSystem` 可能自身负责维护统一的好感度值，并通过注册的回调机制通知其他关心此值的模块（如 `GameManager` 的主游戏状态，`GalGameAgent` 的角色状态）。

### 5.3 对话生成 (`GalGameAgent` 与 LLM)

*   `GalGameAgent.chat()` 方法驱动。
*   **上下文构建:**
    1.  维护一个 `dialogue_history` 列表，存储多轮对话（`user`, `assistant` 角色）。
    2.  在调用LLM API前，通过 `_get_contextual_guideline()` 方法准备/更新 `system` prompt。这个 `system` prompt 非常关键，它包含了角色的核心设定、当前情绪、与玩家的关系阶段、正在讨论的话题、以及对AI行为的即时指导。
*   **API调用:**
    *   使用 `openai` 库 (或兼容库如 `deepseek`) 的 `self.client.chat.completions.create()` 方法。
    *   将包含系统提示和对话历史的 `messages` 列表发送给LLM。
    *   配置模型参数 (如 `model`, `temperature`, `max_tokens`)。
*   **回复处理:**
    *   获取LLM返回的 `assistant` 回复。
    *   对回复进行必要的后处理（如去除不必要的前缀/后缀，敏感词过滤等，虽然代码中不明显）。
    *   将AI的回复添加到 `dialogue_history`。
*   **状态反馈:** AI的回复和玩家的输入会反过来影响角色的内部状态（情绪、无聊度、对玩家的尊重评价），这些状态又会进入下一轮的 `_get_contextual_guideline`，形成动态循环。
*   **特殊逻辑:** 代码中包含对特定情况的硬编码处理，如好感度达到极高/极低时的特殊对话或结局，以及通过特定调试命令直接修改状态。

### 5.4 场景与时间 (`core.scene.manager.SceneManager`)

*   **场景数据:** `SceneManager` 从 `config/scene_config.yaml` 加载场景定义，包括：
    *   场景ID、名称、描述。
    *   场景的背景音乐、图片 (供Web版使用)。
    *   可从当前场景转换到的其他场景列表。
    *   场景转换所需消耗的游戏内时间。
    *   进入场景的特定条件 (可能，但当前不明显)。
*   **场景转换 (`analyze_conversation`):**
    *   该方法在每轮对话后由 `DialogueSystem` 调用。
    *   输入参数：玩家输入、AI回复、当前场景、当前日期时间。
    *   逻辑：分析对话内容是否提及了与场景转换相关的关键词 (例如，玩家说"我们去公园吧"，或者AI建议"天气这么好，不如去咖啡厅坐坐？")。
    *   判断：如果检测到转换意图，并且目标场景是当前场景可达的，则返回一个包含新场景ID、是否应转换等信息的字典。
*   **时间推进 (`_advance_time`):**
    *   当场景成功转换时，或执行某些特定行动后，`SceneManager` 会调用此方法。
    *   根据场景转换的定义或行动的耗时，推进游戏内的 `current_date` 和 `current_time` (通常是时间段，如上午、下午、黄昏、夜晚)。
    *   时间推进可能会影响可用话题、剧情触发、角色行为模式等。
*   **状态同步:** `GameManager` 保存和管理全局的当前场景ID、日期和时间。`SceneManager` 的操作结果会更新到 `GameManager` 中。

### 5.5 主题与剧情 (`TopicManager`, `StorylineManager`)

*   **`TopicManager`:**
    *   **话题数据:** 从配置加载话题列表，每个话题可能包含名称、解锁条件（如好感度等级）、持续时间、关联的特殊效果等。
    *   **可用性:** `get_available_topics()` 根据当前游戏状态（主要是好感度，也可能包括已谈论历史、当前场景等）决定哪些话题对玩家开放。
    *   **兴趣与糖豆:** 管理"兴趣话题"（可能提供额外好感度）和"糖豆话题"（一种奖励机制，可能解锁特殊对话或奖励）。
    *   **对话引导:** 玩家选择的话题会影响 `GalGameAgent` 生成的 `_get_contextual_guideline`，从而引导AI的对话方向。
    *   **状态更新:** `GalGameAgent` 或 `DialogueSystem` 会通知 `TopicManager` 当前正在讨论的话题，以及话题的完成情况。

*   **`StorylineManager`:**
    *   **剧情数据:** 从配置加载剧情点，每个剧情点包括：
        *   剧情ID、名称。
        *   触发条件：通常是好感度达到某个阈值，但也可能涉及特定日期、时间、场景、或已完成的前置剧情/话题。
        *   剧情内容：一段或多段对话文本，或者一个特殊事件的描述。
        *   剧情效果：触发后可能改变游戏状态，如好感度大幅变化、解锁新场景/话题、获得道具/成就等。
    *   **触发检查 (`check_storyline_triggers`):** 在每轮对话后，或特定游戏事件发生后，由 `DialogueSystem` 或 `GameManager` 调用。
    *   `StorylineManager` 遍历所有未触发的剧情，检查其条件是否满足当前游戏状态。
    *   **执行与反馈:** 如果剧情触发，`StorylineManager` 返回剧情内容给调用者显示，并记录该剧情已被触发，以避免重复。
    *   **调试模式:** 可以查看所有剧情状态或强制触发剧情。

### 5.6 成就系统 (`AchievementSystem`)

*   **定义与存储:** 成就的完整定义（ID, 名称, 描述, 解锁条件JSON, 奖励文本, 图标, 是否隐藏）存储在 `data/dialogues.db` 的 `achievements` 表。玩家的解锁进度（是否解锁, 解锁日期, 当前进度值）存储在 `player_achievements` 表。
*   **初始化:** `_initialize_default_achievements()` 预置了一系列基础成就。
*   **检查逻辑 (`check_achievements`):**
    *   由 `DialogueSystem` 在每轮对话处理完毕后调用，并传入 `GameManager` 实例以获取全面的游戏状态。
    *   遍历所有未解锁的成就。
    *   对每个成就，解析其 `requirements` JSON字段。该字段定义了成就类型和具体条件，例如：
        *   `"type": "dialogue_count", "character": "Su_Tang", "count": 10` (与苏糖对话10次)
        *   `"type": "affection", "character": "Su_Tang", "level": 500` (苏糖好感度达到500)
        *   `"type": "scene", "scenes": ["park", "library"]` (访问过公园和图书馆)
        *   `"type": "storyline_triggered", "story_id": "confession_success"` (成功触发告白剧情)
        *   `"type": "consecutive_positive", "count": 5` (连续5次积极互动)
    *   根据 `GameManager` 提供的实时状态 (如 `game_manager.game_state['closeness']`, `game_manager.game_state['conversation_count']`, `game_manager.character_states[character_id]['scenes_visited']` 等) 判断条件是否满足。
*   **解锁与保存:** 如果条件满足，成就被标记为解锁，`_save_unlocked_achievements()` 将此状态和解锁日期写入数据库。
*   **通知与奖励:**
    *   `get_achievement_notification()` 生成解锁通知文本。
    *   `DialogueSystem` 在收到新解锁成就后，会将通知附加到AI回复中。
    *   如果成就定义了奖励 (如 "好感度+20")，`DialogueSystem` 会解析并应用该奖励 (例如，调用 `AffectionSystem.update_value()` 来增加好感度)。

## 6. 安装与运行

### 6.1 环境设置

1.  **Python:** 确保安装 Python 3.8 或更高版本。
2.  **克隆仓库 (如果通过Git):**
    ```bash
    git clone <repository_url>
    cd Su_Tang 
    ```
3.  **创建并激活虚拟环境 (推荐):**
    ```bash
    python -m venv venv 
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```
4.  **安装依赖:**
    ```bash
    pip install -r requirements.txt
    ```
    这会安装 `requirements.txt` 文件中列出的所有库，例如 `Flask`, `openai`, `pyyaml`, `jieba`, `SnowNLP`, `colorama`。
5.  **配置 API Key:**
    *   复制 `.env.example` 文件并重命名为 `.env`。
    *   打开 `.env` 文件，将其中的 `DEEPSEEK_API_KEY=` (或相应的LLM API密钥字段) 替换为你自己的有效API密钥。
    ```
    DEEPSEEK_API_KEY=your_actual_api_key_here
    ```
6.  **(可选) 下载 jieba 词典:**
    第一次运行 `NaturalLanguageProcessor` 时，`jieba` 可能会尝试下载其默认词典。确保网络连接通畅。如果项目包含自定义词典 (如 `user_dict.txt`)，确保路径配置正确。

### 6.2 运行游戏

*   **命令行版本:**
    在项目根目录下，激活虚拟环境后运行：
    ```bash
    python main.py
    ```
    或者直接运行 `game` 目录下的 `main.py`:
    ```bash
    python game/main.py
    ```

*   **Web 版本:**
    在项目根目录下，激活虚拟环境后运行：
    ```bash
    python web_start.py
    ```
    或者 (如果在Windows上，且 `start_web.bat` 配置正确)：
    ```bash
    ./start_web.bat
    ```
    启动成功后，通常会在终端显示类似 `* Running on http://127.0.0.1:5000/` 的信息。
    然后在你的网页浏览器中打开显示的地址 (通常是 `http://127.0.0.1:5000` 或 `http://localhost:5000`)。

## 7. 开发者建议与注意事项

*   **理解 `GameManager` 和 `DialogueSystem`:** 这两个类是游戏流程控制的核心。大部分新功能的集成或修改都会涉及到它们。
*   **掌握 `AffectionSystem`:** 好感度是游戏的情感核心。深入理解其输入、计算逻辑和输出，对于调整游戏平衡和角色行为至关重要。
*   **Prompt Engineering (`GalGameAgent._get_contextual_guideline`):** AI角色的行为和回复质量高度依赖于提供给LLM的系统提示。调整这部分是提升AI表现的关键。
*   **配置驱动:** 游戏的大部分内容（角色、场景、剧情、话题、成就条件、NLP关键词）都通过 `config/` 和 `data/` 目录下的YAML/JSON文件进行配置。熟悉这些配置文件的结构可以让你在不修改代码的情况下调整游戏内容。
*   **日志与调试:**
    *   项目广泛使用了 Python 的 `logging` 模块。注意日志级别和输出位置，以便于调试。
    *   游戏内通常包含调试命令 (如 `/debug affection`, `/debug topic` 等) 或调试模式开关 (`GameManager.debug_mode`)，可以提供运行时状态信息。
*   **数据持久化:**
    *   存档 (`saves/*.json`): 理解存档结构，便于问题排查。
    *   数据库 (`data/dialogues.db`): 可以使用SQLite浏览器查看成就、对话日志等数据。
*   **模块化与解耦:** 在添加新功能时，尽量遵循现有模块的职责划分，保持模块间的低耦合。
*   **错误处理:** 注意代码中（尤其是在API调用、文件读写、用户输入处理部分）的错误处理逻辑。
*   **版本控制:** 使用 Git 进行版本控制，并遵循良好的提交习惯。

## 8. 未来可扩展方向

*   **更丰富的角色互动:**
    *   **多角色支持:** `CharacterFactory` 已为此奠定基础。可以设计新的角色配置文件和Prompt。
    *   **非对话交互:** 增加如送礼物、小游戏、特殊行动等，影响好感度或触发事件。
*   **深化游戏系统:**
    *   **道具系统:** 引入可收集或购买的道具，用于解锁特殊对话、提升好感度或在特定情境下使用。
    *   **状态效果:** 引入更复杂的角色状态（如生病、疲劳、兴奋），影响其行为和对话。
    *   **经济系统:** 如果有商店或需要购买物品。
*   **增强NLP与AI:**
    *   **更精细的情感分析:** 识别更复杂的情感，如嫉妒、失望、期待等。
    *   **意图识别:** 更准确地理解玩家的深层意图，而不仅仅是表面文字。
    *   **记忆系统增强:** 让AI能更好地记住过去的对话细节和重要事件，并在后续对话中提及。
*   **内容扩展:**
    *   **更多场景与剧情线:** 增加新的地点、事件和多分支的故事。
    *   **自定义事件编辑器:** 开发工具，方便非程序员编辑剧情、对话、成就和NPC行为。
*   **UI/UX 改进 (Web版):**
    *   **视觉效果提升:** 使用更美观的UI设计和动效。
    *   **移动端适配:** 优化在手机和平板上的体验。
    *   **可访问性:** 确保界面对所有用户友好。
*   **国际化与本地化:** 支持多种语言。

---

希望这份更新后的开发者文档能帮助您和其他开发者更深入、更准确地理解和参与"绿园中学物语"项目的开发与维护！ 