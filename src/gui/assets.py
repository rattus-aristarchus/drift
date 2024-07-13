import dataclasses
from typing import Dict


@dataclasses.dataclass
class Assets:

    colors: Dict = dataclasses.field(default_factory=lambda: {})


    def get_color(self, name):
        if name in self.colors.keys():
            return self.colors[name]
        else:
            return None
