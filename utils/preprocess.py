
import os
import logging
import pandas as pd
import random
from airflow.decorators import task
from airflow.models import Variable
from datetime import datetime
import great_expectations as ge 
from . import validation_checks as vc
import shutil
import json
import requests



INPUT_FOLDER = "data/input_data"
GOOD_FOLDER = "data/output_data/good_data"
BAD_FOLDER = "data/output_data/bad_data"
FILE_PREFIX = "test_"
VARIABLE_NAME = "last_processed_file"
EXPECTED_COLUMNS = [
    "Temperature", "Humidity", "PM2.5", "PM10", "NO2", "SO2", "CO",
    "Proximity_to_Industrial_Areas", "Population_Density"
]


@task
def read_data() -> dict:
    files = [f for f in os.listdir(INPUT_FOLDER) if f.startswith(FILE_PREFIX) and f.endswith(".csv")]
    
    if not files:
        logging.info("No files available.")
        return None

    # Randomly choose a file
    selected_file = random.choice(files)
    filepath = os.path.join(INPUT_FOLDER, selected_file)

    try:
        input_data_df = pd.read_csv(filepath)
        logging.info(f"Successfully read data from file: {filepath}")
        return {
            "filename": selected_file,
            "data": input_data_df
        }
    except Exception as e:
        logging.error(f"Failed to read the file {filepath}: {str(e)}")
        return None

@task
def save_data_(data_to_ingest_df: pd.DataFrame, result: bool) -> None:
    if data_to_ingest_df is None:
        logging.info("No data to save.")
        return
    folder = "good_data" if result else "bad_data"
    filepath = f'data/output_data/{folder}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
    logging.info(f'Saving data to {filepath}')
    data_to_ingest_df.to_csv(filepath, index=False)


@task
def save_file(validation_result, data_df: pd.DataFrame, filename: str, filepath: str):
    nb_rows = validation_result["nb_rows"]
    nb_valid = validation_result["nb_valid"]
    nb_invalid = validation_result["nb_invalid"]

    # All good → move file to good_data
    if nb_invalid == 0:
        os.makedirs(GOOD_FOLDER, exist_ok=True)
        shutil.move(filepath, os.path.join(GOOD_FOLDER, filename))
    # All bad → move file to bad_data
    elif nb_valid == 0:
        os.makedirs(BAD_FOLDER, exist_ok=True)
        shutil.move(filepath, os.path.join(BAD_FOLDER, filename))
    # Mixed → split into two files
    else:
        os.makedirs(GOOD_FOLDER, exist_ok=True)
        os.makedirs(BAD_FOLDER, exist_ok=True)

        # Assuming the invalid rows were tracked by index in validation checks

        if "invalid_indices" in validation_result:
            invalid_indices = validation_result["invalid_indices"]
            valid_df = data_df.drop(index=invalid_indices)
            invalid_df = data_df.loc[invalid_indices]
        else:
            # fallback (not ideal): assume top N rows are invalid
            valid_df = data_df.sample(nb_valid)
            invalid_df = data_df.drop(valid_df.index)

        valid_path = os.path.join(GOOD_FOLDER, f"valid_{filename}")
        invalid_path = os.path.join(BAD_FOLDER, f"invalid_{filename}")

        valid_df.to_csv(valid_path, index=False)
        invalid_df.to_csv(invalid_path, index=False)

        # Optionally delete original file
        os.remove(filepath)


@task
def validate_data(input_data: pd.DataFrame) -> dict:
    all_issues = []
    total_invalid = 0

    checks = [
        vc.check_missing_columns(input_data, EXPECTED_COLUMNS),
        vc.check_missing_values(input_data, EXPECTED_COLUMNS),
        vc.check_unknown_values(input_data),
        vc.check_invalid_ranges(input_data),
        vc.check_string_in_numeric(input_data, EXPECTED_COLUMNS),
        vc.check_duplicates(input_data),
        vc.check_outliers(input_data, "Proximity to Industrial Areas", max_value=500)
    ]

    for issue_list, invalid_count in checks:
        all_issues.extend(issue_list)
        total_invalid += invalid_count

    total_rows = len(input_data)
    valid_rows = max(total_rows - total_invalid, 0)

    # Assign criticality
    if total_invalid == 0:
        criticality = "low"
    elif total_invalid < total_rows:
        criticality = "medium"
    else:
        criticality = "high"

    return {
        "nb_rows": total_rows,
        "nb_valid": valid_rows,
        "nb_invalid": total_invalid,
        "issues": list(set(all_issues)),  # remove duplicates
        "criticality": criticality,
    }


@task
def save_statistics(validation_result, file_name):
    stats = {
        "filename": file_name,
        "total_rows": len(validation_result["good_data"]) + len(validation_result["bad_data"]),
        "valid_rows": len(validation_result["good_data"]),
        "invalid_rows": len(validation_result["bad_data"]),
    }
    # Insert into your database here
    print("Saving stats:", stats)


@task
def send_alerts(validation_result, file_name):
    total = len(validation_result["good_data"]) + len(validation_result["bad_data"])
    invalid = len(validation_result["bad_data"])
    criticality = "low"
    if invalid == total:
        criticality = "high"
    elif invalid > 0:
        criticality = "medium"

    summary = {
        "filename": file_name,
        "invalid_rows": invalid,
        "total_rows": total,
        "criticality": criticality,
    }

    # Simulate Teams notification (replace with real webhook later)
    print(f"🚨 ALERT [{criticality.upper()}]: {summary}")

def split_bad_data(validation_result):
    return validation_result["good_data"], validation_result["bad_data"]