import datetime
import os
import shutil
from time import sleep
from typing import List
from typing import Union

import pandas as pd
import plotly.graph_objs as go
import pytz
from tensorflow.keras.models import Model as TF_Model

from aibro.tools.auth import check_authentication
from aibro.tools.service.api_service import aibro_client
from aibro.tools.utils import datetime_to_timestamp_ms
from aibro.tools.utils import hybridmethod
from aibro.tools.utils import ModelAndDataset
from aibro.tools.utils import unpack_base64_encoded_pickle
from aibro.tools.utils_training import deserialize_model_data
from aibro.training import _get_model_from_file
from aibro.training import Training


class Job(object):
    def __init__(self, job_id):
        self.job_id = job_id

    # @hybridmethod
    # def peek_job(cls, job_id):
    #     check_authentication()
    #     job = cls(job_id)
    #     _peek(job.job_id)

    # @peek_job.instancemethod  # type: ignore
    # def peek_job(self):
    #     check_authentication()
    #     _peek(self.job_id)

    # @hybridmethod
    # def pickup_model(
    #     cls,
    #     job_id,
    #     epochs: list = ["best_epoch"],
    #     directory=".",
    #     not_save_as_h5: bool = True,
    # ) -> Union[TF_Model, List[TF_Model], None]:
    #     check_authentication()
    #     job = cls(job_id)
    #     return _pickup_model(job.job_id, epochs, directory, not_save_as_h5)

    # @pickup_model.instancemethod  # type: ignore
    # def pickup_model(
    #     self, epochs: list = ["best_epoch"], directory=".", not_save_as_h5: bool = True
    # ) -> Union[TF_Model, List[TF_Model], None]:
    #     check_authentication()
    #     return _pickup_model(self.job_id, epochs, directory, not_save_as_h5)

    @hybridmethod
    def get_tensorboard_logs(cls, job_id, directory="."):
        """[reference]
        https://doc.aipaca.ai/#get_tensorboard_logs
        """
        check_authentication()
        job = cls(job_id)
        _get_tensorboard_logs(job.job_id, directory)

    @get_tensorboard_logs.instancemethod  # type: ignore
    def get_tensorboard_logs(self, directory="."):
        check_authentication()
        _get_tensorboard_logs(self.job_id, directory)

    @hybridmethod
    def plot_timeline(cls, job_id, char_type=None):
        """[reference]
        https://doc.aipaca.ai/#plot_timeline
        """
        job = cls(job_id)
        _plot_timeline(job.job_id, char_type)

    @plot_timeline.instancemethod  # type: ignore
    def plot_timeline(self, char_type=None):
        """[reference]
        https://doc.aipaca.ai/#plot_timeline
        """
        _plot_timeline(self.job_id, char_type)

    @hybridmethod
    def replay_job(cls, job_id):
        """[reference]
        https://doc.aipaca.ai/#replay_job
        """
        job = cls(job_id)
        _replay_job(job.job_id)

    @replay_job.instancemethod  # type: ignore
    def replay_job(self):
        """[reference]
        https://doc.aipaca.ai/#replay_job
        """
        _replay_job(self.job_id)

    @staticmethod
    def list_job(last_days=1):
        user_id = check_authentication()
        last_day_ts = datetime_to_timestamp_ms(
            datetime.datetime.now() - datetime.timedelta(days=last_days)
        )
        data = {"user_id": user_id, "last_day_ts": last_day_ts}
        resp = aibro_client.post_with_json_data("v1/list_jobs", data)

        _format_job_history(resp.json()["user_jobs"])


def _peek(job_id):
    endpoint = "status/" + job_id

    aibro_client.connect_to_socket()
    resp = aibro_client.post_with_endpoint_only(endpoint=endpoint)
    if resp.json()["job_status"] in ["COMPLETED", "CLOSING SERVER", "IDLE"]:
        # print(123)
        print("Now you can use Job.pickup_model() to pickup your model! 🎉")

        if resp.json()["job_status"] == "CANCELED":
            try:
                aibro_client.post_with_json_data("v1/stop_spot", {"job_id": job_id})
            except Exception as e:
                print(f"Cannot stop server, reason\n: {str(e)}")

    sleep(1)
    aibro_client.disconnect_socket()


