from airflow.models import Connection

from airflow_gpg_plugin.hooks.gpg_hook import GpgHook
from tests.conftest import create_connection


def test_airflow_gpg_hook_with_passphrase_key(gpg_key_with_passphrase):
    gpg_conn_id = "default_gpg_conn"

    conn = Connection(
        conn_id=gpg_conn_id,
        conn_type=GpgHook.conn_type,
        login=gpg_key_with_passphrase["login"],
        password=gpg_key_with_passphrase["password"],
        extra={
            "key_file": gpg_key_with_passphrase["key_file"]
        }
    )

    create_connection(gpg_conn_id, conn)

    hook = GpgHook(
        gpg_conn_id=gpg_conn_id
    )
    with hook.get_conn() as gpg_client:
        keys = gpg_client.list_keys()
        assert len(keys) == 1
        assert keys[0]["type"] == "pub"
        assert keys[0]["fingerprint"] == "818E2DFFE58AE74CB08EA374AD584D1465AF661F"


def test_airflow_gpg_hook_without_passphrase_key(gpg_key_without_passphrase):
    gpg_conn_id = "default_gpg_conn_without_passphrase"

    conn = Connection(
        conn_id=gpg_conn_id,
        conn_type=GpgHook.conn_type,
        login=gpg_key_without_passphrase["login"],
        password=gpg_key_without_passphrase["password"],
        extra={
            "key_file": gpg_key_without_passphrase["key_file"]
        }
    )

    create_connection(gpg_conn_id, conn)

    hook = GpgHook(
        gpg_conn_id=gpg_conn_id
    )
    with hook.get_conn() as gpg_client:
        keys = gpg_client.list_keys()
        assert len(keys) == 1
        assert keys[0]["type"] == "pub"
        assert keys[0]["fingerprint"] == "DC81CBF472309E80AE9A02691D199764DF22F0CC"
