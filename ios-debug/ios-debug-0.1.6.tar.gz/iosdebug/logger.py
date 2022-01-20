import logging
import os

LOG_FILE_NAME = "ios-debug.log"

instance = logging.getLogger(__name__)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(LOG_FILE_NAME)
c_handler.setLevel(logging.WARNING)
f_handler.setLevel(logging.WARNING)

# Create formatters and add it to handlers
c_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
instance.addHandler(c_handler)
instance.addHandler(f_handler)


def delete_old_log_file():
    os.remove(LOG_FILE_NAME)
