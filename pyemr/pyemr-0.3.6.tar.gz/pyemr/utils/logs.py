"""A collection of aws tools"""
import glob
import gzip
import os
import os.path
import pathlib
import re
from functools import lru_cache
from pathlib import Path

import pandas as pd

from .config import cprint, get_cluster_name
from .emr import get_cluster_id, get_log_url, get_step_id
from .s3 import download_s3_folder


SPARK_ERRORS = [
    "filenotfound",
    "error",
    "exception",
    "aborted",
    "failure",
    "failed",
    "reason",
]


@lru_cache()
def get_emr_step_log_url(cluster_name, step_id, name_pattern, state):
    """Returns the s3 log path for an emr step

    Args:
      cluster_name:
      step_id:
      name_pattern:
      state:

    Returns:

    """
    cluster_name = get_cluster_name(cluster_name)
    cluster_id = get_cluster_id(cluster_name)
    log_url = get_log_url(cluster_name)
    step_id = get_step_id(step_id, cluster_name, name_pattern, state)
    return f"{log_url}/{cluster_id}/steps/{step_id}/"


@lru_cache()
def get_application_log_url(cluster_name, step_id, name_pattern, state, out_dir="logs"):
    """

    Args:
      cluster_name:
      step_id:
      name_pattern:
      state:
      out_dir: (Default value = 'logs')

    Returns:

    """
    cluster_name = get_cluster_name(cluster_name)
    cluster_id = get_cluster_id(cluster_name)
    log_url = get_log_url(cluster_name)
    app_id = get_application_id(cluster_name, step_id, name_pattern, state, out_dir)
    if app_id:
        return f"{log_url}/{cluster_id}/containers/{app_id}/"
    else:
        return None


@lru_cache()
def get_application_id(cluster_name, step_id, name_pattern, state, out_dir="logs"):
    """Downloads the step logs for the spark master/client

    Args:
      cluster_name:
      step_id:
      name_pattern:
      state:
      out_dir: (Default value = 'logs')

    Returns:

    """
    out_dir = download_master_logs(cluster_name, step_id, name_pattern, state, out_dir)
    local_stderr = f"{out_dir}/stderr.gz"
    if os.path.isfile(local_stderr):
        return extract_application_id_from_stderr(local_stderr)

    return None


@lru_cache()
def print_emr_log_path(cluster_name, step_id, name_pattern, state):
    """Prints the s3 log path for an emr step

    Args:
      cluster_name:
      step_id:
      name_pattern:
      state:

    Returns:

    """
    step_log_url = get_emr_step_log_url(cluster_name, step_id, name_pattern, state)
    app_log_url = get_application_log_url(cluster_name, step_id, name_pattern, state)

    print("\n")
    step_log_url_ = step_log_url.replace("s3n://", "s3://")
    cprint(f"Step Logs Url: \n\t {step_log_url_}")

    if app_log_url:
        app_log_url_ = app_log_url.replace("s3n://", "s3://")
        cprint(f"Application Logs Url: \n\t {app_log_url_}")


@lru_cache()
def get_log_paths(cluster_name, step_id, name_pattern, state, out_dir):
    """Returns the s3 and local log path of an EMR step.

    Args:
      cluster_name:
      step_id:
      name_pattern:
      state:
      out_dir:

    Returns:

    """

    step_id = get_step_id(step_id, cluster_name, name_pattern, state)

    # download step logs
    step_logs = get_emr_step_log_url(cluster_name, step_id, name_pattern, state)
    out_dir = f"{out_dir}/{step_id}"
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    return step_logs, out_dir


@lru_cache()
def extract_application_id_from_stderr(local_stderr):
    """Get the application id from the logs of an emr step.

    Args:
      local_stderr:

    Returns:

    """
    if os.path.exists(local_stderr):
        with gzip.open(local_stderr, "r") as file:
            stderr = file.read().decode("utf-8")
    else:
        return None

    start = "Application report for application_"
    end = " (state: "
    app_ids = []

    for line in stderr.split("\n"):
        if start in line:
            line = line.split(start)[-1]
            if end in line:
                app_id = line.split(end)[0].strip()
                if app_id:
                    app_ids += [app_id]

    if len(app_ids) == 0:
        return None

    app_id = max(app_ids, key=app_ids.count)
    return f"application_{app_id}"


def print_application_id(cluster_name, step_id, name_pattern, state, out_dir):
    """Prints the application id for an emr step.

    Args:
      cluster_name:
      step_id:
      name_pattern:
      state:
      out_dir:

    Returns:

    """
    app_id = get_application_id(cluster_name, step_id, name_pattern, state, out_dir)
    print("\n")
    cprint(f"Application Id: {app_id}")


def download_master_logs(cluster_name, step_id, name_pattern, state, out_dir):
    """Downloads the step logs for the spark master/client

    Args:
      cluster_name:
      step_id:
      name_pattern:
      state:
      out_dir:

    Returns:

    """
    cluster_name = get_cluster_name(cluster_name)
    cluster_id = get_cluster_id(cluster_name)
    step_id = get_step_id(step_id, cluster_name, name_pattern, state)
    log_url = get_log_url(cluster_name)
    step_logs = f"{log_url}/{cluster_id}/steps/{step_id}/"
    out_dir = f"{out_dir}/{step_id}"
    local_stderr = f"{out_dir}/stderr.gz"

    if not os.path.isfile(local_stderr):
        pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
        download_s3_folder(step_logs, out_dir)

    if not os.path.isfile(local_stderr):
        cprint("No stderr for found. Try again later")

    return out_dir


