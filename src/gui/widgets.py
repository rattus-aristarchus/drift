from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import ColorProperty, ObjectProperty


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
        Logger.debug("removing tooltip")
        Window.remove_widget(self.tooltip)

    def display_tooltip(self, *args):
        Logger.debug("displaying tooltip")
        Window.add_widget(self.tooltip)
