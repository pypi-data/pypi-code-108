import pathlib

import numpy as np
from shapeout2 import pipeline


def test_get_heredity():
    path = pathlib.Path(__file__).parent / "data" / "calibration_beads_47.rtdc"

    # initialize
    slot = pipeline.Dataslot(path)
    ds = slot.get_dataset()
    ray = pipeline.FilterRay(slot)

    # come up with a few filters
    # this does some simple things
    filt1 = pipeline.Filter()
    filt1.boxdict["area_um"] = {"start": ds["area_um"].min(),
                                "end": np.mean(ds["area_um"]),
                                "active": True}
    # this one does nothing (and should be ignored)
    filt2 = pipeline.Filter()
    filt2.filter_used = False
    # another one with simple things
    filt3 = pipeline.Filter()
    filt3.boxdict["deform"] = {"start": ds["deform"].min(),
                               "end": np.mean(ds["deform"]),
                               "active": True}

    # simple
    ds1 = ray.get_dataset(filters=[filt1, filt2], apply_filter=True)
    assert ray._generation == 0

    # leaving out a filter that does nothing will not change anything
    ds2 = ray.get_dataset(filters=[filt1], apply_filter=True)
    assert ray._generation == 0
    assert ds1 is ds2

    # changing the order will not change anything either
    ds3 = ray.get_dataset(filters=[filt2, filt1], apply_filter=True)
    assert ray._generation == 0
    assert ds1 is ds3

    # adding a new filter will change the dataset
    ds4 = ray.get_dataset(filters=[filt1, filt2, filt3], apply_filter=True)
    assert ray._generation == 0
    assert ds1 is not ds4
    assert ds1 is ds4.hparent

    # going back does not increment the generation...
    ds5 = ray.get_dataset(filters=[filt1, filt2], apply_filter=True)
    assert ray._generation == 0
    assert ds1 is ds5

    # ...but changing the order is
    ds5 = ray.get_dataset(filters=[filt3, filt1, filt2], apply_filter=True)
    assert ray._generation == 1
    assert ds1 is not ds5
    assert ds3 is not ds5

    # and then again, when we remove a filter, we get something different
    ds6 = ray.get_dataset(filters=[filt3, filt1], apply_filter=True)
    assert ray._generation == 1
    assert ds1 is not ds6
    assert ds5 is ds6  # b/c filt2 does nothing


def test_filtering():
    path = pathlib.Path(__file__).parent / "data" / "calibration_beads_47.rtdc"

    # initialize
    slot = pipeline.Dataslot(path)
    ds = slot.get_dataset()
    ray = pipeline.FilterRay(slot)

    # come up with a few filters
    # this does some simple things
    filt1 = pipeline.Filter()
    filt1.boxdict["area_um"] = {"start": ds["area_um"].min(),
                                "end": np.mean(ds["area_um"]),
                                "active": True}
    # this one does nothing (and should be ignored)
    filt2 = pipeline.Filter()
    filt2.filter_used = False
    # another one with simple things
    filt3 = pipeline.Filter()
    filt3.boxdict["deform"] = {"start": ds["deform"].min(),
                               "end": np.mean(ds["deform"]),
                               "active": True}

    ds2 = ray.get_dataset(filters=[filt2, filt1], apply_filter=True)
    assert len(ds2) == 47
    ds3 = ray.get_dataset(filters=[filt1, filt3], apply_filter=True)
    assert len(ds3) == 22
    assert np.sum(ds2.filter.all) == 22
    assert np.sum(ds3.filter.all) == 12
    ds1 = ray.get_dataset(filters=[filt2], apply_filter=True)
    assert np.sum(ds1.filter.all) == len(ds)
    ds4 = ray.get_dataset(filters=[filt1, filt2], apply_filter=True)
    assert len(ds4) == 47


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