def _pickup_model(
    job_id, epochs: list = ["best_epoch"], directory=".", not_save_as_h5: bool = True
) -> Union[TF_Model, List[TF_Model], None]:
    model_list = []

    for epoch in epochs:
        data = {"job_id": job_id, "epoch": epoch}
        aibro_client.connect_to_socket()
        resp = aibro_client.post_with_json_data("v1/pickup_model", data)

        if resp.status_code == 200:
            if "job_status" in resp.json().keys():
                if resp.json()["job_status"] == "CANCELED":
                    try:
                        aibro_client.post_with_json_data(
                            "v1/stop_spot", {"job_id": job_id, "error": None}
                        )
                    except Exception as e:
                        print(f"Cannot stop server, reason:\n {str(e)}")
                if resp.json()["job_status"] not in [
                    "COMPLETED",
                    "CLOSING SERVER",
                    "IDLE",
                ]:
                    sleep(1)
                    aibro_client.disconnect_socket()
                    return None
            else:
                if epoch == "best_epoch":
                    epoch = resp.json()["epoch"]
                print(f"picking up model at epoch {epoch}")
                content = resp.json()["model_ckpt_content"]
                unpacked_model_content = unpack_base64_encoded_pickle(content)

                model = _get_model_from_file(
                    model_file_content=unpacked_model_content,
                    directory_to_save_ckpt=directory,
                    not_save_as_h5=not_save_as_h5,
                    epoch=epoch,
                )
                model_list.append(model)
        else:
            aibro_client.disconnect_socket()
            print("Server error")
            return None

    print("models have been picked up successfully")
    aibro_client.disconnect_socket()
    if len(model_list) == 1:
        return model_list[0]
    return model_list


def _get_tensorboard_logs(job_id, directory="."):
    data = {"job_id": job_id}
    resp = aibro_client.post_with_json_data("v1/get_tensorboard_logs", data)
    content = resp.json()["log_zip"]
    log_zip = unpack_base64_encoded_pickle(content)
    file_name = f"{directory}/logs.zip"
    f = open(file_name, "wb")
    f.write(log_zip)
    f.close()
    log_dir = f"{directory}/logs/{job_id}/"
    shutil.unpack_archive(file_name, log_dir, "zip")
    os.remove(file_name)
    print(f"Saved logs to {log_dir}")


def _plot_timeline(job_id: str, char_type: str = None):
    assert char_type in [None, "pie"], """Available chart_type: [None, "pie"]"""
    data = {
        "job_id": job_id,
    }
    resp = aibro_client.post_with_json_data("v1/get_job_timeline", data)
    result = resp.json()
    job_created_at_ms = result["job_created_at_ms"]
    job_ended_at_ms = result["job_ended_at_ms"]
    size_m_d_trans_mb = result["size_m_d_trans_mb"]

    request_created_at_ms = result["request_created_at_ms"]
    request_fulfilled_at_ms = result["request_fulfilled_at_ms"]
    server_connected_at_ms = result["server_connected_at_ms"]
    github_key_received_at_ms = result["github_key_received_at_ms"]
    server_built_up_at_ms = result["server_built_up_at_ms"]
    env_geared_up_at_ms = result["env_geared_up_at_ms"]
    m_d_serialized_at_ms = result["m_d_serialized_at_ms"]
    m_d_received_at_ms = result["m_d_received_at_ms"]
    m_deserialized_at_ms = result["m_deserialized_at_ms"]
    training_completed_at_ms = result["training_completed_at_ms"]
    results_returned_at_ms = result["results_returned_at_ms"]
    results_received_at_ms = result["results_received_at_ms"]

    t_create_job_ms = request_created_at_ms - job_created_at_ms
    t_request_launch_ms = request_fulfilled_at_ms - request_created_at_ms
    t_server_connect_ms = server_connected_at_ms - request_fulfilled_at_ms
    t_api_trans_ms = github_key_received_at_ms - server_connected_at_ms
    t_flask_setup_ms = server_built_up_at_ms - github_key_received_at_ms
    t_gear_up_env_ms = env_geared_up_at_ms - github_key_received_at_ms
    t_m_d_serialization_ms = (
        m_d_serialized_at_ms - env_geared_up_at_ms
        if env_geared_up_at_ms
        else m_d_serialized_at_ms - job_created_at_ms
    )
    t_m_d_trans_ms = m_d_received_at_ms - m_d_serialized_at_ms
    t_m_d_deserialization_ms = m_deserialized_at_ms - m_d_received_at_ms
    t_training_ms = training_completed_at_ms - m_deserialized_at_ms
    t_m_finished_serialization_ms = results_returned_at_ms - training_completed_at_ms
    t_m_finished_trans_ms = results_received_at_ms - results_returned_at_ms
    create_string = "Job Created at: " + pd.to_datetime(
        job_created_at_ms, unit="ms"
    ).strftime("%Y/%m/%d, %H:%M:%S")
    end_string = (
        "Job Ended At: "
        + pd.to_datetime(job_ended_at_ms, unit="ms").strftime("%Y/%m/%d, %H:%M:%S")
        if job_ended_at_ms
        else ""
    )
    size_string = "Submit Model Size: " + str(size_m_d_trans_mb) + "MB"

    labels = [
        "Job Create",
        "Request Launch",
        "Instance Connect",
        "Api Transfer",
        "Server Setup",
        "M&D Serialization",
        "Env Gear Up",
        "M&D Transfer",
        "M&D Deserialization",
        "Model Training",
        "Result Serialization",
        "Result Transfer",
    ]
    values = [
        t_create_job_ms,
        t_request_launch_ms,
        t_server_connect_ms,
        t_api_trans_ms,
        t_flask_setup_ms,
        t_m_d_serialization_ms,
        t_gear_up_env_ms,
        t_m_d_trans_ms,
        t_m_d_deserialization_ms,
        t_training_ms,
        t_m_finished_serialization_ms,
        t_m_finished_trans_ms,
    ]
    colors = (len(values) * ["#494E5E"]).copy()
    colors[-3] = "#597EF9"
    y = labels
    x = [round(v / 1000, 2) if v else 0 for v in values]
    if char_type == "pie":
        y = [tmp_y + "(s)" for tmp_y in y]
        trace = [go.Pie(labels=y, values=x)]
        layout = go.Layout(
            title="Training Timeline for self.job_id: " + job_id,
            annotations=[
                go.layout.Annotation(
                    text=create_string + "<br>" + end_string + "<br>" + size_string,
                    align="right",
                    showarrow=False,
                    x=0,
                    y=0,
                    bordercolor="black",
                    borderwidth=1,
                )
            ],
        )
        fig = go.Figure(data=trace, layout=layout)
        fig.show()
    else:
        fig = go.Figure(
            go.Funnel(
                y=y,
                x=x,
                textinfo="value+percent total",
                hoverinfo="text",
                hovertemplate="Duration: %{x:.2f}s",
                insidetextfont={"color": "white"},
                marker={"color": colors},
                connector={"fillcolor": "lightblue"},
            )
        )
        fig.update_layout(
            title="Training Timeline for job_id: " + job_id,
            annotations=[
                go.layout.Annotation(
                    text=create_string + "<br>" + end_string + "<br>" + size_string,
                    align="left",
                    showarrow=False,
                    x=40,
                    y=0,
                    bordercolor="black",
                    borderwidth=1,
                )
            ],
        )
        fig.show()


