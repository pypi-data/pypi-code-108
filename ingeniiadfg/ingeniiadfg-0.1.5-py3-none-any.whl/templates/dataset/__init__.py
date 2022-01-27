from .config_table import config_table
from .data_lake import data_lake_folder, data_lake_file
from .ftp import ftp_folder, ftp_file
from .sftp import sftp_folder, sftp_file

all_data_sets = {
    ds["name"]: ds
    for ds in [
        config_table,
        data_lake_folder, data_lake_file,
        ftp_folder, ftp_file,
        sftp_folder, sftp_file
    ]
}
