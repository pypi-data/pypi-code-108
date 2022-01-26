import os
from pathlib import Path


class ProjectVariables:
    PROJECT_ROOT_DIR = os.path.dirname(Path(os.path.abspath(__file__)).parent.parent)

    ENVIRONMENT = os.environ['PY_TEST_API_ENVIRONMENT'] \
        if 'PY_TEST_API_ENVIRONMENT' in os.environ else 'local'

    MAIN_CONFIG_YML_PATH = f'/data/config/{ENVIRONMENT}/main-config.yaml'
