"""Store the fake repository implementation."""

import copy
import logging
import re
from typing import Any, Dict, List, Type, TypeVar, Union

from deepdiff import extract, grep

# [Pydantic issue](https://github.com/samuelcolvin/pydantic/issues/1961)
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from ..exceptions import EntityNotFoundError
from ..model import Entity as EntityModel
from .abstract import AbstractRepository

log = logging.getLogger(__name__)

Entity = TypeVar("Entity", bound=EntityModel)

FakeRepositoryDB = Dict[Type[Entity], Dict[Union[str, int], Entity]]


class FakeRepository(BaseModel, AbstractRepository):
    """Implement the repository pattern using a memory dictionary."""

    entities: FakeRepositoryDB[Any] = Field(default_factory=dict)
    new_entities: FakeRepositoryDB[Any] = Field(default_factory=dict)

    def __init__(self, database_url: str = "", **data: Any) -> None:
        """Initialize the repository attributes."""
        super().__init__(**data)
        if database_url == "/inexistent_dir/database.db":
            raise ConnectionError(f"Could not create database file: {database_url}")

    def add(self, entity: Entity) -> None:
        """Append an entity to the repository.

        Args:
            entity: Entity to add to the repository.
        """
        if self.new_entities == {}:
            self.new_entities = copy.deepcopy(self.entities.copy())
        try:
            self.new_entities[type(entity)]
        except KeyError:
            self.new_entities[type(entity)] = {}

        self.new_entities[type(entity)][entity.id_] = entity

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

    def get(self, entity_model: Type[Entity], entity_id: Union[str, int]) -> Entity:
        """Obtain an entity from the repository by it's ID.

        Args:
            entity_model: Type of entity object to obtain.
            entity_id: ID of the entity object to obtain.

        Returns:
            entity: Entity object that matches the search criteria.

        Raises:
            EntityNotFoundError: If the entity is not found.
        """
        try:
            entity = self.entities[entity_model][entity_id]
        except KeyError as error:
            raise EntityNotFoundError(
                f"There are no {entity_model.__name__}s "
                f"with id {entity_id} in the repository."
            ) from error

        return entity

    def all(self, entity_model: Type[Entity]) -> List[Entity]:
        """Obtain all the entities of a type from the repository.

        Args:
            entity_model: Type of entity objects to obtain.

        Returns:
            entities: List of Entity object that matches the search criteria.

        Raises:
            EntityNotFoundError: If the entities are not found.
        """
        try:
            return sorted(
                entity for entity_id, entity in self.entities[entity_model].items()
            )
        except KeyError as error:
            raise EntityNotFoundError(
                f"There are no {entity_model.__name__}s entities in the repository"
            ) from error

    def commit(self) -> None:
        """Persist the changes into the repository."""
        for entity_model, entities in self.new_entities.items():
            self.entities[entity_model] = entities
        self.new_entities = {}

    def search(
        self, entity_model: Type[Entity], fields: Dict[str, Union[str, int]]
    ) -> List[Entity]:
        """Obtain the entities whose attributes match one or several conditions.

        Args:
            entity_model: Type of entity object to obtain.
            fields: Dictionary with the {key}:{value} to search.

        Returns:
            entities: List of Entity object that matches the search criteria.

        Raises:
            EntityNotFoundError: If the entities are not found.
        """
        all_entities = self.all(entity_model)
        entities_dict = {entity.id_: entity for entity in all_entities}
        entity_attributes = {entity.id_: entity.dict() for entity in all_entities}
        error_msg = (
            f"There are no {entity_model.__name__}s that match "
            f"the search filter {fields}"
        )

        for key, value in fields.items():
            # Get entities that have the value `value`
            entities_with_value = entity_attributes | grep(value)
            matching_entity_attributes = {}

            try:
                entities_with_value["matched_values"]
            except KeyError as error:
                raise EntityNotFoundError(error_msg) from error

            for path in entities_with_value["matched_values"]:
                entity_id = re.sub(r"root\[(.*?)\]\[.*", r"\1", path)

                # Convert int ids from str to int
                try:
                    entity_id = int(entity_id)
                except ValueError:
                    entity_id = re.sub(r"'(.*)'", r"\1", entity_id)

                # Add the entity to the matching ones only if the value is of the
                # attribute `key`.
                if re.match(re.compile(fr"root\['?{entity_id}'?\]\['{key}'\]"), path):
                    matching_entity_attributes[entity_id] = extract(
                        entity_attributes, f"root[{entity_id}]"
                    )

            entity_attributes = matching_entity_attributes
        entities = [entities_dict[key] for key in entity_attributes.keys()]

        if len(entities) == 0:
            raise EntityNotFoundError(error_msg)
        return entities

    def apply_migrations(self, migrations_directory: str) -> None:
        """Run the migrations of the repository schema.

        Args:
            migrations_directory: path to the directory containing the migration
                scripts.
        """
        # The fake repository doesn't have any schema
