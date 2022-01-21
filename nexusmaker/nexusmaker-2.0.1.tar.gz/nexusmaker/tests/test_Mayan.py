import pytest

from nexusmaker import Record
from nexusmaker import NexusMaker
from nexusmaker import NexusMakerAscertained
from nexusmaker import NexusMakerAscertainedParameters
from nexusmaker import CognateParser

RECORDS = """
41551	030	Poqomchi	00004	Kaufman_1976	cloud	suutZ'	2
41552	030	Poqomchi	00009	Campbell_1971b	cloud	suutZ'	2
41553	030	Poqomchi	00022	Mayers_ed_1966	cloud	suutZ'	2
41554	030	Poqomchi	00027	Mayers_1960	cloud	suutZ'	2
41555	030	Poqomchi	00061	Stoll_1884	cloud	su'tZ	2
20569	003	Lacandon	00011	Fisher	cloud	muuyar	6c
20570	003	Lacandon	00085	Canger_1970	cloud	muuyaar	6c
20571	003	Lacandon	00085	Canger_1970	cloud	'u-muuy^r-ir	6c
20572	003	Lacandon	00085	Canger_1970	cloud	'u-muuyaar-ir	6c
20573	003	Lacandon	00037	Andrade_1946	cloud	muuyáh	6c
45362	011	Tzotzil	00024	Delgaty_1964	cloud	but'ul	11
45363	011	Tzotzil	00024	Delgaty_1964	cloud	toc	5
45364	011	Tzotzil	00024	Delgaty_1964	cloud	stacel winajel	5
45365	011	Tzotzil	00036	Materials_on_the_Mayan_Languages_of_Mexico_1949b	cloud	toc	5
45366	011	Tzotzil	00034	Weathers_and_Weathers_1949	cloud	toc	5
45367	011	Tzotzil	00061	Stoll_1884	cloud	toc	5
25058	012	Tojolabal	00033	Jackson_and_Supple_1952	cloud	ason	1
25059	012	Tojolabal	00053	Sapper_1897	cloud	ason	1
25060	012	Tojolabal	00061	Stoll_1884	cloud	asón	1
25061	012	Tojolabal	00063	Berendt_1870a	cloud	ason	1
47927	023	Tzutujil	00004	Kaufman_1976	cloud	suutZ'	2
47928	023	Tzutujil	00009	Campbell_1971b	cloud	suutZ'	2
47929	023	Tzutujil	00051	Stoll_1901a	cloud	su'tZ	2
50387	023	Tzutujil	00086	Kaufman_2003	cloud	maayuul	6
49008	028	Uspanteko	00004	Kaufman_1976	cloud	su>utZ'	2
49009	028	Uspanteko	00009	Campbell_1971b	cloud	su>utZ'	2
49010	028	Uspanteko	00053	Sapper_1897	cloud	su'tZ	2
49011	028	Uspanteko	00055	Stoll_1896	cloud	su'tZ	2
49012	028	Uspanteko	00061	Stoll_1884	cloud	su'tZ	2
13219	005	Itza	00007	Schumann_1971	cloud	muyal	6c
13220	005	Itza	00054	Armas_1897a	cloud	muyal	6c
13221	005	Itza	00061	Stoll_1884	cloud	muyál	6c
13222	005	Itza	00070	Baezo	cloud	muyal	6c
13223	005	Itza	00069	Baezo_1832	cloud	muyal	6c
32925	022	Kaqchikel	00004	Kaufman_1976	cloud	sutZ'	2
32926	022	Kaqchikel	00009	Campbell_1971b	cloud	suutZ'	2
32927	022	Kaqchikel	00022	Mayers_ed_1966	cloud	sutZ'	2
32928	022	Kaqchikel	00061	Stoll_1884	cloud	su'tZ	2
50391	022	Kaqchikel	00086	Kaufman_2003	cloud	moyan	6e
08999	013	Chuj	00004	Kaufman_1976	cloud	'asun	1
09000	013	Chuj	00022	Mayers_ed_1966	cloud	asun	1
09001	013	Chuj	00037	Andrade_1946	cloud	asún	1
09002	013	Chuj	00060	Stoll_1887	cloud	asun	1
09003	013	Chuj	00060	Stoll_1887	cloud	taa	u_8341	X
22444	017	Mocho	00016	Schumann_1969	cloud	'asonG	1
22445	017	Mocho	00045	Sapper_1912	cloud	músan	9
22446	017	Mocho	00053	Sapper_1897	cloud	musan	9
50385	017	Mocho	00086	Kaufman_2003	cloud	ma:yu:l	6
42773	029	Poqomam	00004	Kaufman_1976	cloud	suutZ'	2
42774	029	Poqomam	00009	Campbell_1971b	cloud	suutZ'	2
42775	029	Poqomam	00022	Mayers_ed_1966	cloud	co' sutZ'	2
42776	029	Poqomam	00027	Mayers_1960	cloud	suutZ'	2
42777	029	Poqomam	00047	Sapper_1907	cloud	su'tZ	2
42778	029	Poqomam	00053	Sapper_1897	cloud	su'tZ	2
42779	029	Poqomam	00061	Stoll_1884	cloud	su'tZ	2
34124	002	Chicomuceltec	00041	Termer_1930	cloud	siál	4
34125	002	Chicomuceltec	00045	Sapper_1912	cloud	sial	4
34126	002	Chicomuceltec	00053	Sapper_1897	cloud	sial	4
19167	031	Qeqchi	00004	Kaufman_1976	cloud	čoq	5
19168	031	Qeqchi	00004	Kaufman_1976	cloud	čoql	5
19169	031	Qeqchi	00009	Campbell_1971b	cloud	čooql	5
19170	031	Qeqchi	00022	Mayers_ed_1966	cloud	čoq	5
19171	031	Qeqchi	00053	Sapper_1897	cloud	čoq	5
19172	031	Qeqchi	00061	Stoll_1884	cloud	čoq	5
04043	008	Chol	00002	Aulie_and_Aulie_1978	cloud	tyocal	5
04044	008	Chol	00084	Attinasi_1973	cloud	m^c-^l	u_11394	M
04045	008	Chol	00084	Attinasi_1973	cloud	toc-al-i-lal	5
04046	008	Chol	00084	Attinasi_1973	cloud	toc-al	5
04047	008	Chol	00083	Schumann	cloud	tocal	5
04048	008	Chol	00036	Materials_on_the_Mayan_Languages_of_Mexico_1949b	cloud	tocal	5
04049	008	Chol	00047	Sapper_1907	cloud	tyocal	5
04050	008	Chol	00053	Sapper_1897	cloud	tyocal	5
04051	008	Chol	00061	Stoll_1884	cloud	tiocál	5
04052	008	Chol	00075	Moran	cloud	muyal	u_11395	X
44265	010	Tzeltal	00023	Slocum_and_Gerdel_1965	cloud	tocal	5
44266	010	Tzeltal	00053	Sapper_1897	cloud	tojcal	5
44267	010	Tzeltal	00061	Stoll_1884	cloud	tojcál	5
43969	026	Sakapulteko	00004	Kaufman_1976	cloud	suutZ'	2
35003	009	Chontal	00061	Stoll_1884	cloud	buclá	8
35861	007	Chorti	00004	Kaufman_1976	cloud	tocar	5
35862	007	Chorti	00022	Mayers_ed_1966	cloud	tocar	5
35863	007	Chorti	00047	Sapper_1907	cloud	tocar	5
35864	007	Chorti	00053	Sapper_1897	cloud	tocar	5
35865	007	Chorti	00068	Galindo_1834	cloud	toc'ar	5
50388	007	Chorti	00086	Kaufman_2003	cloud	mayuy	u_16438	2
01564	020	Awakateko	00004	Kaufman_1976	cloud	sbaaq'	3
01565	020	Awakateko	00022	Mayers_ed_1966	cloud	sbaq'	3
01566	020	Awakateko	00037	Andrade_1946	cloud	sp'aq'	3
01567	020	Awakateko	00053	Sapper_1897	cloud	ciá	u_16875	X
01568	020	Awakateko	00060	Stoll_1887	cloud	sba'q	3
01569	020	Awakateko	00061	Stoll_1884	cloud	sba'q	3
29690	004	Yucatec	00001	Bolles_1981	cloud	muyál	6c
29691	004	Yucatec	00012	Fisher_and_Vermont-Salas	cloud	mu>uyal	u_17820	L
29692	004	Yucatec	00052	Zavala_and_Medina_1898	cloud	muyal	6c
29693	004	Yucatec	00061	Stoll_1884	cloud	muyál	6c
29694	004	Yucatec	00073	Beltran	cloud	muyal	6c
29695	004	Yucatec	00076	Ticul	cloud	muyal	6c
37033	019	Mam	00004	Kaufman_1976	cloud	muuj	10
37034	019	Mam	00016	Schumann_1969	cloud	muj	10
37035	019	Mam	00022	Mayers_ed_1966	cloud	muuj	10
37036	019	Mam	00044	Jaramilo_1918	cloud	muj	10
37037	019	Mam	00045	Sapper_1912	cloud	múaj	10
37038	019	Mam	00053	Sapper_1897	cloud	muaj	10
37039	019	Mam	00060	Stoll_1887	cloud	muj	10
37040	019	Mam	00061	Stoll_1884	cloud	muj	10
14792	021	Ixil	00004	Kaufman_1976	cloud	sutZ'	2
14793	021	Ixil	00022	Mayers_ed_1966	cloud	sutZ'	2
14794	021	Ixil	00060	Stoll_1887	cloud	su'tZ	2
14795	021	Ixil	00061	Stoll_1884	cloud	su'tZ	2
53370	032	Cholti	00094	Gates_1935	cloud	muyal	6
51398	033	Classical_Maya	00087	Boot_2002	cloud	muyal	6c
51399	033	Classical_Maya	00087	Boot_2002	cloud	tok	5
16282	014	Jakalteko	00004	Kaufman_1976	cloud	'asun	1
16283	014	Jakalteko	00004	Kaufman_1976	cloud	moyan	6
16284	014	Jakalteko	00022	Mayers_ed_1966	cloud	moyan	6
16285	014	Jakalteko	00039	La_Farge_and_Byers_1931	cloud	asun	1
16286	014	Jakalteko	00045	Sapper_1912	cloud	múyan	6
16287	014	Jakalteko	00053	Sapper_1897	cloud	muyan	6
16288	014	Jakalteko	00060	Stoll_1887	cloud	asun	1
00330	018	Teco	00004	Kaufman_1976	cloud	muuj	10
00331	018	Teco	00017	Kaufman_1969a	cloud	muuj	10
18267	016	Qanjobal	00004	Kaufman_1976	cloud	'asun	1
18268	016	Qanjobal	00037	Andrade_1946	cloud	sutZ'án	2b
18269	016	Qanjobal	00037	Andrade_1946	cloud	asún	1
51765	035	Colonial_Yucatec	00077	Vienna_Dictionary_1600	cloud	buyul	12
51766	035	Colonial_Yucatec	00077	Vienna_Dictionary_1600	cloud	muyal	6c
00943	015	Akateco	00004	Kaufman_1976	cloud	'asun	1
50390	015	Akateco	00086	Kaufman_2003	cloud	moyan	6d
51611	034	Colonial_Cakchiquel	00088	Coto_Thomas_de_1647	cloud	suq	u_24152	B
51612	034	Colonial_Cakchiquel	00088	Coto_Thomas_de_1647	cloud	moy	6e
44071	027	Sipakapeno	00004	Kaufman_1976	cloud	muuj	10
10419	001	Huastec	00029	Larsen_1955	cloud	tocou	5b
10420	001	Huastec	00056	Lorenzana_1896a	cloud	tocóu	5b
10421	001	Huastec	00058	Alejandre_1890	cloud	tocob	5b
10422	001	Huastec	00061	Stoll_1884	cloud	tocób	5b
10423	001	Huastec	00072	Tapia_Zanteno_1767	cloud	tocob	5b
10424	001	Huastec	00082	Tapia_Zenteno_1747	cloud	tocob	5b
00030	025	Achi	00022	Mayers_ed_1966	cloud	sutZ'	2
53559	037	Tuzanteco	00086	Kaufman_2003	cloud	7aso:n	1
40164	006	Mopan	00003	Andrade_1977	cloud	muyál	6c
40165	006	Mopan	00004	Kaufman_1976	cloud	muyal	6c
40166	006	Mopan	00022	Mayers_ed_1966	cloud	muyal	6c
40167	006	Mopan	00026	Ulrich_and_Ulrich	cloud	muyal	6c
23136	024	Kiche	00004	Kaufman_1976	cloud	suutZ'	2
23137	024	Kiche	00009	Campbell_1971b	cloud	suutZ'	2
23138	024	Kiche	00022	Mayers_ed_1966	cloud	sutZ'	2
23139	024	Kiche	00061	Stoll_1884	cloud	su'tZ	2
50386	024	Kiche	00086	Kaufman_2003	cloud	mayuul	6
50389	024	Kiche	00086	Kaufman_2003	cloud	mayuy	6b
53557	036	Popti	00086	Kaufman_2003	cloud	xhmoyxi	6d
53558	036	Popti	00086	Kaufman_2003	cloud	asun	1
"""

