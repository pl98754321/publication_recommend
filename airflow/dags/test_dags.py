import json
from datetime import datetime

import requests
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from scraping import *
from script import main

from airflow import DAG


def create_file(ti):

    import os

    root = os.getcwd()
    csvfolder = str(root) + "/plugins/research_csv"
    if not os.path.exists(csvfolder):
        os.mkdir(csvfolder)
    filepath = os.path.join(csvfolder, "demo_json.json")
    demo_json = {"abc": 1, "bcd": 2}
    with open(filepath, "w") as demo:
        json.dump(demo_json, demo)
    ti.xcom_push(key="scraping_path", value=filepath)


def read_file(ti):
    import os

    filepath = ti.xcom_pull(task_ids="craete_file", key="scraping_path")

    if os.path.exists(filepath):
        f = open(filepath)
        abc = json.load(f)
        f.close()
        print(abc)
    print(os.getcwd())


def ds_run_script(ti):
    paper_info_path = ti.xcom_pull(task_ids="scraping_data", key="paper_info_path")
    ref_info_path = ti.xcom_pull(task_ids="scraping_data", key="ref_info_path")
    main(paper_info_path, ref_info_path)


def fastapi_run_update(ti):
    import requests

    resp = requests.get("http://localhost:8081/update_data")
    if resp.status_code == 200:
        print("Update data success")
    else:
        raise ValueError(f"Update data failed {resp.text}")


def scraping(ti):

    paper_info_path, ref_info_path = get_scraping()
    ti.xcom_push(key="paper_info_path", value=paper_info_path)
    ti.xcom_push(key="ref_info_path", value=ref_info_path)


dag = DAG(
    "ds_project",
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

ds_task = PythonOperator(task_id="ds_task", python_callable=ds_run_script, dag=dag)

fastapi_task = PythonOperator(
    task_id="fastapi_task", python_callable=fastapi_run_update, dag=dag
)


# create_file_task >> read_file_task
scraping_task >> ds_task >> fastapi_task
