import base64
import datetime
import hashlib
import math
import os
import pickle
import shutil
import subprocess
import sys
import time
import uuid
import zipfile
import zlib
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Union

from objsize import get_deep_size

from aibro.tools.prints import print_receiving

if os.name == "nt":
    import ctypes  # noqa: F401
    import msvcrt  # noqa: F401

    class _CursorInfo(ctypes.Structure):
        _fields_ = [("size", ctypes.c_int), ("visible", ctypes.c_byte)]


def hide_cursor():
    if os.name == "nt":
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = False
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == "posix":
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()


def show_cursor():
    if os.name == "nt":
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = True
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == "posix":
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


class ModelAndDataset(NamedTuple):
    tensorflow_version: str
    encoded_model_content: str
    encoded_train_X: str
    encoded_train_Y: str
    encoded_validation_X: Optional[str]
    encoded_validation_Y: Optional[str]
    user_id: str
    batch_size: int
    epochs: int
    loss_config: Union[dict, str]
    optimizer_config: Union[dict, str]
    metrics_config: Union[List[Dict], List[str]]
    fit_kwargs: Dict[str, Any]
    job_id: str
    m_d_serialized_at_ms: int
    train_X_shape: list
    train_Y_shape: list
    valid_X_shape: list
    valid_Y_shape: list
    record: bool = False


class hybridmethod:
    def __init__(self, fclass, finstance=None, doc=None):
        self.fclass = fclass
        self.finstance = finstance
        self.__doc__ = doc or fclass.__doc__
        # support use on abstract base classes
        self.__isabstractmethod__ = bool(getattr(fclass, "__isabstractmethod__", False))

    def classmethod(self, fclass):
        return type(self)(fclass, self.finstance, None)

    def instancemethod(self, finstance):
        return type(self)(self.fclass, finstance, self.__doc__)

    def __get__(self, instance, cls):
        if instance is None or self.finstance is None:
            # either bound to the class, or no instance method available
            return self.fclass.__get__(cls, None)
        return self.finstance.__get__(instance, cls)


def pickle_and_base64_decode(data: Any):
    return base64.b64encode(zlib.compress(pickle.dumps(data))).decode("utf-8")


def unpack_base64_encoded_pickle(encoded_pickle: str):
    return pickle.loads(zlib.decompress(base64.b64decode(encoded_pickle)))


def datetime_to_timestamp_ms(dt: datetime.datetime):
    return int(dt.timestamp() * 1000)


def timestamp_ms_to_datetime_str(ts: int, formatter):
    return datetime.datetime.fromtimestamp(ts / 1000).strftime(formatter)


def get_file_size_mb(file_path):
    return round(os.path.getsize(file_path) / 1024 / 1024, 4)


def get_data_size_mb(data):
    # estimated raw data size before dumping to json (json slightly compress the data)
    return round(get_deep_size(data) / 1024 / 1024, 4)


def sha256_encode(data: str):
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def get_encoded_model_content(model):
    # use random index to avoid multi thread R/W locking issue
    random_end_index = str(uuid.uuid4())
    model_name = f"model_{random_end_index}.h5"
    model.save(model_name)
    f = open(f"./{model_name}", "rb")
    model_file_content = f.read()
    f.close()
    os.remove(model_name)

    return pickle_and_base64_decode(model_file_content)


def save_tensorboard_logs(
    tensorboard_logs: Optional[str],
    not_save_log: bool,
    directory_to_save_log: Optional[str],
    job_id: Optional[str],
    f_name: str = "logs",
):
    if tensorboard_logs and not not_save_log:
        try:
            log_zip = unpack_base64_encoded_pickle(tensorboard_logs)
            path = f"{directory_to_save_log}/{f_name}.zip"
            f = open(path, "wb")
            f.write(log_zip)
            f.close()
            log_dir = f"{directory_to_save_log}/logs/{job_id}/"
            shutil.unpack_archive(path, log_dir, "zip")
            os.remove(path)
            print_receiving(f"Saved tensorboard logs file to {log_dir}")
            return path
        except Exception as e:
            return f"Failed to save tensorboard logs: {e}"


def encode_data(train_X, train_Y, validation_X, validation_Y):
    encoded_train_X = pickle_and_base64_decode(train_X) if train_X is not None else None
    encoded_train_Y = pickle_and_base64_decode(train_Y) if train_Y is not None else None
    encoded_validation_X = (
        pickle_and_base64_decode(validation_X) if validation_X is not None else None
    )
    encoded_validation_Y = (
        pickle_and_base64_decode(validation_Y) if validation_Y is not None else None
    )
    return encoded_train_X, encoded_train_Y, encoded_validation_X, encoded_validation_Y


