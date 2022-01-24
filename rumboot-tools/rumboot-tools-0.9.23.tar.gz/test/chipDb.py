from rumboot.chipDb import ChipDb


def test_chipdb():
    db = ChipDb("rumboot.chips")
    c = db["basis"]
    assert c.chip_id == 3
    assert c.chip_rev == 1
