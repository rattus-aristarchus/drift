from src.logic.effects.agent_effects import migration
from src.logic.entities.agents import agents
from src.logic.entities.agents.populations import Population, Need
from src.logic.entities.agents.resources import Resource
from src.logic.entities.basic import recurrents
from src.logic.entities.cells import Cell


def test_migration_brings_along_resources(init_factory):
    """
    When migrating, alongside the migrating pop a
    part of its property should be brought along.
    """

    cell_a = Cell()
    cell_b = Cell()
    cell_a.neighbors.append(cell_b)
    cell_b.neighbors.append(cell_a)
    pop_a = Population(
        name="test_pop",
        size=1000,
        mobility=0.1,
        needs=[Need(per_1000=1000,actual=500)]
    )
    pop_b = Population(
        name="test_pop",
        size=0,
        needs=[Need(per_1000=1000,actual=1000)]
    )
    cell_a.pops.append(pop_a)
    cell_b.pops.append(pop_b)
    res_a = Resource(name="test_res",size=1000)
    cell_a.resources.append(res_a)
    agents.set_ownership(pop_a, res_a)
    cell_a, all_recurrents = recurrents.copy_recurrent_and_add_to_list(cell_a, {})
    cell_b, all_recurrents = recurrents.copy_recurrent_and_add_to_list(cell_b, all_recurrents)

    migration.migrate(cell_a.pops[0], cell_a)
    pop_b = cell_b.pops[0]

    assert pop_b.size == 50
    assert len(pop_b.owned_resources) == 1
    assert pop_b.owned_resources[0].size == 50
