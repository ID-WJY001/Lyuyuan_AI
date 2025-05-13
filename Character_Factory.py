import yaml
import os
from Su_Tang import GalGameAgent

class CharacterFactory:
    """
    角色工厂模块。

    定义了 `CharacterFactory` 类，负责动态创建和管理游戏中的不同角色实例。
    它支持从 YAML 配置文件中加载角色设定，理论上能够支持多角色系统，
    尽管当前所有角色（包括自定义角色）最终都依赖于 `GalGameAgent` 的核心实现。
    工厂还负责处理角色配置的初始化和默认角色（苏糖）的设置。
    """
    
    def __init__(self):
        """
        初始化角色工厂。
        
        创建用于存储角色实例 (`self.characters`) 和角色配置 (`self.character_configs`)
        的字典。在初始化时，会自动调用 `load_character_configs()` 加载所有角色配置。
        """
        self.characters = {}  # 存储已创建的角色实例
        self.character_configs = {}  # 存储角色配置
        self.root_dir = os.path.dirname(os.path.abspath(__file__))  # 项目根目录
        self.load_character_configs()  # 加载所有角色配置
        
    def load_character_configs(self):
        """
        加载所有角色配置文件。
        
        方法会扫描 `config/characters/` 目录下的所有 `.yaml` 文件。
        如果该目录不存在，则会先创建目录，并调用 `_setup_default_character()` 
        来生成一个默认的"苏糖"角色配置文件。
        每个YAML文件被视为一个独立角色的配置，文件名（不含.yaml后缀）作为角色ID。
        加载的配置存储在 `self.character_configs` 字典中。
        """
        config_dir = os.path.join(self.root_dir, "config", "characters")
        
        # 如果角色配置目录不存在，则创建它并设置默认的苏糖角色
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
        内部辅助方法，用于设置和保存默认角色"苏糖"的配置文件。
        
        它会尝试从项目根目录的 `config/character.yaml` (一个可能的旧版或基础配置文件)
        读取苏糖的基本设定，然后添加一些工厂系统必需的额外字段，
        例如 `id`, `display_name`, `description`, `prompt_file` 等，
        最后将整合后的配置保存到 `config/characters/su_tang.yaml` 中。
        如果源文件 `config/character.yaml` 不存在，此方法可能不会成功创建完整配置。
        """
        # 从现有的character.yaml复制
        source_path = os.path.join(self.root_dir, "config", "character.yaml")
        target_dir = os.path.join(self.root_dir, "config", "characters")
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
            config['prompt_file'] = os.path.join(self.root_dir, 'sutang_prompt.txt')
            
            # 保存到新位置
            with open(target_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    
    def get_character(self, character_id, load_slot=None, is_new_game=False):
        """
        获取或创建指定ID的角色实例。

        首先检查缓存中是否已存在该角色实例。如果存在，则直接返回。
        否则，根据 `character_id` 查找对应的角色配置：
        - 如果是默认角色 `su_tang` 且无显式配置，则直接使用 `GalGameAgent` 创建。
        - 如果有配置，则根据配置创建：
            - 对 `su_tang`，仍使用 `GalGameAgent`。
            - 对其他角色，调用 `_create_generic_character` 方法创建。
        - 如果找不到配置且非 `su_tang`，则抛出 `ValueError`。
        创建的角色实例会被缓存。

        Args:
            character_id (str): 要获取或创建的角色的唯一ID。
            load_slot (str, optional): 如果需要从存档加载角色状态，则指定存档槽位。
            is_new_game (bool, optional): 指示是否强制作为新游戏启动角色。

        Returns:
            GalGameAgent: 对应 `character_id` 的角色实例 (当前所有角色均为此类型)。

        Raises:
            ValueError: 如果找不到 `character_id` 的配置且该ID不是默认角色 `su_tang`。
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
        根据提供的配置信息，创建一个通用的角色实例。
        
        当前实现下，即使是"通用"角色，也仍然是使用 `GalGameAgent` 类来实例化的。
        核心区别在于，此方法会尝试从配置中指定的 `prompt_file` 加载详细的角色扮演提示，
        或者如果提示文件不存在，则调用 `_generate_prompt_from_config` 根据配置动态生成一个。
        这个获取到或生成的提示文本会被设置到 `GalGameAgent` 实例的 `custom_prompt` 属性上。

        Args:
            config (dict): 该角色的配置字典。
            load_slot (str, optional): 存档槽位。
            is_new_game (bool, optional): 是否为新游戏。

        Returns:
            GalGameAgent: 创建的通用角色实例。
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
        根据角色配置字典，动态生成一段结构化的角色扮演提示文本。

        生成的提示文本包含了角色的多个方面，例如：
        - 基本身份：姓名、显示名称、简要描述。
        - 性格特点。
        - 学校、年级、班级等基本信息。
        - 生日、参与的社团。
        - 核心爱好、日常兴趣、不喜欢的事物。
        - 一些通用的角色扮演重要指示 (例如，保持角色、符合设定、自然对话等)。
        
        这些信息都是从传入的 `config` 字典中提取的。

        Args:
            config (dict): 角色的配置字典。

        Returns:
            str: 根据配置生成的、供AI模型使用的角色扮演提示文本。
        """
        name = config.get('name', 'UnknownCharacter') # 如果配置中没有name，给一个默认值
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
        获取当前工厂中所有已加载配置的可用角色的ID列表。

        Returns:
            list[str]: 一个包含所有角色ID字符串的列表。
        """
        return list(self.character_configs.keys())
    
    def get_character_info(self, character_id):
        """
        获取指定角色的基本展示信息。
        
        信息从该角色的配置中提取，主要包括ID、名称、显示名称、描述和头像路径。

        Args:
            character_id (str): 要查询信息的角色ID。

        Returns:
            dict or None: 如果找到角色配置，则返回一个包含角色信息的字典：
                          `{'id': str, 'name': str, 'display_name': str, 
                            'description': str, 'avatar': str or None}`。
                          如果角色ID不存在，则返回 None。
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