def download_application_logs(cluster_name, step_id, name_pattern, state, out_dir):
    """Downloads master stderr and returns the application id.

    Args:
      cluster_name:
      step_id:
      name_pattern:
      state:
      out_dir:

    Returns:

    """
    cluster_name = get_cluster_name(cluster_name)
    get_cluster_id(cluster_name)
    step_id = get_step_id(step_id, cluster_name, name_pattern, state)
    app_id = get_application_id(cluster_name, step_id, name_pattern, state, out_dir)
    out_dir_ = f"{out_dir}/{step_id}/{app_id}"

    if app_id:
        app_logs = get_application_log_url(
            cluster_name,
            step_id,
            name_pattern,
            state,
            out_dir,
        )
        pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
        download_s3_folder(app_logs, out_dir_)
        return out_dir
    return None


def download_all_emr_logs(cluster_name, step_id, name_pattern, state, out_dir):
    """Downloads the client logs and application logs.

    Args:
      cluster_name:
      step_id:
      name_pattern:
      state:
      out_dir:

    Returns:

    """

    cluster_name = get_cluster_name(cluster_name)
    get_cluster_id(cluster_name)

    download_master_logs(cluster_name, step_id, name_pattern, state, out_dir)
    download_application_logs(cluster_name, step_id, name_pattern, state, out_dir)


def print_tail_gzip_files(in_path, n_lines, color="OKBLUE"):
    """Prints the last n lines of the emr logs.

    Args:
      in_path:
      n:
      color: (Default value = 'OKBLUE')
      n_lines:

    Returns:

    """
    cprint(f"> tail -n {n_lines} '{in_path}': ")
    print("\n")
    lines = []

    with gzip.open(in_path, "r") as file:
        for line in file:
            lines.append(line.decode("utf-8")[:-1])

    lines = lines[-n_lines:]
    for line in lines:
        cprint(line, color)
    print("\n")


def print_emr_log_files_lines(
    log_type,
    n_lines,
    step_id,
    cluster_name,
    name_pattern,
    state,
    out_dir,
    color="WARNING",
):
    """Downloads and prints the emr logs.

    Args:
      log_type:
      n:
      step_id:
      cluster_name:
      name_pattern:
      state:
      out_dir:
      color: (Default value = 'WARNING')
      n_lines:

    Returns:

    """
    s3_path, step_log_dir = get_log_paths(
        cluster_name,
        step_id,
        name_pattern,
        state,
        out_dir,
    )
    local_path = f"{step_log_dir}/{log_type}.gz"

    # if not os.path.exists(local_path):
    download_s3_folder(s3_path, step_log_dir)

    if not os.path.isfile(local_path):
        if log_type == "stdout":
            print("")
            cprint(f"'{local_path}' does not exists yet. Try again later")
            print(
                "Note: If you are submiting with cluster mode then master stdout will not exist. Use 'pyemr logs'.",
            )
        else:
            cprint("")
            cprint(f"Logs '{local_path}' are not avalible yet. Try again later.")
    else:
        print_tail_gzip_files(f"{step_log_dir}/{log_type}.gz", n_lines, color)


def summarize_logs(cluster_name, step_id, name_pattern, state, out_dir):
    """Create a summary of the emr logs.

    Args:
      cluster_name:
      step_id:
      name_pattern:
      state:
      out_dir:

    Returns:

    """

    _, local_path = get_log_paths(
        cluster_name,
        step_id,
        name_pattern,
        state,
        out_dir,
    )

    logs = []
    logs += glob.glob(f"{local_path}/*.gz")
    logs += glob.glob(f"{local_path}/**/*.gz")
    logs = list(set(logs))

    errors = []
    log_types = ["INFO", "WARN", "ERROR"]

    for pattern in ["*.gz", "**/*.gz"]:
        for log in Path(local_path).rglob("*.gz"):
            with gzip.open(log, "r") as file:
                log_text = file.read().decode("utf-8")
                for i, line in enumerate(log_text.split("\n")):
                    for error in SPARK_ERRORS:
                        if error in line.lower():
                            for log_type in log_types:
                                if log_type in line:
                                    message = log_type + line.split(log_type)[-1]
                                    break
                            else:
                                message = line
                            errors.append(
                                [
                                    error,
                                    log,
                                    i,
                                    line,
                                    message,
                                    re.sub("\\d", "x", line),
                                ],
                            )
                            break

    errors = pd.DataFrame(
        errors,
        columns=["error", "file", "line", "text", "message", "pattern"],
    )
    counts = errors.groupby(["error", "file", "pattern"]).first()
    counts["count"] = errors.groupby(["error", "file", "pattern"]).size()
    counts = counts.reset_index()

    counts = counts.sort_values(["error", "file", "line"])[
        ["count", "file", "error", "line", "message"]
    ]
    counts.to_csv(f"{local_path}/errors.csv")
    print("")
    cprint("Log Summary:", "OKBLUE")
    cprint(counts.head(30).to_string(), "OKBLUE")
