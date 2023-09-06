from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.ddl import DDLElement


def all_subclasses(cls):
    """recursively find subsclasses of `cls`"""
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )


def ddl_to_replicate_command(ddl: str) -> str:
    """
    Given a DDL command as a string, return a pglogical replicate command for that DDL
    """
    # TODO: allow specifying the replication sets
    # TODO: better escaping for the ddl command
    return "SELECT pglogical.replicate_ddl_command('%s')" % ddl


def make_func(ddl):
    """
    Given a subclass of DDL, create a function to wrap the DDL
    command's output in a pglogical replicate_ddl_command call
    """
    visit_name = f"visit_{ddl.__visit_name__}"
    return lambda element, compiler, **kwargs: ddl_to_replicate_command(
        getattr(compiler, visit_name).__call__(element, **kwargs)
    )


# get every DDLElement that can be extended the way we expect (the hueristic here is having a `__visit_name__`)
replicable_ddls = [
    ddl for ddl in all_subclasses(DDLElement) if hasattr(ddl, "__visit_name__")
]

for ddl in replicable_ddls:
    # make a function and decorate it
    compiles(ddl)(make_func(ddl))
