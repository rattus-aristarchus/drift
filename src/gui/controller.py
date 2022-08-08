
from kivy.clock import Clock

import data.control as control


class Controller:

    def __init__(self, map):
        self.stop = True
        self.map = map

    def run(self, view):
        self.view = view
        view.create_grid(self.map)
        Clock.schedule_interval(self.auto_turn, 0.2)

    def auto_turn(self, dt):
        if not self.stop:
            self.do_turn()

    def do_turn(self):
        self.map = control.do_turn(self.map)
        self.view.show_grid(self.map)
