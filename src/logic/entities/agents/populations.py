import dataclasses
import os

from src.logic.entities.agents.agents import Agent
from src.logic.entities.basic import recurrents
from src.logic.entities.basic.entities import Entity
from src.logic.entities.basic.recurrents import Recurrent
from src.logic.models import PopModel, NeedModel


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

    owned_resources: list = recurrents.relations_list()

    # what fraction of labor is spent on what (not used right now)
  #  effort: dict = field(default_factory=lambda: {})
    # how much surplus did each production net (not used right now)
  #  surplus: dict = field(default_factory=lambda: {})

    needs: list = recurrents.deep_copy_list()

    def __str__(self):
        if self.type == "":
            title = f"{self.name}"
        else:
            title = f"{self.name} ({self.type})"
        description = (
            f"{title}: {self.size}{os.linesep}"
            f"возраст: {self.age}")
        return description

    def get_need(self, need_type="", need_id=""):
        if need_type != "":
            for need in self.needs:
                if need.model.type == need_type:
                    return need

        elif need_id != "":
            for need in self.needs:
                if need.model.id == need_id:
                    return need

        return None


@dataclasses.dataclass
class Need(Entity):
    """
    Потребность популяции в определенных ресурсах.
    """

    # сколько нужно на 1000 популяции
    per_1000: int = 0
    # сколько реально есть
    actual: int = 0


def create_pop(model: PopModel, destination=None):
    new_pop = Population(
        name=model.id,
        effects=list(model.effects),
        sapient=model.sapient,
        type=model.type,
        yearly_growth=model.yearly_growth
    )
    new_pop.model = model

    needs = []
    for need_model in model.needs:
        needs.append(create_need(need_model))
    new_pop.needs = needs

    if destination:
        destination.pops.append(new_pop)

    return new_pop


def create_need(model: NeedModel):
    result = Need(
        per_1000=model.per_1000,
        # если не выставить actual, то нулевой год всегда
        # будет адом
        actual=model.per_1000
    )
    result.model = model
    return result

