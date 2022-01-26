import dask

from .utils import experimental


@experimental
def register_analytics():
    """
    Register Coiled analytics with your Dask cluster.

    This will configure preload scripts for Dask schedulers which feed analytics
    data into Coiled. You can activate it by doing

        from coiled.analytics import register_analytics
        from distributed import Client

        register_analytics()
        client = Client()
    """

    COILED_SERVER_URL = dask.config.get("coiled.server", None)
    COILED_TOKEN = dask.config.get("coiled.token", None)
    if not COILED_SERVER_URL or not COILED_TOKEN:
        raise RuntimeError("You do not seem to be logged into Coiled")

    preload_url = COILED_SERVER_URL + "/preloads/insights.py"

    preloads = dask.config.get("distributed.scheduler.preload", None) or []
    dask.config.set({"distributed.scheduler.preload": preloads + [preload_url]})
