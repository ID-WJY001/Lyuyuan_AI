# 角色配置文件

本目录包含所有角色的YAML配置文件。

## 文件结构

```
characters/
├── su_tang.yaml          # 苏糖配置
├── lin_yuhan.yaml        # 林雨含配置
├── luo_yimo.yaml         # 罗一莫配置
├── gu_pan.yaml           # 顾盼配置
├── xia_xingwan.yaml      # 夏星晚配置
└── schema.yaml           # 配置文件Schema定义
```

## 配置文件格式

每个角色配置文件包含以下字段：

```yaml
# 基本信息
id: su_tang                    # 角色唯一标识符
name: 苏糖                     # 角色显示名称
display_name: 苏糖             # UI显示名称

# 初始状态
initial_state:
  closeness: 30                # 初始好感度
  mood: normal                 # 初始心情
  relationship_state: 初始阶段  # 初始关系状态

# 人格特征
personality:
  traits:                      # 性格特征列表
    - 温柔
    - 细心
    - 喜欢烘焙
  mbti: ISFJ                   # MBTI类型（可选）
  keywords:                    # 关键词（用于记忆检索）
    - 烘焙
    - 钢琴
    - 甜点

# Prompt配置
prompts:
  persona: prompts/su_tang/su_tang_prompt.txt      # 人设文件路径
  analysis: prompts/su_tang/analysis_prompt.txt    # 分析模板路径
  welcome_message: "你好~ 我这边负责烘焙社今天的招新..."  # 欢迎消息

# 场景设置
scene:
  location: 烘焙社摊位
  description: 绿园中学百团大战活动现场。你在烘焙社摊位负责招新与讲解活动内容。

# 高级配置（可选）
advanced:
  history_size: 100            # 对话历史大小
  confession_keywords:         # 表白接受关键词
    - 我也喜欢你
    - 我愿意
  backup_replies:              # 备用回复列表
    - 抱歉，我刚才走神了...
```

## 添加新角色

1. 创建新的YAML文件（如 `new_character.yaml`）
2. 按照schema填写配置
3. 将prompt文件放到 `prompts/new_character/` 目录
4. 重启服务器，新角色自动加载

## 验证配置

使用验证工具检查配置文件：

```bash
python -m backend.infrastructure.character_loader validate characters/su_tang.yaml
```
