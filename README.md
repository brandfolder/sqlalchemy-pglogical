# sqlalchemy-pglogical

`sqlalchemy-pglogical` is a sqlalchemy extension to automatically send DDL through 
`pglogical.replicate_ddl_command`

## How do I use it?

There are two keys to using `sqlalchemy-pglogical`:

1. `import sqlalchemy_pglogical` - because of the way extending
   `sqlalchemy` works, you can do this in pretty much any file that 
   is loaded before DDL is called
2. Explicitly define your schema. If you're using `sqlalchemy`'s declaritive
   syntax, you define your schema by adding `__table_args__` to each table:
   ```python
   Base = declarative_base()
   
   
   class User(Base):
       __tablename__ = "users"
       __table_args__ = {"schema": "public"}
   ```
   if you're using `sqlalchemy` core and using `MetaData` to define your tables, 
   add `schema` as a keyword arg to your `MetaData` initialization:
   ```python
   metadata = Metadata(schema="public")
   ```

It probably makes the most sense to import it wherever you create your engine
to be sure it's always applied. For most apps, this is probably most important
for your migration toolchain (e.g. `alembic`), and less likely to be needed 
for your running application. If you're relying on `alembic` to build your 
`sqlalchemy.engine` (e.g, it's only defined in your alembic.ini), then you
should probably add this to your migration mako template.

```python
from sqlalchemy import create_engine
import sqlalchemy_pglogical
```

## How does it work?

DDL operations are represented in SQLAlchemy 1.x with a subclass of `DDLElement`. To
extend a DDL type, you can do this:

```python
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.ddl import CreateTable

@compiles(CreateTable)
def visit_create_table(element, compiler, **kwargs) -> str:
    normal_ddl_sql: str = compiler.visit_create_table(element, **kwargs)
    modified: str = some_modification_we_define_elsewhere(normal_ddl_sql)
    return modified
```

We use this to extend _all_ subclasses of `DDLElement` and wrap them in `pglogical.replicate_ddl_command`


## Development

Dependencies and packaging are managed with `poetry`. Get started with `poetry install --with=test`.

There are two test suites: unit tests and integration tests. Unit tests live in [the tests directory](./tests/)
and can be run with `nox` (if you don't have `nox`, install it with `pipx install nox` (if you don't have `pipx`,
install it with `python3 -m pip install pipx-in-pipx`)).
`nox` expects you to have several python versions installed (currently 3.8, 3.9, 3.10, and 3.11).
I recommend installing those all with [`pyenv`](https://github.com/pyenv/pyenv#installation),
then making them globally available with `pyenv global 3.8 3.9 3.10 3.11`

The integration tests run in [the integrations directory](./integration/)
and can be run via the [test.sh script](./integration/test.sh) in that directory. The integration tests require 
a trio of docker containers, so they're not currently well-suited to running in CI. 

Code is formatted with `black` - format with `black .`