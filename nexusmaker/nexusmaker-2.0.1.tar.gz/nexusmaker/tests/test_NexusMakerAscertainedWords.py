import pytest
from nexusmaker.tests.test_NexusMaker import TestNexusMaker


class TestNexusMakerAscertainedParameters(TestNexusMaker):
    @pytest.fixture
    def maker(self, nexusmakerascparameters):
        return nexusmakerascparameters

    def test_nsites(self, nexus):
        # 1 more site per word than in ascertainment is none:
        #   6 cognates + 3 words = 9
        assert len(nexus.data.keys()) == 9

    def test_get_characters_simple(self, maker, nexus):
        chars = maker._get_characters(nexus)
        # NOTE characters are zero indexed
        assert chars['arm'] == [0, 1, 2, 3]
        assert chars['eye'] == [4, 5]
        assert chars['leg'] == [6, 7, 8]

    def test_get_characters_error(self, maker, nexus):
        with pytest.raises(ValueError):
            maker._get_characters(nexus, delimiter="X")

    def test_create_assumptions_simple(self, maker, nexus):
        assumpt = maker.create_assumptions(nexus)
        assert 'begin assumptions' in assumpt[0]
        assert 'arm = 1-4' in assumpt[1]
        assert 'eye = 5-6' in assumpt[2]
        assert 'leg = 7-9' in assumpt[3]
        assert 'end;' in assumpt[4]

    def test_eye_0(self, maker, nexus):
        cog = 'eye_%s' % maker.ASCERTAINMENT_LABEL
        assert nexus.data[cog]['A'] == '0'
        assert nexus.data[cog]['B'] == '0'
        assert nexus.data[cog]['C'] == '0'
        assert nexus.data[cog]['D'] == '?'

    def test_leg_0(self, maker, nexus):
        cog = 'leg_%s' % maker.ASCERTAINMENT_LABEL
        assert nexus.data[cog]['A'] == '0'
        assert nexus.data[cog]['B'] == '0'
        assert nexus.data[cog]['C'] == '?'
        assert nexus.data[cog]['D'] == '0'

    def test_arm_0(self, maker, nexus):
        cog = 'arm_%s' % maker.ASCERTAINMENT_LABEL
        assert nexus.data[cog]['A'] == '0'
        assert nexus.data[cog]['B'] == '0'
        assert nexus.data[cog]['C'] == '0'
        assert nexus.data[cog]['D'] == '0'

    def test_write_extra(self, maker):
        out = maker.write()
        assert 'begin assumptions;' in out
        assert 'charset arm' in out
        assert 'charset eye' in out
        assert 'charset leg' in out

    def test_is_sequential(self, maker):
        assert maker._is_sequential([1, 2, 3, 4, 5])
        assert maker._is_sequential([3, 4, 5, 6, 7])
        assert not maker._is_sequential([1, 3])
        assert not maker._is_sequential([9, 2])
