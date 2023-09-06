ARG DOCKER_IMAGE
FROM ${DOCKER_IMAGE}

COPY entrypoint.sh /usr/local/bin/entrypoint.sh

WORKDIR /app/integration/app/example-app
ENTRYPOINT [ "/usr/local/bin/entrypoint.sh" ]
