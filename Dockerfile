FROM python:3.13-alpine AS build

WORKDIR /app

# hadolint ignore=DL3018
RUN apk add --no-cache uv

COPY pyproject.toml uv.lock README.md /app/
COPY src tests /app/

ENV UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0

RUN uv sync --locked --all-extras --dev \
    && uv build

FROM python:3.13-alpine AS app

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

LABEL maintainer="Phillipe Smith <phsmithcc@gmail.com>" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="rundeck-exporter" \
      org.label-schema.description="Rundeck metrics exporter for Prometheus" \
      org.label-schema.url="https://hub.docker.com/r/phsmith/rundeck-exporter" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/phsmith/rundeck_exporter" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"

# hadolint ignore=DL3018
RUN apk upgrade -U \
    && adduser --disabled-password --gecos '' rundeck

USER rundeck

COPY --from=build /app/dist/ /tmp/dist/

RUN pip install --no-cache-dir /tmp/dist/rundeck_exporter*.whl

ENTRYPOINT ["/home/rundeck/.local/bin/rundeck_exporter"]
