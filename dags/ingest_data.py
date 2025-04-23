import pandas as pd
from datetime import timedelta
from airflow.decorators import dag
from airflow.utils.dates import days_ago
import great_expectations as ge
from utils import preprocess
from utils.validation_checks import CustomDataset


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
    file_name, data_to_ingest = preprocess.read_data()
    validate_results = CustomDataset.validate_data(data_to_ingest)
    if len(validate_results["bad_data"])>0:
        preprocess.send_alerts(validate_results, file_name)
        preprocess.save_statistics(validate_results, file_name)
        # TODO: Update split function
    preprocess.save_data(validate_results, True)


ingest_data_dag = ingest_data()
