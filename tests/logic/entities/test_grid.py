import ast

import pytest

from src.logic.computation import GridCPU
from src.logic.entities import grids
from src.logic.entities.agents.structures import Structure
from src.logic.entities.cells import Cell
from src.logic.entities.grids import Grid
from src.logic.entities.histories import World


def test_increase_grid_age(fresh_grid):
    grids.increase_age_for_everything(fresh_grid, 2)

    assert fresh_grid.cells[0][0].pops[0].age == 2


@pytest.fixture
def cell_representation():
    return '{"biome": "test_biome"}'

"""
def test_create_cell_from_dict(cell_representation, model_base):
    cell_dict = ast.literal_eval(cell_representation)
    cell = grids.create_cell_from_dict(0, 0, cell_dict, model_base)

    assert cell.biome.name == "test_biome"
"""

class __EffectSpy:
    calls: int = 0


@pytest.fixture
def effect_spy():
    spy = __EffectSpy()

    def __effect(structure, buffer):
        spy.calls += 1

    yield __effect, spy


def test_effect_calls_for_structures_are_not_repeated(effect_spy):
    grid = Grid()
    cell_0 = Cell()
    cell_1 = Cell()
    grid.cells[0] = {0: cell_0}
    grid.cells[1] = {0: cell_1}
    structure = Structure()
    effect, spy = effect_spy
    structure.effects.append(effect)
    cell_0.structures.append(structure)
    cell_1.structures.append(structure)
    grid.structures.append(structure)
    cpu = GridCPU(World())
    cpu.refresh_cpus(grid)

    cpu.do_effects()

    assert spy.calls == 1


def test_get_neighbors():
    grid = Grid()
    a = Cell(name="a")
    b = Cell(name="b")
    c = Cell(name="c")
    d = Cell(name="d")
    e = Cell(name="e")
    f = Cell(name="f")
    grid.cells = {
        0: {
            0: a,
            1: b,
            2: c
        },
        1: {
            0: d,
            1: e,
            2: f
        }
    }

    grids.set_neighbors_for_cells(grid)

    assert len(a.neighbors) == 3
    assert b in a.neighbors
    assert d in a.neighbors
    assert c not in a.neighbors
