"""Tests the entity model."""

import pytest
from tests.cases.entities import BookFactory, GenreFactory
from tests.cases.model import Book

from repository_orm import Entity


class TestCompare:
    """Test the comparison of entities."""

    def test_compare_less_than_entities(self) -> None:
        """Comparison between entities is done by the ID attribute.

        2 and 10 are deliberately chosen to avoid disordering if we transform id's to
        strings.
        """
        small = Entity(id_=2)
        big = Entity(id_=10)

        result = small < big

        assert result

    def test_compare_greater_than_entities(self) -> None:
        """Comparison between entities is done by the ID attribute."""
        small = Entity(id_=2)
        big = Entity(id_=10)

        result = big > small

        assert result

    def test_compare_less_than_entities_with_string_ids(self) -> None:
        """Comparison between entities is done by the ID attribute on string IDS."""
        small = Entity(id_="a")
        big = Entity(id_="b")

        result = small < big

        assert result

    def test_compare_greater_than_entities_with_string_ids(self) -> None:
        """Comparison between entities is done by the ID attribute on string IDS."""
        small = Entity(id_="a")
        big = Entity(id_="b")

        result = big > small

        assert result

    def test_compare_less_than_entities_can_compare_string_and_id(self) -> None:
        """Comparison between entities is done by the ID attribute on string IDS."""
        entity_string = Entity(id_="a")
        entity_int = Entity(id_=1)

        result = entity_int < entity_string

        assert result

    def test_compare_greater_than_entities_can_compare_string_and_id(self) -> None:
        """Comparison between entities is done by the ID attribute on string IDS."""
        entity_string = Entity(id_="a")
        entity_int = Entity(id_=1)

        result = entity_string > entity_int

        assert result


class TestHash:
    """Test the hashing of entities."""

    def test_hash_uses_the_entity_id_and_model_name(self) -> None:
        """
        Given: A configured entity.
        When: The __hash__ method is used.
        Then: The hash of the identity and model name are used
        """
        entity = Entity(id_=1)

        result = entity.__hash__()

        assert result == hash("Entity-1")


class TestCopy:
    """Test the copy of the model."""

    def test_copy_creates_new_object_by_default(self) -> None:
        """
        Given: An entity
        When: copy is called
        Then: The returning entity is not the same object as the original, so if we
            change any attribute in the copy, the original is not changed.
        """
        entity = Entity()

        result = entity.copy()

        result.id_ = 3
        assert entity.id_ == -1


class TestModelName:
    """Test the return of the model name."""

    def test_model_name_returns_expected_name(self) -> None:
        """
        Given: An entity
        When: model_name is called
        Then: The name of the model is returned
        """
        entity = Entity()

        result = entity.model_name

        assert result == "Entity"

    @pytest.mark.skip("Wait until only versions higher than Python 3.9 are supported")
    def test_model_name_returns_expected_name_with_classes(self) -> None:
        """
        Given: An entity model
        When: model_name is called
        Then: The name of the model is returned
        """
        model = Entity

        result = model.model_name

        assert result == "Entity"  # noqa


class TestMerge:
    """Test the merging of two sources."""

    def test_cant_merge_if_not_same_model(self) -> None:
        """
        Given: Two entities with different models
        When: Trying to merge
        Then: An error is raised
        """
        original = BookFactory.build()
        other = GenreFactory.build()

        with pytest.raises(ValueError, match="Can't merge objects of different models"):
            original.merge(other)

    def test_cant_merge_if_id_is_not_equal(self) -> None:
        """
        Given: Two entities with different ids
        When: Trying to merge
        Then: An error is raised
        """
        original = BookFactory.build()
        other = BookFactory.build()

        with pytest.raises(ValueError, match="Can't merge two Books with different id"):
            original.merge(other)

    def test_merge_doesnt_overwrite_default_values(self) -> None:
        """
        Given: Two mergeable entities
        When: Trying to merge an entity with another that has attributes not set by
            the user and therefore have the default values defined in the class.
        Then: The default values are not propagated to the original entity.
        """
        original = BookFactory.build()
        original_copy = original.copy()
        other = Book(id_=original.id_, name=original.name)

        original.merge(other)  # act

        assert original.dict() == original_copy.dict()

    def test_merge_does_overwrite_defined_values(self) -> None:
        """
        Given: Two mergeable entities
        When: Merging an entity with other that has user defined values when
            initializing the object.
        Then: The manually defined attributes are updated.

            The factory manually sets all values.
        """
        original = BookFactory.build()
        other = BookFactory.build(id_=original.id_)

        original.merge(other)  # act

        assert original.dict() == other.dict()

    def test_merge_overwrites_manually_updated_value(self) -> None:
        """
        Given: Two mergeable entities
        When: Merging an entity with another where the user has updated an attribute
            value after object creation.
        Then: The manually updated attributes are propagated
        """
        original = BookFactory.build()
        other = original.copy()
        other.name = "New name"

        original.merge(other)  # act

        assert original.name == "New name"

    def test_merge_ignores_merge_skip_attributes(self) -> None:
        """
        Given: Two mergeable entities
        When: Merging an entity with another whose only changed attribute is defined
            in the class `skip_on_merge` attributes configuration.
        Then: The attribute is not propagated

        The Genre model has the `rating` attribute in the `skip_on_merge` configuration
        """
        original = GenreFactory.build()
        original_rating = original.rating
        other = original.copy()
        other.rating = 2

        original.merge(other)  # act

        assert original.rating == original_rating
