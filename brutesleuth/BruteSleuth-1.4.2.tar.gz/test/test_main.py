import pytest
import brutesleuth


# Testing functions of Base chain chains
@pytest.mark.parametrize(("length", "base", "expected_results"), [
    (4, 2, [7]),
    (3, 8, [16]),
    (2, 16, [226]),
])
def test_basechain(length, base, expected_results):
    chain = brutesleuth.BaseChain(base, length)
    # testing length
    assert len(chain) == base ** length
    # testing setting a value
    chain.setIndex(expected_results[0])
    assert chain.__next__() == expected_results[0]
    # testing that every iteration is correct
    chain.setIndex(0)
    for result, expected in zip(chain, range(base ** length)):
        assert result == expected
