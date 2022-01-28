import requests
import json

import os


MONIPE_URL = os.environ.get("MONIPE_URL")
MONIPE_TOKEN = os.environ.get("MONIPE_TOKEN")
TESTPOINT = os.environ.get("TESTPOINT")


class HomologationRequestManager:
    def __init__(self, test_request_file_path) -> None:
        self.monipe_homologation_test_request = json.load(
            fp=open(test_request_file_path, "r"))
        if not MONIPE_TOKEN and not MONIPE_URL:
            self.token = '''eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvbG9jYWxob3N0OjgwMDFcL3Rva2VucyIsImlhdCI6MTYyNzQwMDE5NSwibmJmIjoxNjI3NDAwMTk1LCJqdGkiOiJzcTk3c0NnWlhhNWhneXg2Iiwic3ViIjoiY2RhZDczZTktY2ZjZC00ZmRiLWIyODAtYjMxNjNjYzE3NTRmIiwicHJ2IjoiODdlMGFmMWVmOWZkMTU4MTJmZGVjOTcxNTNhMTRlMGIwNDc1NDZhYSJ9.V1MV2pQobCUoBBYYDeLKpLVlwIeG-L2PyijwFs1DpD0'''
            self.url = "https://localhost:8001/api/v1/"
            self.headers = {'Content-type': 'application/json',
                            'Authorization': 'Bearer '+self.token,
                            'Accept': 'application/json'}
            self.testpoint = "99"
            self.cert_verify = False
        else:
            self.token = MONIPE_TOKEN
            self.url = MONIPE_URL
            self.headers = {'Content-type': 'application/json',
                            'Authorization': 'Bearer '+self.token}
            self.testpoint = TESTPOINT
            self.cert_verify = True
        self.test_error = None
        self.test_id = None
        self.test_status = None
        self.test_status_error = None
        self.test_request_file_path = test_request_file_path

    def schedule_test(self):
        # curl --insecure --location --request POST 'https://localhost:8001/api/v1/testpoint/99/tests' --header "Authorization: Bearer $TOKEN" --header 'Content-Type: application/json' -d @teste.json
        test_url = f"testpoint/{self.testpoint}/tests"
        test_response = requests.post(
            self.url+test_url, data=json.dumps(self.monipe_homologation_test_request), headers=self.headers, verify=self.cert_verify)
        if test_response.status_code == 201:
            self.test_id = test_response.json()['id']
        else:
            self.test_error = test_response.json()

    def get_test_status(self):
        if self.test_error:
            raise Exception(self.test_error)
        status_url = f"testpoint/{self.testpoint}/test/{self.test_id}/status"
        status = requests.get(
            self.url+status_url, headers=self.headers, verify=self.cert_verify)
        if status.status_code == 200:
            self.test_status = status.json()
        else:
            self.test_status_error = status.json()
        return self.test_status

    def get_test_report(self):
        if self.test_error:
            raise Exception(self.test_error)
        report_url = f"testpoint/{self.testpoint}/test/{self.test_id}/report"
        report_name = "%s.pdf" % self.test_request_file_path.split('.')[0]
        response = requests.get(
            self.url+report_url, headers=self.headers, verify=self.cert_verify)
        if response.status_code == 200:
            open(report_name, 'wb').write(response.content)
            print(f"Report downloaded as {report_name}!")
            report_download_ack = True
        else:
            print("Could not get report!")
            print(f"Server error code {response.status_code}")
            report_download_ack = False
        return report_download_ack