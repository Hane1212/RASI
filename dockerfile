FROM apache/airflow:2.10.5-python3.9

# Switch to airflow user before installing Python packages
USER airflow

# Install great_expectations as airflow user
RUN pip install --no-cache-dir great_expectations

ENV PATH="/home/airflow/.local/bin:${PATH}"

# Set working directory
WORKDIR /opt/airflow

# inside Dockerfile
COPY utils/ /opt/airflow/utils/
