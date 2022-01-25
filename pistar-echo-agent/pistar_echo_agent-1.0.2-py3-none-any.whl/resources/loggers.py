from pathlib import Path
from pistar_echo_agent.utilities.logger import Logger
from pistar_echo_agent.utilities.constants import LOGGING_LEVEL
from pistar_echo_agent.utilities.constants import LOG_PATH

# this is factory server logger.
server_logger = Logger(
    name="pistar_echo_agent",
    level=getattr(LOGGING_LEVEL, "DEBUG"),
    logger_format="[%(asctime)s] [%(levelname)s] [%(pathname)s:%(lineno)d] %(message)s",
    output_path=str(Path.cwd().joinpath(LOG_PATH.ECHO_AGENT))
)
