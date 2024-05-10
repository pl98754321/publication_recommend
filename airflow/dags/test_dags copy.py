from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import datetime
import requests
import json
from scraping import *


def read_file(ti):
    import os

    filepath = ti.xcom_pull(task_ids="craete_file", key="scraping_path")

    if os.path.exists(filepath):
        f = open(filepath)
        abc = json.load(f)
        f.close()
        print(abc)
    print(os.getcwd())


def scraping(ti):

    paper_info_path, ref_info_path = get_scraping()
    ti.xcom_push(key="paper_info_path", value=paper_info_path)
    ti.xcom_push(key="ref_info_path", value=ref_info_path)


def get_current_directory():
    print(os.getcwd())


def print_complete():
    print("Complete scraping!!")


dag = DAG(
    "nearly_project",
    default_args={"start_date": days_ago(1)},
    schedule_interval="0 12 * * *",
    catchup=False,
)


# create_file_task = PythonOperator(
#     task_id = 'craete_file',
#     python_callable = create_file,
#     dag=dag
# )

# read_file_task = PythonOperator(
#     task_id = 'read_file',
#     python_callable = read_file,
#     dag = dag
# )

scraping_task = PythonOperator(
    task_id="scraping_data", python_callable=scraping, dag=dag
)

print_complete_task = PythonOperator(
    task_id="print_complete", python_callable=print_complete, dag=dag
)

print_current_directory = PythonOperator(
    task_id="print_current_directory",
    python_callable=get_current_directory,
    dag=dag,
)

# create_file_task >> read_file_task
scraping_task >> print_current_directory
