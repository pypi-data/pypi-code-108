import distutils.util
import os

from pytestapilib.core.file import FileReader
from pytestapilib.core.log import log
from pytestapilib.core.system import ProjectVariables


class MainConfig:
    YAML = FileReader(ProjectVariables.MAIN_CONFIG_YML_PATH).read_yml()


class WireMockConfig:
    log.info('Initializing wiremock configuration')

    __WIREMOCK = MainConfig.YAML['wiremock']

    ENABLED = bool(distutils.util.strtobool(os.environ['PY_TEST_API_WIREMOCK_ENABLED'])) \
        if 'PY_TEST_API_VAR_WIREMOCK_ENABLED' in os.environ else __WIREMOCK['enabled']
    HOST = __WIREMOCK['host']
    PORT = __WIREMOCK['port']
    DIR = __WIREMOCK['dir']
    JAR = __WIREMOCK['jar']
