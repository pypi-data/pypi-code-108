import json
import os
import requests
import sys
from datetime import datetime
from typing import Dict

# # TODO should not ignore this warning. Remove when the pkm certificate will
# # be corrected
# from requests.packages.urllib3.exceptions import SubjectAltNameWarning
# requests.packages.urllib3.disable_warnings(SubjectAltNameWarning)


class PKMClient(object):

    def __init__(self, cacert=False, key=None):
        self.protocol = self.get_pkm_protocol()
        self.host = self.get_pkm_host()
        self.port = self.get_pkm_port()
        self.key = key
        self.cacert = cacert

    def get_pkm_protocol(self):
        protocol = os.environ.get('PKM_PROTOCOL')
        if protocol:
            print(f"PKMClient.get_pkm_protocol: {protocol}", flush=True)
            return protocol
        else:
            print(f"PKMClient.get_pkm_protocol: http", flush=True)
            return 'http'

    def get_pkm_host(self):
        host = os.environ.get('PKM_HOST')
        if host:
            print(f"PKMClient.get_pkm_host: {host}", file=sys.stderr)
            return host
        else:
            print(f"PKMClient.get_pkm_host: pkm", file=sys.stderr)
            return 'pkm-api_pkm_1'

    def get_pkm_port(self):
        port = os.environ.get('PKM_PORT')
        if port is not None:
            return port
        else:
            return 8080

    def call(self, method='POST', path='', payload={}):
        headers = {"accept": "application/json",
                   "Content-Type": "application/json"}
        if self.key is not None:
            headers['key'] = self.key
        try:
            url = f'{self.protocol}://{self.host}:{self.port}/{path}'
            resp = requests.request(
              method,
              url,
              headers=headers,
              json=payload,
              verify=(self.cacert if self.protocol == 'https' else False))
        except Exception as e:
            print(f'Catch exception accessing pkm: {e}, {url}',
                  file=sys.stderr)
            return 1, {}

        http_code = resp.status_code

        print(f"response: {http_code}, '{resp.headers}', '{resp.text[:100]}…'",
              file=sys.stderr)
        answer = ''

        if http_code < 300:
            STATUS = 0
            if ('Content-Type' in resp.headers
                    and 'application/json' in resp.headers['Content-Type']):
                answer = resp.json()
        else:
            error_message = (f"Call to PKM server on {url} failed: {resp}, "
                             f"{resp.headers}, {resp.text}")
            print(error_message, file=sys.stderr)
            answer = error_message
            STATUS = http_code

        return STATUS, answer

    def login(self, user_name, user_password):
        # print(f"PKMClient.login {user_name}/***", file=sys.stderr)

        status, USER_KEY = self.call(method='POST',
                                     path="user/login",
                                     payload={"user_name": user_name,
                                              "user_password": user_password})
        if status != 0:
            print("user's login failed", file=sys.stderr)
            return False

        USER_KEY = USER_KEY['key']

        self.key = USER_KEY
        return True

    def now(self):
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def update_invocation(self, project_id: str, invocationId: str, status: int,
                          resultsToAdd: Dict[str, str]):
        """
        """
        invocationUpdate = dict()
        invocationUpdate["invocationID"] = invocationId

        if status == 0:
            invocationUpdate["invocationStatus"] = "COMPLETED"
        else:
            invocationUpdate["invocationStatus"] = "FAILED"
            invocationUpdate["invocationResults"] = resultsToAdd.update(
                path="FAILED", type="message")

        invocationUpdate["invocationResults"] = resultsToAdd

        invocationUpdate["timestampCompleted"] = self.now()

        getSt, getTx = self.call(
            method='GET',
            path=f"/invocations/{project_id}/{invocationUpdate['invocationID']}")

        inv = json.loads(getTx)
        inv.update(invocationUpdate)
        return self.call(method='PUT', path='/invocations/'+project_id,
                         payload=json.dumps([inv]))


class Log(object):

    def __init__(self, pkm: PKMClient, project: str,
                 tool: str, status: str = "",
                 details: dict = {}, nature: str = "Execution report",
                 max_msg_len=80, invocation_id=None):
        self.pkm = pkm
        self.project = project
        # tool name/tag
        self.tool = tool
        # Proof report, Modeling report, Testing report, GUI report,
        # NER report, Summarization report, etc.
        self.nature_of_report = nature
        # Messages longer than max_msg_len will be truncated. No truncation if
        # None
        self.max_msg_len = max_msg_len
        # start running time
        self.start_running_time = str(datetime.now())
        # end running time
        self.end_running_time = None
        self.messages = []
        self.warnings = []
        self.errors = []
        self.status = True
        self.details = {}
        self.invocation_id = invocation_id

    def __del__(self):
        status, result = self.pkm.call(method='POST',
                                       path=f"log/{self.project}",
                                       payload=[self.json()])
        if status != 0:
            print(f"Logging {self.json()} failed with {status}: {result}",
                  file=sys.stderr)
        elif self.invocation_id is not None:
            newLogID = json.loads(result)[0]
            self.pkm.update_invocation(
                self.project, self.invocation_id, status,
                dict(path=f"log/{self.project}"+str(newLogID), type="log"))

    def _log_to(self, msg: str, dest: list):
        dest.append(msg
                    if self.max_msg_len is None or len(msg) <= self.max_msg_len
                    else msg[:self.max_msg_len]+"…")

    def message(self, msg: str):
        self._log_to(msg, self.messages)

    def error(self, msg: str):
        self.status = False
        self._log_to(msg, self.errors)

    def warn(self, msg: str):
        self._log_to(msg, self.warnings)

    def json(self):
        log_object = {
            "tool": self.tool,
            "nature of report": self.nature_of_report,
            "start running time": self.start_running_time,
            "end running time": str(datetime.now()),
            "messages": self.messages,
            "warnings": self.warnings,
            "errors": self.errors,
            "status": len(self.errors) == 0,
            "details": self.details
            }
        return log_object

