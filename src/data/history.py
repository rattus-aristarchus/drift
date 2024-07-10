from kivy import Logger

from src.data import grid
from src.data.effects import GridBuffer, CellBuffer
from src.data.grid import Grid
from src.storage import Output


def do_turn(history):
    """
    Executes one turn by creating a new grid object and adding it to the
    list of grids for past turns.
    :param history: the history object
    """
    Logger.info("History: doing turn")

    history.turn += 1

    old_grid = history.current_state()
    new_grid = _create_new_turn_grid(history)

    _do_effects(new_grid, old_grid)

    _write_output(new_grid)


def _create_new_turn_grid(history):
    old_grid = history.past_grids[-1]
    new_grid = grid.copy(old_grid)
    grid.increase_age(new_grid)
    history.past_grids.append(new_grid)
    return new_grid


def _do_effects(new_grid, old_grid):
    # the gridbuffer and cellbuffers help avoid doing some
    # calculations multiple times
    grid_buffer = GridBuffer(new_grid, old_grid)
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

class History:

    def __init__(self, world_width, world_height):
        self.past_grids = []
        self.turn = 0
        self.width = world_width
        self.height = world_height
        first_grid = Grid(world_width, world_height)
        grid.populate(first_grid)
        self.past_grids.append(first_grid)

    def new_turn(self):
        """
        Create a new grid for the new turn.
        """
        self.turn += 1
        old_grid = self.past_grids[-1]
        new_grid = grid.copy(old_grid)
        grid.increase_age(new_grid)
        self.past_grids.append(new_grid)
        return new_grid

    def current_state(self):
        return self.past_grids[-1]

    def state_at_turn(self, turn):
        if turn < len(self.past_grids):
            return self.past_grids[turn]
        else:
            return None
