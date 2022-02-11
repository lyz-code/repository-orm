"""Tests the integration between the repositories and their storage layer.

The tests are all the same for all the repositories. If you want to add a new one
add them to the cases.
"""

import logging
import os
from typing import Any, List, Type

import pytest
from _pytest.logging import LogCaptureFixture
from py._path.local import LocalPath
from pydantic import ValidationError

from repository_orm import (
    AutoIncrementError,
    EntityNotFoundError,
    Repository,
    TinyDBRepository,
)
from repository_orm.exceptions import TooManyEntitiesError

from ..cases import Entity, OtherEntity, RepositoryTester
from ..cases.entities import ListEntityFactory
from ..cases.model import Author, Book, BoolEntity, ListEntity


class TestDBConnection:
    """Test the connection to the databases."""

    def test_apply_repository_creates_schema(  # noqa: AAA01
        self,
        database: Any,
        empty_repo: Repository,
        caplog: LogCaptureFixture,
        repo_tester: RepositoryTester[Repository],
    ) -> None:
        """
        Given: an empty repository.
        When: the apply_migrations method is called.
        Then: The migrations are applied as expected.
        """
        caplog.set_level(logging.DEBUG)

        repo_tester.apply_migrations(empty_repo)

        repo_tester.assert_schema_exists(database, caplog)

    def test_repository_handles_inexistent_database_file(
        self, repo: Repository, tmpdir: LocalPath
    ) -> None:
        """
        Given: A database url pointing to an inexistent file
        When: the repository is initialized
        Then: The object is well initialized, and the database file is created.
            The FakeRepository should not create any file, as all entities are stored in
            memory.
        """
        database_url = str(tmpdir.join("inexistent.db"))  # type: ignore

        result = repo.__class__(database_url=database_url)

        assert isinstance(result, repo.__class__)
        if result.__class__.__name__ != "FakeRepository":
            assert os.path.isfile(database_url)
        result.close()

    def test_repository_handles_connection_errors(self, repo: Repository) -> None:
        """
        Given: A database url pointing to an inexistent file
        When: the repository is initialized with an inexistent directory
        Then: a ConnectionError is raised. This doesn't apply to FakeRepository as it
            doesn't create a database
        """
        with pytest.raises(ConnectionError):
            repo.__class__(database_url="/inexistent_dir/database.db")  # act

    def test_repository_closes_connection(
        self, repo: Repository, repo_tester: RepositoryTester[Repository]
    ) -> None:
        """
        Given: A configured repository
        When: calling the close method
        Then: the connection to the database is closed.
        """
        repo.close()  # act

        assert repo_tester.connection_is_closed(repo)


