"""A collection of aws tools"""
import fnmatch
import os
import time
from functools import lru_cache

import awswrangler as wr
import boto3
import pandas as pd
from tqdm import tqdm

from .config import (
    _pyproject_toml_exists, color_text, cprint, get_cluster_name, get_env_name,
    load_config,
)


CLUSTER_STATES = ["WAITING", "RUNNING", "STARTING"]
ALL_CLUSTER_STATES = [
    "STARTING",
    "BOOTSTRAPPING",
    "RUNNING",
    "WAITING",
    "TERMINATING",
    "TERMINATED",
    "TERMINATED_WITH_ERRORS",
]


def cancel_emr_step(cluster_id, step_id):
    """Cancel the last emr step.

    Args:
      cluster_id:
      step_id:

    Returns:

    """
    client = boto3.client("emr")
    response = client.cancel_steps(
        ClusterId=cluster_id,
        StepIds=[step_id],
    )
    cprint(f"Canceled step {step_id}")
    return response


def yield_step_state(cluster_id, step_id, sleep=4):
    """Fields the state (complete/canceled/failed) of the specified step.

    Args:
      cluster_id:
      step_id:
      sleep: (Default value = 4)

    Returns:

    """

    while True:
        time.sleep(sleep)
        state = wr.emr.get_step_state(cluster_id, step_id)
        yield state


def wait_else_cancel(cluster_id, step_id, description="Waiting"):
    """Waits on a step to complete. If interrupted it cancels the step.

    Args:
      cluster_id:
      step_id:
      description: (Default value = 'Waiting')

    Returns:

    """
    colors = {"COMPLETED": "OKGREEN", "FAILED": "FAIL"}
    last_state = None
    pbar = tqdm(
        yield_step_state(cluster_id, step_id, sleep=5),
        desc=color_text(f"{description}:step_id={step_id},state=SUBMITTING", "OKCYAN"),
    )

    # wait for step to complete
    try:
        for state in pbar:
            if state != last_state:
                color = colors.get(state, "OKCYAN")
                pbar.set_description(
                    color_text(f"{description}:step_id={step_id},state={state}", color),
                )

            last_state = state
            if state in ["COMPLETED", "FAILED"]:
                cprint(state, colors[state])
                break
    except KeyboardInterrupt:
        color = colors.get("FAILED")
        pbar.set_description(
            color_text(
                f"{description}:step_id={step_id},state=KeyboardInterrupt",
                color,
            ),
        )
        cancel_emr_step(cluster_id, step_id)


def get_cluster_states(state_pattern: str):
    """Takes the state str pattern then returns the matching emr states."""
    if state_pattern.strip() == "*":
        return ALL_CLUSTER_STATES

    if state_pattern in ALL_CLUSTER_STATES:
        states = [states]
    elif type(state_pattern) == str:
        if "|" in state_pattern:
            states = state_pattern.upper().split("|")
            states = [x.strip() for x in states]

    for state in states:
        if state not in ALL_CLUSTER_STATES:
            raise ValueError(
                f"State {state} does not exists. Options {ALL_CLUSTER_STATES}",
            )

    return states


def get_clusters_list_df(states, n) -> pd.DataFrame:
    """Returns a dictionary of cluster and cluster ids

    Args:
      states:
      n:

    Returns:

    """

    states = get_cluster_states(states)

    client = boto3.client("emr")
    clusters = client.list_clusters(ClusterStates=states)
    clusters = pd.json_normalize(clusters["Clusters"], sep="_").sort_values(
        "Status_Timeline_CreationDateTime",
        ascending=False,
    )

    return clusters[["Id", "Name", "Status_State", "Status_Timeline_CreationDateTime"]]


def get_clusters() -> dict:
    """Returns a dictionary of cluster and cluster ids"""

    res = {}
    client = boto3.client("emr")
    clusters = client.list_clusters(ClusterStates=CLUSTER_STATES)
    for cluster in clusters["Clusters"]:
        res[cluster["Name"]] = cluster["Id"]

    return res


@lru_cache()
def get_cluster_id(cluster_name: str) -> str:
    """Returns the id of a cluster from its name. If no exact name match is found then a lower case is used.
    
    Returns:
      str: The id for cluster with name <cluster_name>

    """

    cluster_name = get_cluster_name(cluster_name)

    client = boto3.client("emr")
    clusters = client.list_clusters(ClusterStates=CLUSTER_STATES)
    for cluster in clusters["Clusters"]:
        if cluster["Name"] == cluster_name:
            return cluster["Id"]

    for cluster in clusters["Clusters"]:
        if (isinstance(cluster["Name"], str)) and (isinstance(cluster_name, str)):
            if cluster["Name"].lower() == cluster_name.lower():
                return cluster["Id"]

    raise ValueError(
        f"No cluster called '{cluster_name}' in states '{CLUSTER_STATES}' .",
    )


def describe_cluster(cluster_name):
    """Describe a cluster from its name.

    Args:
      cluster_name:

    Returns:

    """
    client = boto3.client("emr")
    cluster_name = get_cluster_name(cluster_name)
    cluster_id = get_cluster_id(cluster_name)
    cluster_desc = client.describe_cluster(ClusterId=cluster_id)
    return cluster_desc


def get_log_url(cluster_name):
    """Returns the s3 locations of the clusters logs.

    Args:
      cluster_name: Name of cluster.

    Returns:
      str: The s3 log path for the cluster.

    """
    cluster_name = get_cluster_name(cluster_name)
    desc = describe_cluster(cluster_name)
    log_url = desc["Cluster"]["LogUri"]
    if log_url.endswith("/"):
        log_url = log_url[:-1]

    return log_url


