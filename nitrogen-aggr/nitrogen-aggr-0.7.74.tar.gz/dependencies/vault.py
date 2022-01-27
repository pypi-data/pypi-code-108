import requests
from dependencies import job_history
import yaml
import time
from datetime import datetime
from datetime import timedelta
import json


class Vault(job_history.CadmiumJobHistory):
    def __init__(self, _self_config={}, _log_handler=None, _step=None):
        job_history.CadmiumJobHistory.__init__(self)
        self._step = _step
        self._log = _log_handler
        self._self_config = _self_config
        self._env = _self_config.get("env", "")
        self._client = _self_config.get("client", "")
        self._user = _self_config.get("user", "")
        self._workflow = _self_config.get("workflow", "")

        self._vault_configs = self.get_vault_config_values()
        self._log.info(self._vault_configs)
        self._config = self.get_step_config_values()


    @staticmethod
    def generic_parser(s):
        def try_as(loader, s, on_error):
            try:
                loader(s)
                return True
            except on_error:
                return False
            #
            # def json_parser(s):
            #     return try_as(json.loads, s, ValueError)

        def is_yaml(s):
            return try_as(yaml.safe_load, s, yaml.scanner.ScannerError)

        def is_json(s):
            return try_as(json.loads, s, ValueError)

        if not isinstance(s, str):
            return s
        if is_yaml(s):
            return yaml.safe_load(s)

        elif is_json(s):
            return json.loads(s)

        return s

    def get_step_config(self, step_name):
        if step_name in self._vault_configs['vault']['client']['data']:
            return self.generic_parser(self._vault_configs['vault']['client']['data'][step_name])

        return {}
    def get_step_config_values(self):
        '''

        :return:
            {
                "project": {project_config},
                "metadata": {metadata},
                "step":  { client/step specific data}
        '''


        # return this value to etl_job_base line 262, self.vault = Vault(...
        _configs = {
            "project": self.generic_parser(self._vault_configs['vault']['client']['data']['project']),
            "metadata": self._vault_configs['vault']['client']['metadata']
        }

        step_name = f"step_{self._step}"
        if step_name and step_name in self._vault_configs['vault']['client']['data']:
            _configs['step'] = self.generic_parser(self._vault_configs['vault']['client']['data'][step_name])

        return _configs

    def get_vault_config_values(self):
        '''

        :return: dict
            # key values in Vault
            self._config = {
                data:
                    step_lablabalba
                    project:
                    value
                metadata:
            }


        '''
        self_config = self._self_config
        vault_config = json.loads(self_config.get("vault_key", ""))
        self._log.info("Vault Token Loaded")
        self._log.info(vault_config)
        initial_config_path = vault_config["initial_config_path"]
        # config_len = vault_config["config_len"]
        aging_hour = vault_config["aging_hour"]
        current_datetime = datetime.strptime(
            datetime.now().strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M"
        )

        self._log.info(f"current_datetime: {current_datetime}.")

        # 1. use mnt volume file
        try:
            with open(initial_config_path, "r") as conf_file:
                data = conf_file.read()

            __config = json.loads(data)
            created_at = __config.get("created_at", "")
            self._log.info(f"created_at :{created_at}.")
            if not created_at or (
                created_at and self.is_file_aged(created_at, aging_hour)
            ):
                # 2 Or use vault values due to file is aged.
                self._log.info(
                    f"The file: {initial_config_path} is aged or has no created time, calling vault, and saving to mount volume."
                )
                data = self.read_from_vault_save_to_mnt_volume(
                    initial_config_path=initial_config_path,
                    vault_config=vault_config,
                    current_datetime=current_datetime,
                )
                return data
        # except FileNotFoundError or json.decoder.JSONDecodeError:
        except Exception as e:
            self._log.warn(
                f"The file  does not exist: {initial_config_path}, calling vault, and saving to mount volume. {e}"
            )
            # 3 Or use vault values as no file was found
            data = self.read_from_vault_save_to_mnt_volume(
                initial_config_path=initial_config_path,
                vault_config=vault_config,
                current_datetime=current_datetime,
            )
            return data
        else:
            self._log.info(f"Not calling vault use volume mount config.")
            return __config

    def read_from_vault_save_to_mnt_volume(
        self, initial_config_path, vault_config, current_datetime
    ):
        '''

            all_yaml = {
                data:
                    step_lablabalba
                    project:
                    value
                metadata:

            }
        '''

        all_vault_configs = self.read_all(_client=self._client, vault_config=vault_config)
        # data = yaml.load(all_vault_configs, Loader=yaml.FullLoader)
        data = {
            "vault": all_vault_configs,
            "client": self._client,
            "env": self._env,
            "created_at": str(current_datetime),
            "vault_metadata": self.job_history
        }
        data["vault_metadata"]["mount_store_at"] = str(
            current_datetime
        )  # vault meta save time at mnt volume
        # self._log.info(data)
        with open(initial_config_path, "w") as outfile:
            json.dump(data, outfile)

        return data

    def is_file_aged(self, _created_at, _aging_hour):
        d2 = datetime.strptime(_created_at, "%Y-%m-%d %H:%M:%S")
        d = datetime.now()
        hourly_diff = (d - d2) / timedelta(hours=1)
        self._log.info(f"hourly_diff: {hourly_diff}")
        return float(str(hourly_diff)) > _aging_hour

    def read_all(self, _client, vault_config):
        '''
        The url is a vault configuration passed as the arguemtn to the project.
        The urls are dicts with key and values {key1: url1, key2: url2}
        The return all_configs is a dictionary {key1: config_dict, key2: config_dict}

        :param _client:
        :param vault_config:
        :return:
        '''
        token = vault_config["vault"]["token"]
        retry = vault_config["vault"]["retry"]
        all_configs = {}
        i = 0
        for key, url in vault_config["vault"]["urls"].items():
            if '{client}' in url:
                url = url.replace('{client}', _client)

            all_configs[key]= self.vault_secrets_with_retry(
                    vault_token=token,
                    url=url,
                    retry=retry,
                    _initial_retry=retry + 1,
                    _url_count=i + 1,
                )
            i += 1

        return all_configs

    def vault_secrets_with_retry(
        self, vault_token, url, retry=5, _initial_retry=5, _url_count=0
    ):
        rj = self.read_from_vault(vault_token, url, _url_count=_url_count)
        if rj:
            completed = _initial_retry - retry
            self._log.info("Success getting vault secrets , {}".format(completed))
            # self._log.info(rj)
            return rj
        if retry == 0:
            self._log.info("Something is wrong here at vault {}".format(url))
            return f"{url}: error {retry}"
        if retry > 0:
            time.sleep(5)
            retry = retry - 1
            self.vault_secrets_with_retry(
                vault_token,
                url,
                retry=retry,
                _initial_retry=_initial_retry,
                _url_count=_url_count,
            )

    def get_last_nth(self, _url, n):
        if _url:
            return "/".join(_url.split("/")[-n:])
        return ""

    def read_from_vault(self, vault_token, url, _url_count):
        try:
            payload = requests.get(url, headers={"X-Vault-Token": vault_token},)
            if payload.status_code == 200:
                pl_json = payload.json()
                # With version
                value_version = pl_json["data"].get("data", "")
                if value_version:
                    return pl_json["data"]
                    # value = pl_json["data"]["data"]["value"]  # with version
                    # vault_metadata = pl_json["data"]["metadata"]
                    # vault_metadata["url_path"] = self.get_last_nth(url, 2)
                    # self.job_history[_url_count] = vault_metadata
                    # return value

                # No versioning.
                value = pl_json["data"]["value"]  # no version
                return value
        except Exception as e:
            print(e)
            return f"{url}: error"
        return f"{url}: error"

    @property
    def config(self):
        return self._config
