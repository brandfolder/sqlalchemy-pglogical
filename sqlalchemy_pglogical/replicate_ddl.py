from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.ddl import DDLElement

try:
    from alembic.ddl.base import AlterTable
except ImportError:
    HAS_ALEMBIC = False
else:
    import sqlalchemy_pglogical.replicate_alembic

from sqlalchemy_pglogical.base import ddl_to_replicate_command


def all_subclasses(cls):
    """recursively find subsclasses of `cls`"""
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )


def make_func_sqlalchemy(ddl):
    """
    Given a subclass of DDL, create a function to wrap the DDL
    command's output in a pglogical replicate_ddl_command call
    """
    visit_name = f"visit_{ddl.__visit_name__}"
    return lambda element, compiler, **kwargs: ddl_to_replicate_command(
        getattr(compiler, visit_name).__call__(element, **kwargs)
    )


def make_func_alembic(ddl):
    pass


alembic_ddls = {ddl for ddl in all_subclasses(AlterTable)}
# get every DDLElement that can be extended the way we expect (the hueristic here is having a `__visit_name__`)
sqlalchemy_ddls = {
    ddl
    for ddl in all_subclasses(DDLElement)
    if hasattr(ddl, "__visit_name__") and ddl not in alembic_ddls
}

for ddl in sqlalchemy_ddls:
    # make a function and decorate it
    compiles(ddl)(make_func_sqlalchemy(ddl))

# for ddl in alembic_ddls:
#    compiles(ddl)(make_func_alembic(ddl))
#
