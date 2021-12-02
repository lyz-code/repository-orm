"""Tests the entity model."""

import pytest

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


def test_hash_uses_the_entity_id_and_model_name() -> None:
    """
    Given: A configured entity.
    When: The __hash__ method is used.
    Then: The hash of the identity and model name are used
    """
    entity = Entity(id_=1)

    result = entity.__hash__()

    assert result == hash("Entity-1")


def test_model_name_returns_expected_name() -> None:
    """
    Given: An entity
    When: model_name is called
    Then: The name of the model is returned
    """
    entity = Entity()

    result = entity._model_name

    assert result == "Entity"


def test_compare_less_than_entities_with_string_ids() -> None:
    """Comparison between entities is done by the ID attribute on string IDS."""
    small = Entity(id_="a")
    big = Entity(id_="b")

    result = small < big

    assert result


def test_compare_greater_than_entities_with_string_ids() -> None:
    """Comparison between entities is done by the ID attribute on string IDS."""
    small = Entity(id_="a")
    big = Entity(id_="b")

    result = big > small

    assert result


def test_compare_less_than_entities_cant_compare_string_and_id() -> None:
    """Raise TypeError if one object id is a string and the other an int"""
    entity_string = Entity(id_="a")
    entity_int = Entity(id_=1)

    with pytest.raises(TypeError):
        entity_string < entity_int  # noqa: B015, W0104


def test_compare_greater_than_entities_cant_compare_string_and_id() -> None:
    """Raise TypeError if one object id is a string and the other an int"""
    entity_string = Entity(id_="a")
    entity_int = Entity(id_=1)

    with pytest.raises(TypeError):
        entity_string > entity_int  # noqa: B015, W0104
