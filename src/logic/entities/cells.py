import dataclasses
import os
from dataclasses import field

from src.logic.entities.agents import resources
from src.logic.entities.basic import custom_fields
from src.logic.entities.basic.entities import Entity
from src.logic.entities.basic.recurrents import Recurrent
from src.logic.models.models import BiomeModel


@dataclasses.dataclass
class Biome(Entity):
    """
    Экология клетки карты.
    """

    model: BiomeModel = None
    # сколько популяций или ресурсов может вместить данная клетка:
    capacity: dict = dataclasses.field(default_factory=lambda: {})

    def __str__(self):
        description = self.name
        if len(self.capacity) > 0:
            description += f"{os.linesep}вместимость:"
            for pop_type, amount in self.capacity.items():
                description += f"{os.linesep}{pop_type}: {amount}"
        return description

    def get_capacity(self, pop_name):
        if pop_name in self.capacity.keys():
            return self.capacity[pop_name]
        else:
            return 0


@dataclasses.dataclass
class Cell(Entity, Recurrent):
    """
    Клетка карты.
    """

    x: int = 0
    y: int = 0
    effects: list = field(default_factory=lambda: [])
    markets: list = field(default_factory=lambda: [])
    pops: list = custom_fields.relations_list()
    structures: list = custom_fields.relations_list()
    resources: list = custom_fields.relations_list()
    biome: Biome = None

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

        for market in self.markets:
            market.do_effects(cell_buffer, grid_buffer)

    def on_copy(self, original, all_recurrents):
        # рынкам ничего от прошлой итерации сохранять не нужно
        self.markets = []
        return all_recurrents

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

    def has_res(self, type):
        for res in self.resources:
            if res.type == type:
                return True
        return False


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


def get_pop(name, pop_list):
    for check in pop_list:
        if check.name == name:
            return check
    return None


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
        resource = resources.create_resource(res_model, result)
        resource.size = size
    return result


def create_biome(biome_model):
    result = Biome(name=biome_model.id, model=biome_model)
    if biome_model.capacity:
        result.capacity = dict(biome_model.capacity)
    return result

