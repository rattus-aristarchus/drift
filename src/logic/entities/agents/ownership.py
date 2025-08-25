from src.logger import CustomLogger

logger = CustomLogger(__name__)


def set_ownership(agent, resource, amount=None):
    """
    Сделать agent владельцем amount ресурса resource.
    """

    if amount is None:
        resource.owners[agent.name] = resource.size
        if resource not in agent.owned_resources:
            agent.owned_resources.append(resource)

    elif amount <= 0:
        resource.owners.pop(agent.name, None)
        if resource in agent.owned_resources:
            agent.owned_resources.remove(resource)

    else:
        resource.owners[agent.name] = amount
        if resource not in agent.owned_resources:
            agent.owned_resources.append(resource)

        ttl_owned = _get_ttl_owned(resource)
        if ttl_owned > resource.size:
            logger.error(
                f"owned {resource.name} ({ttl_owned}) exceeded total "
                f"amount of that resource ({resource.size}) when trying "
                f"to add {amount} owned by {agent.name}"
            )


def _get_ttl_owned(resource):
    ttl = 0

    for agent, size in resource.owners.items():
        ttl += size

    return ttl


def add_ownership(agent, resource, amount):
    if amount <= 0:
        return

    if agent.name not in resource.owners.keys():
        set_to = amount
    else:
        set_to = resource.owners[agent.name] + amount

    set_ownership(agent, resource, set_to)


def subtract_ownership(agent, resource, amount):
    if amount <= 0:
        return

    if agent.name not in resource.owners.keys():
        logger.warning(f"trying to subtract {amount} of ownership "
                       f"by agent {agent.name} from resource {resource.name} that "
                       f"doesn't have that owner")
        return

    current = resource.owners[agent.name]

    set_ownership(agent, resource, current - amount)
