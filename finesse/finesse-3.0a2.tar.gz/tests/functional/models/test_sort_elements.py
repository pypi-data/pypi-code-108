from finesse.components import Mirror, Beamsplitter


def test_sort(model):
    model.add(Mirror("m1"))
    model.add(Beamsplitter("bs1"))
    # Current order should be insertion order.
    # NOTE: fsig is always present and always the first element by default.
    assert list(model.elements) == ["fsig", "m1", "bs1"]

    # Sort alphabetically. Note the first object in the tuple is the name.
    model.sort_elements(key=lambda item: item[0])
    assert list(model.elements) == ["bs1", "fsig", "m1"]

    # Add a beamsplitter.
    model.add(Beamsplitter("bs2"))
    assert list(model.elements) == ["bs1", "fsig", "m1", "bs2"]

    # Sort alphabetically again.
    model.sort_elements(key=lambda item: item[0])
    assert list(model.elements) == ["bs1", "bs2", "fsig", "m1"]
