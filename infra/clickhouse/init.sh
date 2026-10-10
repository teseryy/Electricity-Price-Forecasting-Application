#!/bin/bash

if [ -z "$CLICKHOUSE_ADMIN_USER" ] || [ -z "$CLICKHOUSE_ADMIN_PASSWORD" ]; then
    echo "ERROR with env variables"
    exit 1
fi

clickhouse-client -u "${CLICKHOUSE_ADMIN_USER}" --password "${CLICKHOUSE_ADMIN_PASSWORD}" --query="CREATE DATABASE IF NOT EXISTS prices;"

clickhouse-client -u "${CLICKHOUSE_ADMIN_USER}" --password "${CLICKHOUSE_ADMIN_PASSWORD}" --query="
CREATE TABLE IF NOT EXISTS prices.daily_prices
(
    date Date,
    price Nullable(Float32),
    temperature Float32,
    inserted_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree()
ORDER BY date;"

clickhouse-client -u "${CLICKHOUSE_ADMIN_USER}" --password "${CLICKHOUSE_ADMIN_PASSWORD}" --query="
CREATE TABLE IF NOT EXISTS prices.hourly_prices
(
    date DateTime,
    price Nullable(Float32),
    temperature Float32,
    inserted_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree()
ORDER BY date;"