import dask
import distributed
import pytest
from coiled.analytics import register_analytics


@pytest.fixture
def analytics():
    dask.config.set({"distributed.scheduler.preload": []})
    register_analytics()
    yield
    # Cleanup
    dask.config.set({"distributed.scheduler.preload": []})


@pytest.mark.asyncio
async def test_register_analytics_with_non_coiled_cluster(
    sample_user, remote_access_url, analytics
):
    async with distributed.LocalCluster() as cluster:
        assert len(cluster.scheduler.preloads) == 1

        # Dask compat, different versions have this as a list or dict
        if isinstance(cluster.scheduler.plugins, list):
            plugins = cluster.scheduler.plugins
        else:
            plugins = list(cluster.scheduler.plugins.values())

        assert any([remote_access_url in str(p) for p in plugins])
