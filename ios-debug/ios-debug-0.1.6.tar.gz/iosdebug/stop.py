from iosdebug.processing.stopping.remove_run_script_build_phase import (
    remove_run_script_build_phase,
)
import os
from .processing.find_swift_files import find_swift_files
from .processing.create_path_to_content_dict import create_path_to_content_dict
from .processing.stopping import (
    store_mocked_implementations,
    set_original_root_view_controller,
    remove_mock_registrations,
)


def stop(path=os.getcwd(), update_project=True):
    swift_files = find_swift_files(path)
    path_to_content_map = create_path_to_content_dict(swift_files)
    store_mocked_implementations(path_to_content_map, path)
    set_original_root_view_controller(swift_files, path_to_content_map, path)
    remove_mock_registrations(swift_files)
    if update_project:
        remove_run_script_build_phase(path)
    print("Debug mode stooped.")
