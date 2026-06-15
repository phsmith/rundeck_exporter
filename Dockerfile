FROM python:3.13-alpine@sha256:420cd0bf0f3998275875e02ecd5808168cf0843cbb4d3c536432f729247b2acc AS build

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.11.0 /uv /uvx /bin/
COPY pyproject.toml uv.lock README.md /app/
COPY src /app/

ENV UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0

RUN uv sync --locked --no-dev \
    && uv build

FROM python:3.13-alpine@sha256:420cd0bf0f3998275875e02ecd5808168cf0843cbb4d3c536432f729247b2acc AS app

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

LABEL maintainer="Phillipe Smith <phsmithcc@gmail.com>" \
      org.opencontainers.image.created=$BUILD_DATE \
      org.opencontainers.image.title="rundeck-exporter" \
      org.opencontainers.image.description="Rundeck metrics exporter for Prometheus" \
      org.opencontainers.image.url="https://hub.docker.com/r/phsmith/rundeck-exporter" \
      org.opencontainers.image.revision=$VCS_REF \
      org.opencontainers.image.source="https://github.com/phsmith/rundeck_exporter" \
      org.opencontainers.image.version=$VERSION

RUN adduser --disabled-password --gecos '' rundeck

USER rundeck

COPY --from=build --chown=rundeck:rundeck /app/dist/ /tmp/dist/

RUN pip install --no-cache-dir /tmp/dist/rundeck_exporter*.whl \
    && rm -rf /tmp/dist/

ENV RUNDECK_EXPORTER_PORT=9620

EXPOSE ${RUNDECK_EXPORTER_PORT}

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD nc -z localhost ${RUNDECK_EXPORTER_PORT} || exit 1

ENTRYPOINT ["/home/rundeck/.local/bin/rundeck_exporter"]
