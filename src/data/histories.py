from kivy import Logger

from src.data import grids
from src.data.buffers import GridBuffer, CellBuffer
from src.io.output import Output


def do_turn(history):
    """
    Executes one turn by creating a new grid object and adding it to the
    list of grids for past turns.
    :param history: the history object
    """

    history.turn += 1

    old_grid = history.current_state()
    new_grid = _create_new_turn_grid(history)

    _do_effects(history, new_grid, old_grid)

    Logger.info(f"The age is {new_grid.state.age}. Global temeprature"
                f" is {new_grid.state.temperature}.")

    _write_output(new_grid)


def _create_new_turn_grid(history):
    old_grid = history.past_grids[-1]
    new_grid = grids.copy(old_grid)
    grids.increase_age(new_grid)
    history.past_grids.append(new_grid)
    return new_grid


def _do_effects(history, new_grid, old_grid):
    # the gridbuffer and cellbuffers help avoid doing some
    # calculations multiple times
    grid_buffer = GridBuffer(new_grid, old_grid, history)
    history.do_effects(grid_buffer)

    for cell in new_grid.cells_as_list():
        cell_buffer = CellBuffer(cell, grid_buffer)

        # this is the main call that calls do_effects for all agents in a cell
        cell.do_effects(cell_buffer, grid_buffer)

        # remove pops that have died out
        to_remove = []
        for pop in cell.pops:
            if pop.size <= 0:
                to_remove.append(pop)
        for pop in to_remove:
            cell.pops.remove(pop)


def _write_output(new_grid):
    # this is bad
    output = Output()
    for cell in new_grid.watched_cells:
        output.write_cell(cell)
    output.write_end_of_turn()


def create_history(world_model, model_base):
    result = History(world_model.width, world_model.height)
    first_grid = grids.create_grid(world_model.width, world_model.height, model_base.get_biome('basic'))
    result.past_grids.append(first_grid)
    result.effects = list(world_model.effects)

    return result


class History:

    def __init__(self, world_width, world_height):
        self.past_grids = []
        self.turn = 0
        self.width = world_width
        self.height = world_height
        self.effects = []

    def current_state(self):
        return self.past_grids[-1]

    def state_at_turn(self, turn):
        if turn < len(self.past_grids):
            return self.past_grids[turn]
        else:
            return None

    def do_effects(self, grid_buffer):
        for func in self.effects:
            func(self, grid_buffer)
