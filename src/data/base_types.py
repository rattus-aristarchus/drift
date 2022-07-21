from util import CONST


class Grid:

    def __init__(self, height, width):
        self.width = width
        self.height = height
        #dict of dicts
        self.cells = {}

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

    def get_pop(self, name):
        for pop in self.pops:
            if pop.name == name:
                return pop
        return None


class Population:

    def __init__(self, name):
        self.name = name
        self.number = 0
        self.age = 0
        self.sapient = CONST['pops'][name]['sapient']

        self.increase = None
        self.pressure = None
        self.migrate = None
