# web_app/game_core.py

from su_tang_character import SuTangCharacter

class SimpleGameCore:
    def __init__(self):
        self.agent = SuTangCharacter(is_new_game=True)

    def start_new_game(self):
        return self.agent.start_new_game(is_new_game=True)

    def chat(self, user_input):
        response = self.agent.chat(user_input)
        return response

    def get_current_state(self):
        return self.agent.game_state
    
    def save_game(self, slot):
        return self.agent.save(slot)

    def load_game(self, slot):
        return self.agent.load(slot)

game_core = SimpleGameCore()