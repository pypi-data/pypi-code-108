import pytest

from exoedge.configs import ExoEdgeConfig
from murano_client.client import MuranoClient


@pytest.fixture(params=['https', 'mqtt'])
def muranoClient(request):
    return MuranoClient(murano_host=request.param+"://dne.m2.exosite.io/",
                          watchlist=['data_out'])

@pytest.fixture(params=[True, False], ids=["ack_successful", "ack_failed"])
def exoEdgeConfig(mocker, request, muranoClient):
    # mocker comes from pytest-mock
    # request comes from params

    mocker.patch.object(muranoClient, 'ack', return_value=(
        request.param, 'result: code: 204, body: \'No content\', success: True, authorized: True'))
    ExoEdgeConfig.resource = 'config_io'
    config = ExoEdgeConfig(
        name="ConfigIO",
        device=muranoClient
    )
    return config


def test_ack_config(exoEdgeConfig):
    assert exoEdgeConfig.acktime == 0.0
    assert exoEdgeConfig.ack_config() == None
    assert not exoEdgeConfig.acktime == 0.0
