import dataclasses
import os
from dataclasses import field

from src.logic.entities.basic import custom_fields, entities
from src.logic.computation import Agent
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

    def do_effects(self, cell, buffer):
        for func in self.effects:
            func(self, buffer)

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

    def __str__(self):
        if self.product is not None:
            title = f"{self.product.name}"
        elif self.type != "":
            title = f"{self.type}"
        else:
            title = f"просто рынок"

        if self.exchange:
            exchange_str = self.exchange.name
        else:
            exchange_str = ""

        description = (
            f"{title} - {exchange_str}{os.linesep}"
            f"цена: {self.price}")
        return description
