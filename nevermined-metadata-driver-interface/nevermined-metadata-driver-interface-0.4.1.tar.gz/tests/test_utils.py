# import os
# import sys
#
# from metadata_driver_interface.utils import retrieve_module_path
#
#
# def test_retrieve_module_path():
#     _type = 'data'
#     module = 'onprem'
#     config = './tests/config.ini'
#     assert retrieve_module_path(_type=_type, module=module,
#                                 config=config) == f'{os.getenv("VIRTUAL_ENV")}/lib/python3.{sys.version_info[1]}' \
#                                                   f'/site-packages/metadata_driver_{module}/{_type}_plugin.py'