class TestAdd:
    """Test the saving of entities."""

    def test_repository_can_save_an_entity(
        self,
        database: Any,
        repo: Repository,
        repo_tester: RepositoryTester[Repository],
        entity: Entity,
    ) -> None:
        """Saved entities remain in the repository.

        And the entity is saved to the repository cache.
        """
        repo.add(entity)

        repo.commit()  # act

        assert entity == repo_tester.get_entity(database, entity)
        assert repo.cache.get(entity) == entity

    def test_repository_can_save_an_entity_without_id_in_empty_repo(
        self,
        repo: Repository,
        int_entity: Entity,
    ) -> None:
        """
        Given: An empty repository and an entity whose id_ type is an int
        When: adding an entity without id
        Then: the id 0 is set
        """
        entity = int_entity.__class__(name="Entity without id")
        added_entity = repo.add(entity)

        repo.commit()  # act

        entities = repo.all(type(entity))
        assert len(entities) == 1
        assert added_entity.id_ == 0
        assert entities[0].id_ == 0

    def test_repository_can_save_an_two_entities_without_id_in_empty_repo(
        self,
        repo: Repository,
        int_entity: Entity,
    ) -> None:
        """
        Given: An empty repository and an entity whose id_ type is an int
        When: adding two entity without id
        Then: the ids 0 and 1 are set
        """
        first_entity = int_entity.__class__(name="First entity without id")
        second_entity = int_entity.__class__(name="Second entity without id")
        repo.add([first_entity, second_entity])  # type: ignore

        repo.commit()  # act

        entities = repo.all(type(int_entity))
        assert len(entities) == 2
        assert entities[0].id_ == 0
        assert entities[0].name == "First entity without id"
        assert entities[1].id_ == 1
        assert entities[1].name == "Second entity without id"

    def test_repository_can_save_an_entity_without_id(
        self,
        repo: Repository,
        inserted_int_entity: Entity,
    ) -> None:
        """
        Given: A repository with an entity whose id_ type is an int
        When: adding an entity without id
        Then: the id of the new entity is one unit greater than the last one.
        """
        entity = inserted_int_entity.__class__(name="Entity without id")
        repo.add(entity)

        repo.commit()  # act

        saved_entity = repo.last(type(inserted_int_entity))
        # ignore: we know that the entities have an int id_
        assert saved_entity.id_ == inserted_int_entity.id_ + 1  # type: ignore
        assert saved_entity.name == "Entity without id"

    def test_repository_can_save_two_entities_without_id_full_repo(
        self,
        repo: Repository,
        inserted_int_entity: Entity,
    ) -> None:
        """
        Given: A repository with an entity whose id_ type is an int
        When: adding two entities without id
        Then: the id of the new entities is one unit greater than the last one.
        """
        first_entity = inserted_int_entity.__class__(name="First entity without id")
        second_entity = inserted_int_entity.__class__(name="Second entity without id")
        repo.add([first_entity, second_entity])  # type: ignore

        repo.commit()  # act

        entities = repo.all(type(inserted_int_entity))
        assert len(entities) == 3
        # ignore: we know that the entities have an int id_
        assert entities[1].id_ == inserted_int_entity.id_ + 1  # type: ignore
        assert entities[1].name == "First entity without id"
        # ignore: we know that the entities have an int id_
        assert entities[2].id_ == inserted_int_entity.id_ + 2  # type: ignore
        assert entities[2].name == "Second entity without id"

    def test_repository_cant_save_an_entity_with_a_negative_id(
        self,
        repo: Repository,
        inserted_int_entity: Entity,
    ) -> None:
        """
        Given: A repository with an entity
        When: adding an entity with a negative id
        Then: the id of the new entity is one unit greater than the last one.
        """
        entity = inserted_int_entity.__class__(id=-3, name="Entity with negative id")
        repo.add(entity)

        repo.commit()  # act

        saved_entity = repo.last(type(inserted_int_entity))
        # ignore: we know for sure that the id_ is an int
        assert saved_entity.id_ == inserted_int_entity.id_ + 1  # type: ignore
        assert saved_entity.name == "Entity with negative id"

    def test_repo_add_entity_is_idempotent(
        self,
        database: Any,
        repo: Repository,
        repo_tester: RepositoryTester[Repository],
        entity: Entity,
    ) -> None:
        """
        Given: An empty repository.
        When: We insert the same entity twice and then commit.
        Then: Only one item exists.
        """
        repo.add(entity)
        repo.add(entity)

        repo.commit()  # act

        entities = repo_tester.get_all(database, type(entity))
        assert len(entities) == 1
        assert entity == entities[0]

    def test_repo_add_entity_is_idempotent_if_entity_is_commited(
        self,
        database: Any,
        repo: Repository,
        repo_tester: RepositoryTester[Repository],
        entity: Entity,
    ) -> None:
        """
        Given: A repository with the identity we want to add already commited.
        When: We insert the same entity again and then commit.
        Then: Only one item exists.
        """
        repo_tester.insert_entity(database, entity)
        repo.add(entity)

        repo.commit()  # act

        entities = repo_tester.get_all(database, type(entity))
        assert len(entities) == 1
        assert entity == entities[0]

    def test_repo_add_entity_updates_attribute(
        self,
        database: Any,
        repo: Repository,
        repo_tester: RepositoryTester[Repository],
        entity: Entity,
    ) -> None:
        """
        Given: A repository with the identity we want to add already commited.
        When: We insert the same entity with an attribute changed then commit.
        Then: Only one item exists.
        """
        repo_tester.insert_entity(database, entity)
        entity.active = False
        repo.add(entity)

        repo.commit()  # act

        entities = repo_tester.get_all(database, type(entity))
        assert len(entities) == 1
        assert not entity.active

    def test_repository_doesnt_add_an_entity_if_we_dont_commit_changes(
        self,
        database: Any,
        repo: Repository,
        repo_tester: RepositoryTester[Repository],
        entity: Entity,
    ) -> None:
        """
        Given: an empty repository.
        When: an entity is added but we don't commit the changes.
        Then: the entity is not found in the repository.
        """
        repo.add(entity)

        with pytest.raises(EntityNotFoundError):
            repo_tester.get_entity(database, entity)

    def test_repository_doesnt_allow_adding_non_entity_types(
        self,
        database: Any,
        repo: Repository,
        repo_tester: RepositoryTester[Repository],
    ) -> None:
        """
        Given: an empty repository.
        When: an object that is not an entity is added.
        Then: an error is returned.
        """
        with pytest.raises(
            ValueError, match="Please add an entity or a list of entities"
        ):
            repo.add(1)  # type: ignore

    def test_repository_doesnt_add_entities_equal_to_cache_ones(
        self,
        database: Any,
        repo: Repository,
        repo_tester: RepositoryTester[Repository],
        entity: Entity,
        caplog: LogCaptureFixture,
    ) -> None:
        """
        Given: A repository with an entity in the cache
        When: Adding the same entity
        Then: The entity is not added to the staged entities

        This way we save database calls for things that haven't changed.
        """
        caplog.set_level(logging.DEBUG)
        repo.cache.add(entity)

        repo.add(entity)  # act

        assert (
            "repository_orm.adapters.data.abstract",
            logging.DEBUG,
            f"Skipping the addition of entity {entity} as it hasn't changed",
        ) in caplog.record_tuples


