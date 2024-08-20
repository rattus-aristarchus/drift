import os

import kivy.resources
from kivy.logger import Logger, LOG_LEVELS

from src.io.output import Output
from src.logic.entities import generate_history
from util import CONF, RES_DIR, ASSETS_DIR, ENTITIES_DIR, WORLDS_DIR, MAPS_DIR, ICONS_DIR, BACKGROUNDS_DIR
from src.logic.effects import util as effects_util
Logger.setLevel(LOG_LEVELS[CONF["log_level"]])
os.environ["KIVY_GL_DEBUG"] = "0"
import gui.main as gui
from src.io import storage


if __name__ == '__main__':
    model_base = storage.make_model_base(ENTITIES_DIR, WORLDS_DIR, MAPS_DIR)

    effects_util.model_base = model_base
    world_model = model_base.get_world(CONF['world'])
    output = Output()
    history = generate_history.do(world_model, model_base, output.write_grid)

    assets = storage.load_assets(ASSETS_DIR)
    kivy.resources.resource_add_path(ASSETS_DIR)
    kivy.resources.resource_add_path(BACKGROUNDS_DIR)
    kivy.resources.resource_add_path(ICONS_DIR)

    gui = gui.Main(history, assets).run()
