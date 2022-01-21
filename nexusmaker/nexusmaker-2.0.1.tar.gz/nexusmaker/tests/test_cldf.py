import pytest
from nexusmaker import load_cldf
from nexusmaker.tools import slugify
from nexusmaker import NexusMaker
from nexusmaker import NexusMakerAscertained
from nexusmaker import NexusMakerAscertainedParameters


EXPECTED_COGNATES = {
#   85  1_hand            ringa(ringa)     1, 64, 34         111 // filterable
#  763  1_hand                    rika         1, 64         110
# 1636  1_hand                    rima         1, 64         110
    ('hand', '1'): {'Maori_85', 'South_Island_Maori_763', 'Tahitian_1636'},
    ('hand', '34'): {'Maori_85'},
    ('hand', '64'): {'Maori_85', 'South_Island_Maori_763', 'Tahitian_1636'},

#   85    3_right                   katau         5, 40       101
#   85    3_right                   matau         5, 13       110
# 1636    3_right                   'atau          5,40       101
    ('right', '5'): {'Maori_85', 'Tahitian_1636'},
    ('right', '13'): {'Maori_85'},
    ('right', '40'): {'Maori_85', 'Tahitian_1636'},

#   85   23_blood                    toto             4       1
#  763   23_blood                    toto             4       1
# 1636   23_blood                    toto             4       1
    ('blood', '4'): {'Maori_85', 'South_Island_Maori_763', 'Tahitian_1636'},

#   85  39_tocook                     tao            10       10
#  763  39_tocook                    pupu                     .
#  763  39_tocook                   taona            10       10
#  763  39_tocook                tao(-na)            10       XXXDUPE
# 1636  39_tocook                    tunu             9       01
# 1636  39_tocook                  fa'a'ā            2?       .. DOUBT
    ('to cook', '9'): {'Tahitian_1636'},
    ('to cook', '10'): {'Maori_85', 'South_Island_Maori_763'},
    # 'pupu' not unique as 763 already in ('to cook', '10')
    # 'fa'a'ā' not unique as 1636 already in ('to cook', '9')

#   85       45_eye                    mata             1       10
# 1636       45_eye                    mata             1       10
#  763       45_eye                  konohi             4       01
    ('eye', '1'): {'Maori_85','Tahitian_1636'},
    ('eye', '4'): {'South_Island_Maori_763'},

#   85    68_needle                   ngira           LOAN      ??
#  763    68_needle                     tui            66       01
# 1636    68_needle                      au             1       10
# 1636    68_needle                    nira           LOAN      XX
    ('needle', '1'): {'Tahitian_1636'},
    ('needle', '66'): {'South_Island_Maori_763'},

#   85    104_fatgrease                   ngako            14       01
#  763    104_fatgrease                   ihinu            12       10
# 1636    104_fatgrease                    'a'o            14       01
# 1636    104_fatgrease                   poria                     u
    ('fat/grease', '12'): {'South_Island_Maori_763'},
    ('fat/grease', '14'): {'Maori_85', 'Tahitian_1636'},
    # 'poria' not unique as 1636 already in set ('fat/grease', '14')
    
#   85     120_stone                koowhatu          1,39       1001
#  763     120_stone                   boatu          1,19       1010
# 1636     120_stone                  'ōfa'i      1, 39, 3       1101
    ('stone', '1'): {'Maori_85', 'South_Island_Maori_763', 'Tahitian_1636'},
    ('stone', '3'): {'Tahitian_1636'},
    ('stone', '19'): {'South_Island_Maori_763'},
    ('stone', '39'): {'Maori_85', 'Tahitian_1636'},

#   85    150_yellow                 koowhai                     U
#   763                                                          ?  // no form
# 1636    150_yellow                re'are'a            10       1
    ('yellow', '10'): {'Tahitian_1636'},
    ('yellow', 'u_1'): {'Maori_85'},
}


