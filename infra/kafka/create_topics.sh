#!/bin/bash

while ! kafka-topics.sh --bootstrap-server localhost:9092 --list >/dev/null 2>&1; do
  echo "Waiting for Kafka to be ready..."
  sleep 5
done

kafka-topics.sh --bootstrap-server localhost:9092 --create --topic ltopic --partitions 3 --replication-factor 1
kafka-topics.sh --bootstrap-server localhost:9092 --create --topic confirm_topic --partitions 3 --replication-factor 1
kafka-topics.sh --bootstrap-server localhost:9092 --create --topic test_topic --partitions 3 --replication-factor 1

echo "Topics created successfully!"