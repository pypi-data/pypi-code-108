import sys
import json
from traceback import print_exc


def json_pretty(data):
    return json.dumps(data, indent=4, sort_keys=True)


def write_json_to_file(path, data, log=None):
    if log:
        log.info(f"### Writing output to {path}")
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def read_json_file_into_object(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit(f"{path} not found")


def write_json_yield_to_file(file_path, generator_function, *args):
    with open(file_path, "w") as f:
        output = []
        for data in generator_function(*args):
            output.append(data)
        f.write(json_pretty(output))


def stream_json_yield_to_file(
        file_path, generator_function, *args, log=None, **kwargs):
    with open(file_path, 'w') as f:
        f.write("[\n")
        try:
            for data, last_result in generator_function(*args, **kwargs):
                f.write(json_pretty(data))
                if not last_result:
                    f.write(",")
        except Exception as e:
            if log:
                log.error("Streamed write failed with error:\n{}".format(e))
                log.error(print_exc())
            else:
                print_exc()
        finally:
            f.write("\n]")
