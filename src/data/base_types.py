from util import CONST
from storage import Output


class Grid:

    def __init__(self, height, width):
        self.width = width
        self.height = height
        #dict of dicts
        self.cells = {}
        self.watched_cells = []
        self.output = Output()

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
