from kivy.clock import Clock

from src.logic.entities import histories


class Controller:

    def __init__(self, history):
        self.stop = True
        self.history = history
        self.viewed_turn = self.history.turn

    def run(self, view):
        self.view = view
        view.create_grid(self.history.current_state(), self.history.world_model.id)
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

