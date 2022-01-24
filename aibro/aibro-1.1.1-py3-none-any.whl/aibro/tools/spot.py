import json
import os
import sys
import threading
from time import sleep
from typing import Any
from typing import Dict
from typing import Optional

from requests.models import Response

from aibro.tools.service.api_service import aibro_client
from aibro.tools.service.api_service import spot_client
from aibro.tools.service.api_service import spot_client_follow
from aibro.tools.service.api_service import SpotClient
from aibro.tools.utils import unpack_base64_encoded_pickle


def _remove_old_m_d_if_exist(filename):
    try:
        os.remove(filename)
        files = os.listdir(".")
        for file in files:
            if file.startswith("model_and_data_"):
                os.remove(os.path.join(".", file))
    except Exception:
        pass


def _find_filename(job_id):
    return f"./model_and_data_{job_id}.json"


def try_get_model_json(file_name, retries=-1, interval=5):
    json_str = ""
    retries = retries if retries > 0 else 9999999
    while retries:
        try:
            f = open(file_name)
            json_str = f.read()
            counter = -1
            while json_str[counter] == "\n":
                counter -= 1
            assert json_str[counter] == "}"
            break
        except Exception:
            sleep(interval)
            retries -= 1
            pass
    if json_str == "":
        raise Exception(
            "Failed to receive trained model data. This issue could be caused by slow internet."
        )
    model_and_data_json = json.loads(json_str)
    return model_and_data_json


def connect_to_spot_server_online(
    data: Dict[str, Any],
    endpoint: str,
    job_id: str,
    server_public_ip: str,
    directory_to_save_log: Optional[str],
):

    spot_client_follow.set_host(server_public_ip)
    spot_client_follow.connect_to_socket()
    spot_client_follow.add_job_to_socket(job_id)
    spot_client.set_host(server_public_ip)

    filename = _find_filename(job_id)
    _remove_old_m_d_if_exist(filename)

    follow_server_thread = threading.Thread(
        target=spot_client_follow.post_with_json_data,
        args=("v1/follow", {"job_id": job_id}),
    )
    follow_server_thread.start()

    # start training
    spot_client.post_with_byte_data(endpoint, data)
    # download dumped data
    spot_client.connect_to_socket()
    spot_client.add_job_to_socket(job_id)
    download_tensorflow_log = directory_to_save_log
    spot_client.post_with_json_data(
        "v1/download_train_result",
        {
            "job_id": job_id,
            "user_id": data["user_id"],
            "download_tensorflow_log": download_tensorflow_log,
        },
    )

    # data will be returned by socket
    model_and_data_json = try_get_model_json(filename)
    # decode data
    model_history = model_and_data_json["model_history"]
    history = unpack_base64_encoded_pickle(model_history)
    model_file_content = unpack_base64_encoded_pickle(
        model_and_data_json["model_file_content"]
    )
    tensorboard_logs = (
        model_and_data_json["tensorboard_logs"]
        if "tensorboard_logs" in model_and_data_json
        else None
    )
    epoch = model_and_data_json["epoch"]
    # got everything and disconnect socket
    _disconnect_everything(
        follow_server_thread, spot_client, spot_client_follow, job_id
    )
    return (
        history,
        model_file_content,
        tensorboard_logs,
        epoch,
    )


def connect_to_spot_server_offline(
    data: Dict[str, Any], endpoint: str, job_id: str, server_public_ip: str
):
    spot_client.set_host(server_public_ip)
    spot_client.connect_to_socket()
    # resp = spot_client.post_with_json_data(endpoint, data)
    resp = spot_client.post_with_byte_data(endpoint, data)
    if isinstance(resp, Response) and resp.status_code == 202:
        print(resp.content.decode("utf-8"))
    spot_client.disconnect_socket()


def _stop_instance(
    job_id: str, e: str, instance_ip: str = None, endpoint="v1/inference/stop_instance"
):
    data = {"job_id": job_id, "error": e, "instance_ip": instance_ip}
    aibro_client.connect_to_socket()
    resp_stop_spot = aibro_client.post_with_json_data(endpoint, data)
    aibro_client.disconnect_socket()
    return resp_stop_spot


def save_cancel_job_reason(
    job_id: str, reason: str, endpoint="v1/inference/save_cancel_job_reason"
):
    data = {"job_id": job_id, "reason": reason}
    aibro_client.post_with_json_data(endpoint, data)


def _disconnect_everything(
    follow_server_thread: threading.Thread,
    spot_client: SpotClient,
    spot_client_follow: SpotClient,
    job_id: str,
):
    follow_server_thread.join(timeout=1)
    if follow_server_thread.is_alive():
        print("[Warning]: follow server didn't join succussfully")
    try:
        spot_client.del_job_to_socket(job_id)
        spot_client.disconnect_socket()
    except Exception as e:
        if "google.colab" not in sys.modules:
            print(f"[WARNING]: spot_client: {e}")
    try:
        spot_client_follow.del_job_to_socket(job_id)
        spot_client_follow.disconnect_socket()
    except Exception as e:
        if "google.colab" not in sys.modules:
            print(f"[WARNING]: spot_client_follow: {e}")
