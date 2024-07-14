import dataclasses
from typing import Dict


@dataclasses.dataclass
class Assets:

    colors: Dict = dataclasses.field(default_factory=lambda: {})
    icons: Dict = dataclasses.field(default_factory=lambda: {})
    map_filters: List = dataclasses.field(default_factory=lambda: [])

    def get_map_filter(self, name):
        for filter in self.map_filters:
            if filter.name == name:
                return filter
        return None

    def get_color(self, name):
        return self.get_asset(name, self.colors)

    def get_icon_name(self, name):
        return self.get_asset(name, self.icons)

    def get_asset(self, name, dictionary):
        if name in dictionary.keys():
            return dictionary[name]
        else:
            return "none"
