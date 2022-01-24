from dynamo_io.mock import _expressions


def test_parse_set():
    """Should extract the expected clause for the scenario."""
    sets = _expressions.parse_sets(
        "SET #k1 =  :v1, #k2=:v2, #k3 = if_not_exists (#k3, :v3 )"
    )
    assert len(sets) == 3
    assert sets[0] == _expressions.Update("SET", "#k1", ":v1", "assign")
    assert sets[1] == _expressions.Update("SET", "#k2", ":v2", "assign")
    assert sets[2] == _expressions.Update(
        action="SET",
        name_key="#k3",
        value_key=":v3",
        function="if_not_exists",
        secondary_value_key="#k3",
    )
