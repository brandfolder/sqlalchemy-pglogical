import nox


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
@nox.parametrize("sqlalchemy", ["1.4", "2.0"])
def test(session, sqlalchemy):
    session.install("psycopg2-binary")
    session.install("/app/dist/sqlalchemy_pglogical-0.1.0-py3-none-any.whl")
    session.install(f"sqlalchemy=={sqlalchemy}")
    session.install("pytest")

    session.run("pytest")
