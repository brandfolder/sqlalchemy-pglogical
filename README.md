# sqlalchemy-pglogical

`sqlalchemy-pglogical` is a sqlalchemy extension to automatically send DDL through 
`pglogical.replicate_ddl_command`

## Who's this for?

`sqlalchemy-pglogical` may be for you if:
- you use `sqlalchemy` and/or `alembic` for DDL, and 
- you use `pglogical` for logical replication

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

## Known limitations

### Only one publication

We currently assume you're using the `default_ddl` publication and only publish to that publication.

### CREATE INDEX CONCURRENTLY

`pglogical` can't propagate `{CREATE, DROP} INDEX CONCURRENTLY` statements. `sqlachemy-pglogical` makes
no attempt to catch the `CONCURRENTLY` keyword in `INDEX` statements, so they will likely fail.


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

