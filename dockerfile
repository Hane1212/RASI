FROM apache/airflow:2.10.5  

# Switch to airflow user before installing Python packages
USER airflow

# Install great_expectations as airflow user
RUN pip install --no-cache-dir great_expectations

# Set working directory
WORKDIR /opt/airflow
