from kivy.app import App
from kivy.logger import Logger
from kivy.core.window import Window

from src.gui.widgets import View
from src.gui.controller import Controller


class Main(App):

    def __init__(self):
        super().__init__()
        self.controller = None
        self.view = None

    def build(self):
        Logger.info("Main: building the app")

        self.title = "Drift"
        Window.size = (1200, 900)

        self.controller = Controller()
        self.view = View(self.controller,
                         cells_x=self.controller.history.current_state().width,
                         cells_y=self.controller.history.current_state().height)
        self.controller.run(self.view)
#        Window.add_widget(Label(text='Hello world', size_hint=(None, None), size=(200, 100)))
        return self.view


