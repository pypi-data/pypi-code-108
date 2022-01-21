#!/usr/bin/env python3
import time
import sys
import json
from pathlib import Path
import re
import gzip
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_extract_transform_load
from qualys_etl.etld_lib import etld_lib_datetime
from qualys_etl.etld_knowledgebase import knowledgebase_02_workflow_manager
from qualys_etl.etld_host_list import host_list_02_workflow_manager
from qualys_etl.etld_host_list_detection import host_list_detection_02_workflow_manager
from qualys_etl.etld_asset_inventory import asset_inventory_02_workflow_manager
from qualys_etl.etld_was import was_04_extract_from_qualys


def validate_json_file(open_file_method=open, file_path: Path = Path()):
    last_characters = []
    validation_type = 'tail file'
    with open_file_method(file_path, "rt", encoding='utf-8') as read_file:
        last_characters_test_passed = False
        try:
            # light validation detecting closure of json with curly brace closure
            last_characters = tail_file_by_last_characters(open_file_method=open_file_method,
                                                           file_path=file_path,
                                                           number_of_characters=25)
            validate_last_characters_are_str = '}'
            if last_characters[-1:] == validate_last_characters_are_str:
                last_characters_test_passed = True
        except Exception as e:
            last_characters_test_passed = False

        try:
            if last_characters_test_passed is False:
                validation_type = 'json.load file'
                json.load(read_file)
        except Exception as e:
            raise Exception(f"WARNING: MALFORMED JSON, COULD NOT json.load batch file, "
                            f"validation_test_type={validation_type}, "
                            f"directory={Path(file_path).parent.name}, "
                            f"batch file={etld_lib_extract_transform_load.get_batch_name_from_filename(file_path)}, "
                            f"Exception={e}"
                            )

        etld_lib_functions.logger.info(f"PASS: JSON VALIDATED, "
                                       f"validation_test_type={validation_type}, "
                                       f"directory={Path(file_path).parent.name}, "
                                       f"batch file={etld_lib_extract_transform_load.get_batch_name_from_filename(file_path)}, "
                                       f"tail file={last_characters}")


def validate_extract_directories_json_files_downloaded():
    json_dir_list = []
    json_dir_list.append(Path(etld_lib_config.host_list_extract_dir))
    json_dir_list.append(Path(etld_lib_config.host_list_detection_extract_dir))
    json_dir_list.append(Path(etld_lib_config.kb_extract_dir))
    json_dir_list.append(Path(etld_lib_config.asset_inventory_extract_dir))
    json_dir_search_glob = '*.json.gz'

    for json_dir in json_dir_list:
        json_file_list = sorted(Path(json_dir).glob(json_dir_search_glob))
        for json_file_path in json_file_list:
            try:
                validate_json_file(open_file_method=gzip.open,
                                   file_path=json_file_path)
            except Exception as e:
                etld_lib_functions.logger.error(f'Exception {e}')


def tail_file_by_last_characters(open_file_method=open, file_path: Path = Path(), number_of_characters: int = 1000):
    file_position = number_of_characters
    last_lines_from_file = []
    file_length_in_utf_8_characters = 0
    with open_file_method(file_path, mode="rt", encoding='utf-8') as f:
        try:
            f.seek(0, 2)
            file_length_in_utf_8_characters = f.tell()
            if file_length_in_utf_8_characters <= number_of_characters:
                file_position = 0
            else:
                file_position = file_length_in_utf_8_characters - number_of_characters

            f.seek(file_position, 0)
            last_characters_list = []
            while True:
                char = f.read(1)
                if not char:
                    break
                last_characters_list.append(char)
        except IOError as ioe:
            raise Exception(ioe)
        finally:
            last_lines_from_file = ''.join(last_characters_list)
            return last_lines_from_file


