import pytest
from src.endpoints import client
from taktile_types.enums.endpoint import EndpointKinds


@pytest.mark.parametrize(
    "endpoint",
    [
        endpoint
        for endpoint in client.endpoints
        if endpoint.kind in [EndpointKinds.ARROW, EndpointKinds.PROFILED]
    ],
)
def test_endpoints(json_metadata, endpoint):
    """test_endpoints.
    This test ensures the provided sample data on endpoints can be correctly
    processed by the endpoints.

    It is recommended to keep these tests around.
    """

    json_metadata["section"] = "Taktile Automatic Endpoint Tests"
    json_metadata["pass_message"] = f"Sample data for {endpoint.name} is valid"
    json_metadata["fail_message"] = f"Sample data for {endpoint.name} is invalid"

    endpoint.func(endpoint.X)
