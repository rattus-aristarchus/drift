
from kivy.clock import Clock

import src.data.control as control
import src.data.effects.util
from src.data import histories
from src.io import storage
from src.util import CONF


class Controller:

    def __init__(self):
        self.stop = True

        self.model_base = storage.load_models()
        src.data.effects.util.model_base = self.model_base
        world_model = self.model_base.get_world(CONF['world'])
        self.history = control.generate_history(world_model, self.model_base)
        self.viewed_turn = self.history.turn

    def run(self, view):
        self.view = view
        view.create_grid(self.history.current_state())
        view.show_grid(self.history.current_state())
        Clock.schedule_interval(self.auto_turn, 0.2)

    def auto_turn(self, dt):
        if not self.stop:
            self.forwards()

    def forwards(self):
        self.viewed_turn += 1
        if self.viewed_turn > self.history.turn:
            histories.do_turn(self.history)

        self.view.show_grid(self.history.state_at_turn(self.viewed_turn))

    def backwards(self):
        if self.viewed_turn > 0:
            self.viewed_turn -= 1
            self.view.show_grid(self.history.state_at_turn(self.viewed_turn))
