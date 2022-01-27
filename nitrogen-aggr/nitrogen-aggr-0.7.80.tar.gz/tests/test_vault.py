"""
test_vault.py
~~~~~~~~~~~~~~~
This module contains unit tests for vault functionality tests. Test assertions are to
ensure payload data format are within expectations. As version number for the vault
payload is important, a few assertions are made to ensure it exists.

Another feature the vault request test must have is the ability to retry when the url
request is not available. Currently, for test purposes the retry is set to 2.

Assumptions:
Since, pytest is run locally or at the Travis CI environment, a direct connection to
the EpiSource Hashicorp Vault is not available as those environments, i.e. local and
Travis CI, are not within the same AWS Security Group, thus assertions are tested for
functionality tests.

"""

import unittest
import requests
import requests_mock
import time


class VaultTest:
    def __init__(self):
        self.data = self.data_on_success()
        self.job_history = {
            "job_run_at": "2020-07-09 11:12:00",
            "create_at": "2020-07-09 11:12:00",
            1: {
                "created_time": "2020-07-07T15:34:01.598860826Z",
                "deletion_time": "",
                "destroyed": False,
                "url_path": "conf/cadmium",
                "version": 1
            },
            2: {
                "created_time": "2020-07-07T15:34:01.598860826Z",
                "deletion_time": "",
                "destroyed": False,
                "url_path": "conf/thp",
                "version": 1
            },
            3: {
                "created_time": "2020-07-07T15:34:01.598860826Z",
                "deletion_time": "",
                "destroyed": False,
                "url_path": "infra/thp",
                "version": 1
            }
        }

    @staticmethod
    def data_on_success():
        cadmium_pl = {
            "request_id": "e8602044-0fdb-6290-234a-e185a2849a0c",
            "lease_id": "",
            "renewable": False,
            "lease_duration": 0,
            "data": {"data": {"value": "name: CADMIUM\npath: conf/cadmium\n"},
                     "metadata": {"created_time": "2020-07-07T15:34:01.598860826Z",
                                  "deletion_time": "", "destroyed": False, "version": 2}},
            "wrap_info": None, "warnings": None, "auth": None
        }

        with requests_mock.Mocker() as mock_request:
            mock_request.get("http://127.0.0.1:8200/v1/secret/data/cadmium/conf/cadmium", json=cadmium_pl)
            response = requests.get("http://127.0.0.1:8200/v1/secret/data/cadmium/conf/cadmium")

        return response.json()

    def vault_secrets_with_retry(self, vault_token, url, retry=5, _initial_retry=5, _url_count=0, _timeout=0.10):
        rj = self.read_from_vault(vault_token, url, _url_count=_url_count, _timeout=_timeout)
        msg = f"Request timeout at {_timeout}"
        if rj != msg:
            completed = _initial_retry - retry
            print("Success getting vault secrets , {}".format(completed))
            return msg
        if retry == 0:
            msg1 = "Something is wrong here at vault {}".format(url)
            return msg1
        if retry > 0:
            time.sleep(1)
            retry = retry - 1
            print("retry")
            print(retry)
            self.vault_secrets_with_retry(vault_token, url, retry=retry, _initial_retry=_initial_retry,
                                          _url_count=_url_count)

    def get_last_nth(self, _url, n):
        if _url:
            return "/".join(_url.split("/")[-n:])
        return ""

    def read_from_vault(self, vault_token, url, _url_count, _timeout):
        _job_history = self.job_history
        payload = {}
        try:
            payload = requests.get(
                url,
                headers={'X-Vault-Token': vault_token},
                timeout=_timeout
            )
        except requests.exceptions.Timeout:
            return f"Request timeout at {_timeout}"
        except requests.exceptions.TooManyRedirects:
            print("Too many redirect")
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print("there is an error", e)
            return

        __code = payload.get('status_code', "404")
        if __code == 200:
            pl_json = payload.json()
            # With version
            value_version = pl_json['data'].get('data', '')
            if value_version:
                value = pl_json['data']['data']['value']  # with version
                vault_metadata = pl_json['data']['metadata']
                vault_metadata["url_path"] = self.get_last_nth(url, 2)
                self.job_history[_url_count] = vault_metadata
                return value

            # No versioning.
            value = pl_json['data']['value']  # no version
            return value

        return __code


class TestHTTPRequest(unittest.TestCase):

    def test_request_vault_retry(self):
        _timeout = 0.10
        data = VaultTest().vault_secrets_with_retry("aTokenValue",
                                                    "http://10.1.1.1:8200/v1/secret/cadmium/conf/cadmium",
                                                    retry=2, _initial_retry=2,
                                                    _url_count=1,
                                                    _timeout=_timeout)

        assert data is None

    def test_request_vault_timeout(self):
        _timeout = 2.18
        data = VaultTest().read_from_vault("aTokenValue", "http://10.1.1.1:8200/v1/secret/cadmium/conf/cadmium", 1,
                                           _timeout=_timeout)
        assert data == f"Request timeout at {_timeout}"

    def test_lease_duration(self):
        d = VaultTest().data
        assert d["lease_duration"] == 0
        assert "request_id" in d.keys()

    def test_data_path(self):
        d = VaultTest().data
        assert d["data"]["data"]["value"] == "name: CADMIUM\npath: conf/cadmium\n"

    def test_vault_with_version(self):
        d = VaultTest().data
        assert "version" in d["data"]["metadata"].keys()

    def test_vault_with_version_number(self):
        d = VaultTest().data
        assert d["data"]["metadata"]["version"] == 2
