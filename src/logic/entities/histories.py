import dataclasses

from dataclasses import field

from src.logic.computation import Agent, GridCPU
from src.logic.entities.basic import recurrents
from src.logic.entities import grids
from src.logic.entities.basic.recurrents import copy_recurrent_and_add_to_list


@dataclasses.dataclass
class World(Agent):

    width: int = 10
    height: int = 10
    age: int = 0
    mean_temp: float = 7
    # how much the temperature needs to deviate for
    # pops to change by 50%:
    deviation_50: float = 1

    map: str = ""
    # инструкции для наполнения регионов
    cell_instructions: dict = field(default_factory=lambda: {})


class History:
    """
    Все итерации модели. В сущности, список из Grid,
    каждый из которых соответствует состоянию модели на определенный момент времени.
    """

    def __init__(self, world, write_output=lambda *args: None):
        self.past_grids = []
        self.turn = 0
        self.world = world
        self.write_output = write_output

        self.cpu = GridCPU(self.world)

    def current_state(self):
        return self.past_grids[-1]

    def state_at_turn(self, turn):
        if len(self.past_grids) > turn >= 0:
            return self.past_grids[turn]
        else:
            return None


def do_turn(history):
    """
    Executes one turn by creating a new grid object and adding it to the
    list of grids for past turns.
    :param history: the history object
    """

    history.turn += 1

    old_grid = history.current_state()
    new_grid = _create_new_turn_grid(history)
    history.cpu.refresh_cpus(new_grid)

    history.cpu.do_effects()

    history.write_output(new_grid)


def _create_new_turn_grid(history):
    old_grid = history.past_grids[-1]
    new_grid, all_recurrents = recurrents.copy_recurrent_and_add_to_list(old_grid, {})
    grids.increase_age_for_everything(new_grid)
    history.past_grids.append(new_grid)
    return new_grid


def create_with_premade_map(world, write_output):
    result = History(world, write_output)
    first_grid, all_recurrents = copy_recurrent_and_add_to_list(world.map, {})
    result.past_grids.append(first_grid)
    result.cpu.effects = list(world.effects)
    return result


def create_with_generated_map(world, factory, write_output):
    result = History(world, write_output)
    first_grid = grids.create_grid_with_default_biome(world.width, world.height, 'basic', factory)
    result.past_grids.append(first_grid)
    result.cpu.effects = list(world.effects)
    return result
