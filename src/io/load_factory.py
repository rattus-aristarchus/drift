from src.logic.entities.factory import Factory
from src.io import models
from src.io.models import PopModel, StructureModel, ResourceModel, BiomeModel


def make_factory_from_models(all_models):
    """
    Generate a model storage object with models sorted into categories.
    """

    result = Factory()

    for model in all_models:
        if isinstance(model, PopModel):
            entity = models.create_from_model(model)
            result.populations.append(entity)
        elif isinstance(model, StructureModel):
            entity = models.create_from_model(model)
            result.structures.append(entity)
        elif isinstance(model, ResourceModel):
            entity = models.create_from_model(model)
            result.resources.append(entity)
        elif isinstance(model, BiomeModel):
            entity = models.create_from_model(model)
            result.biomes.append(entity)

    return result