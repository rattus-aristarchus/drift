import ast

import pytest

from src.logic.computation import CPU
from src.logic.entities import grids, histories
from src.logic.entities.agents.structures import Structure
from src.logic.entities.cells import Cell
from src.logic.entities.grids import Grid
from src.logic.entities.histories import History
from src.logic.entities.worlds import World


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

    def __effect(structure, structure_read, buffer):
        spy.calls += 1

    yield __effect, spy


@pytest.fixture
def cpu_with_history():
    grid = Grid()
    cell_0 = Cell(name="first cell")
    cell_1 = Cell(name="second cell")
    grid.cells[0] = {0: cell_0}
    grid.cells[1] = {0: cell_1}
    world = World()
    history = History(world)
    history.past_grids.append(grid)
    cpu = CPU(
        world,
        lambda: histories._create_intermediate_grid(history)
    )
    cpu.refresh_cpus(grid)

    return cpu, history

def test_effect_calls_for_structures_are_not_repeated(effect_spy, cpu_with_history):
    cpu, history = cpu_with_history
    effect, spy = effect_spy
    structure = Structure()
    structure.effects.append(effect)
    grid = cpu.grid
    grid.cells[0][0].structures.append(structure)
    grid.cells[1][0].structures.append(structure)
    grid.structures.append(structure)
    cpu.grid = histories._create_intermediate_grid(history)

    cpu.do_effects()

    assert spy.calls == 1

class __GridSpy:
    calls: int = 0
    grids: list = []
    grid_cpu: CPU = None
    proper_grid_call = None


@pytest.fixture
def grid_spy():
    spy = __GridSpy()

    def __create_intermediate_grid():
        spy.calls += 1
        new_grid = spy.proper_grid_call()
        spy.grids.append(new_grid)
        return new_grid

    yield __create_intermediate_grid, spy


def test_intermediate_grids_are_created(cpu_with_history, grid_spy):
    callback, spy = grid_spy
    cpu, history = cpu_with_history
    spy.grid_cpu = cpu
    spy.proper_grid_call = cpu._create_intermediate_grid
    cpu._create_intermediate_grid = callback
    first_cell = cpu.grid.cells[0][0]
    world_effect = lambda a, b, c: None
    effect = lambda a, b, c, d, e: None
    cpu.effects.append(world_effect)
    cpu.pop_effects.append(effect)
    cpu.pop_effects.append(effect)
    cpu.res_effects.append(effect)

    cpu.do_effects()

    assert spy.calls == 3
    third_cell = spy.grids[-2].cells[0][0]
    fourth_cell = spy.grids[-1].cells[0][0]
    assert third_cell.next_copy == fourth_cell
    assert fourth_cell.last_copy == third_cell


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