HEADER = ['ID', "Language_ID", "Language", "SID", "Source", "Parameter", "Item", "Cognacy", "Loan"]
COMPLEX_TESTDATA = [
    Record(**dict(zip(HEADER, r.split('\t')))) for r in RECORDS.split("\n") if len(r.strip())
]

EXPECTED_COGNATES = {
    ('cloud', '1'): {
        'Tojolabal_012', 'Chuj_013', 'Mocho_017', 'Jakalteko_014', 'Qanjobal_016',
        'Akateco_015', 'Tuzanteco_037', 'Popti_036'
    },
    ('cloud', '2'): {
        'Achi_025', 'Kaqchikel_022', 'Poqomam_029', 'Sakapulteko_026', 'Ixil_021',
        'Kiche_024', 'Poqomchi_030', 'Tzutujil_023', 'Uspanteko_028'
    },
    ('cloud', '2b'): {'Qanjobal_016'},

    ('cloud', '3'): {'Awakateko_020'},
    ('cloud', '4'): {'Chicomuceltec_002'},
    ('cloud', '5'): {
        'Tzeltal_010', 'Chorti_007', 'Tzotzil_011', 'Qeqchi_031', 'Chol_008',
        'Classical_Maya_033',
    },
    ('cloud', '5b'): {'Huastec_001'},
    ('cloud', '6'): {
        'Jakalteko_014', 'Tzutujil_023', 'Mocho_017', 'Cholti_032', 'Kiche_024',
    },
    ('cloud', '6b'): {'Kiche_024'},
    ('cloud', '6c'): {
        'Lacandon_003', 'Itza_005', 'Yucatec_004', 'Classical_Maya_033',
        'Colonial_Yucatec_035', 'Mopan_006'
    },
    ('cloud', '6d'): {'Akateco_015', 'Popti_036'},
    ('cloud', '6e'): {'Kaqchikel_022', 'Colonial_Cakchiquel_034'},
    ('cloud', '8'): {'Chontal_009'},
    ('cloud', '9'): {'Mocho_017'},
    ('cloud', '10'): {'Mam_019', 'Teco_018', 'Sipakapeno_027'},
    ('cloud', '11'): {'Tzotzil_011'},
    ('cloud', '12'): {'Colonial_Yucatec_035'},
}
# COMBINED COGNATE SETS
# (i.e. we need to merge in the extra items so that a language coded as
# "2b" is also present in set "2"
EXPECTED_COGNATES[('cloud', '2')] = EXPECTED_COGNATES[('cloud', '2')] | EXPECTED_COGNATES[('cloud', '2b')]
EXPECTED_COGNATES[('cloud', '5')] = EXPECTED_COGNATES[('cloud', '5')] | EXPECTED_COGNATES[('cloud', '5b')]
EXPECTED_COGNATES[('cloud', '6')] = EXPECTED_COGNATES[('cloud', '6')] | EXPECTED_COGNATES[('cloud', '6b')]
EXPECTED_COGNATES[('cloud', '6')] = EXPECTED_COGNATES[('cloud', '6')] | EXPECTED_COGNATES[('cloud', '6c')]
EXPECTED_COGNATES[('cloud', '6')] = EXPECTED_COGNATES[('cloud', '6')] | EXPECTED_COGNATES[('cloud', '6d')]
EXPECTED_COGNATES[('cloud', '6')] = EXPECTED_COGNATES[('cloud', '6')] | EXPECTED_COGNATES[('cloud', '6e')]