class TestGet:
    """Test the retrieval of entities."""

    def test_repository_can_retrieve_an_entity(
        self,
        repo: Repository,
        inserted_entity: Entity,
    ) -> None:
        """Given an entity_id the repository returns the entity object.

        The entity is also added to the cache.
        """
        result = repo.get(inserted_entity.id_, type(inserted_entity))

        assert result == inserted_entity
        assert result.id_ == inserted_entity.id_
        assert repo.cache.get(inserted_entity) == inserted_entity

    def test_repository_can_retrieve_an_entity_if_no_model_defined(
        self,
        repo: Repository,
        inserted_entity: Entity,
    ) -> None:
        """Given an entity_id the repository returns the entity object."""
        result: Entity = repo.get(inserted_entity.id_)

        assert result == inserted_entity
        assert result.id_ == inserted_entity.id_

    def test_repository_can_retrieve_an_entity_if_list_of_models_defined(
        self,
        repo: Repository,
        inserted_entity: Entity,
    ) -> None:
        """Given an entity_id the repository returns the entity object."""
        entity_models: List[Type[Entity]] = [type(inserted_entity), OtherEntity]

        result = repo.get(inserted_entity.id_, entity_models)

        assert result == inserted_entity
        assert result.id_ == inserted_entity.id_

    def test_repository_raises_error_if_no_entity_found_by_get(
        self,
        repo: Repository,
        entity: Entity,
    ) -> None:
        """As the entity is not inserted into the repository, it shouldn't be found."""
        with pytest.raises(
            EntityNotFoundError,
            match=(
                f"There are no entities of type {entity._model_name} in the "
                f"repository with id {entity.id_}"
            ),
        ):
            repo.get(entity.id_, type(entity))

    def test_repository_raises_error_if_get_finds_more_than_one_entity(
        self, repo: Repository, inserted_entity: Entity
    ) -> None:
        """
        Given: Two entities of different type with the same ID
        When: We get the ID without specifying the model
        Then: a TooManyEntitiesError error is raised
        """
        other_entity = OtherEntity(id_=inserted_entity.id_, name="Other entity")
        repo.add(other_entity)
        repo.commit()

        with pytest.raises(TooManyEntitiesError, match=""):
            repo.get(inserted_entity.id_)


