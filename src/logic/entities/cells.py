import dataclasses
import os
from dataclasses import field
from kivy import Logger
from src.logic.computation import Agent
from src.logic.entities.basic import custom_fields, entities
from src.logic.entities.basic.entities import Entity
from src.logic.entities.basic.recurrents import Recurrent


@dataclasses.dataclass
class Biome(Entity):
    """
    Экология клетки карты.
    """

    # сколько популяций или ресурсов может вместить данная клетка:
    capacity: dict = dataclasses.field(default_factory=lambda: {})
    starting_resources: list = dataclasses.field(default_factory=lambda: [])
    moisture: str = ""

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
    neighbors: list = custom_fields.relations_list()

    markets: list = field(default_factory=lambda: [])
    pops: list = custom_fields.relations_list()
    structures: list = custom_fields.relations_list()
    resources: list = custom_fields.relations_list()
    biome: Biome = None

    # словарь имя популяци / привлекательность для миграции
    # или социального лифта
    draw: dict = field(default_factory=lambda: {})
    # трудность миграции / социального лифта
    barrier: dict = field(default_factory=lambda: {})


    def on_copy(self, original, all_recurrents):
        # рынкам ничего от прошлой итерации сохранять не нужно
        self.markets = []
        return all_recurrents

    def get_pop(self, name):
        return entities.get_entity(name, self.pops)

    def get_res(self, name):
        return entities.get_entity(name, self.resources)

    def has_res_type(self, type):
        for res in self.resources:
            if res.type == type:
                return True
        return False


def add_territory(cell, structure):
    if structure not in cell.structures:
        cell.structures.append(structure)
    if cell not in structure.territory:
        structure.territory.append(cell)


def _find_structure(name, cell):
    for group in cell.structures:
        if group.name == name:
            return group
    return None


def increase_age_for_everything(cell, value=1):
    for pop in cell.pops:
        pop.age += value


def create_cell(x, y, biome_name, factory):
    result = Cell(x=x, y=y)
    biome = factory.new_biome(biome_name)
    if biome is None:
        Logger.error(f"Trying to create cell with invalid biome name: {biome}")
    else:
        result.biome = biome
    Logger.debug(f"Creating cell at ({str(x)},{str(y)}) with biome {biome_name}")
    for res_name, size in biome.starting_resources:
        resource = factory.new_resource(res_name, result)
        resource.size = size
        Logger.debug(f"Adding {str(size)} of resource {res_name}")
    return result
