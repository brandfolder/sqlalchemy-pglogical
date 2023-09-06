# dockerfile for pglogical container for integration tests
FROM postgres:13.10-bullseye


# we have to do a source install because pglogical isn't published for arm64
RUN apt update && \
    apt install -y curl make build-essential postgresql-server-dev-13 libkrb5-dev libxslt1-dev libselinux1-dev libpam0g-dev zlib1g-dev && \
    curl -LO https://github.com/2ndQuadrant/pglogical/archive/refs/tags/REL2_4_2.tar.gz && \
    tar xzf REL2_4_2.tar.gz && \
    cd pglogical-REL2_4_2 && \
    make clean && make install

COPY postgresql.conf /etc/postgresql/postgresql.conf