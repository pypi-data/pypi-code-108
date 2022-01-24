import os

import pandas
import pytest
from pandas.testing import assert_index_equal

from tktl.core.clients.arrow import ArrowFlightClient
from tktl.core.config import set_api_key
from tktl.core.exceptions import TaktileSdkError


def test_instantiate_client():

    key = os.environ["TEST_USER_API_KEY"]
    set_api_key(key)

    with pytest.raises(TaktileSdkError):
        ArrowFlightClient(
            api_key=key,
            repository_name=f"{os.environ['TEST_USER']}/test-new",
            branch_name="master",
            endpoint_name="repayment",
        )
    client = ArrowFlightClient(
        api_key=key,
        repository_name=f"{os.environ['TEST_USER']}/integ-testing",
        branch_name="master",
        endpoint_name="repayment",
    )
    assert client.location is not None


def test_instantiate_by_url(sample_deployed_url):
    key = os.environ["TEST_USER_API_KEY"]
    set_api_key(key)
    client = ArrowFlightClient.for_url(
        api_key=key, url=sample_deployed_url, endpoint_name="repayment"
    )
    assert client.location == f"grpc+tls://{sample_deployed_url}:5005"


def test_predict_flow(sample_deployed_url, capsys):
    key = os.environ["TEST_USER_API_KEY"]
    set_api_key(key)
    client = ArrowFlightClient(
        api_key=key,
        repository_name="tktl-admin/grpc-test",
        endpoint_name="repayment_input_idx",
        branch_name="main",
    )
    x, y = client.get_sample_data()
    small = x.head()
    assert isinstance(x, pandas.DataFrame)
    predictions = client.predict(small.head(10))
    assert isinstance(predictions, pandas.Series)

    small.index = pandas.Series(["A"] * len(small))
    predictions = client.predict(small, use_input_index=True)
    assert_index_equal(predictions.index, small.index)

    client = ArrowFlightClient(
        api_key=key,
        repository_name="tktl-admin/grpc-test",
        endpoint_name="repayment",
        branch_name="main",
    )
    client.predict(small.head(10), use_input_index=True)
    out, err = capsys.readouterr()
    assert (
        "Inputs or Outputs are not of type series or dataframe, use_input_index has no effect\n"
        in out
    )
