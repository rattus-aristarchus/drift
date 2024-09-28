import pytest

from src.logic.effects.agent_effects import migration
from src.logic.entities.agents import agents
from src.logic.entities.agents.populations import Population, Need
from src.logic.entities.agents.resources import Resource
from src.logic.entities.basic import recurrents
from src.logic.entities.cells import Cell
from src.logic.entities.grids import Grid


@pytest.fixture
def two_cell_grid():
    grid = Grid()

    cell_a = Cell(x=0, y=0)
    cell_b = Cell(x=1, y=0)
    cell_a.neighbors.append(cell_b)
    cell_b.neighbors.append(cell_a)

    grid.cells = {
        0: {0: cell_a},
        1: {0: cell_b}
    }
    return grid


@pytest.fixture
def mig_setup(two_cell_grid):
    cell_a = two_cell_grid.cells[0][0]
    cell_b = two_cell_grid.cells[1][0]
    pop_a = Population(
        name="test_pop",
        size=1000,
        mobility=0.1,
        needs=[Need(per_1000=1000, actual=500)]
    )
    pop_b = Population(
        name="test_pop",
        size=1,
        # при оценки привлекательности миграции не принимаются в
        # расчет популяции возраста 0, поскольку для них еще не
        # выполнен расчет потребностей
        age=1,
        needs=[Need(per_1000=1000, actual=1000)]
    )
    cell_a.pops.append(pop_a)
    cell_b.pops.append(pop_b)
    res_a = Resource(name="test_res",size=1000)
    cell_a.resources.append(res_a)
    agents.set_ownership(pop_a, res_a)
    new_grid, all_recurrents = recurrents.copy_recurrent_and_add_to_list(two_cell_grid, {})
    return new_grid, cell_a.next_copy, cell_b.next_copy, pop_a.next_copy, pop_b.next_copy


def test_brownian_migration_creates_pop(init_factory, two_cell_grid):
    cell_a = two_cell_grid.cells[0][0]
    cell_b = two_cell_grid.cells[1][0]
    cell_a.pops.append(
        Population(name="test_pop", size=1000, looks_for=["test_res"])
    )
    cell_b.resources.append(
        Resource(name="test_res", size=1)
    )
    recurrents.copy_recurrent_and_add_to_list(two_cell_grid, {})

    migration.brownian_migration(cell_a.next_copy.pops[0], cell_a.next_copy)

    assert len(cell_b.next_copy.pops) == 1
    assert cell_b.next_copy.pops[0].size == 1


def test_migration_brings_along_resources(init_factory, mig_setup):
    """
    When migrating, alongside the migrating pop a
    part of its property should be brought along.
    """
    grid = mig_setup[0]
    cell_a = mig_setup[1]
    cell_b = mig_setup[2]
    pop_a = mig_setup[3]
    pop_b = mig_setup[4]

    migration.migrate(pop_a, cell_a)

    assert pop_b.size == 51
    assert len(pop_b.owned_resources) == 1
    assert pop_b.owned_resources[0].size == 50


def test_migration_cant_be_negative(init_factory, mig_setup):
    grid = mig_setup[0]
    cell_a = mig_setup[1]
    cell_b = mig_setup[2]
    pop_a = mig_setup[3]
    pop_b = mig_setup[4]
    pop_a.last_copy.needs = [Need(per_1000=1000, actual=1000)]
    pop_b.last_copy.needs = [Need(per_1000=1000, actual=500)]
    pop_b.last_copy.size = 1

    migration.migrate(pop_a, cell_a)

    assert pop_b.size == 1
