import tempfile, os
import time

import nox

nox.options.sessions = ["unit", "lint"]


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
@nox.parametrize("sqlalchemy", ["1.4", "2.0"])
@nox.parametrize("alembic", ["1.9", "1.10", "1.11", "1.12"])
def unit(session, sqlalchemy, alembic):
    session.install("psycopg2-binary")
    session.install(".")
    session.install(f"sqlalchemy=={sqlalchemy}")
    session.install(f"alembic=={alembic}")
    session.install("pytest")

    session.run("pytest", "tests/unit/")


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
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
    session.run("poetry", "install", "--no-root", "--only=dev", external=True)
    session.run("black", ".")
    session.run("isort", ".")


@nox.session(venv_backend=None)
def release(session):
    CHANGELOG = "CHANGELOG.md"
    PYPROJECT = "pyproject.toml"
    target_version_or_bump = session.posargs[0]
    
    # make sure we don't have work to commit
    try:
        session.run("git", "diff-files", "--quiet", external=True, silent=True)
        session.run("git", "diff-index", "--quiet", "--cached", "HEAD", "--", external=True, silent=True)
    except Exception as e:
        session.error("Working tree dirty - stash, commit, or revert local changes to continue")
        
    # make sure we're pushing a unique version
    tags = session.run("git", "ls-remote", "--tags", "git@github.com:brandfolder/sqlalchemy-pglogical.git", external=True, silent=True)
    versions = tags.split("\n")
    new_version = session.run("poetry", "version", "--short", target_version_or_bump)
    if new_version in versions:
        session.error(f"New Version {new_version} already exists in remote tags.")
    
    # confirm the user knows what we're doing
    confirm = input(f"You're about to release version {new_version}. Are you sure? [y/N]")
    if confirm.lower().strip() != "y":
        session.error(f"Aborting because you said no!")

    # get the release notes
    EDITOR = os.environ.get('EDITOR', 'vim')
    initial_message = f'''# {new_version}\n\n<!-- replace this line with your release notes in markdown format -->'''
    
    with tempfile.NamedTemporaryFile() as tf:
        tf.write(initial_message)
        tf.flush()
        session.run(EDITOR, tf.name)
    
        with open(tf.name, "r+t") as rf:
          release_notes = rf.read()

    with open(CHANGELOG, "r") as f:
        old_changelog = f.read()
    with open(CHANGELOG, "t") as f:
        f.write(release_notes)
        f.write(old_changelog)

    session.run("git", "add", PYPROJECT, CHANGELOG)
    session.run("git", "commit", "-m", f"Bumping version to {new_version}")

    print("Release created! Check the most recent commit to confirm everything looks good, then push the release tag to trigger a build")
    
    # open file for release notes
    # put notes into changelog
    # tag and annotate with notes

