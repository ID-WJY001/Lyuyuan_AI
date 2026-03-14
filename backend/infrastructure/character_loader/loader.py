"""角色配置加载器

从YAML文件加载角色配置，支持热加载和配置验证。
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class CharacterConfig:
    """角色配置数据类"""

    def __init__(self, config_dict: Dict):
        """从字典初始化配置

        Args:
            config_dict: 配置字典
        """
        self.raw_config = config_dict

        # 基本信息
        self.id = config_dict.get("id")
        self.name = config_dict.get("name")
        self.display_name = config_dict.get("display_name", self.name)
        self.role_key = config_dict.get("role_key", self.id)

        # 初始状态
        self.initial_state = config_dict.get("initial_state", {})

        # 人格特征
        personality = config_dict.get("personality", {})
        self.traits = personality.get("traits", [])
        self.mbti = personality.get("mbti")
        self.keywords = personality.get("keywords", [])
        self.description = personality.get("description", "")

        # Prompt配置
        prompts = config_dict.get("prompts", {})
        self.persona_file = prompts.get("persona_file")
        self.analysis_file = prompts.get("analysis_file")
        self.welcome_message = prompts.get("welcome_message")

        # 场景设置
        scene = config_dict.get("scene", {})
        self.location = scene.get("location")
        self.scene_description = scene.get("description", "")
        self.scene_context = scene.get("context", "")

        # 玩家信息
        player = config_dict.get("player", {})
        self.player_name = player.get("default_name", "陈辰")

        # 高级配置
        advanced = config_dict.get("advanced", {})
        self.history_size = advanced.get("history_size", 100)
        self.confession_keywords = advanced.get("confession_keywords", [])
        self.backup_replies = advanced.get("backup_replies", [])
        self.guidelines = advanced.get("guidelines", [])
        self.important_notes = advanced.get("important_notes", [])

        # 元数据
        metadata = config_dict.get("metadata", {})
        self.version = metadata.get("version", "1.0")
        self.tags = metadata.get("tags", [])

    def to_base_character_config(self) -> Dict:
        """转换为BaseCharacter所需的配置格式

        Returns:
            Dict: BaseCharacter配置字典
        """
        # 读取prompt文件内容
        persona_text = self._read_prompt_file(self.persona_file)
        analysis_path = self._resolve_prompt_path(self.analysis_file)

        # 构建system prompts
        system_prompts = []

        # 添加persona
        if persona_text:
            if self.scene_context:
                system_prompts.append(f"{persona_text}\n\n{self.scene_context}")
            else:
                system_prompts.append(persona_text)

        # 添加guidelines
        if self.guidelines:
            system_prompts.append("\n".join(self.guidelines))

        return {
            "role_key": self.role_key,
            "name": self.name,
            "player_name": self.player_name,
            "prompt_template_path": str(analysis_path),
            "system_prompts": system_prompts,
            "welcome_message": self.welcome_message,
            "current_scene_description": self.scene_description,
            "history_size": self.history_size,
            "initial_state": self.initial_state,
        }

    def _read_prompt_file(self, file_path: Optional[str]) -> str:
        """读取prompt文件内容

        Args:
            file_path: 文件路径

        Returns:
            str: 文件内容
        """
        if not file_path:
            return ""

        try:
            path = self._resolve_prompt_path(file_path)
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.warning(f"Prompt file not found: {file_path}")
            return ""
        except Exception as e:
            logger.error(f"Error reading prompt file {file_path}: {e}")
            return ""

    def _resolve_prompt_path(self, file_path: Optional[str]) -> Path:
        """解析prompt文件路径

        Args:
            file_path: 相对或绝对路径

        Returns:
            Path: 解析后的路径
        """
        if not file_path:
            raise ValueError("File path is empty")

        path = Path(file_path)

        # 如果是绝对路径，直接返回
        if path.is_absolute():
            return path

        # 否则相对于项目根目录
        project_root = Path.cwd()
        return (project_root / path).resolve()

    def validate(self) -> List[str]:
        """验证配置完整性

        Returns:
            List[str]: 错误信息列表，空列表表示验证通过
        """
        errors = []

        # 必填字段检查
        if not self.id:
            errors.append("Missing required field: id")
        if not self.name:
            errors.append("Missing required field: name")
        if not self.persona_file:
            errors.append("Missing required field: prompts.persona_file")
        if not self.analysis_file:
            errors.append("Missing required field: prompts.analysis_file")

        # 文件存在性检查
        if self.persona_file:
            try:
                path = self._resolve_prompt_path(self.persona_file)
                if not path.exists():
                    errors.append(f"Persona file not found: {self.persona_file}")
            except Exception as e:
                errors.append(f"Invalid persona file path: {e}")

        if self.analysis_file:
            try:
                path = self._resolve_prompt_path(self.analysis_file)
                if not path.exists():
                    errors.append(f"Analysis file not found: {self.analysis_file}")
            except Exception as e:
                errors.append(f"Invalid analysis file path: {e}")

        return errors


class CharacterLoader:
    """角色配置加载器"""

    def __init__(self, characters_dir: str = "characters"):
        """初始化加载器

        Args:
            characters_dir: 角色配置文件目录
        """
        self.characters_dir = Path(characters_dir)
        self._cache: Dict[str, CharacterConfig] = {}

    def load_character(self, character_id: str) -> Optional[CharacterConfig]:
        """加载指定角色配置

        Args:
            character_id: 角色ID

        Returns:
            CharacterConfig: 角色配置对象，失败返回None
        """
        # 检查缓存
        if character_id in self._cache:
            logger.debug(f"Loading character from cache: {character_id}")
            return self._cache[character_id]

        # 加载配置文件
        config_file = self.characters_dir / f"{character_id}.yaml"

        if not config_file.exists():
            logger.error(f"Character config file not found: {config_file}")
            return None

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_dict = yaml.safe_load(f)

            config = CharacterConfig(config_dict)

            # 验证配置
            errors = config.validate()
            if errors:
                logger.error(f"Character config validation failed for {character_id}:")
                for error in errors:
                    logger.error(f"  - {error}")
                return None

            # 缓存配置
            self._cache[character_id] = config
            logger.info(f"Successfully loaded character: {character_id}")

            return config

        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {config_file}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading character {character_id}: {e}")
            return None

    def list_characters(self) -> List[str]:
        """列出所有可用的角色ID

        Returns:
            List[str]: 角色ID列表
        """
        if not self.characters_dir.exists():
            logger.warning(f"Characters directory not found: {self.characters_dir}")
            return []

        character_ids = []
        for file in self.characters_dir.glob("*.yaml"):
            if file.stem != "schema":  # 排除schema文件
                character_ids.append(file.stem)

        return sorted(character_ids)

    def reload_character(self, character_id: str) -> Optional[CharacterConfig]:
        """重新加载角色配置（清除缓存）

        Args:
            character_id: 角色ID

        Returns:
            CharacterConfig: 角色配置对象
        """
        if character_id in self._cache:
            del self._cache[character_id]

        return self.load_character(character_id)

    def clear_cache(self):
        """清除所有缓存"""
        self._cache.clear()
        logger.info("Character cache cleared")


# 全局加载器实例
_global_loader: Optional[CharacterLoader] = None


def get_character_loader() -> CharacterLoader:
    """获取全局角色加载器实例

    Returns:
        CharacterLoader: 加载器实例
    """
    global _global_loader
    if _global_loader is None:
        _global_loader = CharacterLoader()
    return _global_loader