# Print iterations progress
def printProgressBar(
    iteration,
    total,
    prefix="",
    suffix="",
    decimals=1,
    length=100,
    fill="█",
    printEnd="\r",
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


class ProgressUpload:
    def __init__(
        self, filename, chunk_size=1250, filled_char=">", width=10, empty_char=" "
    ):
        self.filename = filename
        self.chunk_size = chunk_size
        self.file_size = os.path.getsize(filename)
        self.size_read = 0
        self.divisor = min(
            math.floor(math.log(self.file_size, 1024)) * 3, 9
        )  # cap unit at a GB
        self.unit_index = self.divisor
        self.unit = {0: "B", 3: "KiB", 6: "MiB", 9: "GiB"}[self.unit_index]
        self.divisor = 10 ** self.divisor
        self.width = width
        self.filled_char = filled_char
        self.empty_char = empty_char

    def __iter__(self):
        hide_cursor()
        progress_str = f"0 / {self.file_size / self.divisor:.2f} {self.unit}"
        progress_bar = self.empty_char * self.width
        progress_full = (
            f"\r[SENDING]: |{progress_bar}| 0.0% {progress_str} [avg: 0{self.unit}/s]"
        )
        sys.stderr.write(progress_full)
        time_start = time.time()

        with open(self.filename, "rb") as f:
            for chunk in iter(lambda: f.read(self.chunk_size), b""):
                self.size_read += len(chunk)
                # accumulate time
                time_spend = time.time() - time_start
                # calculate stuff for plotting progress bar
                rate = round(self.size_read / self.divisor / time_spend, 2)
                while not rate:
                    self.unit_index -= 3
                    self.unit = {0: "B", 3: "KiB", 6: "MiB", 9: "GiB"}[self.unit_index]
                    self.divisor /= 10 ** 3
                    rate = round(self.size_read / self.divisor / time_spend, 2)
                while rate > 1000:
                    self.unit_index += 3
                    self.unit = {0: "B", 3: "KiB", 6: "MiB", 9: "GiB"}[self.unit_index]
                    self.divisor *= 10 ** 3
                    rate = round(self.size_read / self.divisor / time_spend, 2)
                yield chunk
                percentage = self.size_read / self.file_size * 100
                completed_str = f"{self.size_read / self.divisor:.2f}"
                to_complete_str = f"{self.file_size / self.divisor:.2f} {self.unit}"
                n_prograss_bar = int(self.width * percentage / 100)
                progress_bar = (
                    n_prograss_bar * self.filled_char
                    + (self.width - n_prograss_bar) * self.empty_char
                )
                progress_str = f"{percentage:.2f} % {completed_str} / {to_complete_str}"
                progress_full = f"\r[SENDING]: |{progress_bar}| {progress_str} [avg: {rate}{self.unit}/s]"
                sys.stderr.write(progress_full)
        sys.stderr.write("\n")
        show_cursor()

    def __len__(self):
        return self.file_size


def zipdir(src, zip_path):
    ziph = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)
    # ziph is zipfile handle
    for root, dirs, files in os.walk(src):
        for file in files:
            ziph.write(
                os.path.join(root, file),
                os.path.relpath(os.path.join(root, file), os.path.join(src, "..")),
            )
    ziph.close()


def subprocess_to_stdout(
    cmd: List[str],
    raise_error_if_any: bool = False,
    with_stdin: bool = False,
    line_to_stop_streaming: Optional[str] = None,
    wait: bool = True,
):
    if with_stdin:
        p = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
        )
    else:
        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
    if wait:
        p = wait_subprocess_to_stdout(p, line_to_stop_streaming, raise_error_if_any)
    return p


def wait_subprocess_to_stdout(
    p: subprocess.Popen,
    line_to_stop_streaming: Optional[str] = None,
    raise_error_if_any: bool = False,
):
    done = False
    if p.stdout:
        for line in iter(p.stdout.readline, b""):
            decoded_str = line.rstrip().decode("utf8")
            print(decoded_str + "\r")
            if line_to_stop_streaming and line_to_stop_streaming in decoded_str:
                done = True
                break
        if not done and raise_error_if_any:
            _, _ = p.communicate()
            # If returncode != 0 then means the subprocess had an error
            if p.returncode != 0:
                raise InterruptedError()
    return p
