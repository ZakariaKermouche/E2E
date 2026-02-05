#!/bin/bash

set -e

if [ -e "/opt/airflow/requirements.txt" ]; then
    $(command python) pip install --upgrade pip
    $(command -v pip) install --user -r requirements.txt
fi


if [ ! -f "/opt/airflow/airflow.db" ]; then
    airflow db init && \
    airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --password admin \
        --email admin@example.com
fi

$(command -v airflow) db upgrade

exec airflow webserver