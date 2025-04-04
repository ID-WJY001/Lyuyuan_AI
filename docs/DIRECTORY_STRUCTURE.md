# 项目目录结构说明

本文档描述了绿园中学物语项目的目录结构和文件组织，帮助开发者和用户更好地理解项目结构。

## 主要目录结构

```
绿园中学物语/
├── core/               # 核心模块目录
│   ├── affection/      # 亲密度系统实现
│   ├── nlp/            # 自然语言处理实现
│   ├── scene/          # 场景管理系统实现
│   └── __init__.py     # 核心模块初始化和导出
│
├── game/               # 游戏逻辑目录
│   ├── managers/       # 游戏管理器目录
│   │   ├── game_manager_new.py   # 游戏主管理器
│   │   ├── scene_manager.py      # 场景管理器
│   │   ├── topic_manager.py      # 话题管理器
│   │   ├── storyline_manager.py  # 剧情管理器
│   │   └── __init__.py           # 管理器模块初始化
│   │
│   ├── dialogue_system.py    # 对话系统
│   ├── affection_manager.py  # 亲密度管理器
│   ├── game_manager.py       # 游戏管理器（兼容层）
│   ├── main.py               # 游戏主入口
│   └── __init__.py           # 游戏模块初始化
│
├── utils/              # 工具函数目录
│   ├── common.py       # 通用工具函数
│   └── __init__.py     # 工具模块初始化
│
├── web_app/            # Web应用目录
│   ├── static/         # 静态资源
│   │   ├── images/     # 图像资源
│   │   ├── css/        # 样式表
│   │   └── js/         # JavaScript文件
│   │
│   ├── templates/      # HTML模板
│   ├── app.py          # Flask应用
│   └── requirements.txt # Web应用依赖
│
├── data/               # 数据文件目录
│   ├── keyword_groups.json  # 关键词组配置
│   ├── userdict.txt         # 用户词典
│   └── dialogues.db         # 对话数据库
│
├── scripts/            # 脚本文件目录
│   ├── installation/    # 安装相关脚本
│   └── tools/           # 工具脚本
│
├── tests/              # 测试文件目录
│
├── config/             # 配置文件目录
│   ├── character.yaml       # 角色配置
│   └── affection_config.json # 亲密度系统配置
│
├── docs/               # 文档目录
│   ├── OPTIMIZATION.md       # 优化文档
│   └── DIRECTORY_STRUCTURE.md # 目录结构说明
│
├── sutang_prompt.txt   # 苏糖角色提示文本
├── .env.example        # 环境变量示例
├── README.md           # 项目说明
└── main.py             # 主入口（重定向到game.main）
```

## 文件分类和组织

### 1. 核心系统文件

核心系统文件被组织在`core/`目录中，按功能模块分为三个子目录：
- `affection/`: 亲密度系统相关实现
- `nlp/`: 自然语言处理相关实现
- `scene/`: 场景管理相关实现

### 2. 游戏逻辑文件

游戏逻辑文件位于`game/`目录，其中：
- `managers/`: 包含各种游戏管理器实现
- 根目录包含对话系统、亲密度管理和游戏主入口

### 3. 工具和辅助文件

- `utils/`: 通用工具函数
- `scripts/`: 安装、构建和工具脚本
- `tests/`: 单元测试和集成测试

### 4. Web应用文件

Web应用相关文件位于`web_app/`目录，遵循标准Flask应用结构。

### 5. 数据和配置文件

- `data/`: 游戏运行所需的数据文件
- `config/`: 配置文件

## 文件职责说明

### 核心模块 (core/)

核心模块提供游戏的基础功能组件，采用模块化设计，各子模块互相独立但可协同工作。

### 游戏模块 (game/)

游戏模块负责协调各核心组件，实现具体的游戏逻辑和流程控制。

### 工具模块 (utils/)

工具模块提供通用功能支持，如环境变量加载、文件操作等，被其他模块广泛使用。

### Web应用 (web_app/)

Web应用提供基于浏览器的游戏界面，使用Flask框架实现，调用游戏模块的功能。

### 脚本文件 (scripts/)

脚本文件用于自动化任务，如安装、构建、测试等，提高开发和部署效率。 