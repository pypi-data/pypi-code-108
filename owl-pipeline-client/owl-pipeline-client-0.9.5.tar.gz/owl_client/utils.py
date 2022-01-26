import logging
import os
import re
import socket
import sys
import traceback
from contextlib import closing, suppress
from functools import wraps
from pathlib import Path
from typing import IO, Any, Callable, Dict, Union

import pkg_resources
import requests
import voluptuous as vo
import yaml
from distributed import Client, WorkerPlugin
from loky import ProcessPoolExecutor

log = logging.getLogger("owl.cli")

_path_matcher = re.compile(r"(\S+)?(\$\{([^}^{]+)\})")


def _path_constructor(loader, node):
    """Extract the matched value, expand env variable, and replace the match."""
    value = node.value
    match = _path_matcher.match(value)
    env_var = match.groups()[2]
    return value.replace(match.groups()[1], os.environ.get(env_var, ""))


yaml.add_implicit_resolver("!path", _path_matcher, None, yaml.SafeLoader)
yaml.add_constructor("!path", _path_constructor, yaml.SafeLoader)


def print_table(data, pad=2, header=True):
    col_length = []
    for d in data:
        this_l = [*map(len, map(str, d))]
        col_length.append(this_l)
    col_l = [*map(max, zip(*col_length))]
    fmt = " ".join("{:" + f"{l+pad}" + "s}" for l in col_l)
    for i, d in enumerate(data):
        if header and (i == 1):
            print(fmt.format(*["-" * (l + pad) for l in col_l]))
        print(fmt.format(*map(str, d)))


def read_config(
    config: Union[str, IO[str]], validate: Callable = None
) -> Dict[str, Any]:
    """Read configuration file.

    Parameters
    ----------
    config
        input configuration
    validate
        validation schema

    Returns
    -------
    parsed configuration
    """
    try:
        conf = yaml.safe_load(config)
    except:  # noqa
        log.critical("Unable to read configuration file.")
        raise
    if validate:
        conf = validate(conf)
    return conf


def get_auth():
    owlrc = Path("~/.owlrc").expanduser()
    if not owlrc.exists():
        raise SystemExit(
            'Cannot find authentication token. Please login first  "owl auth login"'
        )

    with owlrc.open(mode="r") as fd:
        auth = yaml.safe_load(fd.read())
        username, token = auth["username"], auth["token"]
        headers = {"Authentication": "{} {}".format(username, token)}

    return headers


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        for n in range(6006, 7006, 10):
            with suppress(OSError):
                s.bind(("", n))
                break
        return n


def get_pipeline(name: str) -> Callable:
    for e in pkg_resources.iter_entry_points("owl.pipelines"):
        if e.name == name:
            f = e.load()
            s = f.schema
            s.extra = vo.REMOVE_EXTRA
            res = register_pipeline(validate=s)(f)
            break
    try:
        return res
    except NameError:
        raise Exception("Pipeline %s not found", name)


def make_request(api, route, method, data=None, auth=False):
    headers = get_auth() if auth else None
    res = {}
    try:
        if method == "GET":
            r = requests.get(f"{api}{route}", json=data or {}, headers=headers)
            res = r.json()
        elif method == "POST":
            r = requests.post(f"{api}{route}", json=data or {}, headers=headers)
            res = r.json()
    except (requests.RequestException, ConnectionError):
        print("ERROR: Failed to connect to the API at {}".format(api))
        return {}

    if not res:
        raise SystemExit("Not found")

    if "detail" in res:
        raise SystemExit(res["detail"])

    return res


class LoggingPlugin(WorkerPlugin):
    def __init__(self, config):
        self.config = config

    def setup(self, worker):
        import logging.config

        logging.config.dictConfig(self.config)


class ProcessPoolPlugin(WorkerPlugin):
    def setup(self, worker):
        if hasattr(worker, "executors"):
            executor = ProcessPoolExecutor(max_workers=worker.nthreads)
            worker.executors["processes"] = executor


class register_pipeline:
    """Register a pipeline."""

    def __init__(self, *, validate: vo.Schema = None):
        self.schema = validate
        if self.schema is not None:
            self.schema.extra = vo.REMOVE_EXTRA

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(config: Dict, logconfig: Dict, cluster=None):

            _config = self.schema(config) if self.schema is not None else config
            if cluster is not None:
                try:
                    client = Client(cluster.scheduler_address)
                except Exception:
                    traceback_str = traceback.format_exc()
                    raise Exception(
                        "Error occurred. Original traceback " "is\n%s\n" % traceback_str
                    )
                client.register_worker_plugin(LoggingPlugin(logconfig))
                client.register_worker_plugin(ProcessPoolPlugin)
            else:
                client = None
            try:
                func.main.config = config  # type: ignore
                return func.main(**_config)  # type: ignore
            except Exception:
                traceback_str = traceback.format_exc()
                raise Exception(
                    "Error occurred. Original traceback " "is\n%s\n" % traceback_str
                )
            finally:
                if client is not None:
                    client.close()

        return wrapper
