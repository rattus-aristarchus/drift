"""
Effects for agents are specified in .yml files; in order to
provide the data classes access to functions from effects files
without circular references, get_effects functions are specified
in effects files and then injected into data classes at initialization
"""

from . import storage
from src.logic.effects import pop_effect, structure_effects, world_effects, cell_effects, resource_effects

storage.get_structure_effect = structure_effects.get_effect
storage.get_pop_effect = pop_effect.get_effect
storage.get_cell_effect = cell_effects.get_effect
storage.get_world_effect = world_effects.get_effect
storage.get_resource_effect = resource_effects.get_effect