def _format_job_history(jobs):
    print(
        f"{'Date (EST)' : <20} {'Job id' : <40} {'Status' : <12} {'Substatus' : <12} {'Current epoch' : <20} Description"  # noqa: E501
    )
    for job in jobs:
        dt = datetime.datetime.fromtimestamp(job["job_created_ms"] // 1000)
        formatted_date = dt.astimezone(pytz.timezone("US/Eastern")).strftime(
            "%m/%d/%Y %H:%M:%S"
        )
        current_epoch = job["current_epoch"]
        status = job["status"]
        substatus = job["substatus"]
        job_id = job["job_id"]
        description = job["description"]
        print(
            f"{f'{formatted_date}' : <20} {f'{job_id}' : <40} {f'{status}' : <12} {f'{substatus}' : <12} {f'{current_epoch}' : <20} {description}"  # noqa
        )


def _replay_job(
    job_id: str,
    description: str = "",
    directory_to_save_ckpt: str = ".",
    directory_to_save_log: str = ".",
    wait_request_s: int = 10000,
):
    user_id = check_authentication()
    post_data = {"job_id": job_id, "user_id": user_id}
    print(f"[REPLAYING]: grabing history model & data of job {job_id}.")
    resp = aibro_client.post_with_json_data("v1/replay_job", post_data)
    job = resp.json()["job"]
    model_and_data = resp.json()["model_and_data"]
    data = ModelAndDataset(**model_and_data)
    data_decode = deserialize_model_data(data)
    print("[REPLAYING]: cloning a new job to start replay.")
    description = description if description != "" else job["description"]
    job_id, result_model, history = Training.online_fit(  # type: ignore
        model=data_decode["model"],
        train_X=data_decode["train_X"],
        train_Y=data_decode["train_Y"],
        validation_data=data_decode["validation_data"],
        machine_ids=job["instance_type"],
        batch_size=data.batch_size,
        epochs=data.epochs,
        description=description,
        directory_to_save_ckpt=directory_to_save_ckpt,
        directory_to_save_log=directory_to_save_log,
        wait_request_s=wait_request_s,
    )

    assert history
    print(f"history.history: {history.history}")
    print(f"history.params: {history.params}")
    print(f"OnlinePickupModel: {result_model}")
