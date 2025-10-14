from backend.domain.characters.su_tang_character import SuTangCharacter
from backend.domain.characters.lin_yuhan_character import LinYuhanCharacter
from backend.domain.characters.luo_yimo_character import LuoYimoCharacter
from backend.domain.characters.gu_pan_character import GuPanCharacter
from backend.domain.characters.xia_xingwan_character import XiaXingwanCharacter


class SimpleGameCore:
    def __init__(self):
        print("[BACKEND] Initializing SimpleGameCore (backend.domain)")
        # 默认角色：苏糖
        self.agent = SuTangCharacter(is_new_game=True)

    def _build_agent(self, role: str):
        key = (role or "su_tang").strip().lower()
        if key in ("su_tang", "sutang", "苏糖"):
            return SuTangCharacter(is_new_game=True)
        if key in ("lin_yuhan", "lin", "yuhan", "林雨含", "linyuhan"):
            return LinYuhanCharacter(is_new_game=True)
        if key in ("luo_yimo", "罗一莫", "luoyimo", "luo_yi_mo"):
            return LuoYimoCharacter(is_new_game=True)
        if key in ("gu_pan", "顾盼", "gupan", "gu-pan"):
            return GuPanCharacter(is_new_game=True)
        if key in ("xia_xingwan", "夏星晚", "xiaxingwan", "xia-xingwan"):
            return XiaXingwanCharacter(is_new_game=True)
        # 默认回退到苏糖
        return SuTangCharacter(is_new_game=True)

    def start_new_game(self, role: str | None = None):
        # 根据角色键重建 agent
        if role:
            self.agent = self._build_agent(role)
        return self.agent.start_new_game(is_new_game=True)

    def chat(self, user_input):
        return self.agent.chat(user_input)

    def get_current_state(self):
        return self.agent.game_state

    def save_game(self, slot):
        return self.agent.save(slot)

    def load_game(self, slot):
        return self.agent.load(slot)


game_core = SimpleGameCore()
