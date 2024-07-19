import dataclasses
from typing import List


@dataclasses.dataclass
class MapFilter:
    """
    A map filter controls which entities are displayed on the map
    at any given moment.
    """

    name: str
    can_be_empty: bool = True
    accept_type: str = ""
    accept_key: str = ""
    accept_values: List[str] = dataclasses.field(default_factory=lambda: [])
