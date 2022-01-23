#
import tempfile
from contextlib import contextmanager
from typing import ContextManager

import gnupg
from airflow.hooks.base import BaseHook


class GpgHook(BaseHook):
    # Override to provide the connection name.
    conn_type = 'gpg'
    hook_name = 'gpg'

    def __init__(self, gpg_conn_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gpg_conn_id = gpg_conn_id

    @contextmanager
    def get_conn(self) -> ContextManager[gnupg.GPG]:
        """Returns a connection object"""
        connection_obj = self.get_connection(self.gpg_conn_id)
        key_data = open(connection_obj.extra_dejson['key_file']).read()
        passphrase = connection_obj.password

        with tempfile.TemporaryDirectory() as gnupghome:
            self.log.info(f"Created temporary gnupghome directory {gnupghome}")
            gpg = gnupg.GPG(gnupghome=gnupghome)
            import_result = gpg.import_keys(key_data, passphrase=passphrase)
            gpg.trust_keys([x["fingerprint"] for x in import_result.results], 'TRUST_ULTIMATE')
            self.log.info("Import result")
            self.log.info(import_result.results)
            yield gpg
