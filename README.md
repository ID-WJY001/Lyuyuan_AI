# 绿园中学物语 (Green Garden High School Story)

> v1.1.2 — 插件化角色系统：YAML配置驱动、热加载、零代码添加角色

**绿园中学物语**是一款由 LLM 驱动的轻叙事 RPG。你将扮演主角，在学校百团大战时与多个有”温度”的 AI 角色在绿园中学游逛、搭话与靠近。

---

## 🆕 v1.1.2 更新内容

### 插件化角色系统
- 📝 **YAML配置驱动**: 角色配置完全独立于代码，使用YAML格式定义
- 🔄 **热加载支持**: CharacterLoader自动缓存和验证配置
- ➕ **零代码添加角色**: 只需创建YAML文件即可添加新角色，无需修改代码
- 🎯 **统一配置格式**: 包含基本信息、人格设定、提示词、场景设置等完整配置

### 角色加载器
- 🏗️ **CharacterLoader类**: 统一的角色配置加载和管理
- ✅ **配置验证**: 自动验证YAML配置的完整性和正确性
- 💾 **智能缓存**: 避免重复加载，提升性能
- 🔌 **BaseCharacter转换**: 自动将YAML配置转换为BaseCharacter格式

### 配置结构
- 基本信息：角色ID、名称、初始好感度
- 人格设定：性格特点、说话风格、行为模式
- 提示词路径：角色提示词和分析提示词
- 场景设置：初始场景、位置、氛围描述

---

## 🎮 玩法亮点

- ✨ 多角色可选（5 人）：苏糖、林雨含、罗一莫、顾盼、夏星晚（欢迎页下拉选择）
- 🧠 一次请求，双通道产出：角色回复 + 内心分析（JSON），保证“说/想/改状态”一致
- 💖 情绪与关系：根据分析调整好感度、无聊度、关系阶段，并触发事件
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

- 后端：Python 3.10+ + Flask（`app.py` 路由，`backend/` 领域与服务）
- LLM：多提供商支持（DeepSeek、OpenAI），可通过配置切换
- 基础设施：统一的LLM接口层（`backend/infrastructure/llm/`）
- Agent：`BaseCharacter` 通用基类 + 角色类（`backend/domain/characters/`）
- 存档：`GameStorage`（JSON 到 `saves/`）
- 前端：原生 HTML/Bootstrap/jQuery（伪打字机、进度条动画、选择器、AJAX）
- 立绘：`frontend/static/images/*.png`

```
.
├── web_start.py                 # 统一入口：加载 .env、检查目录、启动 Flask
├── app.py                       # 路由：/api/start_game /api/chat /api/save /api/load
├── backend/
│   ├── infrastructure/          # 基础设施层
│   │   ├── llm/                 # LLM提供商抽象层
│   │   └── character_loader/    # 角色配置加载器（新增）
│   ├── domain/
│   │   ├── characters/          # BaseCharacter + 各角色类
│   │   ├── memory_system.py     # 记忆系统
│   │   └── proactive_system.py  # 主动性系统
│   ├── services/                # Service 包装（game_service）
│   ├── game_storage.py          # JSON 存档
│   └── settings.py              # 配置管理
├── characters/                  # 角色YAML配置（新增）
│   └── su_tang.yaml             # 苏糖角色配置
├── docs/                        # 完整文档
│   ├── testing-guide.md         # 测试流程
│   ├── openapi.md               # API规范
│   └── development-plan.md      # 发展计划
└── tests/                       # 测试脚本
    ├── api_test.py              # 自动化测试
    └── test_character_loader.py # 角色加载器测试（新增）
```
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

- 已安装 Python 3.10+（建议 3.12/3.13）。检查：

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

## ⚡ 一行启动（可选：使用 uv）

[uv](https://github.com/astral-sh/uv) 是一个超快的 Python 包管理与执行工具，支持按 `pyproject.toml` 自动解析依赖。已提供 `pyproject.toml`，可无需手动创建虚拟环境：

### 安装 uv

Windows (PowerShell)：
```powershell
pip install uv  # 或参考官方安装脚本
```

macOS/Linux：
```bash
pip install uv  # 或使用官方安装方式
```

### 直接运行

```bash
uv run web_start.py
```

第一次会自动解析依赖并创建隔离环境（缓存复用）。你仍可并行保留传统 venv 方式；二者互不冲突。

> 若需要进入一个交互 shell：`uv run python`；或安装开发可选依赖：`uv add <package>`。

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

### 最新版本：v1.0.1 （2025.10.15）
---

## 📚 文档

- **[QUICKSTART.md](QUICKSTART.md)** - 快速启动指南
- **[CLAUDE.md](CLAUDE.md)** - 项目开发指南
- **[docs/testing-guide.md](docs/testing-guide.md)** - 完整测试流程
- **[docs/openapi.md](docs/openapi.md)** - API规范文档
- **[docs/development-plan.md](docs/development-plan.md)** - 5阶段发展计划

## 🧪 测试

运行自动化测试：
```bash
# 确保服务器正在运行
python web_start.py

# 在新终端运行测试
python tests/api_test.py
```

查看完整测试文档：[docs/testing-guide.md](docs/testing-guide.md)

---

## 🔄 版本历史

### v1.1.2 (2026-03-14)
- 📝 YAML配置驱动的角色系统
- 🔄 CharacterLoader角色加载器
- ➕ 零代码添加新角色
- ✅ 配置验证和智能缓存

### v1.1.1 (2026-03-14)
- ✨ LLM提供商解耦，支持多提供商（DeepSeek、OpenAI）
- 📋 完整测试体系（测试文档、自动化脚本、OpenAPI规范）
- 🏗️ 基础设施层重构
- 📚 完善的开发文档

### v1.0.1 (2025-10-15)
- ✨ 多角色首发版：五名可选角色
- 🧠 统一分析模板
- 💖 人设去标签化
