import dataclasses
from typing import List


@dataclasses.dataclass
class MapFilter:
    """
    A map filter controls which entites are displayed on the map
    at any given moment.
    """

    name: str
    groups_to_show: List[str] = None
    pops_to_show: List[str] = None
    show_biome: bool = False
