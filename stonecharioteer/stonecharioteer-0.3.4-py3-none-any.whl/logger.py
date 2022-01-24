import logging
import logging.handlers
import pathlib

logger = logging.getLogger("stonecharioteer")


def configure_logger():
    logfile = pathlib.Path.home() / pathlib.Path(".logs/stonecharioteer.log")
    logfile.parent.mkdir(parents=True, exist_ok=True)
    # TODO: Read config and set the log level.
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    file_handler = logging.handlers.RotatingFileHandler(
        filename=logfile.absolute(), maxBytes=1024 * 1024
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.debug("Configured the logger")
