from shapeout2 import util


def test_get_valid_filename():
    assert util.get_valid_filename("KLµ123$)]") == "KLu123?))"
    assert util.get_valid_filename("..KLµ123$)].") == "KLu123?))"
    assert util.get_valid_filename(". KLµ123$)]") == "_KLu123?))"


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
