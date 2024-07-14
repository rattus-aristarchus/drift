import os.path
from src.io import storage


def test_load_map():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')
    path = os.path.join(RESOURCES_DIR, "map.csv")

    map = storage._load_map(path)
    assert map.cells[0] == "id:0,links:[1,00]"
