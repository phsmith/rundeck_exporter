FROM phsmith/rundeck-exporter:2.7.0

RUN adduser --disabled-password --gecos '' nonroot

USER nonroot

ENTRYPOINT ["/app/rundeck_exporter.py"]