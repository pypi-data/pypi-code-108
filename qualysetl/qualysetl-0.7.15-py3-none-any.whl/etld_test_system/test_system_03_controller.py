#!/usr/bin/env python3
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_test_system


def main():
    etld_lib_test_system.main()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='test_system_03_controller')
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()
