import pytest

from src.data import cells


def sample_effect():
    return "effect executed"


@pytest.fixture
def sample_cell():
    return cells.create_cell(0, 0)