class TestAll:
    """Test the retrieval of all entities."""

    def test_repository_can_retrieve_all(
        self,
        repo: Repository,
        inserted_entities: List[Entity],
    ) -> None:
        """
        Given: A repository with inserted entities
        When: all is called
        Then: all entities are returned and saved to the repo cache.
        """
        result: List[Entity] = repo.all()

        assert result == inserted_entities
        assert len(result) == 3
        assert result[0].id_ == inserted_entities[0].id_
        for entity in result:
            assert repo.cache.get(entity) == entity

    def test_repository_can_retrieve_all_objects_of_an_entity_type(
        self,
        repo: Repository,
        inserted_entities: List[Entity],
    ) -> None:
        """Given an entity type all the entity objects that match should be returned."""
        entity_type = type(inserted_entities[0])

        result = repo.all(entity_type)

        assert result == inserted_entities
        assert len(result) == 3
        assert result[0].id_ == inserted_entities[0].id_

    def test_repository_can_retrieve_all_objects_of_a_list_of_entity_types(
        self,
        repo: Repository,
        inserted_entities: List[Entity],
    ) -> None:
        """
        Given: Three entities of a type and another of other type.
        When: all is called using a list of entities
        Then: all elements are returned.
        """
        other_entity = OtherEntity(id_=0, name="Other entity")
        repo.add(other_entity)
        repo.commit()
        entity_types: List[Type[Entity]] = [type(inserted_entities[0]), OtherEntity]

        result = repo.all(entity_types)

        assert result == inserted_entities + [other_entity]
        assert len(result) == 4

    def test_repository_all_is_idempotent(
        self,
        repo: Repository,
        inserted_entities: List[Entity],
    ) -> None:
        """
        Given: A repository that has already used the all method.
        When: all is called again.
        Then: it returns the same results.
        """
        entity_type = type(inserted_entities[0])
        expected_results = repo.all(entity_type)

        result = repo.all(entity_type)

        assert result == expected_results

    def test_repository_all_returns_empty_list_if_there_are_no_entities_of_a_type(
        self,
        repo: Repository,
        entity: Entity,
    ) -> None:
        """
        Given: An empty repo
        When: all is used with an entity type
        Then: An empty list is returned
        """
        result: List[Entity] = repo.all()

        assert result == []


class TestSearch:
    """Test the search of entities."""

    def test_repository_can_search_by_property(
        self,
        repo: Repository,
        inserted_entities: List[Entity],
    ) -> None:
        """Search should return the objects that match the desired property.

        And the entity is saved to the cache.
        """
        expected_entity = inserted_entities[1]

        result = repo.search({"id_": expected_entity.id_}, type(inserted_entities[1]))

        assert result == [expected_entity]
        assert repo.cache.get(expected_entity) == expected_entity

    def test_repository_can_search_by_property_without_specifying_the_type(
        self,
        repo: Repository,
        inserted_entities: List[Entity],
    ) -> None:
        """Search should return the objects that match the desired property."""
        expected_entity = inserted_entities[1]

        result: List[Entity] = repo.search({"id_": expected_entity.id_})

        assert result == [expected_entity]

    def test_repository_can_search_by_property_specifying_a_list_of_types(
        self,
        repo: Repository,
        inserted_entities: List[Entity],
    ) -> None:
        """Search should return the objects that match the desired property."""
        entity_types: List[Type[Entity]] = [type(inserted_entities[0]), OtherEntity]
        expected_entity = inserted_entities[1]

        result = repo.search({"id_": expected_entity.id_}, entity_types)

        assert result == [expected_entity]

    def test_repository_can_search_by_bool_property(
        self,
        repo: Repository,
        inserted_entities: List[Entity],
    ) -> None:
        """Search should return the objects that have a bool property."""
        expected_entity = BoolEntity(name="Name", active=True)
        repo.add(expected_entity)
        repo.commit()

        result = repo.search({"active": True}, [BoolEntity])

        assert result == [expected_entity]

    def test_repository_can_search_regular_expression(
        self, repo: Repository, inserted_entities: List[Entity]
    ) -> None:
        """
        Given: More than one entity is inserted in the repository.
        When: We search using a regular expression
        Then: The matching entity is found
        """
        expected_entities = [
            entity_
            for entity_ in inserted_entities
            if entity_.name == inserted_entities[0].name
        ]
        regular_expression = rf"^{expected_entities[0].name}.*"

        result = repo.search({"name": regular_expression}, type(expected_entities[0]))

        assert result == expected_entities

    def test_repository_search_by_regular_expression_is_case_insensitive(
        self, repo: Repository, inserted_entities: List[Entity]
    ) -> None:
        """
        Given: More than one entity is inserted in the repository.
        When: We search using a regular expression with the wrong capitalization
        Then: The matching entity is found

        If you come to disable this functionality, make it configurable instead, being
        the default the search as case insensitive
        """
        expected_entities = [
            entity_
            for entity_ in inserted_entities
            if entity_.name == inserted_entities[0].name
        ]
        regular_expression = rf"^{expected_entities[0].name.upper()}.*"

        result = repo.search({"name": regular_expression}, type(expected_entities[0]))

        assert result == expected_entities

    def test_repository_search_raises_error_if_searching_by_inexistent_field(
        self,
        repo: Repository,
        inserted_entities: List[Entity],
    ) -> None:
        """If no object has the property of the search criteria, raise the desired
        error.
        """
        entity = inserted_entities[0]

        with pytest.raises(
            EntityNotFoundError,
            match=(
                f"There are no entities of type {entity._model_name} in the repository"
                " that match the search filter {'inexistent_field': 'inexistent_value'}"
            ),
        ):
            repo.search({"inexistent_field": "inexistent_value"}, type(entity))

    def test_repository_search_raises_error_if_searching_by_inexistent_value(
        self,
        repo: Repository,
        inserted_entities: List[Entity],
    ) -> None:
        """If no object has a value like the search criteria raise the desired error."""
        entity = inserted_entities[0]

        with pytest.raises(
            EntityNotFoundError,
            match=(
                f"There are no entities of type {entity._model_name} in the "
                "repository that match the search filter {'id_': 'inexistent_value'}"
            ),
        ):
            repo.search({"id_": "inexistent_value"}, type(entity))

    def test_repository_can_search_by_multiple_properties(
        self,
        repo: Repository,
        inserted_entities: List[Entity],
    ) -> None:
        """
        Given: a full repository.
        When: a search is performed by multiple properties.
        Then: the matching objects are returned.
        """
        entity = inserted_entities[1]

        result = repo.search({"state": entity.state, "name": entity.name}, type(entity))

        assert result == [entity]

    def test_repo_can_search_entity_if_two_different_entities_match(
        self,
        repo: Repository,
    ) -> None:
        """
        Given: Two different entities with the same ID
        When: we search by a property equal in both entities and give only one model.
        Then: only the entity that matches the model is returned
        """
        author = Author(id_="author_id", name="common name")
        book = Book(id_=1, name="common name")
        repo.add(author)
        repo.add(book)
        repo.commit()

        result = repo.search({"name": "common name"}, [Author])

        assert result == [author]

    def test_repo_can_search_entity_if_two_different_entities_match_giving_both_models(
        self,
        repo: Repository,
    ) -> None:
        """
        Given: Two different entities with the same ID
        When: we search by a property equal in both entities and give both models.
        Then: both entities that matches the model are returned
        """
        author = Author(id_="author_id", name="common name")
        book = Book(id_=1, name="common name")
        repo.add(author)
        repo.add(book)
        repo.commit()

        result = repo.search({"name": "common name"}, [Author, Book])

        assert result == [author, book]

    @pytest.mark.skip(
        "Supported by Fake and TinyDB, not by Pypika yet. Once mappers are supported "
        "it should be easy to add this particular case."
    )
    def test_repo_can_search_in_list_of_str_attribute(self, repo: Repository) -> None:
        """
        Given: A repository with an entity that contains an attribute with a list of str
        When: search is called with a regexp that  matches one of the list elements
        Then: the entity is returned
        """
        expected_entity = ListEntityFactory.build()
        repo.add(expected_entity)
        repo.commit()
        regexp = rf"{expected_entity.elements[0][:-1]}."

        result = repo.search({"elements": regexp}, ListEntity)

        assert result == [expected_entity]


