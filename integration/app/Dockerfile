ARG DOCKER_IMAGE
FROM ${DOCKER_IMAGE}

RUN python3 -m pip install poetry

COPY entrypoint.sh /usr/local/bin/entrypoint.sh

WORKDIR /app/integration/app/example-app
ENTRYPOINT [ "/usr/local/bin/entrypoint.sh" ]
