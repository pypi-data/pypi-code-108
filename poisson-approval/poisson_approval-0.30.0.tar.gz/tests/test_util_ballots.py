import pytest
from poisson_approval import allowed_ballots


def test_allowed_ballots():
    with pytest.raises(NotImplementedError):
        allowed_ballots(voting_rule='Non implemented voting rule')
