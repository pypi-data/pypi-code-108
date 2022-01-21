import shutil
import os
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions


def copy_results_to_external_target(source_list=None, target=None):

    if target == 'default':
        etld_lib_functions.logger.info(f"No export_dir set: {target}")
        pass
    elif os.path.isdir(target):
        try:
            for file_path in source_list:
                if os.path.exists(file_path):
                    shutil.copy2(str(file_path), str(target), follow_symlinks=True)
                    etld_lib_functions.logger.info(f"{str(file_path)} distributed to {str(target)}")

                else:
                    etld_lib_functions.logger.warning(f"file doesn't exists:{str(file_path)} "
                                            f"cannot distribute to {str(target)}")
        except Exception as e:
            etld_lib_functions.logger.error(f"Exception: {e}")
            etld_lib_functions.logger.error(f"Error distributing files.  ")
            etld_lib_functions.logger.error(f"etld_lib_config_settings.yaml [named]_export_dir "
                                            f"directory accessibility issue: {target}")
            exit(1)
    else:
        etld_lib_functions.logger.error(f"Program aborting, etld_lib_config_settings.yaml "
                                        f"[named]_export_dir directory does not exist: {target}")
        exit(1)
