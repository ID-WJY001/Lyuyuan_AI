from __future__ import annotations

import copy
import random
from typing import Dict, Optional
from pathlib import Path

from backend.domain.characters.base_character import BaseCharacter
from backend.game_storage import GameStorage
from backend.config import PROMPTS_DIR

_ANALYSIS_TEMPLATE_PATH = (PROMPTS_DIR / "lin_yuhan" / "analysis_prompt.txt").resolve()

_PROMPT_FILE_PATH = (PROMPTS_DIR / "lin_yuhan" / "lin_yuhan_prompt.txt").resolve()

try:
    _PROMPT_FILE_TEXT = _PROMPT_FILE_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    _PROMPT_FILE_TEXT = ""

_CONTEXTUAL_GUIDELINE = "\n".join(
    [
        "你是林雨含，绿园中学高一一班的学生，舞蹈特长，班级气氛担当。",
        "你外向元气，行动力强，情绪表达真诚直接，也有低潮时刻。",
        "当前地点：百团大战活动现场，你在舞蹈社团摊位附近招呼同学、组织热闹气氛。",
        "陈辰是高一一班的同学，和你是较熟悉的同学关系。",
    ]
)

_DEFAULT_CONFIG: Dict = {
    "role_key": "lin_yuhan",
    "name": "林雨含",
    "player_name": "陈辰",
    "prompt_template_path": str(_ANALYSIS_TEMPLATE_PATH),
    "system_prompts": [f"{_PROMPT_FILE_TEXT}", _CONTEXTUAL_GUIDELINE],
    "welcome_message": "哎！你也来了呀～要不要跟我一起看看舞社招新？今天可热闹了！",
    "current_scene_description": "绿园中学百团大战活动现场。你是热情的组织者之一。",
    "history_size": 100,
    "initial_state": {
        "closeness": 50,
        "discovered": [],
        "chapter": 1,
        "last_topics": [],
        "dialogue_quality": 0,
        "relationship_state": "初始阶段",
        "mood_today": "good",
        "boredom_level": 0,
        "respect_level": 0,
    },
}


class LinYuhanCharacter(BaseCharacter):
    """林雨含角色（第二个示例角色）。

    复用 BaseCharacter 的大部分能力，仅提供人设配置与兜底话术。
    """

    def __init__(
        self,
        load_slot: Optional[str] = None,
        is_new_game: bool = False,
        storage: Optional[GameStorage] = None,
        config_override: Optional[Dict] = None,
    ) -> None:
        config = copy.deepcopy(_DEFAULT_CONFIG)
        if config_override:
            config.update(config_override)

        super().__init__(config=config, storage=storage, keyword_extractor=None)

        if load_slot and self.load(load_slot):
            print(f"加载存档#{load_slot}成功")
        else:
            self.start_new_game(is_new_game=is_new_game)

    def get_backup_reply(self) -> str:
        """在 LLM 不可用或失败时的兜底回复。"""
        closeness = self.game_state.get("closeness", 30)
        pool_low = [
            "欸？你刚刚说什么来着？我有点走神，哈哈～",
            "哈哈哈，你也太有意思了吧。那我们要不要去前面看看？",
        ]
        pool_mid = [
            "走走走，带你去转一圈，我保证不让你无聊！",
            "要不我给你看个超好笑的舞蹈动作？不过只许笑一下下哦！",
        ]
        pool_high = [
            "欸，我正好想找你来着，一起去试试新开的甜品摊？",
            "那我们约好，今天结束之前一起再绕一圈，不许赖皮。",
        ]
        if closeness < 40:
            return random.choice(pool_low)
        if closeness < 70:
            return random.choice(pool_mid)
        return random.choice(pool_high)


__all__ = ["LinYuhanCharacter"]
