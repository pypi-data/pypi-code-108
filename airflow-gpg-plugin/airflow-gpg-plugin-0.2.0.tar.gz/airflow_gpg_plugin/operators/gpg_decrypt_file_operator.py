from typing import Any

from airflow.models import BaseOperator

from airflow_gpg_plugin.hooks.gpg_hook import GpgHook


class GPGDecryptFileOperator(BaseOperator):
    """
    Decrypt a file with private GPG key from provided gpg connection
    :param conn_id: GPG connection id to use for decryption
    :param input_file_path: Encrypted File to decrypt
    :param output_file_path: Output path of decrypted file
    """

    template_fields = ('input_file_path', 'output_file_path')

    def __init__(self,
                 conn_id: str,
                 input_file_path: str,
                 output_file_path: str,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.conn_id = conn_id
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path

    def execute(self, context: Any):
        gpg_hook = GpgHook(
            self.conn_id
        )
        conn_obj = gpg_hook.get_connection(self.conn_id)
        self.log.info(f"Decrypting file {self.input_file_path}")
        with gpg_hook.get_conn() as gpg_client:
            with open(self.input_file_path, 'rb') as f:
                status = gpg_client.decrypt_file(
                    file=f,
                    always_trust=True,
                    output=self.output_file_path,
                    passphrase=conn_obj.password
                )

        self.log.info(f"Decrypted file {self.input_file_path} to location {self.output_file_path}")
        self.log.info(f"Ok: {status.ok}")
        self.log.info(f"Status: {status.status}")
        self.log.error(f"Stderr: {status.stderr}")
