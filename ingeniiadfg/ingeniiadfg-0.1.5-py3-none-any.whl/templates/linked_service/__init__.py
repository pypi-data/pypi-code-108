from .config_table_storage import config_table_storage
from .credentials_store import credentials_store
from .data_lake import data_lake
from .ftp import ftp_basic_key_vault
from .sftp import sftp_basic_key_vault

all_linked_services = {
    ls["name"]: ls
    for ls in [
        config_table_storage, credentials_store, data_lake,
        ftp_basic_key_vault, sftp_basic_key_vault
    ]
}
