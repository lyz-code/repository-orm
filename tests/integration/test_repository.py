"""Tests the integration between the repositories and their storage layer.

The tests are all the same for all the repositories. If you want to add a new one
add them to the cases.
"""

import logging
from typing import Any, List

import pytest
from _pytest.logging import LogCaptureFixture

from repository_pattern import Entity, EntityNotFoundError, Repository

from ..cases import RepositoryTester


def test_apply_repository_creates_schema(  # noqa: AAA01
    database: Any,
    empty_repo: Repository,
    caplog: LogCaptureFixture,
    repo_tester: RepositoryTester,
) -> None:
    """
    Given: an empty repository.
    When: the apply_migrations method is called.
    Then: The migrations are applied as expected.
    """
    caplog.set_level(logging.DEBUG)

    repo_tester.apply_migrations(empty_repo)  # type: ignore

    repo_tester.assert_schema_exists(database, caplog)


def test_repository_handles_connection_errors(repo: Repository) -> None:
    """
    Given: A wrong database url
    When: the repository is initialized
    Then: a ConnectionError exception is raised
    """
    with pytest.raises(ConnectionError):
        repo.__class__("wrong_database_url")


def test_repository_can_save_an_entity(
    database: Any,
    repo: Repository,
    repo_tester: RepositoryTester,
    entity: Entity,
) -> None:
    """Saved entities remain in the repository."""
    repo.add(entity)

    repo.commit()  # act

    assert entity == repo_tester.get_entity(database, entity)


def test_repo_add_entity_is_idempotent(
    database: Any, repo: Repository, repo_tester: RepositoryTester, entity: Entity
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
    database: Any, repo: Repository, repo_tester: RepositoryTester, entity: Entity
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
    database: Any, repo: Repository, repo_tester: RepositoryTester, entity: Entity
) -> None:
    """
    Given: A repository with the identity we want to add already commited.
    When: We insert the same entity with an attribute changed then commit.
    Then: Only one item exists.
    """
    repo_tester.insert_entity(database, entity)
    # ignore: Although Entity doesn't have the rating attribute, all the entities
    #   defined in the tests models do.
    entity.rating += 1  # type: ignore
    repo.add(entity)

    repo.commit()  # act

    entities = repo_tester.get_all(database, type(entity))
    assert len(entities) == 1
    assert entity.rating == entities[0].rating  # type: ignore


def test_repository_doesnt_add_an_entity_if_we_dont_commit_changes(
    database: Any,
    repo: Repository,
    repo_tester: RepositoryTester,
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


def test_repository_can_retrieve_an_entity(
    repo: Repository,
    inserted_entity: Entity,
) -> None:
    """Given an entity_id the repository returns the entity object."""
    result = repo.get(type(inserted_entity), inserted_entity.id_)

    assert result == inserted_entity
    assert result.id_ == inserted_entity.id_


def test_repository_raises_error_if_no_entity_found_by_get(
    repo: Repository,
    entity: Entity,
) -> None:
    """As the entity is not inserted into the repository, it shouldn't be found."""
    with pytest.raises(EntityNotFoundError) as error:
        repo.get(type(entity), entity.id_)

    assert (
        f"There are no {entity.__class__.__name__}s with id "
        f"{entity.id_} in the repository" in str(error.value)
    )


def test_repository_can_retrieve_all_objects(
    repo: Repository,
    inserted_entities: List[Entity],
) -> None:
    """Given an entity type all the entity objects that match should be returned."""
    entity_type = type(inserted_entities[0])

    result = repo.all(entity_type)

    assert result == inserted_entities
    assert len(result) == 3
    assert result[0].id_ == inserted_entities[0].id_


def test_repository_all_raises_error_if_empty_repository(
    repo: Repository,
    entity: Entity,
) -> None:
    """If there are no entities, an error should be raised."""
    with pytest.raises(EntityNotFoundError) as error:
        repo.all(type(entity))

    assert (
        f"There are no {entity.__class__.__name__}s entities in the repository"
        in str(error.value)
    )


def test_repository_can_search_by_property(
    repo: Repository,
    inserted_entities: List[Entity],
) -> None:
    """Search should return the objects that match the desired property."""
    expected_entity = inserted_entities[1]

    result = repo.search(type(expected_entity), {"id_": expected_entity.id_})

    assert result == [expected_entity]


def test_repository_search_raises_error_if_searching_by_unexistent_field(
    repo: Repository,
    inserted_entities: List[Entity],
) -> None:
    """If no object has the property of the search criteria, raise the desired
    error.
    """
    entity = inserted_entities[0]

    with pytest.raises(EntityNotFoundError) as error:
        repo.search(type(entity), {"unexistent_field": "unexistent_value"})

    assert (
        f"There are no {entity.__class__.__name__}s that match "
        "the search filter {'unexistent_field': 'unexistent_value'}" in str(error.value)
    )


def test_repository_search_raises_error_if_searching_by_unexistent_value(
    repo: Repository,
    inserted_entities: List[Entity],
) -> None:
    """If no object has a value like the search criteria raise the desired error."""
    entity = inserted_entities[0]

    with pytest.raises(EntityNotFoundError) as error:
        repo.search(type(entity), {"id_": "unexistent_value"})

    assert (
        f"There are no {entity.__class__.__name__}s that match "
        "the search filter {'id_': 'unexistent_value'}" in str(error.value)
    )


def test_repository_can_search_by_multiple_properties(
    repo: Repository,
    inserted_entities: List[Entity],
) -> None:
    """
    Given: a full repository.
    When: a search is performed by multiple properties.
    Then: the matching objects are returned.
    """
    entity = inserted_entities[1]
    search_criteria = entity.dict()

    result = repo.search(type(entity), search_criteria)

    assert result == [entity]


@pytest.mark.secondary
def test_repository_can_delete_an_entity(
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


@pytest.mark.secondary
def test_repository_doesnt_delete_the_entity_if_we_dont_commit(
    database: Any,
    repo: Repository,
    repo_tester: RepositoryTester,
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


def test_repository_raise_error_if_entity_not_found(
    repo: Repository,
    entity: Entity,
) -> None:
    """
    Given: an empty repository.
    When: trying to delete an unexistent entity.
    Then: An EntityNotFoundError error is raised.
    """
    with pytest.raises(EntityNotFoundError) as error:
        repo.delete(entity)

    assert (
        f"Unable to delete entity {entity} because it's not in the repository"
        in str(error.value)
    )
