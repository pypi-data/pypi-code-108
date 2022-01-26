from atqo.resource_handling import Capability, NumStore


def test_num_store():

    d1 = {"A": 10}
    ns1 = NumStore(d1)
    ns2 = ns1 + NumStore({"A": 5})
    assert ns2 == NumStore({"A": 15})
    assert ns1 == (ns2 - NumStore({"A": 5}))
    assert ns1.__repr__() == d1.__repr__()
    assert ns2 > ns1 and ns2 >= ns1 and ns1 < ns2

    assert ns1.min_value == 10
    {ns1: "works in dict"}
    set([ns1, ns2])


def test_caps():
    c1 = Capability({"A": 1}, "nx")
    assert "nx" in c1.__repr__()
    assert c1 == c1
    assert c1 != Capability({"A": 1})
