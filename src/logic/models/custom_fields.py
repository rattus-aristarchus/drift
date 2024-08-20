import dataclasses


def model_list():
    """
    Список, содержащий ссылки на другие модели.
    """
    return dataclasses.field(
        default_factory=lambda: [],
        metadata={"type": "model_list"}
    )


def model_list_list():
    """
    Список, содержащий ссылки на другие модели.
    """
    return dataclasses.field(
        default_factory=lambda: [],
        metadata={"type": "model_list_list"}
    )
