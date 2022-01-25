"""Tools for packaging poetry projects"""

import awswrangler as wr

from pyemr.utils.build import get_amazonlinux_build_path_s3
from pyemr.utils.config import (
    _pyproject_toml_exists, get_config_attr, get_datetime_string, get_env_name,
    get_static_files_dir,
)
from pyemr.utils.emr import get_cluster_id, wait_else_cancel
from pyemr.utils.s3 import upload_to_s3_stage
from pyemr.utils.sys import argskwargs_to_argv


def get_client_mode_runner_path():
    """Returns the path of the client mode runner script."""
    files_dir = get_static_files_dir()
    return f"{files_dir}/sh/client_mode_runner.sh"


def upload_client_mode_runner_to_s3():
    """Upload client mode runner script to s3."""
    client_runner_path = get_client_mode_runner_path()
    return upload_to_s3_stage(client_runner_path, "latest", "code")


def _get_standalone_spark_step(
    s3_script_path,
    submit_mode="client",
    action_on_failure="CONTINUE",
    script_args=None,
    script_kwargs=None,
):
    """

    Args:
      s3_script_path:
      submit_mode: (Default value = 'client')
      action_on_failure: (Default value = 'CONTINUE')
      args_str: (Default value = '')
      kwargs_str: (Default value = '')
      script_args: (Default value = [])
      script_kwargs: (Default value = {})

    Returns:

    """

    script_name = s3_script_path.split("/")[-1]
    env_name = "pyemr"
    step_name = f"{env_name}:spark-submit:{script_name}"
    jar_args = ["spark-submit", "--deploy-mode", submit_mode, s3_script_path]
    jar_args += argskwargs_to_argv(script_args, script_kwargs)

    spark_step = {
        "Name": step_name,
        "ActionOnFailure": action_on_failure,
        "HadoopJarStep": {
            "Jar": "command-runner.jar",
            "Args": jar_args,
        },
    }

    return spark_step


def _get_client_spark_step(
    s3_script_path,
    action_on_failure="CONTINUE",
    script_args=None,
    script_kwargs=None,
):
    """

    Args:
      s3_script_path:
      action_on_failure: (Default value = 'CONTINUE')
      args_str: (Default value = '')
      kwargs_str: (Default value = '')
      script_args: (Default value = [])
      script_kwargs: (Default value = {})

    Returns:

    """

    script_name = s3_script_path.split("/")[-1]
    client_runner_s3_path = upload_client_mode_runner_to_s3()
    s3_build_path = get_amazonlinux_build_path_s3()

    jar_args = [
        client_runner_s3_path,
        s3_build_path,
        "sudo",
        "PYARROW_IGNORE_TIMEZONE=1",
        "ARROW_PRE_0_15_IPC_FORMAT=1",
        "PYSPARK_DRIVER_PYTHON=./env/bin/python3",
        "PYSPARK_PYTHON=./env/bin/python3",
        "spark-submit",
        "--deploy-mode",
        "client",
        s3_script_path,
    ]

    # add args if they exist
    jar_args += argskwargs_to_argv(script_args, script_kwargs)

    region = get_config_attr("region")
    env_name = get_env_name()
    step_name = f"{env_name}:spark-submit:{script_name}"
    jar = f"s3://{region}.elasticmapreduce/libs/script-runner/script-runner.jar"
    spark_step = {
        "Name": step_name,
        "ActionOnFailure": action_on_failure,
        "HadoopJarStep": {
            "Jar": jar,
            "Args": jar_args,
        },
    }
    return spark_step


