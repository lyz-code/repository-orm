"""Test the implementation of the data repository cache."""

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
