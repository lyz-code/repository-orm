[ADR](https://lyz-code.github.io/blue-book/adr/) are short text documents that
captures an important architectural decision made along with its context and
consequences.

```mermaid
graph TD
    001[001: Entity ID definition]
    002[002: Support String IDs]
    003[003: Make entity_model optional arguments]
    004[004: Add complex queries]
    005[005: Simplify search and all signature]

    click 001 "https://lyz-code.github.io/repository-orm/adr/001-entity_id_definition/" _blank
    click 002 "https://lyz-code.github.io/repository-orm/adr/002-support_string_ids/" _blank
    click 003 "https://lyz-code.github.io/repository-orm/adr/003-make_entity_models_optional_arguments/" _blank
    click 004 "https://lyz-code.github.io/repository-orm/adr/004-add_complex_queries/" _blank
    click 005 "https://lyz-code.github.io/repository-orm/adr/005-simplify_search_and_all_signature/" _blank

    001 -- Partially superseeded --> 002
    003 -- Superseeded --> 005

    001:::superseeded
    002:::accepted
    003:::superseeded
    004:::draft
    005:::draft

    classDef draft fill:#CDBFEA;
    classDef proposed fill:#B1CCE8;
    classDef accepted fill:#B1E8BA;
    classDef rejected fill:#E8B1B1;
    classDef deprecated fill:#E8B1B1;
    classDef superseeded fill:#E8E5B1;
```
