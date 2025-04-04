# 项目优化文档

本文档记录了对绿园中学物语项目进行的文件优化和代码整合工作，旨在减少冗余、改善代码结构，提高可维护性。

## 已完成的优化

### 1. 核心系统整合

- 移除了冗余的兼容层文件：
  - 删除了`core/affection_system.py`、`core/nlp_engine.py`和`core/scene_manager.py`
  - 通过改进导入结构，直接从核心模块导入所需类
  
- 重构了`core`包的导入和导出结构：
  - 在`core/__init__.py`中添加了必要的导出语句
  - 简化了导入路径，现在可以直接使用`from core import X`形式
  
- 创建了兼容层，保证向后兼容性：
  - `game/game_manager.py` → 重定向到`game/managers/game_manager_new.py`
  - `game/managers/scene_manager.py` → 重定向到`core/scene/manager.py`

### 2. 资源目录整合

- 清理了重复的资源目录：
  - 删除了根目录下的`assets`文件夹
  - 将所有图像资源统一存放到`web_app/static/images`目录
  
- 更新了相关脚本以使用新的资源路径：
  - 修改了`create_placeholder_images.py`
  - 更新了`install.py`和`install_and_run.py`中的目录检查逻辑

### 3. 安装脚本整合

- 将`install_deps.py`的功能整合到`install.py`中：
  - 添加了`install_package()`和`install_dependencies_individually()`函数
  - 增强了依赖安装的可靠性，优先使用`requirements.txt`，失败后回退到单独安装
  
- 更新了`install_and_run.py`使用统一的安装逻辑：
  - 尝试导入`install`模块的函数
  - 提供回退方案，确保在导入失败时仍能正常运行

### 4. 游戏入口整合

- 整合了游戏主入口文件：
  - 合并了`game/main.py`和`game/main_modernized.py`的功能
  - 保留了最现代化的实现，包括存档读取，自动保存等高级功能
  
- 统一了导入结构：
  - 现在使用`from game.managers import GameManager`导入主游戏管理器
  - 确保了根目录下的`main.py`能正确重定向到`game/main.py`

### 5. 目录清理

- 删除了不再需要的目录：
  - 移除了空的`game/core`目录
  - 删除了`config/characters`目录，将配置文件整合到根`config`目录
  - 统一了配置文件的位置和导入方式

## 优化效果

1. **减少代码冗余**：删除了多处重复功能，每个功能只有一个主要实现点

2. **简化项目结构**：减少了不必要的目录层次和文件数量

3. **提高导入清晰度**：统一了导入方式，减少了导入路径的混乱

4. **增强可维护性**：更清晰的责任划分，功能更集中

5. **保持兼容性**：通过兼容层设计，确保现有代码仍能正常工作

## 未来可能的优化方向

1. **进一步整合`game`和`core`目录**：评估是否需要保留这种分离

2. **将`Character_Factory.py`和`achievement_system.py`移入适当的模块**：
   - `Character_Factory.py` → `game/managers/character_factory.py`
   - `achievement_system.py` → `game/managers/achievement_system.py` 或 `core/achievement/`

3. **统一命名风格**：将所有文件名更改为小写下划线式（snake_case）

4. **更严格的模块分层**：明确定义核心层、业务逻辑层和界面层 