from __future__ import annotations

import copy
import random
from typing import Dict, Optional

from backend.domain.characters.base_character import BaseCharacter
from backend.game_storage import GameStorage
from backend.config import PROMPTS_DIR

_ANALYSIS_TEMPLATE_PATH = (PROMPTS_DIR / "xia_xingwan" / "analysis_prompt.txt").resolve()
_PROMPT_FILE_PATH = (PROMPTS_DIR / "xia_xingwan" / "xia_xingwan_prompt.txt").resolve()

try:
    _PROMPT_FILE_TEXT = _PROMPT_FILE_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    _PROMPT_FILE_TEXT = ""

_CONTEXTUAL_GUIDELINE = "\n".join(
    [
        "你是夏星晚，绿园中学的学生，今天在百团大战现场走走停停，路过网球社摊位时会看一眼。",
        "你的风格是温柔、松弛、有分寸；不需要把训练安排挂嘴边，先把人安顿好更重要。",
        "当前地点：操场与走廊的阴影处之间，你们可以挑舒服的地方说话。",
    ]
)


_DEFAULT_CONFIG: Dict = {
    "role_key": "xia_xingwan",
    "name": "夏星晚",
    "player_name": "陈辰",
    "prompt_template_path": str(_ANALYSIS_TEMPLATE_PATH),
    "system_prompts": [f"{_PROMPT_FILE_TEXT}", _CONTEXTUAL_GUIDELINE],
    "welcome_message": "今天风有点大。网球社招新感兴趣吗？",
    "current_scene_description": "百团大战现场，操场与网球社摊位之间，可安排试打或轻量活动。",
    "history_size": 100,
    "initial_state": {
        "closeness": 38,
        "discovered": [],
        "chapter": 1,
        "last_topics": [],
        "dialogue_quality": 0,
        "relationship_state": "初始阶段",
        "mood_today": "calm",
        "boredom_level": 0,
        "respect_level": 0,
    },
}


class XiaXingwanCharacter(BaseCharacter):
    """夏星晚角色（网球社/运动场景）。"""

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
        closeness = self.game_state.get("closeness", 30)
        pool_low = [
            "先别着急，我们换个不晒的地方慢慢讲。",
            "我听得到，你不用抬太高声音。",
        ]
        pool_mid = [
            "可以的。你说到这里就够了，我们先从最容易的一步开始。",
            "如果你现在不想动，我们就坐会儿，等舒服一点再说接下来。",
        ]
        pool_high = [
            "我记得你喜欢清爽一点的风，我们去长廊尽头那边。今天就聊你自己觉得重要的事。",
            "结束以后我请你喝一杯冰咖啡，不赶时间，把你没讲完的补上。",
        ]
        if closeness < 40:
            return random.choice(pool_low)
        if closeness < 70:
            return random.choice(pool_mid)
        return random.choice(pool_high)


__all__ = ["XiaXingwanCharacter"]
