# 更新日志 (Changelog)

本文档记录Lyuyuan AI项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.1.3] - 2026-03-14

### 新增 (Added)
- **事件系统核心**: 事件驱动架构实现 (`backend/infrastructure/events.py`)
  - `EventType` 枚举：定义所有事件类型（对话、状态、游戏、系统）
  - `Event` 数据类：事件数据结构，包含类型、数据、时间戳、来源、优先级
  - `EventBus` 类：事件总线实现
    - 事件订阅和取消订阅
    - 事件发布和分发
    - 事件历史记录（最多1000条）
    - 事件类型过滤
    - 错误处理和日志记录
  - `get_event_bus()` 函数：全局事件总线单例

- **BaseCharacter事件集成**: 角色状态变更自动触发事件
  - `GAME_STARTED` 事件：游戏开始时触发
  - `CLOSENESS_CHANGED` 事件：好感度变化时触发
  - `RELATIONSHIP_CHANGED` 事件：关系状态变化时触发
  - `GAME_SAVED` 事件：游戏保存时触发
  - `GAME_LOADED` 事件：游戏加载时触发

- **示例监听器**: 展示事件系统使用方法 (`backend/infrastructure/event_listeners.py`)
  - `EventLogger`：日志监听器，记录所有事件到日志
  - `GameStatistics`：统计监听器，收集游戏数据和好感度历史
  - `AchievementSystem`：成就系统监听器，监听事件解锁成就

- **测试**: 完整的单元测试和集成测试
  - `tests/test_events.py`：事件系统核心功能测试
  - `tests/test_character_events.py`：BaseCharacter事件集成测试
  - 所有测试通过 ✅

### 变更 (Changed)
- **BaseCharacter**: 集成事件系统
  - 在 `__init__` 中初始化事件总线
  - 在关键方法中添加事件发布
  - 保持向后兼容，事件系统为可选功能

- **README更新**: 更新为v1.1.3，添加事件驱动架构说明

### 技术改进 (Technical)
- 解耦系统架构：模块间通过事件通信，无需直接依赖
- 提升可扩展性：添加新功能只需注册监听器
- 改善可调试性：事件历史记录方便追踪问题
- 支持动态扩展：可以在运行时添加/移除监听器

---

## [1.1.2] - 2026-03-14

### 新增 (Added)
- **角色配置系统**: YAML格式的角色配置文件
  - 示例配置: `characters/su_tang.yaml`
  - 包含基本信息、人格设定、提示词路径、场景设置
- **CharacterLoader**: 角色配置加载器 (`backend/infrastructure/character_loader/loader.py`)
  - `CharacterConfig` 数据类：结构化角色配置
  - `CharacterLoader` 类：加载、验证、缓存角色配置
  - 自动转换为 `BaseCharacter` 格式
- **角色加载器测试**: 完整的单元测试 (`tests/test_character_loader.py`)
  - 测试初始化、列表、加载、验证、转换功能
  - 所有测试通过

### 变更 (Changed)
- **依赖更新**: 添加 `pyyaml==6.0.1` 用于YAML解析
- **README更新**: 更新为v1.1.2，添加插件化角色系统说明
- **项目结构**: 新增 `characters/` 目录存放角色配置

### 技术改进 (Technical)
- 零代码添加新角色：只需创建YAML配置文件
- 配置热加载：CharacterLoader自动缓存和验证
- 统一配置格式：标准化的角色定义结构
- 插件化架构：角色配置与代码完全解耦

---

## [1.1.1] - 2026-03-14

### 新增 (Added)
- **LLM基础设施层**: 创建统一的LLM提供商抽象层 (`backend/infrastructure/llm/`)
  - `BaseLLMProvider` 抽象基类
  - `DeepSeekProvider` 实现
  - `OpenAIProvider` 实现
  - `LLMFactory` 工厂类
  - `LLMAdapter` 同步适配器
- **配置系统**: 新增LLM相关配置项到 `backend/settings.py`
  - `LLM_PROVIDER`: 选择LLM提供商
  - `LLM_MODEL`: 指定模型名称
  - `LLM_TEMPERATURE`: 温度参数
  - `LLM_MAX_TOKENS`: 最大token数
  - `LLM_TIMEOUT`: 请求超时时间
- **测试体系**:
  - 完整测试流程文档 (`docs/testing-guide.md`)
  - 测试检查清单 (`docs/testing-checklist.md`)
  - OpenAPI 3.0规范 (`docs/openapi.md`)
  - Python自动化测试脚本 (`tests/api_test.py`)
  - Bash自动化测试脚本 (`tests/api_test.sh`)
- **开发文档**:
  - 项目开发指南 (`CLAUDE.md`)
  - 快速启动指南 (`QUICKSTART.md`)
  - 5阶段发展计划 (`docs/development-plan.md`)
  - 架构设计文档 (`docs/architecture.md`)
  - 第一阶段实施文档 (`docs/phase1-1-*.md`)
- **配置模板**: `.env.example` 包含所有配置项说明

### 变更 (Changed)
- **依赖更新**: 添加 `httpx==0.27.0` 用于异步HTTP请求
- **README更新**: 更新为v1.1.1，添加新功能说明和文档链接
- **项目结构**: 新增 `backend/infrastructure/` 和 `docs/` 目录

### 技术改进 (Technical)
- 支持通过环境变量切换LLM提供商
- 原生支持异步调用和流式输出（基础设施层）
- 可扩展的工厂模式设计
- 100%的API端点测试覆盖

---

## [1.0.1] - 2025-10-15

### 新增 (Added)
- 多角色系统：5个可选角色（苏糖、林雨含、罗一莫、顾盼、夏星晚）
- 统一分析模板
- 记忆系统 (`backend/domain/memory_system.py`)
- 主动性系统 (`backend/domain/proactive_system.py`)
- JSON存档系统（5个槽位）
- 前端UI（Bootstrap + jQuery）

### 变更 (Changed)
- 人设去标签化
- 优化对话质量

---

## [0.3.0] - 2025-XX-XX

### 新增 (Added)
- 重构后端和前端
- 添加保存/加载功能

---

## [0.2.0] - 2025-XX-XX

### 新增 (Added)
- 解耦SuTang到BaseCharacter

---

## 版本说明

### 版本号格式: MAJOR.MINOR.PATCH

- **MAJOR**: 重大架构变更或不兼容的API变更
- **MINOR**: 新功能添加，向后兼容
- **PATCH**: Bug修复和小改进

### 变更类型

- **新增 (Added)**: 新功能
- **变更 (Changed)**: 现有功能的变更
- **弃用 (Deprecated)**: 即将移除的功能
- **移除 (Removed)**: 已移除的功能
- **修复 (Fixed)**: Bug修复
- **安全 (Security)**: 安全相关的修复

---

**最后更新**: 2026-03-14 (v1.1.2)
