import click
import inspect

from functools import wraps
from cnvrgv2 import Cnvrg
from cnvrgv2.cli.logger.logger import CnvrgLogger
from cnvrgv2.cli.utils import messages
from cnvrgv2.cli.utils.validators import verify_login
from cnvrgv2.config import error_messages
from cnvrgv2.config import Config


def prepare_command():
    """
    This decorator logs a start log for a cli command, can validate if the user is logged in, and injects
    the cnvrg object and logger object to the cli command function, if the arguments are expected by the function
    @return: the decorator function
    """
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            verify_login()
            cnvrg = Cnvrg()
            config = Config()
            logger = CnvrgLogger(click)
            command_name = func.__name__

            log_message = messages.LOG_START_COMMAND.format(command_name, str(kwargs))
            logger.info(log_message)

            func_args = inspect.getfullargspec(func).args
            inject_args = dict()

            if "cnvrg" in func_args:
                inject_args["cnvrg"] = cnvrg
            if "logger" in func_args:
                inject_args["logger"] = logger
            if "project" in func_args:
                project_slug = config.data_owner_slug
                if not project_slug:
                    logger.log_and_echo(error_messages.LOCAL_CONFIG_MISSING_DATA_OWNER_SLUG, error=True)
                inject_args["project"] = cnvrg.projects.get(project_slug)
            if "dataset" in func_args:
                dataset_slug = config.data_owner_slug
                if not dataset_slug:
                    logger.log_and_echo(error_messages.LOCAL_CONFIG_MISSING_DATA_OWNER_SLUG, error=True)
                inject_args["dataset"] = cnvrg.datasets.get(dataset_slug)

            n_kwargs = {**kwargs, **inject_args}
            func(*args, **n_kwargs)

        return inner
    return decorator
