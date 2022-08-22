from util import CONST
from storage import Output


class History:

    def __init__(self, world_width, world_height):
        self.past_grids = []
        self.turn = 0
        first_grid = Grid(world_width, world_height, history=self)
        self.past_grids.append(first_grid)

    def new_turn(self):
        """
        Create a new grid for the new turn.
        """
        self.turn += 1
        old_grid = self.past_grids[-1]
        new_grid = Grid(old_grid.width, old_grid.height, history=self)
        self.past_grids.append(new_grid)
        return new_grid

    def current_state(self):
        return self.past_grids[-1]

    def state_at_turn(self, turn):
        if turn < len(self.past_grids):
            return self.past_grids[turn]
        else:
            return None


class Grid:

    def __init__(self, height, width, history):
        self.width = width
        self.height = height
        #dict of dicts
        self.cells = {}
        self.watched_cells = []
        self.output = Output()
        self.history = history

        for x in range(0, width):
            self.cells[x] = {}
            for y in range(0, height):
                cell = Cell(x, y)
                self.cells[x][y] = cell

    def cells_as_list(self):
        result = []
        for column in self.cells.values():
            result += column.values()
        return result


class Cell:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pops = []
        self.biome = CONST['biomes']['basic']
        self.caps = {}
        for cap, value in self.biome['capacity'].items():
            self.caps[cap] = value

    def do_effects(self, cell_buffer, grid_buffer):
        for pop in self.pops:
            pop.do_effects(cell_buffer, grid_buffer)

    def get_pop(self, name):
        for pop in self.pops:
            if pop.name == name:
                return pop
        return None


def migrate_and_merge(pop, start, destination):
    if pop in start.pops:
        start.pops.remove(pop)
    arrive_and_merge(pop, destination)


def arrive_and_merge(pop, destination):
    present = destination.get_pop(pop.name)
    if present is None:
        destination.pops.append(pop)
    else:
        present.size += pop.size
