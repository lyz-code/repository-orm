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
