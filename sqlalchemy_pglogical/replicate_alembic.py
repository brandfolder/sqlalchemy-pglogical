from alembic.ddl import base
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.compiler import DDLCompiler

from sqlalchemy_pglogical.base import ddl_to_replicate_command


@compiles(base.RenameTable)
def visit_rename_table(element: base.RenameTable, compiler: DDLCompiler, **kw) -> str:
    return ddl_to_replicate_command(base.visit_rename_table(element, compiler, **kw))


@compiles(base.AddColumn)
def visit_add_column(element: base.AddColumn, compiler: DDLCompiler, **kw) -> str:
    return ddl_to_replicate_command(base.visit_add_column(element, compiler, **kw))


@compiles(base.DropColumn)
def visit_drop_column(element: base.DropColumn, compiler: DDLCompiler, **kw) -> str:
    return ddl_to_replicate_command(base.visit_drop_column(element, compiler, **kw))


@compiles(base.ColumnNullable)
def visit_column_nullable(
    element: base.ColumnNullable, compiler: DDLCompiler, **kw
) -> str:
    return ddl_to_replicate_command(base.visit_column_nullable(element, compiler, **kw))


@compiles(base.ColumnType)
def visit_column_type(element: base.ColumnType, compiler: DDLCompiler, **kw) -> str:
    return ddl_to_replicate_command(base.visit_column_type(element, compiler, **kw))


@compiles(base.ColumnName)
def visit_column_name(element: base.ColumnName, compiler: DDLCompiler, **kw) -> str:
    return ddl_to_replicate_command(base.visit_column_name(element, compiler, **kw))


@compiles(base.ColumnDefault)
def visit_column_default(
    element: base.ColumnDefault, compiler: DDLCompiler, **kw
) -> str:
    return ddl_to_replicate_command(base.visit_column_default(element, compiler, **kw))


@compiles(base.ComputedColumnDefault)
def visit_computed_column(
    element: base.ComputedColumnDefault, compiler: DDLCompiler, **kw
):
    return ddl_to_replicate_command(base.visit_computed_column(element, compiler, **kw))


@compiles(base.IdentityColumnDefault)
def visit_identity_column(
    element: base.IdentityColumnDefault, compiler: DDLCompiler, **kw
):
    return ddl_to_replicate_command(base.visit_identity_column(element, compiler, **kw))
