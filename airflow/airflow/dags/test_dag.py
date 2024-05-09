from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import datetime
import requests
import json

def create_file(ti):

    import os
    if not os.path.exists('./research_csv'):
        os.mkdir('./research_csv')
    filepath = os.path.join('./research_csv' , 'demo_json.json')
    demo_json = {'abc':1 , 'bcd':2}
    with open(filepath, 'w') as demo:
        json.dump(demo_json , demo)
    ti.xcom_push(key='scraping_path',value = filepath)

def read_file(ti):
    import os
    filepath = ti.xcom_pull(task_ids ='craete_file' , key='scraping_path' )

    if os.path.exists(filepath):
        f = open(filepath)
        abc = json.load(f)
        f.close()
        print(abc)
    print(os.getcwd())
    


def print_welcome():
    print('Welcome to Airflow!')



def print_date():
    print('Today is {}'.format(datetime.today().date()))



def print_random_quote():
    response = requests.get('https://api.quotable.io/random')
    quote = response.json()['content']
    print('Quote of the day: "{}"'.format(quote))



dag = DAG(
    'welcome_dag4',
    default_args={'start_date': days_ago(1)},
    schedule_interval='0 23 * * *',
    catchup=False
)


create_file_task = PythonOperator(
    task_id = 'craete_file',
    python_callable = create_file,
    dag=dag
)

read_file_task = PythonOperator(
    task_id = 'read_file',
    python_callable = read_file,
    dag = dag
)

# print_welcome_task = PythonOperator(
#     task_id='print_welcome',
#     python_callable=print_welcome,
#     dag=dag
# )



# print_date_task = PythonOperator(
#     task_id='print_date',
#     python_callable=print_date,
#     dag=dag
# )



# print_random_quote = PythonOperator(
#     task_id='print_random_quote',
#     python_callable=print_random_quote,
#     dag=dag
# )
# Set the dependencies between the tasks

create_file_task >> read_file_task 