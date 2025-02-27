#!/bin/bash

# Wait for Airflow DB to be ready
sleep 10  

# Create an admin user if it doesn't exist
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