@pytest.fixture
def cldf_metadata(test_dir):
    return test_dir / 'test-cldf' / 'Wordlist-metadata.json'


@pytest.fixture
def cldf_records(cldf_metadata):
    return list(load_cldf(cldf_metadata, table='ValueTable'))



def test_load_cldf(cldf_records):
    assert len(cldf_records) == 31
    assert cldf_records[-1].ID == '1636-150_yellow-1'
    assert cldf_records[-1].Language_ID == '1636'
    assert cldf_records[-1].Language == 'Tahitian'
    assert cldf_records[-1].Parameter_ID == '150_yellow'
    assert cldf_records[-1].Parameter == 'yellow'
    assert cldf_records[-1].Item == "re'are'a"
    assert cldf_records[-1].Loan is False, cldf_records[-1].Loan
    assert cldf_records[-1].Cognacy == "10"
    assert cldf_records[-1].get_taxon() == 'Tahitian_1636'


class TestNexusMakerCLDF:
    # number of cognate sets expected
    expected_ncog = len(EXPECTED_COGNATES)
    # number of characters expected in the nexus file
    expected_nchar = len(EXPECTED_COGNATES)

    @pytest.fixture
    def maker(self, cldf_records):
        return NexusMaker(data=cldf_records)

    @pytest.fixture
    def nexus(self, maker):
        return maker.make()

    def test_languages(self, maker):
        assert maker.languages == {
            'Maori_85', 'Tahitian_1636', 'South_Island_Maori_763'
        }

    def test_parameters(self, maker):
        assert maker.parameters == {
            'hand',
            'right',
            'blood',
            'to cook',
            'eye',
            'needle',
            'fat/grease',
            'stone',
            'yellow',
        }

    def test_ncognates(self, maker):
        assert len(maker.cognates) == self.expected_ncog

    @pytest.mark.parametrize("key,members",
        [(e, EXPECTED_COGNATES[e]) for e in EXPECTED_COGNATES]
    )
    def test_cognate_sets(self, maker, key, members):
        assert key in maker.cognates, key
        obtained = maker.cognates.get(key, set())
        assert obtained == members, \
            "Cognate set %s incorrect %r != %r" % (key, members, obtained)

    def test_simaori_is_all_missing_for_right(self, nexus):
        for cog in [cog for cog in nexus.data if cog.startswith('right_')]:
            assert nexus.data[cog]['South_Island_Maori_763'] == '?'

    def test_maori_is_all_missing_for_needle(self, nexus):
        for cog in [cog for cog in nexus.data if cog.startswith('needle_')]:
            assert nexus.data[cog]['Maori_85'] == '?'

    def test_nexus_symbols(self, nexus):
        assert sorted(nexus.symbols) == sorted(['0', '1']), nexus.symbols

    def test_nexus_taxa(self, maker, nexus):
        assert maker.languages == nexus.taxa

    @pytest.mark.parametrize("label", EXPECTED_COGNATES.keys())
    def test_nexus_characters_expected_cognates(self, nexus, label):
        # test that we have all the characters labelled in the nexus
        charlabel = "_".join([slugify(label[0]), label[1]]).replace("to_", "to")
        assert charlabel in nexus.characters, 'Mismatch on %r -> %r' % (label, charlabel)

    def test_nexus_nchar(self, nexus):
        assert len(nexus.characters) == self.expected_nchar


class TestNexusMakerCLDFAscertained(TestNexusMakerCLDF):
    expected_nchar = len(EXPECTED_COGNATES) + 1

    @pytest.fixture
    def maker(self, cldf_records):
        return NexusMakerAscertained(data=cldf_records)


class TestNexusMakerCLDFAscertainedParameters(TestNexusMakerCLDFAscertained):
    expected_nchar = len(EXPECTED_COGNATES) + 9

    @pytest.fixture
    def maker(self, cldf_records):
        return NexusMakerAscertainedParameters(data=cldf_records)
