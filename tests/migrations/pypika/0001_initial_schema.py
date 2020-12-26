"""Initial schema yoyo migrations script."""

from yoyo import step

steps = [
    step(
        "CREATE TABLE author ("
        "ID VARCHAR(26), "
        "first_name VARCHAR(20), "
        "last_name VARCHAR(20), "
        "country VARCHAR(20), "
        "PRIMARY KEY (ID))",
        "DROP TABLE author",
    ),
    step(
        "CREATE TABLE book ("
        "ID INT, "
        "title VARCHAR(20), "
        "summary VARCHAR(255), "
        "released DATETIME, "
        "PRIMARY KEY (ID))",
        "DROP TABLE book",
    ),
    step(
        "CREATE TABLE genre ("
        "ID INT, "
        "name VARCHAR(20), "
        "description VARCHAR(255), "
        "PRIMARY KEY (ID))",
        "DROP TABLE genre",
    ),
]
