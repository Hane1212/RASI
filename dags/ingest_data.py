import os
import logging
import pandas as pd
from datetime import datetime
from datetime import timedelta
from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from airflow.models import Variable


INPUT_FOLDER = "data/input_data"
FILE_PREFIX = "test_" 
VARIABLE_NAME = "last_processed_file"

@dag(
    dag_id='ingest_data',
    description='Ingest data from a file to another DAG',
    tags=['dsp', 'data_ingestion'],
    schedule=timedelta(minutes=1),
    start_date=days_ago(n=0, hour=1),  # sets the starting point of the DAG
    max_active_runs=1  # Ensure only one active run at a time
)
def ingest_data():
    
    @task
    def get_next_file() -> str:
        """Get the next file in the sequence based on the last processed file"""
        processed_file = Variable.get(VARIABLE_NAME, default_var="")  # Get last file processed
        files = sorted(f for f in os.listdir(INPUT_FOLDER) if f.startswith(FILE_PREFIX) and f.endswith(".csv"))
        
        if not files:
            logging.info("No files available.")
            return None
        
        next_file = files[0] if processed_file == "" else None
        if processed_file in files:
            index = files.index(processed_file)
            if index + 1 < len(files):
                next_file = files[index + 1]
        
        if next_file:
            logging.info(f"Next file to process: {next_file}")
            Variable.set(VARIABLE_NAME, next_file)  # Save progress
            return os.path.join(INPUT_FOLDER, next_file)
        else:
            logging.info("No new files to process.")
            return None

    @task
    def get_data_to_ingest_from_local_file(filepath: str) -> pd.DataFrame:
        if not filepath:
            logging.info("No file to process this run.")
            return None

        nb_rows = 5
        input_data_df = pd.read_csv(filepath)
        logging.info(f'Extract {nb_rows} rows from the file {filepath}')
        data_to_ingest_df = input_data_df.sample(n=nb_rows)
        return data_to_ingest_df

    @task
    def save_data(data_to_ingest_df: pd.DataFrame) -> None:
        filepath = f'data/output_data/good_data/{datetime.now().strftime("%Y-%M-%d_%H-%M-%S")}.csv'
        logging.info(f'Ingesting data to the file: {filepath}')
        data_to_ingest_df.to_csv(filepath, index=False)

    # Task relationships
    file_path = get_next_file()
    data_to_ingest = get_data_to_ingest_from_local_file(file_path)
    save_data(data_to_ingest)


ingest_data_dag = ingest_data()
