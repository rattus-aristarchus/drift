import pytest

from src.logic.entities import structures, cells
from src.logic.entities.cells import Cell
from src.logic.entities.grids import Grid
from src.logic.entities.structures import Structure


def test_copy_transfers_territory():
    old_cell = Cell(
        name="old_cell",
        x=0,
        y=0
    )
    new_cell = cells.copy_cell_without_structures(old_cell)
    new_cell.name = "new_cell"
    new_grid = Grid()
    new_grid.cells = {0: {0: new_cell}}
    structure = Structure()
    structure.territory.append(old_cell)

    new_structure = structures.copy_structure(structure, grid=new_grid)

    assert len(new_structure.territory) == 1
    assert new_structure.territory[0] == new_cell