class TestDelete:
    """Test the removal of entities."""

    @pytest.mark.secondary()
    def test_repository_can_delete_an_entity(
        self,
        repo: Repository,
        inserted_entities: List[Entity],
    ) -> None:
        """
        Given: a full repository.
        When: an entity is deleted.
        Then: the entity is not longer in the repository.
        """
        entity_to_delete = inserted_entities[1]
        repo.delete(entity_to_delete)

        repo.commit()  # act

        remaining_entities = repo.all(type(entity_to_delete))
        assert entity_to_delete not in remaining_entities

    @pytest.mark.secondary()
    def test_repository_doesnt_delete_the_entity_if_we_dont_commit(
        self,
        database: Any,
        repo: Repository,
        repo_tester: RepositoryTester[Entity],
        inserted_entities: List[Entity],
    ) -> None:
        """
        Given: a full repository.
        When: an entity is deleted but we don't commit the changes.
        Then: the entity is still in the repository.
        """
        entity_to_delete = inserted_entities[1]

        repo.delete(entity_to_delete)  # act

        remaining_entities = repo_tester.get_all(database, type(entity_to_delete))
        assert entity_to_delete in remaining_entities

    def test_repository_delete_raise_error_if_entity_not_found(
        self,
        repo: Repository,
        entity: Entity,
    ) -> None:
        """
        Given: an empty repository.
        When: trying to delete an inexistent entity.
        Then: An EntityNotFoundError error is raised.
        """
        with pytest.raises(EntityNotFoundError) as error:
            repo.delete(entity)

        assert (
            f"Unable to delete entity {entity} because it's not in the repository"
            in str(error.value)
        )


