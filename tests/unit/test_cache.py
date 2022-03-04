"""Test the implementation of the data repository cache."""

import pytest
from tests.cases.model import Entity

from repository_orm.adapters.data.cache import Cache


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

    cache.remove([entity, entity])  # type: ignore # act

    with pytest.raises(KeyError):
        cache.get(entity)
