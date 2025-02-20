# dockerfile for pglogical container for integration tests
FROM postgres:14-bullseye

RUN apt update && apt install postgresql-14-pglogical

COPY postgresql.conf /etc/postgresql/postgresql.conf
