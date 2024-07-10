from src.data.base_types import Population, Group
from src.util import CONST


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


def copy_cell(old_cell):
    new_cell = Cell(old_cell.x, old_cell.y)
    new_cell.caps = dict(old_cell.caps)
    for pop in old_cell.pops:
        pop.copy_pop(new_cell)
    for group in old_cell.groups:
        new_cell.create_group(group.name)
    return new_cell


def increase_age(cell, value=1):
    for pop in cell.pops:
        pop.age += value


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
