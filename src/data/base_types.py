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
        new_grid = old_grid.copy_grid(self)
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

    def __init__(self, width, height, history, old_grid=None):
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
                if old_grid is None:
                    cell = Cell(x, y)
                else:
                    cell = old_grid.cells[x][y].copy_cell()
                self.cells[x][y] = cell

        if old_grid is not None:
            for cell in old_grid.watched_cells:
                self.watched_cells.append(self.cells[cell.x][cell.y])

    def cells_as_list(self):
        result = []
        for column in self.cells.values():
            result += column.values()
        return result

    def copy_grid(self, history):
        new_grid = Grid(self.width,
                        self.height,
                        history,
                        old_grid=self)
        return new_grid


class Agent:

    def __init__(self, name):
        self.name = name
        self.effects = []

    def do_effects(self, cell_buffer, grid_buffer):
        pass


class Group(Agent):

    def __init__(self, name):
        super().__init__(name)
        self.pops = []
        # a list of cells
        self.territory = []

   # def copy_group(self, destination):
    #    new_group = destination.create_group(self.name)
     #   new_group.pops =
        # TODO: allright, this is a really big problem. here we need not the pops
        # in the old group, but the new pops at the new cell
        # maybe this is a sign that my approach with creating a new grid for every turn
        # is wrong
      #  return new_group


class Population(Agent):

    def __init__(self, name):
        super().__init__(name)
        self.group = None
        self.size = 0
        self.age = 0
        self.sapient = CONST['pops'][name]['sapient']

    def do_effects(self, cell_buffer, grid_buffer):
        for func in self.effects:
            func(self, cell_buffer, grid_buffer)

    def copy_pop(self, destination):
        new_pop = Population(self.name)
        new_pop.size = self.size
        new_pop.age = self.age
        new_pop.group = self.group
        new_pop.sapient = self.sapient
        new_pop.effects = self.effects
        destination.pops.append(new_pop)
        return new_pop


class Cell:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pops = []
        self.groups = []
        self.biome = CONST['biomes']['basic']
        self.caps = {}
        for cap, value in self.biome['capacity'].items():
            self.caps[cap] = value

    def do_effects(self, cell_buffer, grid_buffer):
        for pop in self.pops:
            pop.do_effects(cell_buffer, grid_buffer)
        for group in self.groups:
            group.do_effects(cell_buffer, grid_buffer)

    def get_pop(self, name):
        for pop in self.pops:
            if pop.name == name:
                return pop
        return None

    def create_pop(self, name):
        result = Population(name)
        self.pops.append(result)
        return result

    def create_group(self, name):
        result = Group(name)
        self.groups.append(result)
        result.territory.append(self)
        return result

    def copy_cell(self):
        new_cell = Cell(self.x, self.y)
        for pop in self.pops:
            new_pop = pop.copy_pop(new_cell)
            new_pop.age += 1
        for cap, value in self.caps.items():
            new_cell.caps[cap] = value
        for group in self.groups:
            new_cell.create_group(group.name)
        return new_cell


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


def add_territory(cell, group):
    if group not in cell.groups:
        cell.groups.append(group)
    if cell not in group.territory:
        group.territory.append(cell)
