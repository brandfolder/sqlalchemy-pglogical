import pathlib

import pytest
from alembic import command
from alembic.config import Config


def test_create_with_alembic(capsys):
    config = Config(
        pathlib.Path(__file__).parent.parent / "integration" / "alembic.ini"
    )
    command.upgrade(config, "b67a71ccf11e", sql=True)
    captured = capsys.readouterr()
    assert captured.out is not None
    lines = captured.out.split("\n")
    lines = [line for line in lines if not line.startswith("--")]
    statements = " ".join(lines).split(";")
    begin = statements.pop(0)
    assert begin.lower().strip() == "begin"
    _ = statements.pop(-1)  # this line is empty
    commit = statements.pop(-1)
    assert commit.lower().strip() == "commit"
    version = statements.pop(-1)
    assert version.lower().strip().startswith("insert into public.alembic_version")

    for statement in statements:
        assert (
            statement.lower()
            .strip()
            .startswith("select pglogical.replicate_ddl_command($sqlalchemypglogical$")
        )


@pytest.mark.parametrize(
    ("from_version", "to_version"),
    (
        ("b67a71ccf11e", "4b361a7c7bf3"),
        ("4b361a7c7bf3", "c3d4de521f9a"),
        ("c3d4de521f9a", "5907ff9d291e"),
        ("5907ff9d291e", "2a9b320f3470"),
    ),
)
def test_add_column_with_alembic(capsys, from_version, to_version):
    config = Config(
        pathlib.Path(__file__).parent.parent / "integration" / "alembic.ini"
    )
    command.upgrade(config, f"{from_version}:{to_version}", sql=True)
    captured = capsys.readouterr()
    assert captured.out is not None
    lines = captured.out.split("\n")
    lines = [line for line in lines if not line.startswith("--")]
    statements = " ".join(lines).split(";")
    begin = statements.pop(0)
    assert begin.lower().strip() == "begin"
    _ = statements.pop(-1)  # this line is empty
    commit = statements.pop(-1)
    assert commit.lower().strip() == "commit"
    version = statements.pop(-1)
    assert (
        version.lower().strip()
        == f"update public.alembic_version set version_num='{to_version}' where public.alembic_version.version_num = '{from_version}'"
    )

    for statement in statements:
        assert (
            statement.lower()
            .strip()
            .startswith("select pglogical.replicate_ddl_command($sqlalchemypglogical$")
        )
