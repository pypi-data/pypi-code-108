import os

if True:
    for env_variable in [
        "LOG_LEVEL",
        "MODEL_MANAGER_GRANT_TYPE",
        "MODEL_MANAGER_CLIENT_ID",
        "MODEL_MANAGER_CLIENT_SECRET",
        "MODEL_MANAGER_SCOPE",
        "MODEL_MANAGER_CONTAINER",
        "MODEL_MANAGER_LOGIN_URL",
        "MODEL_MANAGER_GET_FILES_URL",
        "MODEL_MANAGER_DOWNLOAD_FILE_URL",
        "STS_APPLICATION_DEFAULT_TENANT_NAME"
    ]:
        variable = os.environ.get(env_variable, None)
        if (variable is None) or (not variable):
            raise KeyError(f"Environment variable {env_variable} missing.")

import logging
import logging.config

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'logging/logging.conf')
logging.config.fileConfig(filename, disable_existing_loggers=False)
numba_logger = logging.getLogger('numba')
numba_logger.setLevel(logging.WARNING)
urllib_logger = logging.getLogger('urllib3')
urllib_logger.setLevel(logging.WARNING)

from PIModelManager.model_manager import ModelManager
