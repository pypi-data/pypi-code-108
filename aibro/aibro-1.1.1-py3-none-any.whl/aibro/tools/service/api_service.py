import os
import platform
import socket
import uuid
from typing import Any
from typing import Dict
from typing import Union

import requests
import urllib3.connection
from requests import Response

from aibro.constant import IS_LOCAL
from aibro.tools.sio import sio as sio_main
from aibro.tools.sio import sio_follow
from aibro.tools.sio import sio_follow_inf
from aibro.tools.sio import sio_spot
from aibro.tools.utils import ProgressUpload

# Set TCP keep alive options to avoid HTTP requests hanging issue
# Reference: https://stackoverflow.com/questions/61493298/flask-app-response-not-received-client-side
# Reference: https://stackoverflow.com/a/14855726/2360527
platform_name = platform.system()
orig_connect = urllib3.connection.HTTPConnection.connect


def patch_connect(self):
    orig_connect(self)
    if platform_name == "Linux" or platform_name == "Windows":
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1),
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3),
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5),
    elif platform_name == "Darwin":
        TCP_KEEPALIVE = 0x10
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.sock.setsockopt(socket.IPPROTO_TCP, TCP_KEEPALIVE, 3)


urllib3.connection.HTTPConnection.connect = patch_connect


class APIClient:
    def __init__(self, host: str, port: int, sio):
        self.host = host
        self.port = port
        self.sio = sio

    def connect_to_socket(self):
        self.sio.connect_to_server_socket(self.host, self.port)

    def disconnect_socket(self):
        self.sio.sio_disconnect()

    def get(self, endpoint: str):
        try:
            resp = requests.get(f"http://{self.host}:{self.port}/{endpoint}")
        except Exception as e:
            return f"ERROR: {e}"
        if resp.status_code != 200:
            self._handle_error(resp)

        return resp

    def post_with_json_data(
        self, endpoint: str, json_data: Dict[str, Any], handle_error: bool = True
    ) -> Response:
        headers = {"Content-Type": "application/json"}
        resp = requests.post(
            f"http://{self.host}:{self.port}/{endpoint}",
            json=json_data,
            headers=headers,
        )
        if resp.status_code == 202:
            return resp
        if handle_error and resp.status_code != 200:
            self._handle_error(resp)
        return resp

    def post_with_raw_data(self, endpoint: str, raw_data: str) -> Response:
        headers = {"Content-Type": "application/json"}
        resp = requests.post(
            f"http://{self.host}:{self.port}/{endpoint}",
            data=raw_data,
            headers=headers,
        )
        if resp.status_code == 202:
            return resp
        if resp.status_code != 200:
            self._handle_error(resp)

        return resp

    def upload_file(self, upload_url: str, filepath: str):

        return requests.post(
            upload_url,
        )

    def post_with_byte_data(
        self,
        endpoint: str,
        json_data: Dict[str, Any] = None,
        filepath: str = None,
    ) -> Union[Response, str]:
        if not filepath:
            # prevent R/W from multiple processes
            random_postfix = str(uuid.uuid1())
            filepath = f"./user_data_{random_postfix}.json"
            with open(filepath, "w") as f:
                f.write(str(json_data))
        upload_url = f"http://{self.host}:{self.port}/{endpoint}"
        try:
            resp = requests.post(upload_url, data=ProgressUpload(filepath))
        except Exception as e:
            return f"ERROR: {e}"

        files = os.listdir(".")
        for file in files:
            if file.startswith("user_data_"):
                os.remove(os.path.join(".", file))
        if resp.status_code == 202:
            return resp
        if resp.status_code != 200:
            self._handle_error(resp)
        return resp

    def post_with_endpoint_only(self, endpoint: str) -> Response:
        resp = requests.post(
            f"http://{self.host}:{self.port}/{endpoint}",
        )
        if resp.status_code == 202:
            return resp

        if resp.status_code != 200:
            self._handle_error(resp)

        return resp

    def _handle_error(self, resp: Response):
        content = resp.content.decode("utf-8")
        self.sio.sio_disconnect()
        raise Exception(content)

    def add_job_to_socket(self, job_id: str):
        self.sio.add_job_to_socket(job_id)

    def del_job_to_socket(self, job_id: str):
        self.sio.del_job_to_socket(job_id)


class AIbroClient(APIClient):
    def __init__(self):
        host = (
            os.environ.get("SERVER_HOST", "localhost") if IS_LOCAL else "52.204.82.19"
        )
        port = 8000
        sio = sio_main
        super().__init__(host=host, port=port, sio=sio)

    def create_new_job(
        self, data: Dict[str, Any], endpoint="v1/inference/create_new_job"
    ) -> Response:
        headers = {"Content-Type": "application/json"}
        resp = requests.post(
            f"http://{self.host}:{self.port}/{endpoint}",
            json=data,
            headers=headers,
        )
        return resp

    def request_instance(
        self, data: Dict[str, Any], endpoint="v1/inference/request_instance"
    ) -> Response:
        return self.post_with_json_data(endpoint, data)

    def complete_inf_job(
        self, data: Dict[str, Any], endpoint="v1/complete_inf_job"
    ) -> Response:
        return self.post_with_json_data(endpoint, data)

    def update_clients(
        self, data: Dict[str, Any], endpoint="v1/update_clients"
    ) -> Response:
        return self.post_with_json_data(endpoint, data)

    def list_clients(
        self, data: Dict[str, Any], endpoint="v1/list_clients"
    ) -> Response:
        return self.post_with_json_data(endpoint, data)

    def spin_up_server(
        self, data: Dict[str, Any], endpoint="v1/inference/spin_up_server"
    ) -> Response:
        return self.post_with_json_data(endpoint, data)

    def get_serialization_details(self, data: Dict[str, Any]) -> Response:
        return self.post_with_json_data("v1/get_serialization_detail", data)


class SpotClient(APIClient):
    def __init__(self, is_follow_app=False, port=12345, sio=sio_spot):
        port = port
        sio = sio
        super().__init__(host="", port=port, sio=sio)

    def set_host(self, host: str):
        self.host = host


aibro_client = AIbroClient()
spot_client = SpotClient()
spot_client_follow = SpotClient(is_follow_app=True, port=12346, sio=sio_follow)
spot_client_follow_inf = SpotClient(is_follow_app=True, port=12348, sio=sio_follow_inf)
inf_ins_client = SpotClient(port=12347)
