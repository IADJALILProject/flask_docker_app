FROM bitnami/spark:3.5.0

USER root

RUN pip install --upgrade pip && \
    pip install pyspark pandas

RUN pip3 install pandas psycopg2-binary sqlalchemy
WORKDIR /opt/spark_jobs
COPY . /opt/spark_jobs

# Important pour importer les modules depuis spark/utils
ENV PYTHONPATH="/opt/spark_jobs:${PYTHONPATH}"