def _get_cluster_spark_step(
    s3_script_path,
    action_on_failure="CONTINUE",
    script_args=None,
    script_kwargs=None,
):
    """

    Args:
      s3_script_path:
      action_on_failure: (Default value = 'CONTINUE')
      args_str: (Default value = '')
      kwargs_str: (Default value = '')
      script_args: (Default value = [])
      script_kwargs: (Default value = {})

    Returns:

    """

    script_name = s3_script_path.split("/")[-1]
    s3_build_path = get_amazonlinux_build_path_s3()

    jar_args = [
        "sudo",
        "spark-submit",
        "--conf",
        "spark.yarn.appMasterEnv.PYSPARK_PYTHON=./env/bin/python3",
        "--conf",
        f"spark.yarn.dist.archives={s3_build_path}#env",
        "--master",
        "yarn",
        "--deploy-mode",
        "cluster",
        s3_script_path,
    ]

    jar_args += argskwargs_to_argv(script_args, script_kwargs)

    env_name = get_env_name()
    step_name = f"{env_name}:spark-submit:{script_name}"

    spark_step = {
        "Name": step_name,
        "ActionOnFailure": action_on_failure,
        "HadoopJarStep": {
            "Jar": "command-runner.jar",
            "Args": jar_args,
        },
    }

    return spark_step


def get_spark_step(
    local_script_path,
    submit_mode="client",
    action_on_failure="CONTINUE",
    script_args=None,
    script_kwargs=None,
):
    """Get spark step config

    Args:
      local_script_path:
      submit_mode: (Default value = 'client')
      action_on_failure: (Default value = 'CONTINUE')
      script_args: (Default value = [])
      script_kwargs: (Default value = {})

    Returns:

    """

    date_time = get_datetime_string()
    s3_script_path = upload_to_s3_stage(local_script_path, date_time, "code")
    submit_mode = submit_mode.lower()

    if not _pyproject_toml_exists():
        spark_step = _get_standalone_spark_step(
            s3_script_path,
            submit_mode,
            action_on_failure,
            script_args,
            script_kwargs,
        )
    elif submit_mode == "client":
        spark_step = _get_client_spark_step(
            s3_script_path,
            action_on_failure,
            script_args,
            script_kwargs,
        )
    elif submit_mode == "cluster":
        spark_step = _get_cluster_spark_step(
            s3_script_path,
            action_on_failure,
            script_args,
            script_kwargs,
        )
    else:
        raise ValueError(f"No submit mode called '{submit_mode}")

    return spark_step


def submit_spark_step(
    local_script_path,
    submit_mode,
    cluster_name,
    wait,
    script_args: list = None,
    script_kwargs: dict = None,
):
    """Submit python script to emr cluster.

    Args:
      local_script_path: path to local script
      submit_mode:
      cluster_name:
      wait:
      script_args: (Default value = [])
      script_kwargs: (Default value = {})
      script_args: list:  (Default value = None)
      script_kwargs: dict:  (Default value = None)
      script_args: list:  (Default value = None)
      script_kwargs: dict:  (Default value = None)
      script_args: list:  (Default value = None)
      script_kwargs: dict:  (Default value = None)
      script_args: list:  (Default value = None)
      script_kwargs: dict:  (Default value = None)
      script_args: list:  (Default value = None)
      script_kwargs: dict:  (Default value = None)
      script_args: list:  (Default value = None)
      script_kwargs: dict:  (Default value = None)
      script_args: list:  (Default value = None)
      script_kwargs: dict:  (Default value = None)

    Returns:
      str: Step id of submitted step.

    """
    submit_mode = submit_mode.lower().strip()
    assert submit_mode in ["client", "cluster"]

    # get the cluster id
    cluster_id = get_cluster_id(cluster_name)

    # get spark step dict
    spark_step = get_spark_step(
        local_script_path,
        submit_mode,
        "CONTINUE",
        script_args,
        script_kwargs,
    )

    # check if its a script runner of command runner
    script = spark_step["HadoopJarStep"]["Jar"].endswith("script-runner.jar")

    jar_args = spark_step["HadoopJarStep"]["Args"]
    if isinstance(jar_args, list):
        jar_args = [f"{a}" for a in jar_args]
        jar_args = " ".join(jar_args)

    # submit the step
    step_id = wr.emr.submit_step(
        cluster_id=cluster_id,
        name=spark_step["Name"],
        command=jar_args,
        script=script,
    )

    # wait till the step is complete
    if wait:
        wait_else_cancel(
            cluster_id,
            step_id,
        )

    return step_id
