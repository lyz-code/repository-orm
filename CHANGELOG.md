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
