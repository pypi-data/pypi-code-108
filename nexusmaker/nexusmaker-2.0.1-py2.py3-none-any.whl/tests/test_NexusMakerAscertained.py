import pytest
from nexusmaker.tests.test_NexusMaker import TestNexusMaker


class TestNexusMakerAscertained(TestNexusMaker):
    @pytest.fixture
    def maker(self, nexusmakerasc):
        return nexusmakerasc

    # 1 more site than before in ascertainment = none
    def test_nsites(self, nexus):
        assert len(nexus.data.keys()) == 7

    def test_ascertainment_column(self, maker, nexus):
        assert maker.ASCERTAINMENT_LABEL in nexus.data
        for k in nexus.data[maker.ASCERTAINMENT_LABEL]:
            assert nexus.data[maker.ASCERTAINMENT_LABEL][k] == '0'

    def test_error_on_multiple_ascertainment_sites(self, maker, nexus):
        with pytest.raises(ValueError):
            maker._add_ascertainment(nexus)
