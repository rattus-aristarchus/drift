import dataclasses

from src.logic import util
from src.logic.models import Model


def copy_entity(entity):
    copy = util.copy_dataclass_with_collections(entity)
    copy.last_copy = entity
    return copy


@dataclasses.dataclass
class Entity:
    """
    База
    """

    name: str = ""
    # при создании новой итерации модели все сущности
    # копируются в нее; last_copy - ссылка на сущность
    # в прошлой итерации
    last_copy = None
    model: Model = None
