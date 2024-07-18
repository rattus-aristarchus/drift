from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ColorProperty, ObjectProperty, NumericProperty, StringProperty
from kivy.clock import Clock


class Tooltip(Label):
    pass


class CellView(Label):

    icon_source = StringProperty("empty.png")
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
        Window.remove_widget(self.tooltip)

    def display_tooltip(self, *args):
        Window.add_widget(self.tooltip)


class View(BoxLayout):

    cells_x = NumericProperty(0)
    cells_y = NumericProperty(0)

    def __init__(self, controller, assets, **kwargs):
        super().__init__(**kwargs)
        self.assets = assets
        self.controller = controller
        self.cells = {}
        self.filter = self.assets.get_map_filter("population")

    def create_grid(self, map, world_name):
        element = self.ids['grid']
        element.clear_widgets()
        self.size_check(map)

        for x in range(0, map.width):
            self.cells[x] = {}
            for y in range(0, map.height):
                label = CellView(text="")
                self.cells[x][y] = label

        for x in range(0, map.width):
            for y in range(0, map.height):
                element.add_widget(self.cells[x][y])

        self._set_background(world_name)

    def _set_background(self, world_name):
        element = self.ids['grid']
        data = self.assets.get_background_data(world_name)
        element.background_name = data["name"]
        element.background_width = data["size"][0]
        element.background_height = data["size"][1]

    def size_check(self, map):
        if not map.width == self.cells_x:
            self.cells_x = map.width
        if not map.height == self.cells_y:
            self.cells_y = map.height

    def show_grid(self, map):
        element = self.ids['grid']
        self.size_check(map)

        for x in range(0, map.width):
            for y in range(0, map.height):
                cell = map.cells[x][y]
                label = self.cells[x][y]

                max_pop = _get_max_viewable_pop(cell, self.filter)

                label.text = _get_text_for_pop(max_pop)
                label.icon_source = _get_image_for_pop(max_pop, self.assets)


def _get_image_for_pop(max_pop, assets):
    img_name = "none"
    if max_pop is not None:
        img_name = max_pop.name
    return assets.get_icon_name(img_name)


def _get_text_for_pop(max_pop):
    if max_pop == None:
        return ""

    if max_pop.size < 1000:
        result = str(max_pop.size)
    elif max_pop.size < 1000000:
        result = str(round(max_pop.size / 1000)) + "k"
    else:
        result = str(round(max_pop.size / 1000000)) + "m"

    return result


def _get_max_viewable_pop(cell, map_filter):
    """
    Compares all populations in a cell that the current map filter
    allows us to view.
    """
    max_num = 0
    max = None
    for pop in cell.pops:
        if pop.size >= max_num and pop.name in map_filter.pops_to_show:
            max = pop
            max_num = pop.size
    return max


class Map(GridLayout):

    background_name = StringProperty("empty.png")
    background_width = NumericProperty(0)
    background_height = NumericProperty(0)
