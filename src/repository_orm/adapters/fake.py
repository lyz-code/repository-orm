"""Store the fake repository implementation."""

import copy
import re
from contextlib import suppress
from typing import Dict, List, Type

from deepdiff import extract, grep

from ..exceptions import EntityNotFoundError, TooManyEntitiesError
from ..model import EntityID
from .abstract import Entity, Models, OptionalModelOrModels, OptionalModels, Repository

FakeRepositoryDB = Dict[Type[Entity], Dict[EntityID, Entity]]


class FakeRepository(Repository):
    """Implement the repository pattern using a memory dictionary."""

    def __init__(
        self, models: OptionalModels[Entity] = None, database_url: str = ""
    ) -> None:
        """Initialize the repository attributes."""
        super().__init__(models=models)
        if database_url == "/inexistent_dir/database.db":
            raise ConnectionError(f"Could not create database file: {database_url}")
        self.entities: FakeRepositoryDB[Entity] = {}
        self.new_entities: FakeRepositoryDB[Entity] = {}

    def add(self, entity: Entity) -> Entity:
        """Append an entity to the repository.

        If the id is not set, autoincrement the last.

        Args:
            entity: Entity to add to the repository.

        Returns:
            entity
        """
        if isinstance(entity.id_, int) and entity.id_ < 0:
            entity.id_ = self._next_id(entity)
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

    def get(
        self, id_: EntityID, models: OptionalModelOrModels[Entity] = None
    ) -> Entity:
        """Obtain an entity from the repository by it's ID.

        Args:
            models: Entity class or classes to obtain.
            id_: ID of the entity to obtain.

        Returns:
            entity: Entity object that matches the id_

        Raises:
            EntityNotFoundError: If the entity is not found.
            TooManyEntitiesError: If more than one entity was found.
        """
        matching_entities = []
        models = self._build_models(models)

        for model in models:
            with suppress(KeyError):
                matching_entities.append(self.entities[model][id_])

        if len(matching_entities) == 1:
            return matching_entities[0]
        elif len(matching_entities) == 0:
            raise self._model_not_found(models, f" with id {id_}")
        else:
            raise TooManyEntitiesError(
                f"More than one entity was found with the id {id_}"
            )

    def all(self, models: OptionalModelOrModels[Entity] = None) -> List[Entity]:
        """Get all the entities from the repository whose class is included in models.

        Args:
            models: Entity class or classes to obtain.
        """
        entities = []
        models = self._build_models(models)

        for model in models:
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

    def search(
        self,
        fields: Dict[str, EntityID],
        models: OptionalModelOrModels[Entity] = None,
    ) -> List[Entity]:
        """Get the entities whose attributes match one or several conditions.

        Args:
            models: Entity class or classes to obtain.
            fields: Dictionary with the {key}:{value} to search.

        Returns:
            entities: List of Entity object that matches the search criteria.

        Raises:
            EntityNotFoundError: If the entities are not found.
        """
        models = self._build_models(models)
        all_entities: List[Entity] = self.all(models)
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
            except KeyError as error:
                raise self._model_not_found(
                    models, f" that match the search filter {fields}"
                ) from error

            for path in entities_with_value["matched_values"]:
                entity_id = re.sub(r"root\[(.*?)\]\[.*", r"\1", path)

                # Convert int ids from str to int
                try:
                    entity_id = int(entity_id)
                except ValueError:
                    entity_id = re.sub(r"'(.*)'", r"\1", entity_id)

                # Add the entity to the matching ones only if the value is of the
                # attribute `key`.
                if re.match(fr"root\['?{entity_id}'?\]\['{key}'\]", path):
                    matching_entity_attributes[entity_id] = extract(
                        entity_attributes, f"root[{entity_id}]"
                    )
            entity_attributes = matching_entity_attributes
        entities = [entities_dict[key] for key in entity_attributes.keys()]

        return entities

    def apply_migrations(self, migrations_directory: str) -> None:
        """Run the migrations of the repository schema.

        Args:
            migrations_directory: path to the directory containing the migration
                scripts.
        """
        # The fake repository doesn't have any schema

    def last(self, models: OptionalModelOrModels[Entity] = None) -> Entity:
        """Get the biggest entity from the repository.

        Args:
            models: Entity class or classes to obtain.

        Returns:
            entity: Biggest Entity object of type models.

        Raises:
            EntityNotFoundError: If there are no entities.
        """
        try:
            last_index_entity: Entity = super().last(models)
        except EntityNotFoundError as empty_repo:
            models = self._build_models(models)
            try:
                # Empty repo but entities staged to be commited.
                return max(self._staged_entities(models))
            except KeyError as no_staged_entities:
                # Empty repo and no entities staged.
                raise empty_repo from no_staged_entities

        try:
            models = self._build_models(models)
            last_staged_entity: Entity = max(self._staged_entities(models))
        except KeyError:
            # Full repo and no staged entities.
            return last_index_entity

        # Full repo and staged entities.
        return max([last_index_entity, last_staged_entity])

    def _staged_entities(self, models: Models[Entity]) -> List[Entity]:
        """Return a list of staged entities of type models.

        Args:
            models: Return only instances of these models.
        """
        staged_entities = []

        for model in models:
            staged_entities += [
                entity for _, entity in self.new_entities[model].items()
            ]
        return staged_entities
