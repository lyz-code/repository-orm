"""Initial schema yoyo migrations script."""

from yoyo import step

steps = [
    step(
        "CREATE TABLE author ("
        "id VARCHAR(26), "
        "name VARCHAR(20), "
        "last_name VARCHAR(20), "
        "country VARCHAR(20), "
        "rating INT, "
        "PRIMARY KEY (id))",
        "DROP TABLE author",
    ),
    step(
        "CREATE TABLE book ("
        "id INT, "
        "name VARCHAR(20), "
        "summary VARCHAR(255), "
        "released DATETIME, "
        "rating INT, "
        "PRIMARY KEY (id))",
        "DROP TABLE book",
    ),
    step(
        "CREATE TABLE genre ("
        "id INT, "
        "name VARCHAR(20), "
        "description VARCHAR(255), "
        "rating INT, "
        "PRIMARY KEY (id))",
        "DROP TABLE genre",
    ),
]
