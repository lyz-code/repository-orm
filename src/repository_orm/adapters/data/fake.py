"""Store the fake repository implementation."""

import copy
import re
from contextlib import suppress
from typing import Dict, List, Optional, Type, TypeVar

from deepdiff import extract, grep

from ...exceptions import EntityNotFoundError
from ...model import Entity as EntityModel
from ...model import EntityID
from .abstract import Repository, warn_on_models

Entity = TypeVar("Entity", bound=EntityModel)
FakeRepositoryDB = Dict[Type[EntityModel], Dict[EntityID, Entity]]


class FakeRepository(Repository):
    """Implement the repository pattern using a memory dictionary."""

    def __init__(
        self,
        database_url: str = "",
        search_exception: Optional[bool] = None,
    ) -> None:
        """Initialize the repository attributes."""
        super().__init__(search_exception=search_exception)
        if database_url == "/inexistent_dir/database.db":
            raise ConnectionError(f"Could not create database file: {database_url}")
        # ignore: Type variable "repository_orm.adapters.data.fake.Entity" is unbound
        # I don't know how to fix this
        self.entities: FakeRepositoryDB[Entity] = {}  # type: ignore
        self.new_entities: FakeRepositoryDB[Entity] = {}  # type: ignore
        self.is_connection_closed = False

    def _add(self, entity: Entity) -> Entity:
        """Append an entity to the repository.

        Args:
            entity: Entity to add to the repository.

        Returns:
            entity
        """
        if self.new_entities == {}:
            self.new_entities = copy.deepcopy(self.entities.copy())
        try:
            self.new_entities[type(entity)]
        except KeyError:
            self.new_entities[type(entity)] = {}

        self.new_entities[type(entity)][entity.id_] = entity

        return entity

    def delete(self, entity: Entity) -> None:
        """Delete an entity from the repository.

        Args:
            entity: Entity to remove from the repository.

        Raises:
            EntityNotFoundError: If the entity is not found.
        """
        if self.new_entities == {}:
            self.new_entities = copy.deepcopy(self.entities.copy())
        try:
            self.new_entities[type(entity)].pop(entity.id_, None)
        except KeyError as error:
            raise EntityNotFoundError(
                f"Unable to delete entity {entity} because it's not in the repository"
            ) from error

    def _get(
        self,
        value: EntityID,
        model: Type[Entity],
        attribute: str = "id_",
    ) -> List[Entity]:
        """Obtain all entities from the repository that match an id_.

        If the attribute argument is passed, check that attribute instead.

        Args:
            value: Value of the entity attribute to obtain.
            model: Entity class to obtain.
            attribute: Entity attribute to check.

        Returns:
            entities: All entities that match the criteria.
        """
        matching_entities = []

        if attribute == "id_":
            with suppress(KeyError):
                matching_entities.append(self.entities[model][value])
        else:
            matching_entities = self._search({attribute: value}, model)

        return copy.deepcopy(matching_entities)

    def _all(self, model: Type[Entity]) -> List[Entity]:
        """Get all the entities from the repository whose class is included in models.

        Particular implementation of the database adapter.

        Args:
            model: Entity class to obtain.
        """
        entities = []

        with suppress(KeyError):
            entities += sorted(
                entity for entity_id, entity in self.entities[model].items()
            )

        return entities

    def commit(self) -> None:
        """Persist the changes into the repository."""
        for model, entities in self.new_entities.items():
            self.entities[model] = entities
        self.new_entities = {}

    def _search(
        self,
        fields: Dict[str, EntityID],
        model: Type[Entity],
    ) -> List[Entity]:
        """Get the entities whose attributes match one or several conditions.

        Particular implementation of the database adapter.

        Args:
            model: Entity class to obtain.
            fields: Dictionary with the {key}:{value} to search.

        Returns:
            entities: List of Entity object that matches the search criteria.
        """
        all_entities: List[Entity] = self.all(model)
        entities_dict = {entity.id_: entity for entity in all_entities}
        entity_attributes = {entity.id_: entity.dict() for entity in all_entities}

        for key, value in fields.items():
            # Get entities that have the value `value`
            entities_with_value = entity_attributes | grep(
                value, use_regexp=True, strict_checking=False
            )
            matching_entity_attributes = {}

            try:
                entities_with_value["matched_values"]
            except KeyError:
                return []

            for path in entities_with_value["matched_values"]:
                entity_id = re.sub(r"root\['?(.*?)'?\]\[.*", r"\1", path)

                # Convert int ids from str to int
                try:
                    # ignore: waiting for ADR-006 to be resolved
                    entity_id = int(entity_id)  # type: ignore
                except ValueError:
                    entity_id = re.sub(r"'(.*)'", r"\1", entity_id)

                # Add the entity to the matching ones only if the value is of the
                # attribute `key`.
                if re.match(rf"root\['?{entity_id}'?\]\['{key}'\]", path):
                    matching_entity_attributes[entity_id] = extract(
                        entity_attributes, f"root[{entity_id}]"
                    )
            # ignore: waiting for ADR-006 to be resolved
            entity_attributes = matching_entity_attributes  # type: ignore
        entities = [entities_dict[key] for key in entity_attributes.keys()]

        return entities

    def apply_migrations(self, migrations_directory: str) -> None:
        """Run the migrations of the repository schema.

        Args:
            migrations_directory: path to the directory containing the migration
                scripts.
        """
        # The fake repository doesn't have any schema

    def last(
        self,
        model: Optional[Type[Entity]] = None,
        models: Optional[Type[Entity]] = None,
    ) -> Entity:
        """Get the biggest entity from the repository.

        Args:
            model: Entity class to obtain.

        Returns:
            entity: Biggest Entity object of type models.

        Raises:
            EntityNotFoundError: If there are no entities.
        """
        try:
            last_index_entity: Entity = super().last(model)
        except EntityNotFoundError as empty_repo:
            model = warn_on_models(models, "last", model)
            try:
                # Empty repo but entities staged to be commited.
                return max(self._staged_entities(model))
            except KeyError as no_staged_entities:
                # Empty repo and no entities staged.
                raise empty_repo from no_staged_entities

        try:
            model = warn_on_models(models, "last", model)
            last_staged_entity: Entity = max(self._staged_entities(model))
        except KeyError:
            # Full repo and no staged entities.
            return last_index_entity

        # Full repo and staged entities.
        return max([last_index_entity, last_staged_entity])

    def _staged_entities(self, model: Type[Entity]) -> List[Entity]:
        """Return a list of staged entities of type models.

        Args:
            models: Return only instances of these models.
        """
        return [entity for _, entity in self.new_entities[model].items()]

    def close(self) -> None:
        """Close the connection to the database."""
        self.is_connection_closed = True

    @property
    def is_closed(self) -> bool:
        """Inform if the connection is closed."""
        return self.is_connection_closed

    def empty(self) -> None:
        """Remove all entities from the repository."""
        self.entities = {}
        self.new_entities = {}
