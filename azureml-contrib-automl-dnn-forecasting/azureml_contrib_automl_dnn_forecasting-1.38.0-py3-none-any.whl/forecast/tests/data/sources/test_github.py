import pytest

from forecast.data.sources import GithubDataSource


@pytest.mark.parametrize('horizon', [None, 15])
@pytest.mark.parametrize('split', [None, 400])
@pytest.mark.parametrize('eager', [False, True])
@pytest.mark.parametrize('window_size', [32, 124])
@pytest.mark.parametrize('one_hot,drop_first', [(True, False), (True, True), (False, None)])
def test_github_data_source(horizon, split, eager, window_size, one_hot, drop_first):
    ds = GithubDataSource(forecast_horizon=horizon, test_split=split, eager=eager)
    train, test = ds.get_dataset(window_size=window_size, one_hot=one_hot, drop_first=drop_first)
