import subprocess
import logging

_logger = logging.getLogger(__name__)


def check_n_gpu():
    try:
        from pycuda import driver

        driver.init()
        n_gpus = driver.Device.count()
    except Exception as e:
        raise e
    else:
        if n_gpus == 0:
            raise RuntimeError("No gpu detected to run nabu reconstruction")
        else:
            _logger.info(f"{n_gpus} detected by pycuda")


def _exec_nabu_on_slurm(conf_file: str, scan_path: str) -> tuple:
    check_n_gpu()

    NABU_FULL_FIELD_APP_PATH = "nabu.app.reconstruct"
    # need to be executed in his own context
    command = " ".join(("python", "-m", NABU_FULL_FIELD_APP_PATH, conf_file))
    process = subprocess.Popen(
        command,
        shell=True,
        cwd=scan_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    res = process.communicate()
    return res
