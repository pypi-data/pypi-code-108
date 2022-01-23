import os
from datetime import datetime

from airflow import DAG

from airflow_gpg_plugin.operators.gpg_encrypt_file_operator import GPGEncryptFileOperator
from tests.conftest import decrypt_file


def test_gpg_encrypt_file_operator(gpg_key_with_passphrase_connection, gpg_key_with_passphrase, tmpdir_factory):
    gpg_conn_id = gpg_key_with_passphrase_connection

    input_file_path = str(tmpdir_factory.mktemp("files").join("test_file.txt"))
    output_file_path = str(tmpdir_factory.mktemp("files").join("test_file_enc.txt"))
    f = open(input_file_path, "w")
    f.write("hello world")
    f.flush()
    f.close()

    with DAG(dag_id="test_gpg_encrypt_file_dag_1", start_date=datetime(2021, 1, 1), schedule_interval="@daily") as dag:
        op = GPGEncryptFileOperator(
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
        assert decrypt_file(op.output_file_path, gpg_key_with_passphrase) == "hello world"


def test_gpg_encrypt_file_operator_template_values(gpg_key_with_passphrase_connection, gpg_key_with_passphrase,
                                                   tmpdir_factory):
    gpg_conn_id = gpg_key_with_passphrase_connection
    input_file_path = str(tmpdir_factory.mktemp("files").join("test_file.txt"))
    output_file_path = str(tmpdir_factory.mktemp("files").join("test_file_enc.txt"))
    input_file_path_template = f"{{{{ '{input_file_path}' }}}}"
    output_file_path_template = f"{{{{ '{output_file_path}' }}}}"
    f = open(input_file_path, "w")
    f.write("hello world")
    f.flush()
    f.close()

    with DAG(dag_id="test_gpg_encrypt_file_dag_2", start_date=datetime(2021, 1, 1), schedule_interval="@daily") as dag:
        op = GPGEncryptFileOperator(
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
        assert decrypt_file(output_file_path, gpg_key_with_passphrase) == "hello world"
