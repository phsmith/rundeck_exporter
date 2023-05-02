FROM python:alpine

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

LABEL maintainer="Phillipe Smith <phsmithcc@gmail.com>" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="Rundeck Exporter" \
      org.label-schema.description="Rundeck metrics exporter for Prometheus" \
      org.label-schema.url="https://hub.docker.com/r/phsmith/rundeck-exporter" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/phsmith/rundeck_exporter" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"

COPY VERSION requirements.txt /
COPY rundeck_exporter.py /usr/bin/rundeck_exporter

RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

ENTRYPOINT ["/usr/bin/rundeck_exporter"]
