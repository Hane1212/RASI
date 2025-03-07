from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import random
import os
import great_expectations as gx
import json
import requests

DATA_FOLDER = os.path.expanduser("~/data/input_data")
GOOD_DATA_FOLDER = os.path.expanduser("~/data/output_data/good_data")
BAD_DATA_FOLDER = os.path.expanduser("~/data/output_data/bad_data")
REPORTS_FOLDER = os.path.expanduser("~/demo/data/reports")
WEBHOOK_URL = "https://epitafr.webhook.office.com/webhookb2/9eb1845b-2859-45ce-be7a-b124aae4e064@3534b3d7-316c-4bc9-9ede-605c860f49d2/IncomingWebhook/c294bc2008f348ddb799eb2147b58027/8a70a586-fdee-47fa-a800-b10797e4d75f/V2xV0SA1e9UGZM49c_gx27n86ZsPfU27VISuJLZ8a-CcE1"


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 2, 12),
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

dag = DAG(
    "data_ingestion_dag",
    default_args=default_args,
    description="DAG for data ingestion and validation",
    schedule_interval="*/1 * * * *",  # Runs every minute
    catchup=False
)

def read_data():
    files = os.listdir(DATA_FOLDER)
    if not files:
        print("No files to process.")
        return None
    
    file_to_read = random.choice(files)
    return os.path.join(DATA_FOLDER, file_to_read)

def validate_data(**kwargs):
    ti = kwargs["ti"]
    file_path = ti.xcom_pull(task_ids="read_data")

    if file_path is None:
        return "no_data"

    # Create Great Expectations Context (Ephemeral Mode)
    context = gx.get_context(mode="ephemeral")

    # Create Expectation Suite
    suite_name = "ingestion_suite"
    suite = context.suites.add(gx.ExpectationSuite(name=suite_name))

    # Connect to data source
    data_source = context.data_sources.add_pandas("pandas")
    data_asset = data_source.add_dataframe_asset(name="pd_dataframe_asset")

    # Load CSV into DataFrame
    df = pd.read_csv(file_path)

    # Create Batch Definition and Batch
    batch_definition = data_asset.add_batch_definition_whole_dataframe(f"batch_{os.path.basename(file_path)}")
    batch = batch_definition.get_batch(batch_parameters={"dataframe": df})

    # Create Validator
    validator = context.get_validator(batch=batch, expectation_suite=suite)

    # Add Expectations
    validator.expect_column_values_to_not_be_null("co")
    validator.expect_column_values_to_be_between("temperature", min_value=-50, max_value=60)
    validator.expect_column_values_to_be_between("pm_25", min_value=0, max_value=150)
    validator.expect_column_values_to_match_regex("proximity_level", r"^-?\d+(\.\d+)?$", mostly=0.9)
    # validator.expect_column_values_to_be_of_type("humidity", "int")

    # Validate Data
    validation_result = validator.validate()

    # Print full validation result (for debugging)
    print(f"Full Validation Result for {file_path}:\n", validation_result)

    report_path = os.path.join(REPORTS_FOLDER, f"report_{os.path.basename(file_path)}.html")
    context.build_data_docs()
    with open(report_path, "w") as report_file:
        report_file.write(str(validation_result))
    # docs_path = os.path.join(REPORTS_FOLDER, "great_expectations")
    # os.makedirs(docs_path, exist_ok=True)  # Ensure directory exists
    # context.build_data_docs()
    # report_path = os.path.join(docs_path, "index.html")
    # if not os.path.exists(report_path):  
    #     print("❌ ERROR: Report file was not generated!")

    failed_expectations = sum([1 for res in validation_result.results if not res.success])
    if failed_expectations == 0:
        criticality = "low"
    elif failed_expectations <= 2:
        criticality = "medium"
    else:
        criticality = "high"
    
    alert_info = {
        "criticality": criticality,
        "summary": validation_result.statistics,
        "report_link": report_path
    }
    ti.xcom_push(key="alert_info", value=json.dumps(alert_info))
    # Return "bad_data" if any expectations fail, otherwise "good_data"
    return "bad_data" if not validation_result.success else "good_data"

def send_alerts(**kwargs):
    ti = kwargs["ti"]
    alert_info = json.loads(ti.xcom_pull(task_ids="validate_data", key="alert_info"))
    
    message = {
        "text": f"🚨 Data Quality Alert!\n\n**Criticality:** {alert_info['criticality']}\n\n**Summary:** {alert_info['summary']}\n\n[View Detailed Report]({alert_info['report_link']})"
    }
    requests.post(WEBHOOK_URL, json=message)
    print("Alert sent to Microsoft Teams.")

def move_data(**kwargs):
    ti = kwargs["ti"]
    file_path = ti.xcom_pull(task_ids="read_data")
    validation_result = ti.xcom_pull(task_ids="validate_data")

    if validation_result == "no_data":
        return

    if validation_result == "good_data":
        os.rename(file_path, os.path.join(GOOD_DATA_FOLDER, os.path.basename(file_path)))
    else:
        os.rename(file_path, os.path.join(BAD_DATA_FOLDER, os.path.basename(file_path)))

read_task = PythonOperator(task_id="read_data", python_callable=read_data, dag=dag)
validate_task = PythonOperator(task_id="validate_data", python_callable=validate_data, provide_context=True, dag=dag)
send_alert_task = PythonOperator(task_id="send_alerts", python_callable=send_alerts, provide_context=True, dag=dag)
move_task = PythonOperator(task_id="move_data", python_callable=move_data, provide_context=True, dag=dag)

