import copy
import datetime
import os
import shutil
import sys
import threading
from pathlib import Path
from time import sleep
from typing import List
from typing import Union

from requests.models import Response

from aibro.constant import INF_HOST
from aibro.tools.auth import check_authentication
from aibro.tools.marketplace import _check_machines_exist
from aibro.tools.prints import print_err
from aibro.tools.prints import print_highlight
from aibro.tools.prints import print_launching
from aibro.tools.prints import print_sending
from aibro.tools.prints import print_warning
from aibro.tools.service.api_service import aibro_client
from aibro.tools.service.api_service import inf_ins_client
from aibro.tools.service.api_service import spot_client_follow_inf
from aibro.tools.service.api_service import SpotClient
from aibro.tools.spot import _stop_instance
from aibro.tools.spot import save_cancel_job_reason
from aibro.tools.utils import datetime_to_timestamp_ms
from aibro.tools.utils import subprocess_to_stdout
from aibro.tools.utils import zipdir


class Inference(object):
    def __init__(
        self,
        model_name: str,
        machine_id_config: Union[str, dict],
    ):
        self.model_name = model_name
        self.machine_id_config = machine_id_config

    @staticmethod
    def deploy(
        artifacts_path: Union[str, list],
        model_name: str = None,
        machine_id_config: Union[str, dict] = None,
        dryrun: bool = False,
        cool_down_period_s: int = 600,
        client_ids: List[str] = [],
        access_token: str = None,
        description: str = "",
        wait_request_s: int = 30,
    ) -> str:
        if dryrun:
            if isinstance(artifacts_path, list):
                artifacts_path = _pack_inf_repo(artifacts_path, zip=False)
            assert isinstance(
                artifacts_path, str
            ), "artifacts_path must be either str or list"
            return _dryrun_helper(artifacts_path)
        try:
            assert model_name, "model_name does not exist"
            assert machine_id_config, "machine_id_config does not exist"
            if isinstance(client_ids, str):
                client_ids = [client_ids]
            job_created_at_ms = datetime_to_timestamp_ms(datetime.datetime.now())
            _validate_inference_machine_ids(machine_id_config)
            user_id = check_authentication(access_token)
            print("Please open https://aipaca.ai/inference_jobs to track job status.")
            if not user_id:
                raise Exception("Authentication failed")

            job_type = "inference"
            data = {
                "user_id": user_id,
                "machine_id_config": machine_id_config,
                "model_name": model_name,
                "description": description,
                "job_created_at_ms": job_created_at_ms,
                "job_type": job_type,
                "wait_request_s": wait_request_s,
                "cool_down_period_s": cool_down_period_s,
                "client_ids": client_ids,
            }
            job_id, machine_id_config = _create_new_inf_job(data)
            data["job_id"] = job_id
            data["machine_id_config"] = machine_id_config
            server_public_ips = _request_instance(data)
            data["server_public_ips"] = server_public_ips
            _launch_inf_server(data)
            print_sending("Serializing your artifacts...")
            zip_path = _pack_inf_repo(artifacts_path)
            username, access_token = _deploy_inf_model(
                server_public_ips, job_id, user_id, zip_path, model_name
            )
            api_url = _create_api_url(username, client_ids, model_name)
            client_str = ""
            public = len(client_ids) == 0
            if not public:
                client_str = " for one of clients"
            print_highlight(f"Your Inference API URL{client_str}: {api_url}")
            return api_url
        except KeyboardInterrupt:
            error = "User KeyboardInterrupt"
            job_id = None if "job_id" not in locals() else job_id
            server_public_ips = (
                None if "server_public_ips" not in locals() else server_public_ips
            )
            _handle_exception(error, job_id, server_public_ips)
            return error
        except Exception as e:
            error = str(e)
            job_id = None if "job_id" not in locals() else job_id
            server_public_ips = (
                None if "server_public_ips" not in locals() else server_public_ips
            )
            _handle_exception(error, job_id, server_public_ips)
            return error

    @staticmethod
    def complete(
        model_name: str = None,
        job_id: str = None,
        access_token: str = None,
    ):
        assert (
            job_id or model_name
        ), "To complete a inference job, you should input either its model_name or job_id"
        user_id = check_authentication(access_token)
        data = {"user_id": user_id, "model_name": model_name, "job_id": job_id}
        resp = aibro_client.complete_inf_job(data)
        if resp.status_code != 200:
            print_err(resp.text)
        model_name = resp.json()["model_name"]
        job_id = resp.json()["job_id"]
        print(
            f"Inference job {job_id}, with model {model_name}, successfully completed."
        )

    @staticmethod
    def update_clients(
        add_client_ids: Union[str, List[str]] = [],
        remove_client_ids: Union[str, List[str]] = [],
        be_public: bool = False,
        model_name: str = None,
        job_id: str = None,
        access_token: str = None,
    ) -> List[str]:
        assert (
            job_id or model_name
        ), "To find a inference job, you should input either its model_name or job_id"
        user_id = check_authentication(access_token)
        if isinstance(add_client_ids, str):
            add_client_ids = [add_client_ids]
        if isinstance(remove_client_ids, str):
            remove_client_ids = [remove_client_ids]
        data = {
            "user_id": user_id,
            "model_name": model_name,
            "job_id": job_id,
            "add_client_ids": add_client_ids,
            "remove_client_ids": remove_client_ids,
            "be_public": be_public,
        }
        resp = aibro_client.update_clients(data)
        if resp.status_code != 200:
            error = str(resp.text)
            print_err(error)
            raise Exception(error)
        print("Update client succeeded!")
        client_ids = resp.json()["client_ids"]
        print_highlight(f"Current client ids: {client_ids}")
        return client_ids

    @staticmethod
    def list_clients(
        model_name: str = None,
        job_id: str = None,
        access_token: str = None,
    ) -> List[str]:
        assert (
            job_id or model_name
        ), "To find a inference job, you should input either its model_name or job_id"
        user_id = check_authentication(access_token)
        data = {
            "user_id": user_id,
            "model_name": model_name,
            "job_id": job_id,
        }
        resp = aibro_client.list_clients(data)
        if resp.status_code != 200:
            error = str(resp.text)
            raise Exception(error)
        client_ids = resp.json()["client_ids"]
        print_highlight(f"Current client ids: {client_ids}")
        return client_ids


