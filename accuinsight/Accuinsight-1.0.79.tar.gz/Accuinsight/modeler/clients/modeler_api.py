"""
This http client send run's results data to modeler back-end server
"""

from Accuinsight.modeler.store.tracking.life_cycle_store import RestStore as LcRestStore
from Accuinsight.modeler.store.tracking.monitoring_deploy_store import RestStore as MonitoringDeployRestStore
from Accuinsight.modeler.store.tracking.workspace_store import RestStore as WorkspaceRestStore
from Accuinsight.modeler.utils.rest_utils import ModelerHostCreds
from Accuinsight.modeler.utils.os_getenv import get_os_env
from Accuinsight.modeler.core.LcConst import LcConst

_DEFAULT_USER_ID = "unknown"


class LifecycleRestApi:
    def __init__(self, host_url, port, uri):
        self.base_url = 'http://' + host_url + ':' + str(port) + '/' + uri

    def lc_create_run(self, current_run_meta):
        """Create run."""

        store = LcRestStore(lambda: ModelerHostCreds(self.base_url))
        run = store.lc_create_run(current_run_meta)
        return run


class DeployLogRestApi:
    def __init__(self, host_url, port, uri):
        self.base_url = 'http://' + host_url + ':' + str(port) + '/' + uri

    def call_rest_api(self, method, param, mode="logging"):
        store = MonitoringDeployRestStore(ModelerHostCreds(self.base_url))
        response = store.call_endpoint(method, param, mode)

        return response


class WorkspaceRestApi:
    def __init__(self, host_url, port, uri):
        self.base_url = 'http://' + host_url + ':' + str(port) + '/' + uri

    def call_rest_api(self, param, mode):
        store = WorkspaceRestStore(ModelerHostCreds(self.base_url))
        response = store.call_endpoint(param, mode)

        return response


if __name__ == "__main__":
    env_value = get_os_env('ENV')
    modeler_rest = LifecycleRestApi(env_value[LcConst.BACK_END_API_URL],
                                    env_value[LcConst.BACK_END_API_PORT],
                                    env_value[LcConst.BACK_END_API_URI])

    modeler_rest.lc_create_run()