def tail_file_by_lines(open_file_method=open, file_path: Path = Path(), number_of_lines: int = 10):
    file_position = number_of_lines + 1
    last_lines_from_file = []
    with open_file_method(file_path, mode="rt", encoding='utf-8') as f:
        while len(last_lines_from_file) <= number_of_lines:
            try:
                f.seek(-file_position, 2)
            except IOError:
                f.seek(0)
                break
            finally:
                last_lines_from_file = list(f)
            file_position *= 2
    return last_lines_from_file[-number_of_lines:]


def validate_xml_is_closed_properly(test_by='xml_characters',
                                    open_file_method=gzip.open,
                                    file_path: Path = Path(),
                                    number_of_lines: int = 10,
                                    number_of_characters: int = 1000):
    batch = re.sub('^.*batch', 'batch', str(file_path))
    directory_name = str(file_path.parent.name)
    xml_lines = []
    xml_characters_list = []
    try:
        if 'characters' in test_by:
            xml_lines = tail_file_by_last_characters(open_file_method, file_path, number_of_characters)
        else:
            xml_lines = tail_file_by_lines(open_file_method, file_path, number_of_lines)
    except Exception as e:
        xml_line = ''.join(xml_lines.replace('\n', ''))
        raise Exception(f"WARNING: CANNOT READ, CREATION MAY BE IN PROGRESS "
                        f"test_by={test_by} "
                        f"directory={directory_name} "
                        f"batch file={batch}, "
                        f"Exception={e}, "
                        f"tail file={xml_line}")

    found_end_of_response = False
    end_of_response = '</RESPONSE>'
    found_incident = False
    incident_text = 'incident signature'
    xml_line = ''.join(xml_lines.replace('\n', ''))
    if end_of_response in xml_line:
        found_end_of_response = True
    if incident_text in str(xml_line).lower():
        found_incident = True

    if found_incident is True:
        raise Exception(f"WARNING: INCIDENT FOUND, "
                        f"test_by={test_by} "
                        f"directory={directory_name} "
                        f"batch file={batch}, "
                        f"tail file={xml_line}")
    elif found_end_of_response is False:
        raise Exception(f"WARNING: END OF RESPONSE NOT FOUND, "
                        f"test_by={test_by} "
                        f"directory={directory_name} "
                        f"batch file={batch}, "
                        f"tail file={xml_line}")
    else:
        etld_lib_functions.logger.info(f"PASS: "
                                       f"test_by={test_by} "
                                       f"directory={directory_name} "
                                       f"batch file={batch}, "
                                       f"tail file={xml_line}")
    return xml_line


def validate_extract_directories_xml_files_downloaded(test_by='characters'):
    xml_dir_list = []
    xml_dir_list.append(Path(etld_lib_config.host_list_extract_dir))
    xml_dir_list.append(Path(etld_lib_config.host_list_detection_extract_dir))
    xml_dir_list.append(Path(etld_lib_config.kb_extract_dir))
    xml_dir_search_glob = '*.xml.gz'

    for xml_dir in xml_dir_list:
        xml_file_list = sorted(Path(xml_dir).glob(xml_dir_search_glob))
        for xml_file_path in xml_file_list:
            try:
                if 'characters' in test_by:
                    lines = validate_xml_is_closed_properly(open_file_method=gzip.open,
                                                            file_path=xml_file_path,
                                                            number_of_lines=8,
                                                            number_of_characters=1000)
                else:
                    lines = validate_xml_is_closed_properly(test_by='lines',
                                                            open_file_method=gzip.open,
                                                            file_path=xml_file_path,
                                                            number_of_lines=8,
                                                            number_of_characters=1000)
            except Exception as e:
                etld_lib_functions.logger.error(f'Exception {e}')


def test_knowledgebase(test_name='knowledgebase'):
    etld_lib_config.kb_last_modified_after = etld_lib_datetime.get_utc_date_minus_days(30)
    etld_lib_functions.logger.info(f"Starting test with kb_last_modified_after: {etld_lib_config.kb_last_modified_after}")
    try:
        knowledgebase_02_workflow_manager.main()
    except Exception as e:
        etld_lib_functions.logger.error(f"Failed Test: Exception{e}")
        raise Exception

    etld_lib_functions.logger.info(f"Ending   test with kb_last_modified_after: {etld_lib_config.kb_last_modified_after}")


