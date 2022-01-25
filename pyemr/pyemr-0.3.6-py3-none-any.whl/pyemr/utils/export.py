"""A collection of aws tools"""
import os

from black import FileMode, format_str
from cron_descriptor import get_description
from jinja2 import Template

from pyemr.utils.config import (
    cinput, cprint, get_cluster_name, get_config_attr, get_emails,
    get_package_dir, get_project_attribute, get_project_attributes,
)
from pyemr.utils.emr import get_cluster_id
from pyemr.utils.submit import get_spark_step


def get_crop_expression():
    """ """
    got = False
    cprint("Tip: Try crontab guru -> https://crontab.guru/")
    while not got:
        cron_exp = cinput("Schedule Interval", "0 0 3 ? * MON *").strip()
        description = get_description("0 0 3 ? * MON *")
        correct = cinput(f"Is '{description}' correct?", "y")
        got = correct in ["y", "Y", "yes", "true", "Yes", "YES", True]

    return cron_exp, description


AIRFLOW_TEMPLATE_PATH = "files/templates/airflow_spark_step.template.py"


def export_airflow_template(
    local_script_path,
    submit_mode,
    action_on_failure,
    args,
    kwargs,
):
    """

    Args:
      local_script_path:
      submit_mode: (Default value = 'client')
      action_on_failure:
      args:
      kwargs:

    Returns:

    """
    if not os.path.isfile(local_script_path):
        raise ValueError(f"No such file as '{local_script_path}'")

    package_dir = get_package_dir()
    with open(f"{package_dir}/{AIRFLOW_TEMPLATE_PATH}") as file:
        airflow_template = file.read()

    param = get_project_attributes(["name", "version", "description"])
    param["emails"] = get_emails()
    param["owner"] = get_project_attribute("authors")[0]
    param["emr_cluster_name"] = get_cluster_name("default")
    param["emr_cluster_id"] = get_cluster_id("default")
    param["stage"] = get_config_attr("stage")
    param["spark_step"] = get_spark_step(
        local_script_path,
        submit_mode,
        action_on_failure,
        args,
        kwargs,
    )

    param["hadoop_jar_args"] = param["spark_step"]["HadoopJarStep"].pop("Args")
    param[
        "spep_id_formula"
    ] = "{{ task_instance.xcom_pull(task_ids='add_steps', key='return_value')[0] }}"

    cron_exp, cron_description = get_crop_expression()
    param["schedule_interval"] = cron_exp
    param["cron_description"] = cron_description

    airflow_template = Template(airflow_template)
    airflow_script = airflow_template.render(**param)
    airflow_script = format_str(airflow_script, mode=FileMode())

    with open("./airflow_dag.py", "w") as file:
        file.write(airflow_script.replace("# pylint: skip-file", ""))

    print("EXPORTED:./airflow_dag.py")
