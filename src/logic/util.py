import dataclasses
from dataclasses import fields


def copy_dataclass_with_collections(to_copy):
    """
    Функция dataclass.replace() копирует списки и словари
    ссылкой. Нам нужны не ссылки, а копии, их делает эта
    функция.

    :to_copy: копируемый объект; должен быть dataclass,
    иначе все упадет и я не виноват.
    """

    copy = dataclasses.replace(to_copy)

    for field in fields(type(to_copy)):
        value = getattr(to_copy, field.name)
        if isinstance(value, list) or isinstance(value, dict):
            setattr(copy, field.name, value.copy())

    return copy