def test_host_list(test_name='host_list'):
    etld_lib_config.host_list_vm_processed_after = etld_lib_datetime.get_utc_date_minus_days(180)
    etld_lib_config.host_list_test_system_flag = True
    etld_lib_config.host_list_test_number_of_files_to_extract = 3
    etld_lib_config.host_list_payload_option = {'truncation_limit': '25'}
    etld_lib_functions.logger.info(
        f"Starting test with: "
        f"host_list_vm_processed_after={etld_lib_config.host_list_vm_processed_after}, "
        f"host_list_payload_option={etld_lib_config.host_list_payload_option}, " 
        f"host_list_test_number_of_files_to_extract={etld_lib_config.host_list_test_number_of_files_to_extract}")
    try:
        host_list_02_workflow_manager.main()
    except Exception as e:
        etld_lib_functions.logger.error(f"Failed Test: Exception{e}")
        raise Exception

    etld_lib_functions.logger.info(f"Ending: {etld_lib_config.host_list_vm_processed_after}, "
                                   f"Test {etld_lib_config.host_list_test_number_of_files_to_extract} files")


def test_host_list_detection(test_name='host_list_detection'):
    etld_lib_config.host_list_detection_vm_processed_after = etld_lib_datetime.get_utc_date_minus_days(180)
    etld_lib_config.host_list_vm_processed_after = etld_lib_datetime.get_utc_date_minus_days(180)
    etld_lib_config.host_list_test_system_flag = True
    etld_lib_config.host_list_test_number_of_files_to_extract = 3
    etld_lib_config.host_list_payload_option = {'truncation_limit': '25'}
    etld_lib_functions.logger.info(
        f"Starting test with: "
        f"host_list_vm_processed_after={etld_lib_config.host_list_vm_processed_after}, "
        f"host_list_payload_option={etld_lib_config.host_list_payload_option}, " 
        f"host_list_test_number_of_files_to_extract={etld_lib_config.host_list_test_number_of_files_to_extract}")
    try:
        host_list_detection_02_workflow_manager.main()
    except Exception as e:
        etld_lib_functions.logger.error(f"Failed Test: Exception{e}")
        raise Exception

    etld_lib_functions.logger.info(f"Ending: {etld_lib_config.host_list_vm_processed_after}, "
                                   f"Test {etld_lib_config.host_list_test_number_of_files_to_extract} files")


def test_asset_inventory(test_name='asset_inventory'):
    etld_lib_config.asset_inventory_asset_last_updated = etld_lib_datetime.get_utc_date_minus_days(180)
    etld_lib_config.asset_inventory_test_system_flag = True
    etld_lib_config.asset_inventory_test_number_of_files_to_extract = 3
    etld_lib_functions.logger.info(
        f"Starting test with: "
        f"asset_inventory_asset_last_updated={etld_lib_config.asset_inventory_asset_last_updated}, "
        f"asset_inventory_test_number_of_files_to_extract="
        f"{etld_lib_config.asset_inventory_test_number_of_files_to_extract}")
    try:
        asset_inventory_02_workflow_manager.main()
    except Exception as e:
        etld_lib_functions.logger.error(f"Failed Test: Exception{e}")
        raise Exception

    etld_lib_functions.logger.info(
        f"Ending test with: "
        f"asset_inventory_asset_last_updated={etld_lib_config.asset_inventory_asset_last_updated}, "
        f"asset_inventory_test_number_of_files_to_extract="
        f"{etld_lib_config.asset_inventory_test_number_of_files_to_extract}")


