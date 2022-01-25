import os

from _pistar.pistar_pytest.utils import write_json

# file name for agents.
META_INFO = "task_meta_info.json"
FINISHED = "finished.json"


def generate_start_file(
        case_path: str,
        output_dir: str
) -> None:
    data = {"cur_script": case_path}

    des = os.path.join(output_dir, META_INFO)

    write_json(data, des)


def generate_finish_file(
        output_dir,
        start_time,
        end_time,
        status,
        exception_info=None) -> None:
    """
    description: the finished json file is used to
    offer the test case basic execution info.
    """

    finish_data = dict()
    finish_data["start_time"] = start_time
    finish_data["end_time"] = end_time
    finish_data["duration"] = end_time - start_time
    finish_data["result"] = status
    if exception_info:
        finish_data["exception"] = exception_info

    des = os.path.join(output_dir, FINISHED)
    write_json(finish_data, des)
