#!/bin/bash

if [ -f /opt/airflow/init_completed ]; then
  echo "Removing init marker file to allow reinitialization"
  rm /opt/airflow/init_completed
fi

if [ -f /opt/airflow/airflow.db ]; then
  echo "Removing Airflow database to start fresh"
  rm /opt/airflow/airflow.db
fi

airflow db init

airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

airflow scheduler &

exec airflow webserver