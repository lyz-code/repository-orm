"""Tests the model layer."""

from repository_orm import Entity


def test_compare_less_than_entities() -> None:
    """Comparison between entities is done by the ID attribute."""
    small = Entity(id_=1)
    big = Entity(id_=2)

    result = small < big

    assert result


def test_compare_greater_than_entities() -> None:
    """Comparison between entities is done by the ID attribute."""
    small = Entity(id_=1)
    big = Entity(id_=2)

    result = big > small

    assert result


def test_hash_uses_the_entity_id() -> None:
    """
    Given: A configured entity.
    When: The __hash__ method is used.
    Then: The hash of the identity is used
    """
    entity = Entity(id_=1)

    result = entity.__hash__()

    assert result == hash(1)


def test_model_name_returns_expected_name() -> None:
    """
    Given: An entity
    When: model_name is called
    Then: The name of the model is returned
    """
    entity = Entity()

    result = entity._model_name

    assert result == "Entity"
