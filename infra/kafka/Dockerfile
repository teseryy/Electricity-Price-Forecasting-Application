FROM bitnami/kafka:latest

USER root

COPY create_topics.sh /create_topics.sh

RUN chmod +x /create_topics.sh

CMD /create_topics.sh & /opt/bitnami/scripts/kafka/entrypoint.sh /opt/bitnami/scripts/kafka/run.sh