def _detect(repo_path: str):  # if false,raise err_msg, else return data file's name
    FILE_LIST = ["predict.py", "model", "requirements.txt"]
    for file in FILE_LIST:
        file_path = os.path.join(repo_path, file)
        if not os.path.exists(file_path):
            return False
    for file in os.listdir(repo_path):  # data folder/file is optional
        if file[:4] == "data":
            return True
    return True


def _dryrun_helper(
    artifacts_path: str,
):  # previous parameter is Union[str, list], noqa
    """
    Check if the artifacts_path given by user is valid。
    Test: check if predict.py can return inference result
    """
    err_msg = "Invalid repo structure (checkout https://doc.aipaca.ai for details)."
    check = _detect(artifacts_path)  # firt, check if the repo structure is our format
    aibro_dir_path = os.path.split(os.path.realpath(__file__))[0]
    inf = os.path.join(aibro_dir_path, "scripts", "infer_command.sh")
    call = os.path.join(aibro_dir_path, "scripts", "call_predict.sh")
    artifacts_path_abspath = os.path.abspath(artifacts_path)
    if check:  # if it is suitable
        try:
            bash = f"bash {inf} {artifacts_path_abspath}"
            subprocess_to_stdout(
                [bash],
                raise_error_if_any=True,
                line_to_stop_streaming="Dependencies installed!",
            )
            bash = f"bash {call} {artifacts_path_abspath}"
            subprocess_to_stdout(
                [bash],
                raise_error_if_any=True,
                line_to_stop_streaming="Prediction finished",
            )
        except Exception as e:
            raise Exception(f"DRYRUN TEST: failed - {str(e)}")
    else:
        raise Exception(f"DRYRUN TEST: failed - {err_msg}")

    print_highlight("DRYRUN TEST: passed")


