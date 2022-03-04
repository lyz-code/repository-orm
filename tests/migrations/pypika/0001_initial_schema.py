"""Initial schema yoyo migrations script."""  # noqa: C0103

from yoyo import step

# C0103: Module name doesn't conform to snake_case naming. But it's the way to define
#   yoyo migration scripts names.


steps = [
    step(
        "CREATE TABLE article ("
        "id VARCHAR(26), "
        "name VARCHAR(20), "
        "description VARCHAR(255), "
        "state VARCHAR(20), "
        "active BOOL, "
        "rating INT, "
        "PRIMARY KEY (id))",
        "DROP TABLE article",
    ),
    step(
        "CREATE TABLE author ("
        "id VARCHAR(26), "
        "name VARCHAR(20), "
        "last_name VARCHAR(20), "
        "country VARCHAR(20), "
        "state VARCHAR(20), "
        "active BOOL, "
        "rating INT, "
        "PRIMARY KEY (id))",
        "DROP TABLE author",
    ),
    step(
        "CREATE TABLE book ("
        "id INT, "
        "name VARCHAR(20), "
        "summary VARCHAR(255), "
        "state VARCHAR(20), "
        "released DATETIME, "
        "active BOOL, "
        "rating INT, "
        "PRIMARY KEY (id))",
        "DROP TABLE book",
    ),
    step(
        "CREATE TABLE genre ("
        "id INT, "
        "name VARCHAR(20), "
        "description VARCHAR(255), "
        "state VARCHAR(20), "
        "rating INT, "
        "active BOOL, "
        "PRIMARY KEY (id))",
        "DROP TABLE genre",
    ),
    step(
        "CREATE TABLE otherentity ("
        "id INT, "
        "name VARCHAR(20), "
        "state VARCHAR(20), "
        "description VARCHAR(255), "
        "rating INT, "
        "active BOOL, "
        "PRIMARY KEY (id))",
        "DROP TABLE otherentity",
    ),
    step(
        "CREATE TABLE listentity ("
        "id INT, "
        "name VARCHAR(20), "
        "state VARCHAR(20), "
        "description VARCHAR(255), "
        "active BOOL, "
        "PRIMARY KEY (id))",
        "DROP TABLE listentity",
    ),
    step(
        "CREATE TABLE listentity_has_elements ("
        "id INT, "
        "entity_id INT,"
        "element VARCHAR(255), "
        "PRIMARY KEY (id))",
        "DROP TABLE listentity_has_elements",
    ),
    step(
        "CREATE TABLE boolentity ("
        "id INT, "
        "name VARCHAR(20), "
        "state VARCHAR(20), "
        "description VARCHAR(255), "
        "active BOOL, "
        "PRIMARY KEY (id))",
        "DROP TABLE listentity",
    ),
]
