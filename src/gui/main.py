from kivy.app import App
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.uix.label import Label

from src.data import control

from gui.widgets import View
from gui.controller import Controller
from util import WORLDS, CONF


class Main(App):

    def __init__(self):
        super().__init__()

    def build(self):
        Logger.info("Main: building the app")

        self.title = "Drift"
        Window.size = (1200, 900)

        history = control.generate_history(world=WORLDS[CONF['world']])
        self.controller = Controller(history)
        self.view = View(self.controller,
                         cells_x=history.current_state().width,
                         cells_y=history.current_state().height)
        self.controller.run(self.view)
#        Window.add_widget(Label(text='Hello world', size_hint=(None, None), size=(200, 100)))
        return self.view