def get_master_ec2_instance_id(cluster_name):
    """Returns the master node ec2 instance id.

    Args:
      cluster_name:

    Returns:

    """

    client = boto3.client("emr")
    cluster_id = get_cluster_id(cluster_name)
    cluster_desc = client.describe_cluster(ClusterId=cluster_id)
    master_public_dns_name = cluster_desc["Cluster"]["MasterPublicDnsName"]

    instance_info = client.list_instances(ClusterId=cluster_id)
    for instance in instance_info["Instances"]:
        if master_public_dns_name == instance["PublicDnsName"]:
            master_ec2_instanceid = instance["Ec2InstanceId"]
            print(
                f"'{cluster_name}' cluster master ec2 instance id = {master_ec2_instanceid}",
            )
            return master_ec2_instanceid

    raise ValueError("No ec2 instance id found for {cluster_name}.")


def ssm_cluster(cluster_name: str):
    """Opens an ssm session into the master node of the given cluster"""
    master_ec2_instanceid = get_master_ec2_instance_id(cluster_name)
    cprint(f'Running "aws ssm start-session --target {master_ec2_instanceid}"')
    os.system(f"aws ssm start-session --target {master_ec2_instanceid}")


def ssm_bash(cmd):
    """Run a bash command on a target ec2 instance.

    Args:
      cmd:

    Returns:
      : The cmd response.

    """

    emr_conf = load_config()
    instance_id = get_cluster_id(emr_conf["cluster-name"])

    ssm_client = boto3.client("ssm")
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={"commands": cmd},
    )

    return response


def cancel_step(cluster_name, step_id, step_name_pattern, state_pattern):
    """Cancel an emr step.

    Args:
      cluster_name:
      step_id:
      step_name_pattern:
      state_pattern:

    Returns:

    """

    step_id = get_step_id(step_id, cluster_name, step_name_pattern, state_pattern)
    cluster_id = get_cluster_id(cluster_name)
    boto3.client("emr")
    response = cancel_emr_step(cluster_id, step_id)

    return response


def list_steps(
    cluster_name,
    n,
    step_name_pattern,
    state_patterm,
    print_info=False,
) -> pd.DataFrame:
    """List steps

    Args:
      cluster_name:
      n:
      step_name_pattern:
      state_patterm:
      print_info: (Default value = False)

    Returns:
      pd.DataFrame: Dataframe containing the matching steps.

    """

    cluster_name = get_cluster_name(cluster_name)
    step_name_pattern = str(step_name_pattern)

    if "{env_name}" in step_name_pattern:
        if _pyproject_toml_exists():
            env_name = get_env_name()
            step_name_pattern = step_name_pattern.format(env_name=env_name)
        else:
            step_name_pattern = "*"

    if print_info:
        print(
            f"Steps on '{cluster_name}' matching name '{step_name_pattern}' in state '{state_patterm}'.",
        )

    cluster_id = get_cluster_id(cluster_name)
    client = boto3.client("emr")
    response = client.list_steps(ClusterId=cluster_id)

    steps = pd.json_normalize(response["Steps"], sep="_").sort_values(
        "Status_Timeline_CreationDateTime",
        ascending=False,
    )

    if step_name_pattern not in ["", "*", "None", "True"]:
        mateched_names = fnmatch.filter(steps.Name.tolist(), step_name_pattern)
        steps = steps[steps.Name.isin(mateched_names)]

    if state_patterm not in ["", "*", "None", None]:
        mateched_status_state = fnmatch.filter(
            steps.Status_State.astype(str).tolist(),
            str(state_patterm),
        )
        steps = steps[steps.Status_State.isin(mateched_status_state)]

    if n is not None or n != "":
        steps = steps.head(n)

    steps = steps[["Id", "Name", "Status_State", "Status_Timeline_CreationDateTime"]]
    return steps


@lru_cache()
def get_last_submitted_step(cluster_name, name_pattern, state):
    """Get the last submitted step for the current project.

    Args:
      cluster_name:
      name_pattern:
      state:

    Returns:

    """

    steps = list_steps(cluster_name, None, name_pattern, state)

    if len(steps) > 0:
        step_id = steps["Id"].tolist()[0]
        return step_id

    if "{env_name}" in name_pattern:
        name_pattern = name_pattern.format(env_name=get_env_name())

    raise ValueError(
        f"No running steps for cluster_name='{cluster_name}' and name_pattern='{name_pattern}'",
    )


@lru_cache()
def get_step_id(step_id: str, cluster_name: str, name_pattern: str, state: str):
    """Returns the latest step-id if step_id is none

    Args:
      step_id: str:
      cluster_name: str:
      name_pattern: str:
      state: str:
      
    Returns:

    """

    cluster_name = get_cluster_name(cluster_name)
    if step_id in [None, "", "latest", "None", "last"]:
        step_id = get_last_submitted_step(cluster_name, name_pattern, state)

    return step_id


def describe_step(cluster_name, step_id, name_pattern, state):
    """Describe the last submitted step.

    Args:
      cluster_name:
      step_id:
      name_pattern:
      state:

    Returns:

    """

    step_id = get_step_id(step_id, cluster_name, name_pattern, state)

    cluster_id = get_cluster_id(cluster_name)
    client = boto3.client("emr")
    response = client.describe_step(
        ClusterId=cluster_id,
        StepId=step_id,
    )
    return response


def get_account_id():
    """Get the aws account id."""
    client = boto3.client("sts")
    account_id = client.get_caller_identity()["Account"]
    return account_id


def get_step_state(cluster_name, step_id, name_pattern, state):
    """Get the state of a step.

    Args:
      cluster_name:
      step_id:
      name_pattern:
      state:

    Returns:

    """
    desc = describe_step(cluster_name, step_id, name_pattern, "*")["Step"]
    print(f"Step {desc['Name']} is in state {desc['Status']['State']}.")
