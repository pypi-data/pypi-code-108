from wiremock.server import WireMockServer

from pytestapilib.core.config import WireMockConfig
from pytestapilib.core.log import log
from pytestapilib.core.system import ProjectVariables


class WireMockInstance:
    @classmethod
    def start_wiremock(cls):
        wiremock_root_dir = ProjectVariables.PROJECT_ROOT_DIR + WireMockConfig.DIR
        wiremock_jar = wiremock_root_dir + "\\" + WireMockConfig.JAR
        wiremock_server = WireMockServer(port=WireMockConfig.PORT, root_dir=wiremock_root_dir, jar_path=wiremock_jar)
        log.info('Is WireMock server running: {%d}', str(wiremock_server.is_running))
        wiremock_server.start()
        log.info('Is WireMock server running: {%d}', str(wiremock_server.is_running))
