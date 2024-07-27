import dataclasses
from dataclasses import field

import src.logic.entities.entities
from src.logic import util
from src.logic.entities import agents
from src.logic.entities.entities import Entity
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
    new_cell = src.logic.entities.entities.copy_entity(old_cell)
    new_cell.biome = copy_biome(old_cell.biome)

    new_cell.structures = []
    for structure in old_cell.structures:
        agents.copy_structure(structure, new_cell)

    new_cell.pops = []
    for old_pop in old_cell.pops:
        # this does not replace structures that are not
        # part of this particular cell
        new_pop = agents.copy_pop(old_pop, new_cell)
        if len(old_pop.structures) > 0:
            for old_structure in old_pop.structures:
                structure = _find_structure(old_structure.name, old_cell)
                if structure is None:
                    Logger.error(f"Copy of old pop {old_pop.name} at cell "
                                 f"({old_cell.x},{old_cell.y}) has no "
                                 f"group (should be {old_pop.structures.name})")
                else:
                    new_pop.structures.append(structure)

    new_cell.resources = []
    for res in old_cell.resources:
        new_res = agents.copy_res(res, new_cell)

    return new_cell


def copy_biome(old_biome):
    result = src.logic.entities.entities.copy_entity(old_biome)
    return result


def _find_structure(name, cell):
    for group in cell.structures:
        if group.name == name:
            return group
    return None


def increase_age(cell, value=1):
    for pop in cell.pops:
        pop.age += value


def create_cell(x, y, biome_model: BiomeModel):
    result = Cell(x=x, y=y)
    result.effects = biome_model.effects
    result.biome = create_biome(biome_model)
    for res_model, size in biome_model.resources:
        resource = agents.create_resource(res_model, result)
        resource.size = size
    return result


def create_biome(biome_model):
    result = Biome(name=biome_model.id, model=biome_model)
    if biome_model.capacity:
        result.capacity = dict(biome_model.capacity)
    return result


@dataclasses.dataclass
class Biome(Entity):
    """
    Экология клетки карты.
    """

    model: BiomeModel = None
    # сколько популяций или ресурсов может вместить данная клетка:
    capacity: dict = dataclasses.field(default_factory=lambda: {})

    def get_capacity(self, pop_name):
        if pop_name in self.capacity.keys():
            return self.capacity[pop_name]
        else:
            return 0


@dataclasses.dataclass
class Cell(Entity):
    """
    Клетка карты.
    """

    x: int = 0
    y: int = 0
    pops: list = field(default_factory=lambda: [])
    structures: list = field(default_factory=lambda: [])
    effects: list = field(default_factory=lambda: [])
    resources: list = field(default_factory=lambda: [])
    biome = Biome

    def do_effects(self, cell_buffer, grid_buffer):
        for func in self.effects:
            func(self, cell_buffer, grid_buffer)

        for pop in self.pops:
            # если ссылка на last_copy отсутстввует, эта популяция
            # была создана в эту итерацию, и вычислять ее эффекты
            # не нужно
            if pop.last_copy:
                pop.do_effects(cell_buffer, grid_buffer)

        for resource in self.resources:
            if resource.last_copy:
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


