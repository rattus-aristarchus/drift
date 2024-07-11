"""
Effects for agents are specified in .yml files; in order to
provide the data classes access to functions from effects files
without circular references, get_effects functions are specified
in effects files and then injected into data classes at initialization
"""

from . import agents, histories, cells
from .effects import pop_effects, group_effects, world_effects, cell_effects


agents.get_group_effect = group_effects.get_effect
agents.get_pop_effect = pop_effects.get_effect
cells.get_cell_effect = cell_effects.get_effect
histories.get_world_effect = world_effects.get_effect

