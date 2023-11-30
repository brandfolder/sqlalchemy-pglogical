# Development

## Getting Started

Dependencies and packaging are managed with `poetry`. Get started with `poetry install --with=test`.

There are two test suites: unit tests and integration tests. 
Unit tests and linters can be run with `nox` (if you don't have `nox`, install
it with `pipx install nox` (if you don't have `pipx`, install it with
`python3 -m pip install pipx-in-pipx`)).
`nox` expects you to have several python versions installed (currently 3.8, 3.9, 3.10, and 3.11).
I recommend installing those all with [`pyenv`](https://github.com/pyenv/pyenv#installation),
then making them globally available with `pyenv global 3.8 3.9 3.10 3.11`

The integration tests are available via `nox` but are skipped by default because they're very slow. You can
run them with `nox -s integration`. The integration tests stand up a docker container using docker compose, 
and manage two databases in that container. 

## Integration tests

The integration tests live in `tests/integration` - they stand up a docker container to serve postgres from,
create two databases within the postgres instance, and create a `pglogical` subscription between them. 
Run the integration tests with `nox -s integration`

Some of the integration tests run alembic directly. These tests should remain ordered top to bottom so
failures make more sense. To add a new revision, change directories to `tests/integration`, then run 
`alembic revision -m "some helpful descriptor"`.

## Cutting releases

There's a nox target for creating a release. It will 

- bump the version in the necessary files,
- ask you to provide release notes
- update the changelog
- commit these updates
- tag the commit, annotating the tag with the release notes 

To cut a new release:

1. run the tests again, just to be sure
1. run `nox -s -- <version or bump rule>` where `version` is the new version id (e.g, 0.1.1) or bump rule is 
   a bump rule as recognized by `poetry` (e.g. patch, minor, or major)
1. push the commit + tag it makes
1. approve the pypi publish job on Github


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
