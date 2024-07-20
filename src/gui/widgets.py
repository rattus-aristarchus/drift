import kivy.metrics
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
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
        self.cell = None
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
        # Window.add_widget(self.tooltip)
        pass


class FilterDropdown(DropDown):
    pass


def init_filter_selector(main_button, map_filters, update_callback):

    def dropdown_open(x):
        kivy.clock.Clock.schedule_once(lambda dt: dropdown.open(main_button))

    def change_filter(btn):
        update_callback(btn.text)
        dropdown.select(btn.text)

    dropdown = FilterDropdown()

    for map_filter in map_filters:
        filter_button = Button(text=map_filter.name, size_hint_y=None, height=25)
        filter_button.bind(on_release=change_filter)
        dropdown.add_widget(filter_button)

    main_button.bind(on_release=dropdown_open)
    dropdown.bind(on_select=lambda instance, x: setattr(main_button, 'text', x))


class View(BoxLayout):

    cells_x = NumericProperty(0)
    cells_y = NumericProperty(0)

    def __init__(self, controller, assets, **kwargs):
        super().__init__(**kwargs)
        self.assets = assets
        self.controller = controller
        self.cells = {}
        self.filter = self.assets.get_map_filter("producers")
        self.logical_grid = None
        init_filter_selector(self.ids['filter_selector'], self.assets.map_filters, self.filter_changed)

    def create_grid(self, logical_grid, world_name):
        self.logical_grid = logical_grid

        element = self.ids['grid']
        element.clear_widgets()
        self.size_check(logical_grid)

        for x in range(0, logical_grid.width):
            self.cells[x] = {}
            for y in range(0, logical_grid.height):
                label = CellView(text="")
                self.cells[x][y] = label

        for y in range(0, logical_grid.height):
            for x in range(0, logical_grid.width):
                element.add_widget(self.cells[x][y])

        self._set_background(world_name)

    def filter_changed(self, new_filter):
        self.filter = self.assets.get_map_filter(new_filter)
        self.show_grid(self.logical_grid)

    def _set_background(self, world_name):
        element = self.ids['grid']
        data = self.assets.get_background_data(world_name)
        if not data == "none":
            element.background_name = data["name"]
            element.background_width = data["size"][0]
            element.background_height = data["size"][1]

    def size_check(self, grid):
        if not grid.width == self.cells_x:
            self.cells_x = grid.width
        if not grid.height == self.cells_y:
            self.cells_y = grid.height

    def show_grid(self, grid):
        self.logical_grid = grid
        self.size_check(grid)

        for x in range(0, grid.width):
            for y in range(0, grid.height):
                cell = grid.cells[x][y]
                label = self.cells[x][y]

                text, icon_file = _get_cell_representation(cell, self.filter, self.assets)
                label.text = text
                label.icon_source = icon_file


def _get_cell_representation(cell, filter, assets):
    """
    Return a text and an image name to represent the cell according
    to the current filter.
    """
    entity = None

    if filter.accept_type == "group":
        entity = _get_group(cell, filter)
        if entity:
            pass

    elif filter.accept_type == "pop":
        entity = _get_max_viewable_pop(cell, filter)
        if entity:
            text = _get_text_for_pop(entity)
            image = _get_image(entity, assets)
            return text, image

    elif filter.accept_type == "biome" or filter.accept_type == "":
        image = _get_image(cell.biome, assets)
        if image == "none":
            Logger.error(f"Could not find image for biome {cell.biome.name}")
        return "", image

    if not filter.can_be_empty:
        Logger.error(f"Could not find anything to represent cell ({cell.x}, {cell.y})")

    return "", assets.get_icon_name("none")


#TODO:
def _get_group(cell, filter):
    return None


def _get_biome(cell):
    return


def _get_image(entity, assets):
    img_name = "none"
    if entity is not None:
        img_name = entity.name
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
        if pop.size >= max_num and _should_view(pop, map_filter):
            max = pop
            max_num = pop.size
    return max


def _should_view(agent, map_filter):
    if map_filter.accept_key == "":
        return True

    value = eval(f"agent.{map_filter.accept_key}")
    return value in map_filter.accept_values


class Map(GridLayout):

    background_name = StringProperty("empty.png")
    background_width = NumericProperty(0)
    background_height = NumericProperty(0)
