FROM ghcr.io/dbt-labs/dbt-postgres:1.7.9

WORKDIR /dbt

COPY . /dbt

# 👇 Ajout pour patcher le bug
RUN pip install "protobuf<4.21.0"

