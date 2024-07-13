from kivy.logger import Logger, LOG_LEVELS

from src.data import control
from util import CONF, MAIN_DIR, RES_DIR
from src.data.effects import util as effects_util

Logger.setLevel(LOG_LEVELS[CONF["log_level"]])

import gui.main as gui
from src.io import storage


if __name__ == '__main__':
    model_base = storage.load_models(RES_DIR)
    effects_util.model_base = model_base
    world_model = model_base.get_world(CONF['world'])
    history = control.generate_history(world_model, model_base)
    gui = gui.Main(history).run()
