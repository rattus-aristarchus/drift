import dataclasses
from dataclasses import field
import os
from src.logic.computation import Agent
from src.logic.entities.basic import custom_fields, entities
from src.logic.entities.basic.entities import Entity
from src.logic.entities.basic.recurrents import Recurrent


@dataclasses.dataclass
class Population(Agent, Recurrent):
    """
    Популяция. Ну блин, когда у нас исчислимое нечто, и оно что-то делает.
    """

    size: int = 0
    age: int = 0
    sapient: bool = False
    type: str = ""
    yearly_growth: float = 0.0
    # какая доля готова сняться с места при максимальном желании
    mobility: float = 0.0

    owned_resources: list = custom_fields.relations_list()
    needs: list = custom_fields.deep_copy_list()

    produces: dict = field(default_factory=lambda: {})
    sells: list = field(default_factory=lambda: [])
    looks_for: list = field(default_factory=lambda: [])


    def __str__(self):
        if self.type == "":
            title = f"{self.name}"
        else:
            title = f"{self.name} ({self.type})"
        description = (
            f"{title}: {self.size}{os.linesep}"
            f"возраст: {self.age}")
        return description

    def get_need(self, need_type="", need_name=""):
        if need_type != "":
            for need in self.needs:
                if need.type == need_type:
                    return need

        elif need_name != "":
            for need in self.needs:
                if need.name == need_name:
                    return need

        return None


    def get_resource(self, name):
        return entities.get_entity(name, self.owned_resources)


    def get_fulfilment(self):
        """
        Общая удовлетворенность ситуацией.

        Рассчитываем как среднее от удовлетворения всех потребностей.
        """
        sum_fulfilment = 0.0
        for need in self.needs:
            sum_fulfilment += need.actual / need.per_1000
        avg_fulfilment = sum_fulfilment / len(self.needs)

        return avg_fulfilment

@dataclasses.dataclass
class Need(Entity):
    """
    Потребность популяции в определенных ресурсах.
    """

    resource: str = ""
    type: str = ""
    # сколько нужно на 1000 популяции
    per_1000: int = 0
    # сколько реально есть
    actual: int = 0

