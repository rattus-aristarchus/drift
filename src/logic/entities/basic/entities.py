import dataclasses
from src.logic.models.models import Model


@dataclasses.dataclass
class Entity:
    """
    База
    """

    name: str = ""
    model: Model = None