def test_was_count():
    etld_lib_config.remove_old_files(
        dir_path=etld_lib_config.was_extract_dir,
        dir_search_glob=etld_lib_config.was_extract_dir_file_search_blob_webapp_count
                                     )
    file_info_dict = \
        etld_lib_config.prepare_extract_batch_file_name(
            next_batch_number_str='batch_000001',
            next_batch_date=etld_lib_datetime.get_utc_datetime_qualys_format(),
            extract_dir=etld_lib_config.was_extract_dir,
            file_name_type="was_count_webapp",
            file_name_option="last_scan_date",
            file_name_option_date='1970-01-01T00:00:00Z',
            file_extension="json",
            compression_method=etld_lib_config.was_open_file_compression_method)

    etld_lib_functions.logger.info("Starting test was_04_extract_from_qualys.was_webapp_extract_count")
    try:
        was_04_extract_from_qualys.was_webapp_extract_count(
            batch_number_str='batch_000001',
            qualys_headers_dict={},
            file_info_dict=file_info_dict,
            cred_dict=etld_lib_credentials.get_cred(),
        )
    except Exception as e:
        etld_lib_functions.logger.error(f"Failed Test: Exception{e}")
        raise Exception

    etld_lib_functions.logger.info("Ending test was_04_extract_from_qualys.was_webapp_extract_count")


def main(test_function_to_run='All'):
    return_code_dict = {}
    return_code = 0
    try:
        if test_function_to_run == 'All' or test_function_to_run == 'test_knowledgebase':
            test_knowledgebase()
    except Exception as e:
        return_code_dict['test_knowledgebase'] = 1
        return_code_dict['test_knowledgebase_exception'] = f"{e}"
        return_code = 1
    try:
        if test_function_to_run == 'All' or test_function_to_run == 'test_host_list':
            test_host_list()
    except Exception as e:
        return_code_dict['test_host_list'] = 1
        return_code_dict['test_host_list_exception'] = f"{e}"
        return_code = 1
    try:
        if test_function_to_run == 'All' or test_function_to_run == 'test_host_list_detection':
            test_host_list_detection()
    except Exception as e:
        return_code_dict['test_host_list_detection'] = 1
        return_code_dict['test_host_list_detection_exception'] = f"{e}"
        return_code = 1
    try:
        if test_function_to_run == 'All' or test_function_to_run == 'test_asset_inventory':
            test_asset_inventory()
    except Exception as e:
        return_code_dict['test_asset_inventory'] = 1
        return_code_dict['test_asset_inventory_exception'] = f"{e}"
        return_code = 1
    try:
        if test_function_to_run == 'All' or test_function_to_run == 'validate_extract_directories_json_files_downloaded':
            validate_extract_directories_json_files_downloaded()
    except Exception as e:
        return_code_dict['test_extract_directories_json_files_downloaded'] = 1
        return_code_dict['test_extract_directories_json_files_downloaded_exception'] = f"{e}"
        return_code = 1
    try:
        if test_function_to_run == 'All' or test_function_to_run == 'validate_extract_directories_xml_files_downloaded':
            validate_extract_directories_xml_files_downloaded(test_by='characters')
    except Exception as e:
        return_code_dict['test_extract_directories_xml_files_downloaded'] = 1
        return_code_dict['test_extract_directories_xml_files_downloaded_exception'] = f"{e}"
        return_code = 1
    try:
        if test_function_to_run == 'test_was_count':
            test_was_count()
    except Exception as e:
        return_code_dict['test_was_count'] = 1
        return_code_dict['test_was_count_exception'] = f"{e}"
        return_code = 1

    for return_code_key in return_code_dict.keys():
        etld_lib_functions.logger(f"TEST FAILED: {return_code_key}={return_code_dict[return_code_key]}")

    exit(return_code)


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='etld_lib_test')
    etld_lib_config.main()
    etld_lib_credentials.main()
    arguments = sys.argv
    if len(arguments) > 1:
        test_function_to_run = arguments[1]
    else:
        test_function_to_run = 'All'

    main(test_function_to_run=test_function_to_run)
