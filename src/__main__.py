import kivy.resources
from kivy.logger import Logger, LOG_LEVELS
from src.logic.entities import generate_history
from util import CONF, RES_DIR, ASSETS_DIR, ENTITIES_DIR, WORLDS_DIR, MAPS_DIR, ICONS_DIR, BACKGROUNDS_DIR
from src.logic.effects import util as effects_util
Logger.setLevel(LOG_LEVELS[CONF["log_level"]])
import gui.main as gui
from src.io import storage


if __name__ == '__main__':
    model_base = storage.load_models(ENTITIES_DIR, WORLDS_DIR, MAPS_DIR)

    effects_util.model_base = model_base
    world_model = model_base.get_world(CONF['world'])
    history = generate_history.do(world_model, model_base)

    assets = storage.load_assets(ASSETS_DIR)
    kivy.resources.resource_add_path(ASSETS_DIR)
    kivy.resources.resource_add_path(BACKGROUNDS_DIR)
    kivy.resources.resource_add_path(ICONS_DIR)

    gui = gui.Main(history, assets).run()
