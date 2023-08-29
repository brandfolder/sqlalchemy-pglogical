# sqlalchemy-pglogical

`sqlalchemy-pglogical` is a sqlalchemy extension to automatically send DDL through 
`pglogical.replicate_ddl_command`

## How do I use it?

All you need to do to use this is import it before you call your DDL functions.
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