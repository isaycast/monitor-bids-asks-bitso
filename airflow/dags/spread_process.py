from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 10),
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'partition_spread_books_data',
    default_args=default_args,
    description='DAG to process spread_books table and partition by date',
    schedule_interval=timedelta(minutes=10), 
    catchup=False,  
    start_date=datetime(2024, 7, 10)
)

start = DummyOperator(
    task_id='start_partition_task',
    dag=dag,
)


spark_partition_task = BashOperator(
        task_id='spark_partition_task',
        bash_command='python /opt/airflow/scripts/partition_spread_books.py',
        dag=dag,
    )

end = DummyOperator(
    task_id='end_partition_task',
    dag=dag,
)




start >> spark_partition_task >> end