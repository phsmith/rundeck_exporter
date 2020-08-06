FROM python:alpine

LABEL version="1.2.0" \
      description="Rundeck metrics exporter to Prometheus" \
      maintainer="Phillipe Smith <phillipelnx@gmail.com>"

RUN pip install prometheus-client requests cachetools

COPY rundeck_exporter.py /usr/bin

ENTRYPOINT ["/usr/bin/rundeck_exporter.py"]
