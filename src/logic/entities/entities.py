import dataclasses

from src.logic import util
from src.logic.models import Model


@dataclasses.dataclass
class Entity:
    """
    База
    """

    name: str = ""
    # при создании новой итерации модели все сущности
    # копируются в нее; last_copy - ссылка на сущность
    # в прошлой итерации; next_copy - ссылка на следующую
    # сущность
    last_copy = None
    next_copy = None
    model: Model = None


def copy_entity(entity):
    copy = util.copy_dataclass_with_collections(entity)
    copy.last_copy = entity
    entity.next_copy = copy
    return copy
