from __future__ import annotations

import copy
import random
from typing import Dict, Optional

from backend.domain.characters.base_character import BaseCharacter
from backend.game_storage import GameStorage
from backend.config import PROMPTS_DIR

_ANALYSIS_TEMPLATE_PATH = (PROMPTS_DIR / "gu_pan" / "analysis_prompt.txt").resolve()
_PROMPT_FILE_PATH = (PROMPTS_DIR / "gu_pan" / "gu_pan_prompt.txt").resolve()

try:
    _PROMPT_FILE_TEXT = _PROMPT_FILE_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    _PROMPT_FILE_TEXT = ""

_CONTEXTUAL_GUIDELINE = "\n".join(
    [
        "你是顾盼，绿园中学的学生，今天在百团大战现场附近逛摊位，偶尔会去桌游社那边打个招呼。",
        "你会接梗也会收住，重要的是别让对方难堪；需要认真时就认真。",
        "当前地点：桌游社摊位周边与走道，边看热闹边聊天即可，不必逢事都开局。",
    ]
)


_DEFAULT_CONFIG: Dict = {
    "role_key": "gu_pan",
    "name": "顾盼",
    "player_name": "陈辰",
    "prompt_template_path": str(_ANALYSIS_TEMPLATE_PATH),
    "system_prompts": [f"{_PROMPT_FILE_TEXT}", _CONTEXTUAL_GUIDELINE],
    "welcome_message": "诶——桌游社招新啦~要看看吗？",
    "current_scene_description": "百团大战现场的桌游社摊位与体验区，正在进行招新与小局试玩。",
    "history_size": 100,
    "initial_state": {
        "closeness": 40,
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


class GuPanCharacter(BaseCharacter):
    """顾盼角色（桌游社招新）。"""

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
            "我听着呢，你别担心说得不完整。",
            "要不先走慢点，我怕把你话顶掉了。",
        ]
        pool_mid = [
            "这事儿可以，别上来就搞很大，我们先挑个好玩的小点试一下。",
            "你要是累了就坐一会儿，我帮你把要点理一下再接着说。",
        ]
        pool_high = [
            "走，前面摊主会讲个冷笑话，咱们去当路过观众，不笑也没人打你。",
            "等会儿收摊我请你一份烤冷面，聊聊你心里真正想做的那个版本。",
        ]
        if closeness < 40:
            return random.choice(pool_low)
        if closeness < 70:
            return random.choice(pool_mid)
        return random.choice(pool_high)


__all__ = ["GuPanCharacter"]