def _create_new_inf_job(data):
    aibro_client.connect_to_socket()
    resp = aibro_client.create_new_job(data)
    if resp.status_code != 200:
        raise Exception(resp.text)
    job_id = resp.json()["job_id"]
    contain_spot = False
    if isinstance(data["machine_id_config"], str):
        if ".od" not in data["machine_id_config"]:
            contain_spot = True
    elif isinstance(data["machine_id_config"], dict):
        for k in data["machine_id_config"]:
            if ".od" not in data["machine_id_config"][k]:
                contain_spot = True
    if contain_spot:
        print_warning(
            f"{data['machine_id_config']} contained spot instances. Used its on-demand type instead"
        )
    machine_id_config = resp.json()["machine_id_config"]
    return job_id, machine_id_config


def _request_instance(data):
    machine_id_config = data["machine_id_config"]
    job_id = data["job_id"]
    belong = "public" if len(data["client_ids"]) == 0 else "private"
    print_launching(f"Starting {belong} inference job: {job_id}")
    print_launching(f"Requesting {str(machine_id_config)} to be ready...")
    data["job_id"] = job_id
    aibro_client.add_job_to_socket(data["job_id"])
    resp = aibro_client.request_instance(data)
    aibro_client.del_job_to_socket(data["job_id"])
    aibro_client.disconnect_socket()
    if resp.status_code != 200:
        raise Exception(resp.text)
    server_public_ips = resp.json()["server_public_ips"]
    return server_public_ips


def _launch_inf_server(data):
    # TODO: handle exception happened here
    machine_id_config = data["machine_id_config"]
    job_id = data["job_id"]
    data_spin_up = {
        "job_id": job_id,
    }
    aibro_client.spin_up_server(data_spin_up)
    print(f"Your {machine_id_config} instances are now ready 🎉\n")


def _pack_inf_repo(artifacts_path, zip=True):
    dir = "."
    if isinstance(artifacts_path, str):
        artifacts_dir_path = copy.deepcopy(artifacts_path)
        artifacts_path = [
            os.path.join(artifacts_dir_path, f) for f in os.listdir(artifacts_dir_path)
        ]
    # user passed a list of files
    artifacts_path_new = os.path.join(dir, "aibro_repo")
    counter = 0
    while os.path.exists(artifacts_path_new):
        # if aibro repo already exist in the current root, create a folder copy and create new aibro_repo in there
        counter += 1
        copy_dir_path = os.path.join(dir, f"aibro_repo_copy{counter}")
        artifacts_path_new = os.path.join(copy_dir_path, "aibro_repo")
        if not os.path.exists(copy_dir_path):
            os.mkdir(copy_dir_path)
    if not os.path.exists(artifacts_path_new):
        os.mkdir(artifacts_path_new)
    for f in artifacts_path:
        if os.path.isdir(f):
            folder_name = Path(f).name
            folder_path = os.path.join(artifacts_path_new, folder_name)
            shutil.copytree(f, folder_path)
        else:
            shutil.copy(f, artifacts_path_new)
    artifacts_path = artifacts_path_new
    if not zip:
        return artifacts_path
    zip_name = "aibro_repo.zip"
    zip_path = os.path.join(dir, zip_name)
    if os.path.exists(zip_path):
        os.remove(zip_path)
    zipdir(artifacts_path, zip_path)
    return zip_path


def _deploy_inf_model(server_public_ips, job_id, user_id, zip_path, model_name):
    threads = []
    for server_public_ip in server_public_ips:
        t = threading.Thread(
            target=_deploy_inf_model_setup_helper,
            args=(server_public_ip, job_id, user_id, zip_path),
        )
        t.start()
        threads.append(t)
        sleep(5)
    for t in threads:
        t.join()
    resp_1 = aibro_client.post_with_json_data(
        "v1/get_userinfo", json_data={"user_id": user_id}
    )
    resp_2 = aibro_client.post_with_json_data(
        "v1/add_active_model",
        json_data={"user_id": user_id, "job_id": job_id, "model_name": model_name},
    )
    if resp_1.status_code != 200 or resp_2.status_code != 200:
        reason = resp_1.text if resp_1.status_code != 200 else resp_2.text
        return _terminate_inference_job(job_id, reason, server_public_ips)
    username = resp_1.json()["username"]
    access_token = resp_1.json()["access_token"]
    return username, access_token


