from kivy.app import App
from kivy.logger import Logger
from kivy.core.window import Window

from src.gui.widgets import View
from src.gui.controller import Controller


class Main(App):

    def __init__(self, history, assets):
        super().__init__()
        self.controller = Controller(history)
        self.view = None

        self.assets = assets

    def build(self):
        Logger.info("Main: building the app")

        self.title = "Drift"
        Window.size = (1200, 900)

        self.view = View(self.controller,
                         self.assets,
                         cells_x=self.controller.history.current_state().width,
                         cells_y=self.controller.history.current_state().height)
        self.controller.run(self.view)
        return self.view


