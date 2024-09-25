import os
import kivy.resources
from kivy.logger import Logger, LOG_LEVELS
from src.io.output import Output
from src.logic.entities import populate_history
from util import CONF, ASSETS_DIR, NAMESPACES_DIR, ICONS_DIR, BACKGROUNDS_DIR
from src.logic.effects import util as effects_util
Logger.setLevel(LOG_LEVELS[CONF["log_level"]])
os.environ["KIVY_GL_DEBUG"] = "0"
import gui.main as gui
from src.io import storage


def _get_world(name, world_list):
    for world in world_list:
        if world.name == name:
            return world


if __name__ == '__main__':
    factory, rules = storage.load_entities(NAMESPACES_DIR)

    effects_util.factory = factory
    world = _get_world(CONF['world'], list(factory.worlds.values()))
    output = Output()
    history = populate_history.do(world, factory, output.write_grid)

    assets = storage.load_assets(ASSETS_DIR)
    kivy.resources.resource_add_path(ASSETS_DIR)
    kivy.resources.resource_add_path(BACKGROUNDS_DIR)
    kivy.resources.resource_add_path(ICONS_DIR)

    gui = gui.Main(history, assets).run()

