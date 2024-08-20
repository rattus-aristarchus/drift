"""
Методы - обертки для dataclasses.field.
Это поля, которые требуют особенного поведения при копировании.
Они добавляют метаданные, по которым копирующий метод их узнаёт.
"""
import dataclasses


def relations_list():
    """
    Список, содержащий ссылки на другие сущности
    класса Recurrent.
    """
    return dataclasses.field(
        default_factory=lambda: [],
        metadata={"type": "relations_list"}
    )


def relations_dict():
    """
    Словарь, содержащий ссылки на другие сущности
    класса Recurrent.
    """
    return dataclasses.field(
        default_factory=lambda: {},
        metadata={"type": "relations_dict"}
    )


def deep_copy_list():
    """
    Список, содержащий объекты, которые нужно
    скопировать, а не просто скопировать ссылки на них.
    """
    return dataclasses.field(
        default_factory=lambda: [],
        metadata={"type": "deep_copy_list"}
    )


def deep_copy_dict():
    """
    Словарь, содержащий объекты, которые нужно
    скопировать, а не просто скопировать ссылки на них.
    """
    return dataclasses.field(
        default_factory=lambda: {},
        metadata={"type": "deep_copy_dict"}
    )
