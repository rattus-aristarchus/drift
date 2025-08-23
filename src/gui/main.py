from kivy.app import App
from kivy.core.window import Window

from src.gui.widgets import View
from src.gui.controller import Controller
from src.logger import CustomLogger

logger = CustomLogger(__name__)

class Main(App):

    def __init__(self, history, assets):
        super().__init__()
        self.controller = Controller(history)
        self.view = None

        self.assets = assets

    def build(self):
        logger.info("building the app")

        self.title = "Drift"
        Window.size = (1200, 900)

        self.view = View(self.controller,
                         self.assets,
                         cells_x=self.controller.history.current_state().width,
                         cells_y=self.controller.history.current_state().height)
        self.controller.run(self.view)
        return self.view


