from __future__ import annotations

import copy
import random
from pathlib import Path
from typing import Dict, Optional

from base_character import BaseCharacter
from Game_Storage import GameStorage

# ---------------------------------------------------------------------------
# Static configuration pieces reused across instances

_ROOT_DIR = Path(__file__).resolve().parent
_PROMPT_TEMPLATE_PATH = _ROOT_DIR / "prompts" / "su_tang" / "analysis_prompt.txt"
_PROMPT_FILE_PATH = _ROOT_DIR / "prompts" / "su_tang" / "sutang_prompt.txt"

try:
    _PROMPT_FILE_TEXT = _PROMPT_FILE_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    _PROMPT_FILE_TEXT = ""

_CHARACTER_DETAILS = """
【背景信息】
当前场景：绿园中学百团大战活动，苏糖正在烘焙社摊位前介绍社团活动
互动对象：陈辰（男，高一一班学生）
【重要提示】
1. 请严格遵守角色设定，不要添加任何未在设定中明确提及的背景信息
2. 关于苏糖的家庭情况，请仅限于已提供的信息：独生女，父亲是上市公司高管，母亲是大学老师，家庭和睦美满
请你始终牢记以上设定，在回复中保持角色一致性，任何时候都不要忘记自己是谁、在哪里、和谁说话。
""".strip()

_CONTEXTUAL_GUIDELINE = "\n".join(
    [
        "你是苏糖，绿园中学高一二班的学生，烘焙社社长。",
        "你是个温柔、甜美的女生，但也有自己的原则和底线。",
        "陈辰是高一一班的学生，他对你产生了好感，正在尝试与你搭讪。",
    ]
)

_DEFAULT_CONFIG: Dict = {
    "name": "苏糖",
    "player_name": "陈辰",
    "prompt_template_path": str(_PROMPT_TEMPLATE_PATH),
    "system_prompts": [f"{_PROMPT_FILE_TEXT}\n\n{_CHARACTER_DETAILS}", _CONTEXTUAL_GUIDELINE],
    "welcome_message": "（正在整理烘焙社的宣传材料）有什么我可以帮你的吗？",
    "current_scene_description": "绿园中学百团大战活动，你正在烘焙社摊位前。",
    "history_size": 100,
    "initial_state": {
        "closeness": 30,
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


class SuTangCharacter(BaseCharacter):
    """针对苏糖角色的具体实现，兼容旧版 :class:`GalGameAgent`."""

    CONFESSION_ACCEPT_KEYWORDS = [
        "我也喜欢你",
        "我愿意",
        "做你的男朋友",
        "接受",
        "我也是",
        "同意",
        "在一起",
        "喜欢你",
        "爱你",
        "好的",
    ]
    CONFESSION_REJECT_KEYWORDS = [
        "抱歉",
        "对不起",
        "做朋友",
        "拒绝",
        "不行",
        "不能",
        "不要",
        "不好",
        "朋友",
        "不接受",
    ]

    def __init__(
        self,
        load_slot: Optional[str] = None,
        is_new_game: bool = False,
        storage: Optional[GameStorage] = None,
        config_override: Optional[Dict] = None,
    ) -> None:
        config = copy.deepcopy(_DEFAULT_CONFIG)
        if config_override:
            config = self._merge_config(config, config_override)

        super().__init__(config=config, storage=storage, keyword_extractor=None)

        if load_slot and self.load(load_slot):
            print(f"加载存档#{load_slot}成功")
        else:
            self.start_new_game(is_new_game=is_new_game)

    # ------------------------------------------------------------------
    # Hooks

    def handle_special_commands(self, user_input: str) -> Optional[str]:
        if user_input.startswith("/debug closeness "):
            try:
                value = int(user_input.split("/debug closeness ", 1)[1])
                self.game_state["closeness"] = max(0, min(100, value))
                self._update_relationship_state()
                return f"【调试】亲密度已调整为 {self.game_state['closeness']}"
            except ValueError:
                return "【调试】设置亲密度失败"
        return None

    def handle_pre_chat_events(self, user_input: str) -> Optional[str]:
        if self.game_state.get("closeness", 0) >= 100 and "confession_triggered" not in self.game_state:
            self.game_state["confession_triggered"] = True
            return """【剧情推进：苏糖主动告白】..."""

        if (
            "confession_triggered" in self.game_state
            and "confession_response" not in self.game_state
        ):
            lowered = user_input.strip()
            if any(keyword in lowered for keyword in self.CONFESSION_ACCEPT_KEYWORDS):
                self.game_state["confession_response"] = "accepted"
                self.game_state["closeness"] = 100
                self.save("happy_ending")
                print("游戏已自动保存至存档：happy_ending")
                return """【甜蜜结局：两情相悦】..."""
            if any(keyword in lowered for keyword in self.CONFESSION_REJECT_KEYWORDS):
                self.game_state["confession_response"] = "rejected"
                self.game_state["closeness"] = 60
                self.save("sad_ending")
                print("游戏已自动保存至存档：sad_ending")
                return """【遗憾结局：错过良缘】..."""
        return None

    def get_backup_reply(self) -> str:
        closeness = self.game_state.get("closeness", 30)
        if len(self.dialogue_history) <= 3:
            return "（微笑着看向你）你好！是的，这里就是烘焙社的招新摊位。我是苏糖..."
        if closeness < 40:
            return "（礼貌地点头）嗯，你说得对..."
        if closeness < 70:
            return "（友好地笑了笑）谢谢你这么说..."
        fallback_pool = [
            "（脸上泛起微微的红晕）...",
            "（笑容特别明亮）...",
        ]
        return random.choice(fallback_pool)

    # ------------------------------------------------------------------
    # Internal helpers

    @staticmethod
    def _merge_config(base: Dict, override: Dict) -> Dict:
        merged = copy.deepcopy(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = SuTangCharacter._merge_config(merged[key], value)
            else:
                merged[key] = value
        return merged

    def _update_closeness(self, delta: int) -> None:
        previous = self.game_state.get("closeness", 30)
        super()._update_closeness(delta)
        current = self.game_state.get("closeness", 30)
        if (
            current >= 100
            and "confession_triggered" not in self.game_state
            and previous < 100
        ):
            print("亲密度达到100，下次对话将触发表白事件！")
            self.game_state["closeness"] = 100


__all__ = ["SuTangCharacter"]