# 完整测试流程文档

> 版本: v1.1.2
> 日期: 2026-03-14
> 项目: Lyuyuan AI - 绿园中学物语

## 目录

1. [测试环境准备](#测试环境准备)
2. [后端API测试](#后端api测试)
3. [前端功能测试](#前端功能测试)
4. [集成测试](#集成测试)
5. [性能测试](#性能测试)
6. [故障排查](#故障排查)

---

## 测试环境准备

### 1. 环境配置检查

```bash
# 1. 检查Python版本
python --version  # 应该是 3.10+

# 2. 检查虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.\.venv\Scripts\Activate.ps1  # Windows PowerShell

# 3. 检查依赖安装
pip list | grep -E "(flask|requests|httpx|jieba|python-dotenv)"

# 4. 检查环境变量
cat .env  # 确保包含 DEEPSEEK_API_KEY
```

### 2. 启动服务

```bash
# 方式1: 使用web_start.py（推荐）
python web_start.py

# 方式2: 直接运行app.py
python app.py

# 方式3: 使用uv（如果已安装）
uv run web_start.py
```

**预期输出**:
```
Loading .env file...
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server.
 * Running on http://0.0.0.0:5000
```

### 3. 验证服务启动

```bash
# 测试根路径
curl http://localhost:5000/

# 应该返回HTML页面（index.html）
```

---

## 后端API测试

### API概览

| 端点 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/` | GET | 返回首页 | 否 |
| `/api/start_game` | POST | 开始新游戏 | 否 |
| `/api/chat` | POST | 发送聊天消息 | 否 |
| `/api/save` | POST | 保存游戏 | 否 |
| `/api/load` | POST | 加载游戏 | 否 |
| `/api/saves` | GET | 列出所有存档 | 否 |

### 测试1: 开始新游戏 (POST /api/start_game)

**请求**:
```bash
curl -X POST http://localhost:5000/api/start_game \
  -H "Content-Type: application/json" \
  -d '{"role": "su_tang"}'
```

**请求参数**:

---

## 角色配置加载器测试

### 测试角色加载器

**测试脚本**: `tests/test_character_loader.py` 或 `tests/test_all_characters.py`

```bash
# 基础测试（测试单个角色）
python tests/test_character_loader.py

# 完整测试（测试所有角色）
python tests/test_all_characters.py
```

**预期输出**:
```
============================================================
测试角色配置加载器
============================================================

[OK] 加载器初始化成功

测试1: 列出所有角色
------------------------------------------------------------
找到 5 个角色配置:
  - gu_pan
  - lin_yuhan
  - luo_yimo
  - su_tang
  - xia_xingwan

测试2: 加载苏糖配置
------------------------------------------------------------
[OK] 加载成功
  ID: su_tang
  名称: 苏糖
  显示名称: 苏糖
  MBTI: ISFJ
  性格特征: 温柔, 细心, 喜欢烘焙, 会弹钢琴, 有原则
  关键词: 烘焙, 钢琴, 甜点, 音乐, 烘焙社, 钢琴社
  初始好感度: 30

测试3: 配置验证
------------------------------------------------------------
✓ 配置验证通过

测试4: 转换为BaseCharacter配置
------------------------------------------------------------
✓ 转换成功
  角色键: su_tang
  角色名: 苏糖
  玩家名: 陈辰
  欢迎消息: （抬头露出礼貌的微笑）你好~ 我这边负责烘焙社今天的招新，如果你感兴趣我可以简单介绍一下~
...
  System Prompts数量: 2
  历史大小: 100

测试5: 重新加载配置
------------------------------------------------------------
✓ 重新加载成功

测试6: 加载不存在的角色
------------------------------------------------------------
✓ 正确返回None

============================================================
所有测试通过！✓
============================================================
```

**验证点**:
- [ ] 加载器初始化成功
- [ ] 能列出所有5个角色配置（su_tang, lin_yuhan, luo_yimo, gu_pan, xia_xingwan）
- [ ] 能加载YAML配置文件
- [ ] 配置验证通过
- [ ] 能转换为BaseCharacter格式
- [ ] 缓存机制正常工作
- [ ] 不存在的角色返回None

---

**文档版本**: v1.1.2
**最后更新**: 2026-03-14
