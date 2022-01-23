import os
from datetime import datetime

from airflow import DAG

from airflow_gpg_plugin.operators.gpg_decrypt_file_operator import GPGDecryptFileOperator
from tests.conftest import encrypt_file


def test_gpg_decrypt_file_operator(gpg_key_with_passphrase_connection, gpg_key_with_passphrase, tmpdir_factory):
    gpg_conn_id = gpg_key_with_passphrase_connection

    input_file_path = str(tmpdir_factory.mktemp("files").join("test_file_enc.txt"))
    output_file_path = str(tmpdir_factory.mktemp("files").join("test_file_dec.txt"))
    encrypt_file(data="hello world", encrypted_file_path=input_file_path, key_details=gpg_key_with_passphrase)

    with DAG(dag_id="test_gpg_decrypt_file_dag_1", start_date=datetime(2021, 1, 1), schedule_interval="@daily") as dag:
        op = GPGDecryptFileOperator(
            task_id="gpg_enc",
            dag=dag,
            conn_id=gpg_conn_id,
            input_file_path=input_file_path,
            output_file_path=output_file_path
        )
        dag.clear()
        op.run(
            start_date=dag.start_date,
            end_date=dag.start_date,
            ignore_first_depends_on_past=True,
            ignore_ti_state=True
        )

        assert os.path.exists(op.output_file_path)
        assert open(op.output_file_path, "r").read() == "hello world"


def test_gpg_decrypt_file_operator_with_template_values(gpg_key_with_passphrase_connection, gpg_key_with_passphrase,
                                                        tmpdir_factory):
    gpg_conn_id = gpg_key_with_passphrase_connection

    input_file_path = str(tmpdir_factory.mktemp("files").join("test_file_enc.txt"))
    output_file_path = str(tmpdir_factory.mktemp("files").join("test_file_dec.txt"))
    input_file_path_template = f"{{{{ '{input_file_path}' }}}}"
    output_file_path_template = f"{{{{ '{output_file_path}' }}}}"

    encrypt_file(data="hello world", encrypted_file_path=input_file_path, key_details=gpg_key_with_passphrase)

    with DAG(dag_id="test_gpg_decrypt_file_dag_2", start_date=datetime(2021, 1, 1), schedule_interval="@daily") as dag:
        op = GPGDecryptFileOperator(
            task_id="gpg_enc",
            dag=dag,
            conn_id=gpg_conn_id,
            input_file_path=input_file_path_template,
            output_file_path=output_file_path_template
        )
        dag.clear()
        op.run(
            start_date=dag.start_date,
            end_date=dag.start_date,
            ignore_first_depends_on_past=True,
            ignore_ti_state=True
        )

        assert os.path.exists(output_file_path)
        assert open(output_file_path, "r").read() == "hello world"
