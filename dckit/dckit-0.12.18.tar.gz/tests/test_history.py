"""Test hdf5 logs history"""
import dclab

from dckit import history

from helper_methods import retrieve_data


def test_append_history():
    h5path = retrieve_data("rtdc_data_hdf5_rtfdc.zip")

    newlog = {"peter": "hans",
              "golem": 2}
    history.append_history(h5path, hdict=newlog)

    hlist = history.read_history(h5path)
    assert hlist[0] == newlog

    with dclab.new_dataset(h5path) as ds:
        assert "dckit-history" in ds.logs


def test_multiple():
    h5path = retrieve_data("rtdc_data_hdf5_rtfdc.zip")

    newlog = {"peter": "hans",
              "golem": 2}
    history.append_history(h5path, hdict=newlog)

    newlog2 = {"peter2": "hans",
               "golem": 4}
    history.append_history(h5path, hdict=newlog2)

    hlist = history.read_history(h5path)
    assert hlist[0] == newlog
    assert hlist[1] == newlog2


def test_unicode():
    h5path = retrieve_data("rtdc_data_hdf5_rtfdc.zip")

    newlog = {"peter": "häns",
              "golem": 2}
    history.append_history(h5path, hdict=newlog)

    hlist = history.read_history(h5path)
    assert hlist[0] == newlog

    with dclab.new_dataset(h5path) as ds:
        assert "dckit-history" in ds.logs


if __name__ == "__main__":
    # Run all tests
    _loc = locals()
    for _key in sorted(list(_loc.keys())):
        if _key.startswith("test_") and hasattr(_loc[_key], "__call__"):
            _loc[_key]()
