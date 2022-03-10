Date: 2022-03-10

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Draft

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
Right now the `search` method only allows a dictionary of keys that the objects
must match, this way of selecting objects has become insufficient for the
programs that use the library forcing them to extract from the repository
a greater subset of objects that contain a serie of attributes and then do
another filtering afterwards. This is the case for example when the user wants
to select objects that:

* Have a datetime or integer greater or smaller than an amount.
* Don't have an attribute with a defined value
* Match a combination of criteria, for example:
    * Have an attribute with a value and another that is greater than X
    * Have an attribute with a value and another that doesn't contain the value
        Y.
* Match a criteria on a related object (`JOIN` operations).

This schema has the next disadvantages:

* The user is constrained to a very basic query type
* The repository returns more objects than the user needs, so more traffic is
    sent between the application and the database
* The user needs to do an extra filter afterwards. This is a bad idea because
    doing the filtering at databases level probably gives better performance
    and the user needs to write more code than necessary.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->

Change the way we let the user specify the criteria that it wants to search so
that it can do more powerful searches. I can think of two ways of doing this:

* Writing the query in a string and parsing it afterwards.
* Writing the query with a query builder.

Given [this
analysis](https://lyz-code.github.io/blue-book/architecture/orm_builder_query_or_raw_sql/),
the query builder system looks better.

## Query builder

We will create a `Query` object that follows the theory of [query
builders](https://lyz-code.github.io/blue-book/architecture/orm_builder_query_or_raw_sql/#query-builder).

Right now queries make sense only to extract data from the database, so speaking
in SQL terms, only `SELECT` and `DELETE` queries are interesting for us. To do
a select query you need:

* [The table to extract data from](#table-to-extract-data-from)
* [The fields to extract](#fields-to-extract)
* [The condition to select the rows](#condition-to-select-objects)
* [The sorting method of the results](#sorting-the-results)
* [The number of results to return](#number-of-results)

All of the `Query` methods return `self` in order to be able to construct it
with chained methods and properties. Those methods that don't need an argument
will be coded as properties to save keystrokes on unneeded `()`.

### Table to extract data from

Applied to the `repository_orm` usage, the `FROM` is defined by the model class both
to extract the table name, build the end objects and let the type checker know
what type of objects it's returning, so we need to pass the class of the model
to the `search` and `all` methods. It makes sense then to pass the argument at
initialization time of the `Query` object.

### Fields to extract

In our case it doesn't make sense to let the user select the fields it wants to
extract, as we return built objects and not just the values of the rows.

### Condition to select the objects

#### Simple query operators

Assuming that `query = Query(Model)` there are the next methods to select the
data, it will return the objects if:

* `equal`: Attribute match value.
* `not_equal`: Attribute doesn't match value.
* `greater`: Attribute is greater than value.
* `greater_or_equal`: Attribute is greater or equal than value.
* `smaller`: Attribute is smaller than value.
* `smaller_or_equal`: Attribute is smaller or equal than value.

To act on one attribute and one value you can use `query.method(attribute,
value)`, for example `query.equal('id_', 3)`. To act on many attributes you can
use `query.method({attribute1: value1, attribute2: value2})`, for example
`query.greater({'rating': 3, 'created_at': datetime.datetime.now()})`.

#### Query composition

If you concatenate methods and properties on a query they are supposed to be
conditions that all objects must match.


##### OR

`or` can be used to match one or many conditions but not others. You have to
select two types of criteria, so you need to `Query` objects.

`query.greater('rating', 3).or(Query().smaller('rating', 1))`

Note that if the second `Query` isn't initialized with a model, it will be
assumed to be the same as the first one.

##### AND

`and` can be used if you want to select different criteria for different
objects:

```python
Query(Book).greater('rating', 3).and(Query(Author).equal('id_', 1))
```

##### Join

`join` can be used to match entities if an entity that is related to them
matches one or many condition, for example to get all the books of the author
whose `id` is `1` you can:

```python
Query(Book).join(Query(Author).equal('id_', 1))
```

### Sorting the results

By default the results are sorted by `id_` increasingly, to sort by other
criteria use the `sort` method.

```python
query.sort('rating')
```

To reverse the order of the sorting use the `reverse` argument:

```python
query.sort('rating', reverse=True)
```

To order by many criteria chain `sort` methods, for example if you want to sort
by `rating` and then by `created_date` you can use:

```python
query.sort('rating').sort('created_date')
```

### Number of results

By default all results are returned, if you want to receive only a limited
amount use the `limit` method

```python
query.limit(10)
```

### Delete queries

Right now the `delete` method allows only one or many entities, we can change
the signature so that it also allows a `Query` object that can tweak the delete
query instead of just using the `id_`.

# Decision
<!-- What is the change that we're proposing and/or doing? -->

Implement the proposed solution, adding a `UserWarning` on the old method until
we deprecate it.

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->

Pros:

* We'll improve a lot the extraction of information from the repo

Cons:

Users will need to change their code:

* How they query the repositories.
