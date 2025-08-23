from kivy.logger import Logger

def set_level(level):
    Logger.setLevel(level)

class CustomLogger:

    def __init__(self, file_name):
        self.log_file = file_name.split('.')[-1]


    def debug(self, msg):
        Logger.debug(self._full_msg(msg))


    def warning(self, msg):
        Logger.warning(self._full_msg(msg))


    def info(self, msg):
        Logger.info(self._full_msg(msg))


    def error(self, msg):
        Logger.error(self._full_msg(msg))


    def critical(self, msg):
        Logger.critical(self._full_msg(msg))


    def _full_msg(self, msg):
        return f"{self.log_file}: {msg}"