class TestNexusMakerMayan:
    @pytest.fixture
    def maker(self):
        return NexusMaker(data=COMPLEX_TESTDATA)

    @pytest.fixture
    def nexus(self, maker):
        return maker.make()

    # number of cognate sets expected
    expected_ncog = len(EXPECTED_COGNATES)
    # number of characters expected in the nexus file
    expected_nchar = len(EXPECTED_COGNATES)

    def test_languages(self, maker):
        assert maker.languages == {
            'Mocho_017', 'Tzotzil_011', 'Cholti_032',
            'Colonial_Cakchiquel_034', 'Tzutujil_023', 'Chorti_007',
            'Poqomam_029', 'Chol_008', 'Lacandon_003', 'Chontal_009',
            'Qanjobal_016', 'Sakapulteko_026', 'Mopan_006', 'Kaqchikel_022',
            'Classical_Maya_033', 'Yucatec_004', 'Mam_019', 'Akateco_015',
            'Ixil_021', 'Achi_025', 'Itza_005', 'Poqomchi_030', 'Chuj_013',
            'Jakalteko_014', 'Huastec_001', 'Tzeltal_010', 'Popti_036',
            'Kiche_024', 'Awakateko_020', 'Colonial_Yucatec_035',
            'Uspanteko_028', 'Teco_018', 'Tojolabal_012', 'Tuzanteco_037',
            'Qeqchi_031', 'Sipakapeno_027', 'Chicomuceltec_002'
        }

    def test_parameters(self, maker):
        assert maker.parameters == {'cloud'}

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

    def test_nexus_symbols(self, nexus):
        assert sorted(nexus.symbols) == sorted(['0', '1'])

    def test_nexus_taxa(self, maker, nexus):
        assert maker.languages == nexus.taxa

    @pytest.mark.parametrize("label", EXPECTED_COGNATES.keys())
    def test_nexus_characters_expected_cognates(self, nexus, label):
        assert "_".join(label) in nexus.characters

    def test_nexus_characters_expected_uniques(self, nexus):
        # should be none
        uniques = [
            c for c in nexus.characters if
            CognateParser().is_unique_cognateset(c, labelled=True)
        ]
        assert len(uniques) == 0

    def test_nexus_nchar(self, nexus):
        assert len(nexus.characters) == self.expected_nchar


class TestNexusMakerMayanAscertained(TestNexusMakerMayan):
    expected_nchar = len(EXPECTED_COGNATES) + 1

    @pytest.fixture
    def maker(self):
        return NexusMakerAscertained(data=COMPLEX_TESTDATA)


class TestNexusMakerMayanAscertainedParameters(TestNexusMakerMayanAscertained):
    @pytest.fixture
    def maker(self):
        return NexusMakerAscertainedParameters(data=COMPLEX_TESTDATA)
