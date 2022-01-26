"""
    This is a template for a tear down job. The teardown job removes
    mnt/vol/local.yaml file. This is the last step for dag.
"""

import yaml
import os
import argparse
import json
from dependencies.logger import logger
from dependencies.post_gres import CadmiumPostGres


class TearDown:
    def __init__(self, _config=None):
        self.vault_metadata = {}
        self.postgres = {}
        self.client = "THP"
        self.user = "USER1"
        self.workflow = "SSD"
        self.env = "test"
        self.table_name = "job"
        self._log = logger()

    def init_config(self, _config):
        self.vault_metadata = _config.get('vault_metadata', self.vault_metadata)
        self.postgres = _config.get('job_history').get('postgres', self.postgres)
        self.client = _config.get('client', self.client)
        self.user = _config.get('user', self.user)
        self.workflow = _config.get('workflow', self.workflow)
        self.env = _config.get('env', self.env)

    def clean_vault_metadata(self):
        a = self.vault_metadata.keys()
        selection = [1, 2, 3]
        for el in a:
            if el in selection:
                self.vault_metadata[el].pop('deletion_time', None)
                self.vault_metadata[el].pop('destroyed', None)

    def get_config(self):
        """
            This function retrieves argument from DAG yaml template.
          :return:
          """

        parser = argparse.ArgumentParser(
            description="Argument Parser for teardown "
        )
        parser.add_argument(
            "--mnt_volume", action="store", type=str, required=False, help="mount volume path ",
        )
        args = vars(parser.parse_args())
        config = {"mnt_volume": args["mnt_volume"]}
        return config

    @property
    def log(self):
        return self._log


if __name__ == "__main__":
    # Read and delete
    _local_path = '/mnt/vol/local.yaml'
    td = TearDown()
    _mnt_config = td.get_config()
    local_path = _mnt_config.get('mnt_volume', _local_path)  # from argument

    try:
        with open(local_path, "r") as conf_file:
            __config = yaml.safe_load(conf_file)
        td.init_config(__config)
        _pg_values = td.postgres
        # td.log.info(__config)
        td.clean_vault_metadata()
        _vault_metadata = td.vault_metadata
        # td.log.info(_vault_metadata)
        table_name = _pg_values.get('table_name', td.table_name)
        post_gres = CadmiumPostGres(_pg_values['hostname'], _pg_values['database_name'], _pg_values['user'],
                                    _pg_values['password'], _pg_values['port'], True)

        post_gres.insert_into_table(table_name=table_name,
                                    columns_tuples='(client_name,workflow_name,stage_name,user_name,vault_versions)',
                                    placeholders_tuple='(%s, %s,%s, %s,%s)',
                                    values_tuple=(td.client, td.workflow, td.env, td.user, json.dumps(_vault_metadata)))
        post_gres.close()
        td.log.info("=====================Removing local file =====================")
        os.remove(local_path)  # remove mount file
        td.log.info("Completed")

    except FileNotFoundError:
        td.log.error(f"Sorry, the file  does not exist, {local_path}")
