import time

import nox

nox.options.sessions = ["unit", "lint"]


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
@nox.parametrize("sqlalchemy", ["1.4", "2.0"])
def unit(session, sqlalchemy):
    session.install("psycopg2-binary")
    session.install(".")
    session.install(f"sqlalchemy=={sqlalchemy}")
    session.install("pytest")

    session.run("pytest", "tests/unit/")


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
@nox.parametrize("sqlalchemy", ["1.4", "2.0"])
def integration(session, sqlalchemy):
    session.run("docker", "compose", "down", external=True)
    session.run("docker", "compose", "rm", "-f", external=True)
    session.run("docker", "compose", "up", "--build", "-d", external=True)

    session.install("psycopg2-binary")
    session.install(".")
    session.install(f"sqlalchemy=={sqlalchemy}")
    session.install("pytest")

    for _ in range(30):
        try:
            session.run(
                "docker", "compose", "exec", "primary", "pg_isready", external=True
            )
        except:
            time.sleep(0.5)
        else:
            break

    session.run("pytest", "tests/integration/")


@nox.session
def lint(session):
    session.install("black")
    session.install("isort")
    session.run("black", ".")
    session.run("isort", ".")
