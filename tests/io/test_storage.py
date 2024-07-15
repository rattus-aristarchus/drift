import os.path
from src.io import storage
from tests.conftest import RESOURCES_DIR


def test_load_map():
    path = os.path.join(RESOURCES_DIR, "map.csv")

    map = storage._load_map(path)
    assert map.cell_matrix[0][1] == "id:00,links:[0]"
