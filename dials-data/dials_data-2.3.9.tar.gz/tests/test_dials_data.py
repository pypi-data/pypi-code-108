from __future__ import annotations

import pathlib
from unittest import mock

import py
import pytest

import dials_data
import dials_data.datasets
import dials_data.download


def test_all_datasets_can_be_parsed():
    assert dials_data.datasets.definition


def test_repository_location():
    rl = dials_data.datasets.repository_location()
    assert rl.is_dir()


def test_fetching_undefined_datasets_does_not_crash():
    df = dials_data.download.DataFetcher(read_only=True)
    assert df("aardvark", pathlib=True) is False


def test_requests_for_future_datasets_can_be_intercepted():
    df = dials_data.download.DataFetcher(read_only=True)
    df.result_filter = mock.Mock()
    df.result_filter.return_value = False
    assert df("aardvark", pathlib=True) is False
    df.result_filter.assert_called_once_with(result=False)


@mock.patch("dials_data.datasets.repository_location")
@mock.patch("dials_data.download.fetch_dataset")
def test_datafetcher_constructs_py_path(fetcher, root):
    root.return_value = pathlib.Path("/tmp/root")
    fetcher.return_value = True

    df = dials_data.download.DataFetcher(read_only=True)
    with pytest.warns(DeprecationWarning):
        ds = df("dataset")
    assert pathlib.Path(ds).resolve() == pathlib.Path("/tmp/root/dataset").resolve()
    assert isinstance(ds, py.path.local)
    fetcher.assert_called_once_with(
        "dataset", pre_scan=True, read_only=False, download_lockdir=mock.ANY
    )

    ds = df("dataset", pathlib=False)
    assert pathlib.Path(ds).resolve() == pathlib.Path("/tmp/root/dataset").resolve()
    assert isinstance(ds, py.path.local)
    fetcher.assert_called_once()


@mock.patch("dials_data.datasets.repository_location")
@mock.patch("dials_data.download.fetch_dataset")
def test_datafetcher_constructs_path(fetcher, root):
    test_path = pathlib.Path("/tmp/root")
    root.return_value = test_path
    fetcher.return_value = True

    df = dials_data.download.DataFetcher(read_only=True)
    ds = df("dataset", pathlib=True)
    assert ds == test_path / "dataset"

    assert isinstance(ds, pathlib.Path)
    fetcher.assert_called_once_with(
        "dataset", pre_scan=True, read_only=False, download_lockdir=mock.ANY
    )

    with pytest.warns(DeprecationWarning):
        ds = df("dataset")
    assert pathlib.Path(ds).resolve() == test_path.joinpath("dataset").resolve()
    assert not isinstance(
        ds, pathlib.Path
    )  # default is currently to return py.path.local()
    fetcher.assert_called_once_with(
        "dataset", pre_scan=True, read_only=False, download_lockdir=mock.ANY
    )
