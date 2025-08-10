from src.logic.entities.factories import Factory
from src.io import models
from src.io.models import PopModel, StructureModel, ResourceModel, BiomeModel, WorldModel, EffectModel


def make_factory_from_models(all_models):
    """
    Generate a model storage object with models sorted into categories.
    """

    result = Factory()

    for model in all_models:
        if isinstance(model, PopModel):
            entity = models.create_from_model(model)
            result.populations[entity.name] = entity
        elif isinstance(model, StructureModel):
            entity = models.create_from_model(model)
            result.structures[entity.name] = entity
        elif isinstance(model, ResourceModel):
            entity = models.create_from_model(model)
            result.resources[entity.name] = entity
        elif isinstance(model, BiomeModel):
            entity = models.create_from_model(model)
            result.biomes[entity.name] = entity
        elif isinstance(model, WorldModel):
            world = models.create_from_model(model)
            result.worlds[world.name] = world
        elif isinstance(model, EffectModel):
            entity = models.create_from_model(model)
            result.misc[entity.name] = entity

    return result