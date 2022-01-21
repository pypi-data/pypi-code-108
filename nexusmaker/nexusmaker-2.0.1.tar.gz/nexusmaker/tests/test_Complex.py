import pytest

from nexusmaker import Record
from nexusmaker import NexusMaker
from nexusmaker import NexusMakerAscertained
from nexusmaker import NexusMakerAscertainedParameters
from nexusmaker import CognateParser

RECORDS = """
Aiwoo-501	132312	five	vili	1
Aiwoo-501	133751	leg	nyike	86
Aiwoo-501	133752	leg	nuku	86
Aiwoo-501	208804	hand	nyime	1,66
Aiwoo-501	208805	hand	nyimä	1,66
Banoni-4	1075	leg	rapinna
Banoni-4	250221	five	ghinima	1
Banoni-4	4	hand	numa-	1,64
Dehu-196	129281	five	tripi	1
Dehu-196	196	hand	wanakoim
Eton-1088	265408	five	e-lim	1
Eton-1088	278627	leg	tua-ŋ	95
Hiw-639	164951	hand	mja-	1,78
Hiw-639	164952	leg	ᶢʟoŋo-	17
Hiw-639	165135	five	təβɔjimə	1
Iaai-471	125656	hand	beñi-	14
Iaai-471	125657	hand	HAND
Iaai-471	125659	leg	ca
Iaai-471	125853	five	baa|xaca
Iaai-471	125865	five	thabyŋ
Lamogai-67	83796	five	elmé	1
Lamogai-67	83881	hand	mulǵu	45
Lamogai-67	83882	hand	melsé	45
Lamogai-67	83883	hand	milpí	45
Lamogai-67	83884	hand	melép	45
Lamogai-67	83885	hand	milpú	45
Lamogai-67	83886	hand	meylá	45
Lamogai-67	83887	hand	melsék	45
Lamogai-67	83942	leg	kaip	1
Lamogai-67	83943	leg	kaŋgú	1
"""


def expand(r):  # make sure there are 5 columns in the record
    while len(r) < 5:
        r.append("")
    return r


RECORDS = [expand(r.split("\t")) for r in RECORDS.split("\n") if len(r)]
COMPLEX_TESTDATA = [
    Record(Language=r[0], Parameter=r[2], Item=r[3], Cognacy=r[4])
    for r in RECORDS
]

EXPECTED_COGNATES = {
    ('five', '1'): {
        'Aiwoo-501', 'Banoni-4', 'Dehu-196', 'Eton-1088', 'Hiw-639',
        'Lamogai-67'
    },
    ('leg', '86'): {'Aiwoo-501'},
    ('hand', '1'): {'Aiwoo-501', 'Banoni-4', 'Hiw-639'},
    ('hand', '64'): {'Banoni-4'},
    ('hand', '66'): {'Aiwoo-501'},
    ('leg', '95'): {'Eton-1088'},
    ('hand', '78'): {'Hiw-639'},
    ('leg', '17'): {'Hiw-639'},
    ('hand', '14'): {'Iaai-471'},
    ('hand', '45'): {'Lamogai-67'},
    ('leg', '1'): {'Lamogai-67'},
    ('leg', 'u_1'): {'Banoni-4'},
    ('hand', 'u_2'): {'Dehu-196'},
    ('leg', 'u_4'): {'Iaai-471'},
    ('five', 'u_6'): {'Iaai-471'},
}


class TestNexusMakerComplex:
    # number of cognate sets expected
    expected_ncog = len(EXPECTED_COGNATES)
    # number of characters expected in the nexus file
    expected_nchar = len(EXPECTED_COGNATES)

    @pytest.fixture
    def maker(self):
        return NexusMaker(data=COMPLEX_TESTDATA)

    @pytest.fixture
    def nexus(self, maker):
        return maker.make()
    
    def test_languages(self, maker):
        assert maker.languages == {
            'Aiwoo-501', 'Banoni-4', 'Dehu-196', 'Eton-1088', 'Hiw-639',
            'Iaai-471', 'Lamogai-67'
        }

    def test_parameters(self, maker):
        assert maker.parameters == {'hand', 'leg', 'five'}

    def test_ncognates(self, maker):
        assert len(maker.cognates) == self.expected_ncog

    @pytest.mark.parametrize("key,members",
        [(e, EXPECTED_COGNATES[e]) for e in EXPECTED_COGNATES]
    )
    def test_cognate_sets(self, maker, key, members):
        assert key in maker.cognates, "Missing %s" % key
        obtained = maker.cognates.get(key, set())
        assert obtained == members, \
            "Cognate set %s incorrect %r != %r" % (key, members, obtained)

    def test_dehu_is_all_missing_for_leg(self, nexus):
        for cog in [cog for cog in nexus.data if cog.startswith('leg_')]:
            assert nexus.data[cog]['Dehu-196'] == '?'

    def test_eton_is_all_missing_for_hand(self, nexus):
        for cog in [cog for cog in nexus.data if cog.startswith('hand_')]:
            assert nexus.data[cog]['Eton-1088'] == '?'

    def test_only_one_unique_for_Iaai471(self, nexus):
        iaai = 0
        for cog in [cog for cog in nexus.data if cog.startswith('five_u_')]:
            present = [t for t in nexus.data[cog] if nexus.data[cog][t] == '1']
            if present == ['Iaai-471']:
                iaai += 1

        assert iaai == 1, "Should only have one unique site for Iaai-471-five"

    def test_nexus_symbols(self, nexus):
        assert sorted(nexus.symbols) == sorted(['0', '1']), nexus.symbols

    def test_nexus_taxa(self, maker, nexus):
        assert maker.languages == nexus.taxa

    @pytest.mark.parametrize("label", EXPECTED_COGNATES.keys())
    def test_nexus_characters_expected_cognates(self, nexus, label):
        assert "_".join(label) in nexus.characters

    def test_nexus_nchar(self, nexus):
        assert len(nexus.characters) == self.expected_nchar

    def test_entries_with_a_cognate_in_the_same_parameter_arenot_added_as_unique(self, nexus):
        hand = [c for c in nexus.characters if c.startswith('hand_')]
        hand = [c for c in hand if CognateParser().is_unique_cognateset(c, labelled=True)]
        assert len(hand) == 1, 'Only expecting one unique character for hand'
        assert nexus.data['hand_u_2']['Iaai-471'] in ('0', '?'), \
            'Iaai-471 should not be unique for `hand`'


class TestNexusMakerComplexAscertained(TestNexusMakerComplex):
    expected_nchar = len(EXPECTED_COGNATES) + 1

    @pytest.fixture
    def maker(self):
        return NexusMakerAscertained(data=COMPLEX_TESTDATA)


class TestNexusMakerComplexAscertainedParameters(TestNexusMakerComplexAscertained):
    expected_nchar = len(EXPECTED_COGNATES) + 3

    @pytest.fixture
    def maker(self):
        return NexusMakerAscertainedParameters(data=COMPLEX_TESTDATA)
