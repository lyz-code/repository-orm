"""Define the cache of the data repositories."""

from typing import Dict, List, Type, TypeVar

from ...model import Entity, EntityID

CacheEntry = Dict[EntityID, Entity]
EntityOrEntities = TypeVar("EntityOrEntities", List[Entity], Entity)


class Cache:
    """Define the cache of a repository."""

    def __init__(self) -> None:
        """Initialize the class."""
        self.cache: Dict[Type[Entity], CacheEntry] = {}

    def add(self, entity_or_entities: EntityOrEntities) -> None:
        """Add an entity to the cache."""
        if isinstance(entity_or_entities, Entity):
            entities = [entity_or_entities]
        else:
            entities = entity_or_entities

        for entity in entities:
            self.cache.setdefault(type(entity), {})
            self.cache[type(entity)].setdefault(entity.id_, entity)

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
