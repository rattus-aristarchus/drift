import dataclasses
from typing import Dict, List


@dataclasses.dataclass
class Assets:

    colors: Dict = dataclasses.field(default_factory=lambda: {})
    images: Dict = dataclasses.field(default_factory=lambda: {})
    map_filters: List = dataclasses.field(default_factory=lambda: [])

    def get_map_filter(self, name):
        for filter in self.map_filters:
            if filter.name == name:
                return filter
        return None

    def get_color(self, name):
        return self.get_asset(name, self.colors)

    def get_icon_name(self, name):
        return self.get_asset(name, self.images["icons"])

    def get_background_data(self, name):
        return self.get_asset(name, self.images["backgrounds"])

    def get_asset(self, name, dictionary):
        if name in dictionary.keys():
            return dictionary[name]
        else:
            return "none"
