import pytest
from nexusmaker import Record
from nexusmaker import NexusMaker


def test_nexusmaker_input():
    with pytest.raises(ValueError):
        NexusMaker(['1'])

    # no language
    with pytest.raises(ValueError):
        NexusMaker([
            Record(Parameter="leg", Item="", Cognacy="2")
        ])

    # no parameter
    with pytest.raises(ValueError):
        NexusMaker([
            Record(Language="French", Item="", Cognacy="2")
        ])


def test_error_on_cognates_with_loans(testdata):
    """Test that we generate an error if a loan enters .cognates()"""
    n = NexusMaker(testdata)
    n.data.append(Record(Language="D", Parameter="eye", Item="", Cognacy="1", Loan=True))
    with pytest.raises(ValueError):
        n.cognates


def test_error_on_make_with_uniques_bigger_than_one(testdata):
    """
    Test that we generate an error in .make if a unique cognate set contains
    more than one language.
    """
    n = NexusMaker(testdata)
    n.cognates
    n._cognates[('test', 'u_1')] = ["A", "B"]
    with pytest.raises(AssertionError):
        n.make()


class TestNexusMaker:
    @pytest.fixture
    def maker(self, nexusmaker):
        return nexusmaker

    @pytest.fixture
    def nexus(self, maker):
        return maker.make()

    def test_languages(self, maker):
        assert maker.languages == {'A', 'B', 'C', 'D'}

    def test_parameters(self, maker):
        assert maker.parameters == {'eye', 'leg', 'arm'}

    def test_nsites(self, nexus):
        assert len(nexus.data.keys()) == 6

    def test_cognate_sets(self, maker):
        assert ('eye', '1') in maker.cognates
        assert ('leg', '1') in maker.cognates
        assert ('leg', '2') in maker.cognates
        assert ('arm', '1') in maker.cognates
        assert ('arm', '2') in maker.cognates
        assert ('arm', '3') in maker.cognates

    def test_is_missing_for_parameter(self, maker):
        assert maker._is_missing_for_parameter('A', 'eye') == False
        assert maker._is_missing_for_parameter('A', 'leg') == False
        assert maker._is_missing_for_parameter('A', 'arm') == False

        assert maker._is_missing_for_parameter('B', 'eye') == False
        assert maker._is_missing_for_parameter('B', 'leg') == False
        assert maker._is_missing_for_parameter('B', 'arm') == False

        assert maker._is_missing_for_parameter('C', 'eye') == False
        assert maker._is_missing_for_parameter('C', 'leg') == True, \
            "Should be missing 'leg' for Language 'C'"
        assert maker._is_missing_for_parameter('C', 'arm') == False

        assert maker._is_missing_for_parameter('D', 'eye') == True, \
            "Should be missing 'eye' for Language 'D' (loan)"
        assert maker._is_missing_for_parameter('D', 'leg') == False
        assert maker._is_missing_for_parameter('D', 'arm') == False

    def test_eye_1(self, nexus):
        cog = 'eye_1'
        assert nexus.data[cog]['A'] == '1'
        assert nexus.data[cog]['B'] == '1'
        assert nexus.data[cog]['C'] == '1'
        assert nexus.data[cog]['D'] == '?'

    def test_leg_1(self, nexus):
        cog = 'leg_1'
        assert nexus.data[cog]['A'] == '1'
        assert nexus.data[cog]['B'] == '0'
        assert nexus.data[cog]['C'] == '?'
        assert nexus.data[cog]['D'] == '1'

    def test_leg_2(self, nexus):
        cog = 'leg_2'
        assert nexus.data[cog]['A'] == '0'
        assert nexus.data[cog]['B'] == '1'
        assert nexus.data[cog]['C'] == '?'
        assert nexus.data[cog]['D'] == '1'

    def test_arm_1(self, nexus):
        cog = 'arm_1'
        assert nexus.data[cog]['A'] == '1'
        assert nexus.data[cog]['B'] == '0'
        assert nexus.data[cog]['C'] == '0'
        assert nexus.data[cog]['D'] == '0'

    def test_arm_2(self, nexus):
        cog = 'arm_2'
        assert nexus.data[cog]['A'] == '0'
        assert nexus.data[cog]['B'] == '1'
        assert nexus.data[cog]['C'] == '0'
        assert nexus.data[cog]['D'] == '1'

    def test_arm_3(self, nexus):
        cog = 'arm_3'
        assert nexus.data[cog]['A'] == '0'
        assert nexus.data[cog]['B'] == '0'
        assert nexus.data[cog]['C'] == '1'
        assert nexus.data[cog]['D'] == '1'

    def test_write(self, maker):
        out = maker.write()
        assert out.lstrip().startswith("#NEXUS")
        assert 'NTAX=4' in out
        assert 'CHARSTATELABELS' in out
        assert 'MATRIX' in out
    
    def test_write_to_file(self, tmp_path, maker):
        maker.write(filename=tmp_path / 'test.nex')
        with open(tmp_path / 'test.nex') as handle:
            content = handle.read()
        
        assert content.lstrip().startswith("#NEXUS")
        assert 'NTAX=4' in content
        assert 'CHARSTATELABELS' in content
        assert 'MATRIX' in content
        