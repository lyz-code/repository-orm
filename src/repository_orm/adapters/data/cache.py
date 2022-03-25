"""Define the cache of the data repositories."""

from contextlib import suppress
from typing import Any, Dict, Sequence, Type, TypeVar, Union

from ...model import Entity as EntityModel
from ...model import EntityID

Entity = TypeVar("Entity", bound=EntityModel)
CacheEntry = Dict[EntityID, Entity]
EntityOrEntities = Union[Sequence[EntityModel], EntityModel]


class Cache:
    """Define the cache of a repository.

    The entries are saved in the `cache` attribute under a dictionary similar to:
    {
        Model_1: {
            Entity_1_ID: Entity_1,
            Entity_2_ID: Entity_2,
        },
    }

    """

    def __init__(self) -> None:
        """Initialize the class."""
        self.cache: Dict[Type[EntityModel], CacheEntry[Any]] = {}

    def add(self, entity_or_entities: EntityOrEntities) -> None:
        """Add an entity to the cache."""
        if isinstance(entity_or_entities, EntityModel):
            entities = [entity_or_entities]
        else:
            entities = list(entity_or_entities)

        for entity in entities:
            self.cache.setdefault(type(entity), {})
            self.cache[type(entity)].setdefault(entity.id_, entity.copy())

    def get(self, entity: Entity) -> Entity:
        """Return the cached value of an entity."""
        return self.cache[type(entity)][entity.id_]

    def entity_has_not_changed(self, entity: Entity) -> bool:
        """Check if entity is equal to the version in the cache."""
        try:
            if self.get(entity) == entity:
                return True
        except KeyError:
            return False
        return False

    def remove(self, entity_or_entities: EntityOrEntities) -> None:
        """Remove an entity from the cache if it exists."""
        if isinstance(entity_or_entities, EntityModel):
            entities = [entity_or_entities]
        else:
            entities = list(entity_or_entities)

        for entity in entities:
            with suppress(KeyError):
                self.cache[type(entity)].pop(entity.id_)
