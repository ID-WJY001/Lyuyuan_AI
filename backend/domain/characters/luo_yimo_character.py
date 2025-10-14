from __future__ import annotations

import copy
import random
from typing import Dict, Optional
from pathlib import Path

from backend.domain.characters.base_character import BaseCharacter
from backend.game_storage import GameStorage
from backend.config import PROMPTS_DIR


_ANALYSIS_TEMPLATE_PATH = (PROMPTS_DIR / "luo_yimo" / "analysis_prompt.txt").resolve()
_PROMPT_FILE_PATH = (PROMPTS_DIR / "luo_yimo" / "luo_yimo_prompt.txt").resolve()

try:
    _PROMPT_FILE_TEXT = _PROMPT_FILE_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    _PROMPT_FILE_TEXT = ""

_CONTEXTUAL_GUIDELINE = "\n".join(
    [
        "你是罗一莫，绿园中学的学生，今天在百团大战现场附近，时不时会去科技协会摊位帮忙。",
        "你更喜欢把话说清楚、把事做踏实，但不会拿‘效率’压过对话的温度。",
        "当前地点：科技协会摊位与周边走道，人来人往，你们可以边逛边聊。",
        "与玩家‘陈辰’的关系取决于对话历史，请据此拿捏距离感与语气，不必把‘招新’放在每句话里。",
    ]
)

_DEFAULT_CONFIG: Dict = {
    "role_key": "luo_yimo",
    "name": "罗一莫",
    "player_name": "陈辰",
    "prompt_template_path": str(_ANALYSIS_TEMPLATE_PATH),
    "system_prompts": [f"{_PROMPT_FILE_TEXT}", _CONTEXTUAL_GUIDELINE],
    "welcome_message": "今天挺热闹的。想来看看科技协会招新吗？",
    "current_scene_description": "百团大战现场的科技协会摊位，正在进行招新演示。",
    "history_size": 100,
    "initial_state": {
        "closeness": 35,
        "discovered": [],
        "chapter": 1,
        "last_topics": [],
        "dialogue_quality": 0,
        "relationship_state": "初始阶段",
        "mood_today": "normal",
        "boredom_level": 0,
        "respect_level": 0,
    },
}


class LuoYimoCharacter(BaseCharacter):
    """罗一莫角色（科技协会招新）。"""

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
            "嗯，我在听，你慢慢说，不着急。",
            "要不我们边走边聊？这边风小一点。",
        ]
        pool_mid = [
            "听起来挺有意思的。你想从哪里开始？我先陪你想一小步就好。",
            "可以，不过别太赶，我们先把关键信息对齐下，再往前走。",
        ]
        pool_high = [
            "走，前面有把长椅，我给你讲个我自己踩坑的小故事。",
            "等会儿我请你喝一罐你没试过的汽水，顺便把刚才的话题接着聊。",
        ]
        if closeness < 40:
            return random.choice(pool_low)
        if closeness < 70:
            return random.choice(pool_mid)
        return random.choice(pool_high)


__all__ = ["LuoYimoCharacter"]
