"""
Effects for agents are specified in .yml files; in order to
provide the data classes access to functions from effects files
without circular references, get_effects functions are specified
in effects files and then injected into data classes at initialization
"""

from . import storage
from src.logic.effects import pop_effects, group_effects, world_effects, cell_effects


storage.get_group_effect = group_effects.get_effect
storage.get_pop_effect = pop_effects.get_effect
storage.get_cell_effect = cell_effects.get_effect
storage.get_world_effect = world_effects.get_effect
