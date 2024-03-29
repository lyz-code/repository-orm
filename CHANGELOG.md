## 1.3.3 (2022-12-15)

### Fix

- deprecate search_exception
- simplify signature of repository methods
- simplify signature of load_repository
- remove dependency with py

## 1.3.2 (2022-10-13)

### Fix

- correct the search on tinydb when a value is None
- correct the search on tinydb when a value is None

### Refactor

- clean the Entity TypeVar definitions to EntityT

## 1.3.1 (2022-06-08)

### Fix

- Implement the ADR 005 deprecation

## 1.3.0 (2022-05-02)

### Refactor

- avoid duplication of code in repo._get when there are many entities

### Feat

- repo.get() now accepts an `attribute` different than `id_`
- add `repo.empty()` to remove all entities from the repository

## 1.2.0 (2022-03-28)

### Feat

- add the is_closed property to the repo

## 1.1.8 (2022-03-25)

### Fix

- use Sequence as type hint for repo.add
- use Sequence as type hint for repo.add

## 1.1.7 (2022-03-24)

### Fix

- correct the signature of repo.add to support list of entities
- correct the signature of repo.add to support list of entities

## 1.1.6 (2022-03-16)

### Fix

- return empty desired_values in search and all
- return empty desired_values in search and all

## 1.1.5 (2022-03-16)

### Fix

- remove defined values when doing repo.get

## 1.1.4 (2022-03-11)

## 1.1.3 (2022-03-10)

### Fix

- prevent search from raising exceptions when no entity is found

## 1.1.2 (2022-03-10)

### Fix

- remove userwarning on the add method

## 1.1.1 (2022-03-04)

### Fix

- correct merge errors
- propagate the merge attribute when adding a list of entities

## 1.1.0 (2022-03-04)

### Feat

- support AnyHttpUrl as id_ type

## 1.0.0 (2022-03-04)

### Feat

- allow merging of entities
- rename model name property from `_model_name` to `model_name`

## 0.11.1 (2022-02-16)

### Fix

- correct ordering of entities that both have an integer type

## 0.11.0 (2022-02-16)

### Feat

- allow comparison of entities with different `id_` types

### Fix

- sort the result of `repo.all()`

## 0.10.0 (2022-02-11)

### Fix

- select pdm path editable backed
- remove the python_paths that is no longer needed
- define the log_level attribute of the config object
- **ci**: deprecate dependabot as pdm is not supported yet

### Feat

- change package management to pdm
- mark deprecation warnings as errors
- create the load_config entrypoint function
- **ci**: add the workflow_dispatch event handler
- add close method to the data repositories

## 0.9.1 (2022-02-09)

### Fix

- make cache entries immutable

## 0.9.0 (2022-01-20)

### Feat

- add a repository cache

## 0.8.0 (2022-01-20)

### Refactor

- remove unused code
- organize tests in classes

### Feat

- allow the addition of lists of entities

## 0.7.0 (2021-12-22)

### Feat

- make string search case insensitive

## 0.6.0 (2021-12-02)

### Feat

- add file repositories

### fix

- make Entity hash unique per model

## 0.5.5 (2021-09-23)

### Fix

- make tinydb search return only entities of the asked model

## 0.5.4 (2021-09-22)

### Fix

- allow faker repository to search for bool properties

## 0.5.3 (2021-08-12)

### Fix

- make tinydb search process a dictionary with many fields well

## 0.5.2 (2021-08-12)

### Fix

- correct tinydb search by many fields

## 0.5.1 (2021-05-27)

### Perf

- add method return the entity with the autoincremented id

### Fix

- add a warning if load_repository is called with wrong database_url

## 0.5.0 (2021-05-03)

### Fix

- don't search on list attributes that are not strings

### Feat

- partially support search in attributes of type List

## 0.4.0 (2021-05-02)

### Perf

- improve the type hints

### Feat

- make entity models optional arguments of the repo methods

### refactor

- create the _model_not_found and _build_models abstract repo methods

### Fix

- bump version of deepdiff
- support back the string IDs

### feat

- add a ci job to test that the program is installable
- add the last and first methods to the repositories.

## 0.3.1 (2021-04-15)

### Fix

- use entity typevar for abstract repository definition

## 0.3.0 (2021-04-15)

### Feat

- add _model_name attribute to entities
- make entity id definition optional
- add first and last methods to the repositories

### BREAKING CHANGE

- We're temporarily dropping support for `str` `id_` attributes.

## 0.2.0 (2021-04-08)

### Feat

- add TiniDB repository
- make add idempotent for Fake and Pypika repositories

### feat

- add support for regular expressions in the `search` method

### fix

- ignore the B608 sql injection warning

## 0.1.2 (2020-12-29)

### Fix

- drop support for python 3.6
- use generic typevars to define the entities of the repositories
- replace ID with id_

## 0.1.1 (2020-12-26)

### Fix

- bump version to be able to upload to pypi

## 0.1.0 (2020-12-26)

### Feat

- **fake**: implement the first version of the FakeRepository
- **pypika**: implement the first version of the PypikaRepository
- create initial project structure
