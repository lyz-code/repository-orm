"""Test the implementation of the data repository cache."""

import pytest
from tests.cases.model import Entity

from repository_orm.adapters.data.cache import Cache


def test_cache_can_add_list_of_entities() -> None:
    """
    Given: Two entities
    When: added as a list
    Then: they are added
    """
    entities = [
        Entity(id_=0, name="First"),
        Entity(id_=1, name="Second"),
    ]
    cache = Cache()

    cache.add(entities)  # act

    assert cache.get(entities[0]) == entities[0]
    assert cache.get(entities[1]) == entities[1]


def test_cache_is_immutable_on_external_changes() -> None:
    """
    Given: An entry in the cache
    When: an external function changes the entity
    Then: the cached version is unchanged
    """
    entity = Entity(name="Original name")
    cache = Cache()
    cache.add(entity)
    entity.name = "Modified name"

    result = cache.get(entity)

    assert result.name == "Original name"
    assert not cache.entity_has_not_changed(entity)


def test_cache_can_remove_entity() -> None:
    """
    Given: An entry in the cache
    When: calling remove
    Then: the cached version is removed
    """
    entity = Entity(name="Original name")
    cache = Cache()
    cache.add(entity)

    cache.remove(entity)  # act

    with pytest.raises(KeyError):
        cache.get(entity)


def test_cache_can_remove_entities() -> None:
    """
    Given: Many entities in the cache
    When: calling remove
    Then: the cached version are removed
    """
    entity = Entity(name="Original name")
    cache = Cache()
    cache.add(entity)

    cache.remove([entity, entity])  # act

    with pytest.raises(KeyError):
        cache.get(entity)
