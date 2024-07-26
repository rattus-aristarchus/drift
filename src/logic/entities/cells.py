import dataclasses
from typing import List, Dict

from src.logic.entities import agents
from src.logic.entities.agents import Entity
from src.logic.models import BiomeModel

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


def add_territory(cell, structure):
    if structure not in cell.structures:
        cell.structures.append(structure)
    if cell not in structure.territory:
        structure.territory.append(cell)


def copy_cell(old_cell):
    new_cell = Cell(old_cell.x, old_cell.y)
    new_cell.biome = old_cell.biome
    new_cell.effects = list(old_cell.effects)
    for structure in old_cell.structures:
        agents.copy_structure(structure, new_cell)
    for pop in old_cell.pops:
        new_pop = agents.copy_pop(pop, new_cell)
        if pop.structure is not None:
            structure = _find_group(pop.structure.name, old_cell)
            if structure is None:
                Logger.error(f"Copy of old pop {pop.name} at cell "
                             f"({old_cell.x},{old_cell.y}) has no "
                             f"group (should be {pop.structure.name})")
            else:
                new_pop.structure = structure

    for res in old_cell.resources:
        new_res = agents.copy_res(res, new_cell)

    return new_cell


def _find_group(name, cell):
    for group in cell.structures:
        if group.name == name:
            return group
    return None


def increase_age(cell, value=1):
    for pop in cell.pops:
        pop.age += value


def create_cell(x, y, biome_model: BiomeModel):
    result = Cell(x, y)
    result.effects = biome_model.effects
    result.biome = create_biome(biome_model)
    return result


def create_biome(biome_model):
    result = Biome(name=biome_model.id, model=biome_model)
    if biome_model.capacity:
        result.capacity = dict(biome_model.capacity)
    return result


class Cell:
    """
    Клетка карты.
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pops = []
        self.structures = []
        self.biome = None
        self.effects = []
        self.resources = []

    def do_effects(self, cell_buffer, grid_buffer):
        for func in self.effects:
            func(self, cell_buffer, grid_buffer)
        for pop in self.pops:
            pop.do_effects(cell_buffer, grid_buffer)
        for group in self.structures:
            group.do_effects(cell_buffer, grid_buffer)
        for resource in self.resources:
            resource.do_effects(cell_buffer, grid_buffer)

    def get_pop(self, name):
        for pop in self.pops:
            if pop.name == name:
                return pop
        return None

    def get_res(self, name):
        for res in self.resources:
            if res.name == name:
                return res
        return None


@dataclasses.dataclass
class Biome(Entity):
    """
    Экология клетки карты.
    """

    model: BiomeModel = None
    # сколько популяций или ресурсов может вместить данная клетка:
    capacity: Dict = dataclasses.field(default_factory=lambda: {})

    def get_capacity(self, pop_name):
        if pop_name in self.capacity.keys():
            return self.capacity[pop_name]
        else:
            return 0
