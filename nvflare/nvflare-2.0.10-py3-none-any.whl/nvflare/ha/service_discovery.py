import json
import threading
import time
from signal import Signals
from ssl import cert_time_to_seconds
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

from requests import Request, Session, codes

from nvflare.apis.fl_component import FLComponent
from nvflare.apis.fl_context import FLContext


class FLComponent:
    pass


class S:
    def __init__(self):
        self.triggered = False


class FLContext:
    def get_identity_name(self):
        return "site-1"

    def get_run_abort_signal(self):
        return S()


class ServiceDiscovery(FLComponent):
    def __init__(self, end_point_url: str, root_ca_cert: str, my_cert: str, my_key: str, my_role: str):
        self.end_point_url = end_point_url
        self.root_ca_cert = root_ca_cert
        self.my_cert = my_cert
        self.my_key = my_key
        self.my_role = my_role
        self.status_lock = threading.Lock()
        self.report_and_query = threading.Thread(target=self._rnq, args=())
        self.report_timeout = 1
        self._rnq_interval = 2
        self.asked_to_stop = False
        self.hot_sp_name = ""
        self.hot_sp_fl_port = ""
        self.hot_sp_adm_port = ""

    def initialize(self, fl_ctx: FLContext):
        self.reporter = fl_ctx.get_identity_name()
        self.abort_signal = fl_ctx.get_run_abort_signal()
        self.asked_to_stop = False
        self.report_and_query.start()
        # self.engine = fl_ctx.get_engine()

    def get_hot_sp(self) -> Tuple[str, str, str]:
        """Return current hot service provider as (name, fl_port, adm_port)
        if hot sp not available, such as not reported by SD, connection to SD not established yet
        the name and ports will be empty strings.
        """
        return self.hot_sp_name, self.hot_sp_fl_port, self.hot_sp_adm_port

    def get_sds_status(self) -> Dict[str, Any]:
        return self.sts_status

    def _rnq(self):
        s = Session()
        data = dict(reporter=self.reporter)
        for i in range(3):
            if self.asked_to_stop or self.abort_signal.triggered:
                break

            data["role"] = "server"
            data["project"] = "example"
            data["service_point"] = f"abc.com:808{i}:811{i}"
            data["reporter"] = self.reporter

            req = Request("POST", self.end_point_url, json=data)

            prepped = s.prepare_request(req)

            # resp = s.send(prepped, timeout=self.report_timeout)

            resp = s.send(
                prepped, verify=self.root_ca_cert, cert=(self.my_cert, self.my_key), timeout=self.report_timeout
            )

            if resp.status_code == codes.ok:
                self.sds_status = resp.json()
                hot_sp = self.sds_status.get("hot_sp")
                if hot_sp:
                    self.hot_sp_name, self.hot_sp_fl_port, self.hot_sp_adm_port = hot_sp.split(":")
            time.sleep(self._rnq_interval)


sd = ServiceDiscovery("https://localhost:5000/", "./rootCA.pem", "./client.crt", "client.key", "server")
sd.initialize(FLContext())
time.sleep(2)
print(sd.get_hot_sp())