class TestLast:
    """Test the retrieval of the last entity."""

    def test_repository_last_returns_last_entity(
        self,
        repo: Repository,
        inserted_entities: List[Entity],
    ) -> None:
        """
        Given: A repository with many entities.
        When: using the last method.
        Then: The greater entity is returned and it's also stored into the cache.
        """
        greater_entity = max(inserted_entities)

        result = repo.last(type(greater_entity))

        assert result == greater_entity
        assert repo.cache.get(greater_entity) == greater_entity

    def test_repository_last_returns_last_entity_if_no_type_specified(
        self,
        repo: Repository,
        inserted_entities: List[Entity],
    ) -> None:
        """
        Given: A repository with many entities.
        When: using the last method without any argument.
        Then: The greater entity is returned
        """
        greater_entity = max(inserted_entities)

        result: List[Entity] = repo.last()

        assert result == greater_entity

    def test_repository_last_returns_last_entity_if_list_of_types(
        self,
        repo: Repository,
        inserted_entities: List[Entity],
    ) -> None:
        """
        Given: A repository with many entities.
        When: using the last method with a list of types.
        Then: The greater entity is returned
        """
        entity_types: List[Type[Entity]] = [type(inserted_entities[0]), OtherEntity]
        greater_entity = max(inserted_entities)

        result = repo.last(entity_types)

        assert result == greater_entity

    def test_repository_last_raise_error_if_entity_not_found(
        self,
        repo: Repository,
        entity: Entity,
    ) -> None:
        """
        Given: an empty repository.
        When: trying to get the last entity.
        Then: An EntityNotFoundError error is raised.
        """
        with pytest.raises(
            EntityNotFoundError,
            match=(
                f"There are no entities of type {entity._model_name} in the repository"
            ),
        ):
            repo.last(type(entity))


class TestFirst:
    """Test the retrieval of the first entity."""

    def test_repository_first_returns_first_entity(
        self,
        repo: Repository,
        inserted_entities: List[Entity],
    ) -> None:
        """
        Given: A repository with many entities.
        When: using the first method.
        Then: The smallest entity is returned and saved into the cache
        """
        smaller_entity = min(inserted_entities)

        result = repo.first(type(smaller_entity))

        assert result == smaller_entity
        assert repo.cache.get(smaller_entity) == smaller_entity

    def test_repository_first_raise_error_if_entity_not_found(
        self,
        repo: Repository,
        entity: Entity,
    ) -> None:
        """
        Given: an empty repository.
        When: trying to get the first entity.
        Then: An EntityNotFoundError error is raised.
        """
        with pytest.raises(
            EntityNotFoundError,
            match=(
                f"There are no entities of type {entity._model_name} in the repository"
            ),
        ):
            repo.first(type(entity))


def test_repository_next_id_raise_error_if_entity_has_str_id(
    repo: Repository,
    inserted_str_entity: Entity,
) -> None:
    """
    Given: an empty repository.
    When: trying to get the next id of an entity with str id.
    Then: An AutoIncrementError error is raised.
    """
    with pytest.raises(
        AutoIncrementError,
        match="Auto increment is not yet supported for Entities with string id_s",
    ):
        repo._next_id(inserted_str_entity)


def test_tinydb_raises_error_if_wrong_model_data(
    repo_tinydb: TinyDBRepository, caplog: LogCaptureFixture
) -> None:
    """
    Given: A tinydb repository with data than doesn't match the model.
    When: Get is called
    Then: The id_ of the model and it's data is shown before the error.

    This doesn't apply to the fake repository due to how it handles the entities, and
    in Pypika it would mean a database schema change without change on the model, which
    is much more difficult than in the case of TinyDB, so I'm not going to test it
    in the first approach.
    """
    # The name is required
    entity_data = {"id_": 1, "model_type_": "entity"}
    repo_tinydb.db_.insert(entity_data)

    with pytest.raises(ValidationError, match="name"):
        repo_tinydb.get(1, [Entity])

    assert (
        "repository_orm.adapters.data.tinydb",
        logging.ERROR,
        "Error loading the model Entity for the register {'id_': 1}",
    ) in caplog.record_tuples
