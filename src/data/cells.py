from src.data import agents
from src.data.agents import Population, Group
from src.util import CONST

from kivy.logger import Logger


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
    new_cell.biome = old_cell.biome
    for group in old_cell.groups:
        agents.create_group(group.name, new_cell)
    for pop in old_cell.pops:
        new_pop = agents.copy_pop(pop, new_cell)
        if pop.group is not None:
            group = _find_group(pop.group.name, old_cell)
            if group is None:
                Logger.error(f"Copy of old pop {pop.name} at cell "
                             f"({old_cell.x},{old_cell.y}) has no "
                             f"group (should be {pop.group.name})")
            else:
                new_pop.group = group

    return new_cell


def _find_group(name, cell):
    for group in cell.groups:
        if group.name == name:
            return group
    return None


def increase_age(cell, value=1):
    for pop in cell.pops:
        pop.age += value


def create_cell(x, y):
    result = Cell(x, y)
    result.biome = CONST['biomes']['basic']
    for cap, value in result.biome['capacity'].items():
        result.caps[cap] = value

    return result


class Cell:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pops = []
        self.groups = []
        self.biome = {}
        self.caps = {}

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
