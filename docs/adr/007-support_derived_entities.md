Date: 2022-07-02

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Draft

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
There are some cases where the current use of the entities falls short:

* [When a service updates part of the attributes of an entity.](#service-updates-part-of-the-attributes-of-an-entity)
* When an entrypoint accepts part of the attributes of an entity.
* When an entrypoint returns an entity plus some added attributes.

## Service updates part of the attributes of an entity

Imagine that we have an entity that has two attributes, one is retrieved from an
external API and changes over the time, the second is given by the user at
creation time and it doesn't change over the time:

```python
class Author(Entity):
    number_of_books: int
    added_at: datetime
```

If we have a service called `get_author_books` that gets the `number_of_books`
of an author, it needs to build a valid `Author` object so that it's able to
`repo.add()` it to persist the changes. The problem is that `added_at` is
a required attribute that was filled the first time we created the `Author`
object. But successive calls to `get_author_books` don't need to touch this
attribute, it only needs to update the `number_of_books`.

To solve this we can:

* Make `added_at` signature as `Optional[datetime] = None`, so that we don't
    need to fill up this attribute, and use the `merge` mode of `repo.add()`
    that won't update the value of the stored entity for all attributes that
    were not explicitly set.

    The problem with this approach is that we don't want `added_at` to be `None`
    for the rest of the program, so we would be tweaking the types of the
    model to be able to update part of the model, but actually we will be
    breaking the expected model signature.

* Create a function that `repo.get()` the entity we want to update, update the
    value and `repo.add()` it back.

    This has the downsides that the types of that function don't reflect the




<!-------------------8<------------------->

 [Task] Idea de repository orm, añadir el metodo merge, que acepte id, entity y objeto de update, donde ese objeto esta creado por un servicio y su clase es un subconjunto de los atributos de la clase del entity.

De manera que la mergeabilidad no es solo entre objetos de la misma clase, sino que por objetos con los mismos atributos.

Lo way seria crear esa clase derivada a partir de la clase que representa mediante el borrado de los fields que no necesite y el añadido de fields que le faltan, como muestra este issue

https://github.com/samuelcolvin/pydantic/issues/830

https://github.com/samuelcolvin/pydantic/issues/1937

https://stackoverflow.com/questions/15247075/how-can-i-dynamically-create-derived-classes-from-a-base-class


Quiza no hace falta añador el merge, quiza se pueda usar add(update_object, Entity), y que sea suficientemente inteligente como para hacer el merge

A lo mejor si hace falta un metodo distinto, ya que es probable que el objeto derivado no sepa el id del objeto a actualizar, sino que el merge sea en funcion de otra propiedad, entonces seria repo.merge(authir_up

Para persistir objetos, la clase derivada deberia usar solo un sibconjunto de la clase original. Pero para output de respuestas de entrypoints, si podria ser interesante devolver información procesada adicional

El modo de derivar clases es con el create_model, mirar la docu

https://pydantic-docs.helpmanual.io/usage/models/#dynamic-model-creation

Y el codigo fuente

https://github.com/samuelcolvin/pydantic/blob/81b13ff3b4f67560dc1b5292ab5bb30e91276fd7/pydantic/main.py#L910

Añador fields es trivial a partir de la docu, quitarlos no tanto.

Quiza se puede coger la.base class y acceder al atributo fields y annotations y en funcion de eso construir el argumento de create_model

De ser asi, we can save the parent class in an internal attribute, so that add is able to understand it and we don't need to pass it as an extra argument. Then the signature would be

add(entity: Union[DerivedEntity, Entity], merge_on: optional[str] = None)

Where merge on will be the attribute name that get will use to fetch the parent entity to merge.

If we pass a derived entity, the return value should be the updated entity, but that may be difficult to define as a signature

https://stackoverflow.com/questions/60202691/python-typing-declare-return-value-type-based-on-function-argument

https://docs.python.org/3/library/typing.html#typing.Protocol

We can create derivedentity from basemodel, and when we use create_model, use it as __base__

If we make the derivedentity a generic class that uses entity, the hints may work

We need to handle the cases where the user uses a derived entity on the rest of the models (Use shortcuts or arrow keys)
<!-------------------8<------------------->

# Proposals
<!-- What are the possible solutions to the problem described in the context -->

## Deprecate the merge mode of repo.add()?????

TBD

# Decision
<!-- What is the change that we're proposing and/or doing? -->

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
