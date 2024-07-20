import pytest
from src.logic.effects import util


def test_growth_with_capacity():
    result = util.growth_with_capacity(1000, 10000, 0.05)

    assert result == 45
