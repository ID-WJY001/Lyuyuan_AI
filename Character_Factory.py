import yaml
import os
from Su_Tang import GalGameAgent

class CharacterFactory:
    """
    角色工厂类：负责创建和管理不同的角色实例
    支持从配置文件中加载角色设定，实现多角色系统
    """
    
    def __init__(self):
        """
        初始化角色工厂
        创建角色实例字典和角色配置字典，并加载角色配置
        """
        self.characters = {}  # 存储已创建的角色实例
        self.character_configs = {}  # 存储角色配置
        self.load_character_configs()  # 加载所有角色配置
        
    def load_character_configs(self):
        """
        加载所有角色配置文件
        从config/characters目录读取所有角色配置，如果目录不存在则创建并设置默认角色
        """
        config_dir = os.path.join("config", "characters")
        
        # 如果目录不存在，创建它并添加默认的苏糖配置
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
            # 复制默认的苏糖配置到新目录
            self._setup_default_character()
        
        # 读取所有角色配置文件
        for file in os.listdir(config_dir):
            if file.endswith('.yaml'):
                character_id = file.split('.')[0]
                with open(os.path.join(config_dir, file), 'r', encoding='utf-8') as f:
                    try:
                        self.character_configs[character_id] = yaml.safe_load(f)
                    except Exception as e:
                        print(f"加载角色配置失败: {file}, 错误: {e}")
    
    def _setup_default_character(self):
        """
        设置默认的苏糖角色配置
        从原始配置文件复制并添加额外字段，创建标准化的角色配置
        """
        # 从现有的character.yaml复制
        source_path = os.path.join("config", "character.yaml")
        target_dir = os.path.join("config", "characters")
        target_path = os.path.join(target_dir, "su_tang.yaml")
        
        if os.path.exists(source_path):
            os.makedirs(target_dir, exist_ok=True)
            
            # 读取原配置
            with open(source_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 添加必要的字段
            config['id'] = 'su_tang'
            config['display_name'] = '苏糖'
            config['description'] = '绿园中学高一二班的学生，烘焙社社长。性格温柔甜美，做事认真负责。'
            config['prompt_file'] = 'sutang_prompt.txt'
            
            # 保存到新位置
            with open(target_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    
    def get_character(self, character_id, load_slot=None, is_new_game=False):
        """
        获取指定ID的角色实例
        参数:
            character_id: 角色ID
            load_slot: 存档槽位，可选
            is_new_game: 是否新游戏
        返回值:
            角色实例对象
        抛出:
            ValueError: 找不到指定角色配置时
        """
        # 如果已经创建了这个角色实例，直接返回
        if character_id in self.characters:
            return self.characters[character_id]
        
        # 检查是否有这个角色的配置
        if character_id not in self.character_configs:
            if character_id == 'su_tang':  # 如果是默认角色
                # 使用现有的苏糖类
                character = GalGameAgent(load_slot, is_new_game)
                self.characters[character_id] = character
                return character
            else:
                raise ValueError(f"找不到角色配置: {character_id}")
        
        # 根据配置创建新角色
        config = self.character_configs[character_id]
        
        # 对于苏糖，使用现有的实现
        if character_id == 'su_tang':
            character = GalGameAgent(load_slot, is_new_game)
        else:
            # 这里可以根据配置创建其他类型的角色
            # 目前先用通用的GalGameAgent处理所有角色
            character = self._create_generic_character(config, load_slot, is_new_game)
        
        self.characters[character_id] = character
        return character
    
    def _create_generic_character(self, config, load_slot=None, is_new_game=False):
        """
        创建通用角色实例
        参数:
            config: 角色配置字典
            load_slot: 存档槽位，可选
            is_new_game: 是否新游戏
        返回值:
            角色实例对象
        """
        # 读取角色的提示文件
        prompt_file = config.get('prompt_file', None)
        if prompt_file and os.path.exists(prompt_file):
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt = f.read()
        else:
            # 如果没有提示文件，根据配置生成一个基本提示
            prompt = self._generate_prompt_from_config(config)
        
        # 使用现有的GalGameAgent类，但传入自定义prompt
        character = GalGameAgent(load_slot, is_new_game)
        character.custom_prompt = prompt
        
        return character
    
    def _generate_prompt_from_config(self, config):
        """
        根据配置生成角色提示文本
        参数:
            config: 角色配置字典
        返回值:
            生成的角色提示文本
        """
        name = config.get('name', 'Unknown')
        display_name = config.get('display_name', name)
        description = config.get('description', '')
        
        prompt = f"""
        【角色扮演：{display_name}】
        
        你是{name}，{description}
        
        【性格特点】
        """
        
        if 'personality' in config and 'traits' in config['personality']:
            traits = config['personality']['traits']
            prompt += "、".join(traits) + "\n\n"
        
        prompt += "【基本信息】\n"
        if 'school' in config and 'grade' in config and 'class' in config:
            prompt += f"- 学校：{config['school']}\n"
            prompt += f"- 年级：{config['grade']}\n"
            prompt += f"- 班级：{config['class']}\n"
        
        if 'birthday' in config:
            prompt += f"- 生日：{config['birthday']}\n"
        
        if 'clubs' in config:
            prompt += f"- 社团：{', '.join(config['clubs'])}\n"
        
        if 'interests' in config:
            prompt += "\n【兴趣爱好】\n"
            if 'core' in config['interests']:
                prompt += "- 核心爱好：" + "、".join(config['interests']['core']) + "\n"
            if 'daily' in config['interests']:
                prompt += "- 日常兴趣：" + "、".join(config['interests']['daily']) + "\n"
            if 'dislikes' in config['interests']:
                prompt += "- 不喜欢的事物：" + "、".join(config['interests']['dislikes']) + "\n"
        
        prompt += """
        【重要指示】
        1. 始终保持角色扮演，不要忘记你是谁
        2. 回答应该符合角色的性格和背景设定
        3. 对话要自然流畅，表现出恰当的情感和反应
        4. 不要添加任何未在设定中提及的背景信息
        """
        
        return prompt
    
    def get_all_character_ids(self):
        """
        获取所有可用角色的ID
        返回值:
            角色ID列表
        """
        return list(self.character_configs.keys())
    
    def get_character_info(self, character_id):
        """
        获取指定角色的基本信息
        参数:
            character_id: 角色ID
        返回值:
            包含角色基本信息的字典，如果角色不存在则返回None
        """
        if character_id not in self.character_configs:
            return None
            
        config = self.character_configs[character_id]
        return {
            'id': character_id,
            'name': config.get('name', 'Unknown'),
            'display_name': config.get('display_name', config.get('name', 'Unknown')),
            'description': config.get('description', ''),
            'avatar': config.get('avatar', None)
        } 