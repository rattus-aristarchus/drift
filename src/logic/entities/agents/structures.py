import dataclasses

from src.logic.entities.basic import custom_fields, entities
from src.logic.entities.agents.agents import Agent
from src.logic.entities.basic.recurrents import Recurrent


@dataclasses.dataclass
class Structure(Agent, Recurrent):
    """
    Социальные структуры, состоящие из нескольких
    популяций / территорий (города, государства, рынки).
    """

    pops: list = custom_fields.relations_list()
    # a list of cells
    territory: list = custom_fields.relations_list()
    resources: list = custom_fields.relations_list()

    def do_effects(self, structure_read, cell_write, cell_read, buffer):
        for func in self.effects:
            func(self, structure_read, buffer)

    def get_res(self, name):
        return entities.get_entity(name, self.resources)

    def get_pop(self, name):
        return entities.get_entity(name, self.pops)
