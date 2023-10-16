import time

import nox

nox.options.sessions = ["unit", "lint"]


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
@nox.parametrize("sqlalchemy", ["1.4", "2.0"])
@nox.parametrize("alembic", ["1.9", "1.10", "1.11", "1.12"])
def unit(session, sqlalchemy, alembic):
    session.install("psycopg2-binary")
    session.install(".")
    session.install(f"sqlalchemy=={sqlalchemy}")
    session.install(f"alembic=={alembic}")
    session.install("pytest")

    session.run("pytest", "tests/unit/")


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
@nox.parametrize("sqlalchemy", ["1.4", "2.0"])
@nox.parametrize("alembic", ["1.9", "1.10", "1.11", "1.12"])
def integration(session, sqlalchemy, alembic):
    quiet = False
    if session.posargs and "quiet" in session.posargs:
        quiet = True
    session.run("docker", "compose", "down", "-v", external=True, silent=quiet)
    session.run("docker", "compose", "up", "--build", "-d", external=True, silent=quiet)

    session.install("psycopg2-binary", silent=quiet)
    session.install(".", silent=quiet)
    session.install(f"sqlalchemy=={sqlalchemy}", silent=quiet)
    session.install(f"alembic=={alembic}", silent=quiet)
    session.install("pytest", silent=quiet)
    session.install("flaky", silent=quiet)

    for _ in range(30):
        try:
            session.run(
                "docker",
                "compose",
                "exec",
                "primary",
                "pg_isready",
                external=True,
                silent=quiet,
            )
        except:
            time.sleep(0.5)
        else:
            break

    session.run("pytest", "tests/integration/", silent=quiet)


@nox.session
def lint(session):
    session.install("black")
    session.install("isort")
    session.run("black", ".")
    session.run("isort", ".")
