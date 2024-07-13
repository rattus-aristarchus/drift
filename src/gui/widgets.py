from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ColorProperty, ObjectProperty, NumericProperty
from kivy.clock import Clock


class Tooltip(Label):
    pass


class CellView(Label):

    background = ColorProperty([0, 0, 0, 0])

    tooltip = Tooltip(text='Hello world')

    def __init__(self, **kwargs):
        Window.bind(mouse_pos=self.on_mouse_pos)
        super().__init__(**kwargs)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        self.tooltip.pos = pos
        Clock.unschedule(self.display_tooltip)  # cancel scheduled event since I moved the cursor
        self.close_tooltip()  # close if it's opened
        if self.collide_point(*self.to_widget(*pos)):
            Clock.schedule_once(self.display_tooltip, 0.5)

    def close_tooltip(self, *args):
        # Logger.debug("removing tooltip")
        Window.remove_widget(self.tooltip)

    def display_tooltip(self, *args):
        # Logger.debug("displaying tooltip at pos " + str(self.tooltip.pos))
        Window.add_widget(self.tooltip)


class View(BoxLayout):

    cells_x = NumericProperty(0)
    cells_y = NumericProperty(0)

    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.cells = {}

    def create_grid(self, map):
        element = self.ids['grid']
        element.clear_widgets()
        self.size_check(map)

        for x in range(0, map.width):
            self.cells[x] = {}
            for y in range(0, map.height):
                cell = map.cells[x][y]
                label = CellView(text="")
                label.background = [1, 1, 1, 1]
                self.cells[x][y] = label

        for y in range(0, map.height):
            for x in range(0, map.width):
                element.add_widget(self.cells[x][y])

    def size_check(self, map):
        if not map.width == self.cells_x:
            self.cells_x = map.width
        if not map.height == self.cells_y:
            self.cells_y = map.height

    def show_grid(self, map):
        element = self.ids['grid']
        self.size_check(map)

        def get_max_pop(cell):
            max_num = 0
            max = None
            for pop in cell.pops:
                if pop.size >= max_num and pop.sapient:
                    max = pop
                    max_num = pop.size
            return max

        def get_text(cell):
            result = ""
            for pop in cell.pops:
                if pop.size < 1000:
                    number = str(pop.size)
                elif pop.size < 1000000:
                    number = str(round(pop.size / 1000)) + "k"
                else:
                    number = str(round(pop.size / 1000000)) + "m"
                # result += pop.name[:2] + ": " + number + "\n"
                result += number + "\n"
            return result[:-1]

        for y in range(0, map.height):
            for x in range(0, map.width):
                cell = map.cells[x][y]
                max_pop = get_max_pop(cell)
                color = [1, 1, 1, 1]
                label = self.cells[x][y]
                label.text = get_text(cell)
                label.background = color
