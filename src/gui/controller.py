
from kivy.clock import Clock

import src.data.control as control
import src.data.history


class Controller:

    def __init__(self, history):
        self.stop = True
        self.viewed_turn = history.turn
        self.history = history

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
            src.data.history.do_turn(self.history)

        self.view.show_grid(self.history.state_at_turn(self.viewed_turn))

    def backwards(self):
        if self.viewed_turn > 0:
            self.viewed_turn -= 1
            self.view.show_grid(self.history.state_at_turn(self.viewed_turn))
