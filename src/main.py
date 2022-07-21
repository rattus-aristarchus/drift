from kivy.logger import Logger, LOG_LEVELS
from util import CONF
Logger.setLevel(LOG_LEVELS[CONF["misc"]["log_level"]])

import gui.main as gui


if __name__ == '__main__':

    gui.Main().run()
