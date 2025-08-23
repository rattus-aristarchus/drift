import os
import kivy.resources
import src.logger
from src.io.output import Output
from src.logic.entities import populate_history, factories
from src.util import CONF, ASSETS_DIR, NAMESPACES_DIR, ICONS_DIR, BACKGROUNDS_DIR
from src.logic.effects import effects_util
os.environ["KIVY_GL_DEBUG"] = "0"
import src.gui.main as gui
from src.io import storage
from src.logger import CustomLogger

src.logger.set_level(
    kivy.logger.LOG_LEVELS[CONF["log_level"]]
)

logger = CustomLogger(__name__)

if __name__ == '__main__':
    # load everything from disk, each folder into a separate factory
    f_list = storage.load_namespaces(NAMESPACES_DIR)
    # find the factory and world specified in CONF
    factory = factories.get_factory_with_world_name(CONF['world'], f_list)
    if not factory:
        logger.critical(f"conf specified a name of a non-existent world: {CONF['world']}")
    world = factory.get_world(CONF['world'])
    # make the factory available for effects
    effects_util.factory = factory
    # prepare writing to disk
    output = Output()

    history = populate_history.do(world, factory, output.write_grid)

    # set up graphics
    assets = storage.load_assets(ASSETS_DIR)
    kivy.resources.resource_add_path(ASSETS_DIR)
    kivy.resources.resource_add_path(BACKGROUNDS_DIR)
    kivy.resources.resource_add_path(ICONS_DIR)

    # aaaand liftoff
    gui = gui.Main(history, assets).run()
