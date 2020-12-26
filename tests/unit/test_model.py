"""Tests the model layer."""

import pytest

from repository_pattern import Entity


def test_compare_less_than_entities() -> None:
    """Comparison between entities is done by the ID attribute."""
    small = Entity(ID=1)
    big = Entity(ID=2)

    result = small < big

    assert result


def test_compare_greater_than_entities() -> None:
    """Comparison between entities is done by the ID attribute."""
    small = Entity(ID=1)
    big = Entity(ID=2)

    result = big > small

    assert result


def test_compare_less_than_entities_with_string_ids() -> None:
    """Comparison between entities is done by the ID attribute on string IDS."""
    small = Entity(ID="a")
    big = Entity(ID="b")

    result = small < big

    assert result


def test_compare_greater_than_entities_with_string_ids() -> None:
    """Comparison between entities is done by the ID attribute on string IDS."""
    small = Entity(ID="a")
    big = Entity(ID="b")

    result = big > small

    assert result


def test_compare_less_than_entities_cant_compare_string_and_id() -> None:
    """Raise TypeError if one object id is a string and the other an int"""
    entity_string = Entity(ID="a")
    entity_int = Entity(ID=1)

    with pytest.raises(TypeError):
        entity_string < entity_int  # noqa: B015, W0104


def test_compare_greater_than_entities_cant_compare_string_and_id() -> None:
    """Raise TypeError if one object id is a string and the other an int"""
    entity_string = Entity(ID="a")
    entity_int = Entity(ID=1)

    with pytest.raises(TypeError):
        entity_string > entity_int  # noqa: B015, W0104


def test_hash_uses_the_entity_id() -> None:
    """
    Given: A configured entity.
    When: The __hash__ method is used.
    Then: The hash of the identity is used
    """
    entity = Entity(ID=1)

    result = entity.__hash__()

    assert result == hash(1)
