import os
import logging
import pandas as pd
from datetime import datetime
from datetime import timedelta
from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from airflow.models import Variable
import random
import great_expectations as ge
from utils import *


INPUT_FOLDER = "data/input_data"
GOOD_FOLDER = "data/good_data"
BAD_FOLDER = "data/bad_data"
FILE_PREFIX = "test_" 
VARIABLE_NAME = "last_processed_file"
expected_columns = [
    "Temperature", "Humidity", "PM2.5", "PM10", "NO2", "SO2", "CO",
    "Proximity_to_Industrial_Areas", "Population_Density"
]

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
    def read_data_in_order() -> pd.DataFrame:
        """Get the next file in the sequence based on the last processed file"""
        processed_file = Variable.get(VARIABLE_NAME, default_var="")  # Get last file processed
        files = sorted(f for f in os.listdir(INPUT_FOLDER) if f.startswith(FILE_PREFIX) and f.endswith(".csv"))
        
        if not files:
            logging.info("No files available.")
            filepath =  None
        
        next_file = files[0] if processed_file == "" else None
        if processed_file in files:
            index = files.index(processed_file)
            if index + 1 < len(files):
                next_file = files[index + 1]
        
        if next_file:
            logging.info(f"Next file to process: {next_file}")
            Variable.set(VARIABLE_NAME, next_file)  # Save progress
            filepath = os.path.join(INPUT_FOLDER, next_file)
        else:
            logging.info("No new files to process.")
            filepath =  None
        
        if not filepath:
            logging.info("No file to process this run.")
            return None
        input_data_df = pd.read_csv(filepath)
        logging.info(f'Extract data from the file {filepath}')
        return input_data_df

    @task
    def read_data() -> pd.DataFrame:
        """Randomly select a file from the raw-data folder and read it"""
        files = [f for f in os.listdir(INPUT_FOLDER) if f.startswith(FILE_PREFIX) and f.endswith(".csv")]

        if not files:
            logging.info("No files available.")
            return None

        # Randomly choose a file
        selected_file = random.choice(files)
        filepath = os.path.join(INPUT_FOLDER, selected_file)

        logging.info(f"Randomly selected file to process: {selected_file}")
        Variable.set(VARIABLE_NAME, selected_file)  # Optional: store selected file

        try:
            input_data_df = pd.read_csv(filepath)
            logging.info(f"Successfully read data from file: {filepath}")
            return input_data_df
        except Exception as e:
            logging.error(f"Failed to read the file {filepath}: {str(e)}")
            return None

    @task
    def validate_data(data_to_ingest_df: pd.DataFrame):
        verification_checks = [
        verify_missing_column(data_to_ingest_df),
        verify_missing_values,
        verify_humidity_value,
        verify_PM10_value,
        verify_SO2_value
            ]
    


    @task
    def verify_csv_file(data_to_ingest_df: pd.DataFrame):
        if data_to_ingest_df is None:
            return False
        
        verification_checks = [
        verify_missing_column,
        verify_missing_values,
        verify_humidity_value,
        verify_PM10_value,
        verify_SO2_value
            ]

        results = {func.__name__: func(data_to_ingest_df) for func in verification_checks}

        # Log failed checks
        failed_checks = [name for name, result in results.items() if not result]
        if failed_checks:
            logging.error(f"CSV file failed the following checks: {failed_checks}")
            return False

        logging.info("CSV file passed all checks ✅")
        return True

    @task
    def save_data(data_to_ingest_df: pd.DataFrame, result: bool) -> None:
        if data_to_ingest_df is None:
            logging.info("No data to save.")
            return
        folder = "good_data" if result else "bad_data"
        filepath = f'data/output_data/{folder}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        logging.info(f'Saving data to {filepath}')
        data_to_ingest_df.to_csv(filepath, index=False)
        

    data_to_ingest = utils.read_data()
# result = verify_csv_file(data_to_ingest)
    save_data(data_to_ingest, True)

ingest_data_dag = ingest_data()

# 1. A required feature (column) is missing
def verify_missing_column_(data_to_ingest_df: pd.DataFrame) -> bool:
    actual_columns = list(data_to_ingest_df.columns)
    return set(actual_columns) == set(expected_columns)

def verify_missing_column(data_to_ingest_df: pd.DataFrame):
    ge_df = ge.from_pandas(data_to_ingest_df)
    for col in expected_columns:
        ge_df.expect_column_to_exist(col)
    
    
# 2. Missing values in a required column
def verify_missing_values(data_to_ingest_df: pd.DataFrame)-> bool:
    return not data_to_ingest_df[expected_columns].isnull().any().any()
    
# 4.1. Wrong value of Humidity, range value of Humidity from 0 -> 100%
def verify_humidity_value(df: pd.DataFrame) -> bool:
    col = 'Humidity'
    if (df[col]<=100).all():
        return True
    else:
        return False
    
# 4.2. Wrong value of SO2, range value of SO2 from 0 -> 1000  
def verify_SO2_value(df: pd.DataFrame) -> bool:
    col = 'SO2'
    if (df[col]>0).all():
        return True
    else:
        return False  
    
# 4.3. Wrong value of PM10, range value of PM10 from 0 -> 1000
def verify_PM10_value(df: pd.DataFrame) -> bool:
    col = 'PM10'
    if (df[col]>0).all():
        return True
    else:
        return False  
# 5. A string value in a numerical column
#  

# if __name__ == "__main__":
#     ingest_data_dag.test()