def _deploy_inf_model_setup_helper(
    server_public_ip: str,
    job_id: str,
    user_id: str,
    zip_path: str,
):
    try:
        # setup inference
        spot_client_follow_inf_copy = SpotClient(port=12347)
        spot_client_follow_inf_copy.set_host(server_public_ip)
        spot_client_follow_inf_copy.connect_to_socket()
        resp = spot_client_follow_inf_copy.post_with_byte_data(
            f"v1/{user_id}/inf_setup", filepath=zip_path
        )
        if isinstance(resp, Response) and resp.status_code != 200:
            return _terminate_inference_job(job_id, resp.text, [server_public_ip])
        # disconnect everything
        spot_client_follow_inf_copy.disconnect_socket()
        # _disconnect_inf_follow_app(job_id, follow_server_thread)
    except Exception as e:
        error = str(e)
        _stop_instance(job_id, error, server_public_ip)
        save_cancel_job_reason(job_id, error)
        print_err(f"Job {job_id} successfully canceled")
        return error


def _create_api_url(username: str, client_ids: list, model_name: str):
    client_id = "public" if len(client_ids) == 0 else client_ids[0]
    port_str = ":8000" if "http" not in INF_HOST else ""
    api_url = f"{INF_HOST}{port_str}/v1/{username}/{client_id}/{model_name}/predict"
    return api_url


def _terminate_inference_job(job_id, reason, server_public_ips: list = []):
    print_err(reason)
    save_cancel_job_reason(job_id, reason)
    for server_ip in server_public_ips:
        resp_stop_spot = _stop_instance(job_id, reason, server_ip)
        if resp_stop_spot.status_code != 200:
            print_err(f"Failed to terminate inference server: {resp_stop_spot.text}")
    inf_ins_client.disconnect_socket()
    raise Exception(reason)


def _validate_inference_machine_ids(machine_id_config: Union[str, dict]) -> bool:
    if isinstance(machine_id_config, str):
        machine_ids = [machine_id_config]
    elif isinstance(machine_id_config, dict):
        machine_ids = list(machine_id_config.values())
        assert len(machine_ids) > 0, "Please input at least one machine id"
    else:
        err_msg = "We detected that the cloud machine you selected is not available for inference job"
        raise Exception(err_msg)
    # TODO: check inference machine_ids from markertplace
    marketplace = aibro_client.get("v1/marketplace_machines").json()
    for m_id in machine_ids:
        assert _check_machines_exist(
            m_id, marketplace
        ), f"machine {m_id} not exist or lack of capacity"
    return True


def _handle_exception(error, job_id, server_public_ips):
    if job_id:
        print_err(f"Trying to cancel inference job: {job_id}")
        if not server_public_ips or len(server_public_ips) == 0:
            _stop_instance(job_id, error)
        else:
            for server_public_ip in server_public_ips:
                _stop_instance(job_id, error, server_public_ip)
        save_cancel_job_reason(job_id, error)
        print_err(f"Job {job_id} successfully canceled")
    else:
        print_err(error)


def _disconnect_inf_follow_app(job_id: str, follow_server_thread: threading.Thread):
    follow_server_thread.join(timeout=1)
    if follow_server_thread.is_alive():
        print("[Warning]: follow server didn't join succussfully")
    try:
        spot_client_follow_inf.del_job_to_socket(job_id)
        spot_client_follow_inf.disconnect_socket()
    except Exception as e:
        if "google.colab" not in sys.modules:
            print(f"[WARNING]: spot_client_follow: {e}")
