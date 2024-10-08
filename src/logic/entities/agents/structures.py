import dataclasses
from dataclasses import field

from src.logic.entities.basic import custom_fields, entities
from src.logic.entities.agents.agents import Agent
from src.logic.entities.agents.resources import Resource
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

    def do_effects(self, cell_buffer=None, grid_buffer=None):
        for func in self.effects:
            func(self, grid_buffer)

    def get_res(self, name):
        return entities.get_entity(name, self.resources)

    def get_pop(self, name):
        return entities.get_entity(name, self.pops)


@dataclasses.dataclass
class Commodity:

    seller: Agent = None
    amount: int = 0


@dataclasses.dataclass
class Market(Agent):

    # рынок создается для каждого отдельного вида продукта
    product: Resource = None
    type: str = ""
    exchange: Resource = None
    sale: Commodity = None
    purchases: list[Commodity] = field(default_factory=lambda: [])
    price: float = 0.0
