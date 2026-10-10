FROM clickhouse/clickhouse-server:latest

WORKDIR /etc/clickhouse-server

COPY users.xml /etc/clickhouse-server/users.xml

ENV CLICKHOUSE_ADMIN_USER=myuser
ENV CLICKHOUSE_ADMIN_PASSWORD=mypassword

COPY init.sh /docker-entrypoint-initdb.d/init.sh
RUN chmod +x /docker-entrypoint-initdb.d/init.sh

RUN apt-get update && apt-get install -y curl

EXPOSE 8123