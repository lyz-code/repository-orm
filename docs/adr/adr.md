[ADR](https://lyz-code.github.io/blue-book/adr/) are short text documents that
captures an important architectural decision made along with its context and
consequences.

```mermaid
graph TD
    001[001: Entity ID definition]
    002[002: Support String IDs]

    click 001 "https://lyz-code.github.io/repository-orm/adr/001-entity_id_definition/" _blank
    click 002 "https://lyz-code.github.io/repository-orm/adr/002-support_string_ids/" _blank

    001 -- Partially superseeded --> 002

    001:::superseeded
    002:::accepted

    classDef draft fill:#CDBFEA;
    classDef proposed fill:#B1CCE8;
    classDef accepted fill:#B1E8BA;
    classDef rejected fill:#E8B1B1;
    classDef deprecated fill:#E8B1B1;
    classDef superseeded fill:#E8E5B1;
```
