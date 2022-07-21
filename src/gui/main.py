from kivy.app import App
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import ColorProperty, ObjectProperty
from kivy.clock import Clock
from kivy.core.window import Window

from src.util import CONST
from src.data import control


class Main(App):

    def __init__(self):
        super().__init__()

    def build(self):
        Logger.info("Main: building the app")

        self.title = "Drift"
        Window.size = (1500, 1000)
        self.view = View()
        return self.view


class CellView(Label):

    background = ColorProperty([0, 0, 0, 0])

#    def __init__(self, **kwargs):
 #       super().__init__(**kwargs)


class View(BoxLayout):

    map = ObjectProperty(control.generate_basic())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stop = False
        self.cells = {}
        self.create_grid()
        Clock.schedule_interval(self.auto_turn, 0.2)

    def auto_turn(self, dt):
        if not self.stop:
            self.do_turn()

    def do_turn(self):
        self.map = control.do_turn(self.map)
        self.show_grid()

    def create_grid(self):
        element = self.ids['grid']
        element.clear_widgets()
        for x in range(0, self.map.width):
            self.cells[x] = {}
            for y in range(0, self.map.height):
                cell = self.map.cells[x][y]
                label = CellView(text="")
                label.background = [1, 1, 1, 1]
                self.cells[x][y] = label

        for y in range(0, self.map.height):
            for x in range(0, self.map.width):
                element.add_widget(self.cells[x][y])

    def show_grid(self):
        Logger.info("View: showing grid")
        element = self.ids['grid']

        def get_max_pop(cell):
            max_num = 0
            max = None
            for pop in cell.pops:
                if pop.number >= max_num and pop.sapient:
                    max = pop
                    max_num = pop.number
            return max

        def get_text(cell):
            result = ""
            for pop in cell.pops:
                if pop.number < 1000:
                    number = str(pop.number)
                elif pop.number < 1000000:
                    number = str(round(pop.number / 1000)) + "k"
                else:
                    number = str(round(pop.number / 1000000)) + "m"
                # result += pop.name[:2] + ": " + number + "\n"
                result += number + "\n"
            return result[:-1]

        for y in range(0, self.map.height):
            for x in range(0, self.map.width):
                cell = self.map.cells[x][y]
                max_pop = get_max_pop(cell)
                color = [1, 1, 1, 1] if max_pop is None else CONST['pops'][max_pop.name]['color']
                label = self.cells[x][y]
                label.text = get_text(cell)
                label.background = color
