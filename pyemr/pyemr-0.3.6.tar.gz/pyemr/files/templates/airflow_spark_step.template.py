# pylint: skip-file
import datetime as dt

from airflow import DAG
from airflow.contrib.operators.emr_add_steps_operator import EmrAddStepsOperator
from airflow.contrib.sensors.emr_step_sensor import EmrStepSensor


# emr cluster if
# cluster_name = {{emr_cluster_name}}
cluster_id = "{{emr_cluster_id}}"

# spark step config
spark_step = {{spark_step}}

# add scrip and env param
spark_step["HadoopJarStep"]["Args"] = {{hadoop_jar_args}}

# Schedule Interval ({{cron_description}})
cron_expression = "{{schedule_interval}}"

# create the dag
dag_args = {
    "dag_id": "{{stage}}-{{name}}".replace(" ", "-"),
    "description": "{{description}}",
    "schedule_interval": cron_expression,
    "start_date": dt.datetime(year=2021, month=9, day=5),
    "default_args": {
        "owner": "{{owner}}",
        "depends_on_past": False,
        "email": {{emails}},
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": dt.timedelta(minutes=5),
        "sla": dt.timedelta(hours=4),
    },
}

# command for getting step_id
step_id = "{{spep_id_formula}}"

with DAG(**dag_args) as dag:
    step_adder = EmrAddStepsOperator(
        task_id="add_steps",
        job_flow_id=cluster_id,
        steps=[spark_step],
    )
    step_checker = EmrStepSensor(
        task_id="watch_step",
        job_flow_id=cluster_id,
        step_id=step_id,
    )
    step_adder >> step_checker
