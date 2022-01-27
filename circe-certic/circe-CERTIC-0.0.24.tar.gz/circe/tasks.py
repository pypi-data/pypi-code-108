from circe.config import CONFIG
from huey import SqliteHuey
from shutil import move, rmtree
import tempfile
import tarfile
from os import remove
from uuid import uuid4
import json
import requests
from requests.exceptions import ConnectionError, HTTPError
import logging
from inspect import getmembers, isfunction, isclass, signature
import sys
import os
from pythonjsonlogger import jsonlogger
import datetime


sys.path.insert(0, os.getcwd())


def _stamp():
    return datetime.datetime.now()


registered_transfos = {}


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            # this doesn't use record.created, so it is slightly off
            now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname


if CONFIG["CIRCE_TRANSFORMATIONS_MODULE"]:
    transformations_module = __import__(CONFIG["CIRCE_TRANSFORMATIONS_MODULE"])
    for transformation_name, _ in getmembers(transformations_module):
        if isfunction(getattr(transformations_module, transformation_name)) or isclass(
            getattr(transformations_module, transformation_name)
        ):
            try:
                sign = signature(getattr(transformations_module, transformation_name))
            except ValueError:
                continue
            params = []
            for param in sign.parameters:
                params.append(param)
            if not len(params):
                continue
            if (
                params[0] == "working_dir"
                and params[1] == "logger"
                and params[2] == "options"
            ):
                registered_transfos[transformation_name] = getattr(
                    transformations_module, transformation_name
                )

if not registered_transfos:
    sys.exit(
        "No transformations available. Have you set CIRCE_TRANSFORMATIONS_MODULE ?"
    )


def get_transformations_descriptions():
    descriptions = {}
    for key in registered_transfos.keys():
        descriptions[key] = (
            registered_transfos[key].description
            if hasattr(registered_transfos[key], "description")
            else {"label": key, "help": key, "options": []}
        )
    return descriptions


huey = SqliteHuey(
    filename="{}huey.db".format(CONFIG["CIRCE_WORKING_DIR"]),
    immediate=CONFIG["CIRCE_IMMEDIATE_MODE"],
)


@huey.task()
def remove_tree(tree_path):
    rmtree(tree_path, ignore_errors=True)


@huey.task()
def remove_file(file_path):
    try:
        remove(file_path)
    except FileNotFoundError:
        pass


@huey.task()
def do_transformations(uuid: uuid4, job_archive_path: str):
    with tempfile.TemporaryDirectory() as tmp_dir:

        handler: logging.FileHandler = logging.FileHandler("{}/out.log".format(tmp_dir))
        handler.setFormatter(
            CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
        )
        logger: logging.Logger = logging.Logger("job_logger_{}".format(uuid.hex))
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        with tarfile.open(job_archive_path) as source_archive:
            source_archive.extractall(tmp_dir)
            with open("{}/job.json".format(tmp_dir)) as job_description_fp:
                job_description = json.load(job_description_fp)
                for transfo_description in job_description.get("transformations", []):
                    if (
                        transfo_description.get("name", None)
                        in registered_transfos.keys()
                    ):
                        logger.info(
                            {
                                "message": "Executing transformation {}".format(
                                    transfo_description["name"]
                                ),
                                "time": _stamp(),
                            }
                        )
                        registered_transfos[transfo_description["name"]](
                            tmp_dir, logger, transfo_description.get("options", None)
                        )
                    else:
                        logger.warning(
                            {
                                "message": "No such transformation: {}".format(
                                    transfo_description.get("name", None)
                                ),
                                "time": _stamp(),
                            }
                        )
                _, temp_zip_path = tempfile.mkstemp(suffix=".tar.gz")
                with tarfile.open(temp_zip_path, "w:gz") as destination_archive:
                    destination_archive.add(tmp_dir, recursive=True, arcname="")
                final_archive_path = "{}/done/{}.tar.gz".format(
                    CONFIG["CIRCE_WORKING_DIR"], uuid.hex
                )
                move(temp_zip_path, final_archive_path)
                remove_file.schedule((final_archive_path,), delay=3600)
                if job_description.get("notify_hook", None):
                    try:
                        requests.post(  # request is blocking, maybe try xhttp once stable ?
                            job_description.get("notify_hook"),
                            data={"uuid": uuid.hex},
                            timeout=1,
                        )
                    except (ConnectionError, HTTPError):
                        pass  # tant pis pour toi
            remove(job_archive_path)
