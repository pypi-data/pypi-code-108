def test_link(model):
    """Test that the link command parses correctly."""
    model.parse(
        """
        laser l1
        mirror m1
        mirror m2
        link(l1, m1, m2)
        """
    )

    assert model.path(model.l1.p1.o, model.m2.p1.i)
