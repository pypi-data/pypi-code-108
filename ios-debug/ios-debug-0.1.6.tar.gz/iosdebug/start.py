from iosdebug.processing.stopping.remove_run_script_build_phase import (
    remove_run_script_build_phase,
)
import os
import pickle

from .processing.find_swift_files import find_swift_files
from .processing.create_path_to_content_dict import create_path_to_content_dict
from .processing.starting import *
from iosdebug.constants import DATA_FILE, IGNORE_FILE


def start(path=os.getcwd(), update_project=True):
    if not os.path.isfile(path + os.sep + DATA_FILE):
        with open(path + os.sep + DATA_FILE, "wb") as file:
            pickle.dump("{'mock_implementations': {}}", file)

    if os.path.isfile(path + os.sep + IGNORE_FILE):
        with open(path + os.sep + IGNORE_FILE, "r") as file:
            ignored_protocols = file.read().split("\n")
    else:
        ignored_protocols = []

    swift_files = find_swift_files(path)

    if is_debug_mode_on(swift_files):
        print("Debug mode is already on.")
        return

    path_to_content_map = create_path_to_content_dict(swift_files)

    repository_protocols = find_repository_protocols(path_to_content_map)

    for protocol in ignored_protocols:
        if protocol in repository_protocols:
            index = repository_protocols.index(protocol)
            del repository_protocols[index]

    protocol_to_protocol_functions = get_protocols_to_protocol_functions_dict(
        repository_protocols, path_to_content_map
    )

    registrations = get_registrations(repository_protocols)

    write_mock_implementations(
        path_to_content_map, protocol_to_protocol_functions, path
    )

    protocol_to_mocked_contents = get_protocol_to_mocked_content_dict(
        repository_protocols, path_to_content_map
    )

    protocol_to_mock_function_variants = get_mock_functions_variants(
        protocol_to_mocked_contents
    )

    processed_mock_manager = get_mock_settings_and_mock_cursor(
        protocol_to_protocol_functions, protocol_to_mock_function_variants
    )

    store_mocked_implementation(protocol_to_mocked_contents, path)

    create_and_set_mock_manager(
        swift_files, path_to_content_map, processed_mock_manager, path
    )

    add_mock_registrations_to_container_builder(swift_files, registrations)

    if update_project:
        add_run_script_build_phase(path)

    print("Debug mode started.")
