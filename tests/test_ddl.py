import sqlalchemy as sa
from sqlalchemy.sql.compiler import DDLCompiler
import sqlalchemy_pglogical


def test_create_table_is_replicated():
    bind = sa.create_engine("postgresql://invalid:invalid@invalid/invalid")
    metadata = sa.MetaData()
    table = sa.Table("my_table", metadata, sa.Column("my_column", sa.Integer))
    create = sa.schema.CreateTable(table)
    #compiler = DDLCompiler("postgresql", create)
    compiled = create.compile(bind)
    assert 'create' in compiled.string.lower()
    assert compiled.string.startswith('pglogical.replicate_ddl_command(')


def test_all_subclasses_recursion():
    last = type('a', (object,), {})
    first = last
    for i in range(100):
        last = type(f'a{i}', (last,), {} )
    assert len(sqlalchemy_pglogical.replicate_ddl.all_subclasses(first)) == 100


