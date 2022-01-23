import sys
import re
import logging
import os

from gramadan.noun import Noun
from gramadan.features import Gender, FormSg
from gramadan.opers import Opers
from gramadan.singular_info import SingularInfoA, SingularInfoE, SingularInfoC, SingularInfoL, SingularInfoAX, SingularInfoEAX, SingularInfoD, SingularInfoN
from gramadan.v2.database import Database
from gramadan.v2.semantic_groups import FAMILY
from gramadan.v2.other_groups import POSSIBLE_LOANWORDS_GENITIVELESS, BUNAMO_ONLY_GENITIVELESS

from gramadan.v2.noun import DeclensionInconsistentError, FormsMissingException, FormsAmbiguousException, NounDeclensionGuesser, re_ends


class EmpiricalNounDeclensionGuesser(NounDeclensionGuesser):
    IRREGULAR_INCLUSION = {
            'bocht': 1, # otherwise 4
            'nocht': 1, # otherwise 4
            'brath': 1, # otherwise 3
            'cam': 1, # otherwise 3
            'cleas': 1, # otherwise 3
            'cneas': 1, # otherwise 3
            'daol': 1, # otherwise 3
            'deargadaol': 1, # otherwise 3
            'deimheas': 1, # otherwise 3
            'dlúth': 1, # otherwise 3
            'drochshaol': 1, # otherwise 3
            'forás': 1, # otherwise 3
            'gléas': 1, # otherwise 3
            'gnáth': 1, # otherwise 3
            'gnéas': 1, # otherwise 3
            'gram': 1, # otherwise 3
            'láth': 1, # otherwise 3
            'léas': 1, # otherwise 3
            'lúth': 1, # otherwise 3
            'prás': 1, # otherwise 3
            'stoth': 1, # otherwise 3
            'údarás': 1, # otherwise 3

            'ab': 3, # otherwise 1
            'aimhleas': 3, # otherwise 1
            'ainbhios': 3, # otherwise 1
            'altram': 3, # otherwise 1
            'anam': 3, # otherwise 1
            'athdhreas': 3, # otherwise 1
            'bang': 3, # otherwise 1
            'beart': 3, # otherwise 1
            'bior': 3, # otherwise 1
            'bum': 3, # otherwise 1
            'cac': 3, # otherwise 1
            'cead': 3, # otherwise 1
            'coincheap': 3, # otherwise 1
            'coinsias': 3, # otherwise 1
            'comhfhios': 3, # otherwise 1
            'creat': 3, # otherwise 1
            'crinnghréas': 3, # otherwise 1
            'deann': 3, # otherwise 1
            'dreach': 3, # otherwise 1
            'driuch': 3, # otherwise 1
            'dúshnámh': 3, # otherwise 1
            'feadh': 3, # otherwise 1
            'feart': 3, # otherwise 1
            'flas': 3, # otherwise 1
            'flosc': 3, # otherwise 1
            'fríos': 3, # otherwise 1
            'fág': 3, # otherwise 1
            'fíon': 3, # otherwise 1
            'geaf': 3, # otherwise 1
            'gean': 3, # otherwise 1
            'geábh': 3, # otherwise 1
            'gleann': 3, # otherwise 1
            'gliúc': 3, # otherwise 1
            'gus': 3, # otherwise 1
            'laom': 3, # otherwise 1
            'leithcheal': 3, # otherwise 1
            'lionn': 3, # otherwise 1
            'loch': 3, # otherwise 1
            'mant': 3, # otherwise 1
            'modh': 3, # otherwise 1
            'mogh': 3, # otherwise 1
            'muirdhreach': 3, # otherwise 1
            'mám': 3, # otherwise 1
            'oigheareas': 3, # otherwise 1
            'ollmhaitheas': 3, # otherwise 1
            'rang': 3, # otherwise 1
            'riast': 3, # otherwise 1
            'rámh': 3, # otherwise 1
            'réad': 3, # otherwise 1
            'ríomh': 3, # otherwise 1
            'scol': 3, # otherwise 1
            'seal': 3, # otherwise 1
            'siad': 3, # otherwise 1
            'sioc': 3, # otherwise 1
            'slad': 3, # otherwise 1
            'smealt': 3, # otherwise 1
            'smior': 3, # otherwise 1
            'sos': 3, # otherwise 1
            'spreang': 3, # otherwise 1
            'suanlios': 3, # otherwise 1
            'taom': 3, # otherwise 1
            'tart': 3, # otherwise 1
            'tathant': 3, # otherwise 1
            'tost': 3, # otherwise 1
            'treall': 3, # otherwise 1
            'troch': 3, # otherwise 1
            'trunc': 3, # otherwise 1
            'tréad': 3, # otherwise 1
            'turghleann': 3, # otherwise 1
            'tírdhreach': 3, # otherwise 1
            'uaillbhreas': 3, # otherwise 1
            'urlios': 3, # otherwise 1
            'víol': 3, # otherwise 1
            'áineas': 3, # otherwise 1
            'éad': 3, # otherwise 1
            'éag': 3, # otherwise 1

            'straidhn': 2,
            'tiúin': 2,
            'spairn': 2,
            'diathair': 2,
            'deoir': 2,
            'éitir': 2,
            'cosmhuintir': 2,
            'muintir': 2,
            'aibítir': 2,
            'vacsaín': 2,
            'dín': 2,
            'falacail': 2, # otherwise 4
            'trucail': 2, # otherwise 4
            'fail': 2, # otherwise 4
            'aragail': 2, # otherwise 4
            'máchail': 2, # otherwise 4
            'diail': 2, # otherwise 4
            'gunail': 2, # otherwise 4
            'copail': 2, # otherwise 4
            'gasail': 2, # otherwise 4
            'hiodrocsail': 2, # otherwise 4
            'stail': 2, # otherwise 4
            'uail': 2, # otherwise 4
            'luail': 2, # otherwise 4
            'cáil': 2, # otherwise 4
            'scáil': 2, # otherwise 4
            'léarscáil': 2, # otherwise 4
            'sracléarscáil': 2, # otherwise 4
            'geargáil': 2, # otherwise 4
            'páil': 2, # otherwise 4
            'sáil': 2, # otherwise 4
            'miúil': 2, # otherwise 4
            'clibirt': 2, # otherwise 4
            'beirt': 2, # otherwise 4
            'ceirt': 2, # otherwise 4
            'caismirt': 2, # otherwise 4
            'contúirt': 2, # otherwise 4

            'bail': 2, # otherwise 3
            'scil': 2, # otherwise 3
            'beicireil': 2, # otherwise 3
            'stil': 2, # otherwise 3
            'cuil': 2, # otherwise 3
            'carrchuil': 2, # otherwise 3
            'urchuil': 2, # otherwise 3
            'druil': 2, # otherwise 3
            'hipearbóil': 2, # otherwise 3
            'líonóil': 2, # otherwise 3
            'cúpóil': 2, # otherwise 3
            'seachtain': 2, # otherwise 3
            'balcóin': 2, # otherwise 3
            'sionfóin': 2, # otherwise 3
            'sclóin': 2, # otherwise 3
            'armóin': 2, # otherwise 3
            'dlútharmóin': 2, # otherwise 3
            'hearóin': 2, # otherwise 3
            'íoróin': 2, # otherwise 3
            'gnáthscair': 2, # otherwise 3
            'teanchair': 2, # otherwise 3
            'catagóir': 2, # otherwise 3
            'glóir': 2, # otherwise 3
            'póir': 2, # otherwise 3
            'ruíleas': 2, # otherwise 3

            'íobairt': 3, # otherwise 4
            'forbairt': 3, # otherwise 4
            'athfhorbairt': 3, # otherwise 4
            'treascairt': 3, # otherwise 4
            'coscairt': 3, # otherwise 4
            'diúscairt': 3, # otherwise 4
            'labhairt': 3, # otherwise 4
            'tabhairt': 3, # otherwise 4
            'cnuchairt': 3, # otherwise 4
            'faghairt': 3, # otherwise 4
            'íospairt': 3, # otherwise 4
            'buairt': 3, # otherwise 4

            'ban-ab': 3, # otherwise 2
            'máthairab': 3, # otherwise 2
            'Cáisc': 3, # otherwise 2
            'scread': 3, # otherwise 2
            'troid': 3, # otherwise 2
            'cuid': 3, # otherwise 2
            'cuaird': 3, # otherwise 2
            'feag': 3, # otherwise 2
            'eang': 3, # otherwise 2
            'luaith': 3, # otherwise 2
            'cáith': 3, # otherwise 2
            'both': 3, # otherwise 2
            'scoth': 3, # otherwise 2
            'fíorscoth': 3, # otherwise 2
            'feoil': 3, # otherwise 2
            'toil': 3, # otherwise 2
            'béicíl': 3, # otherwise 2
            'cáithíl': 3, # otherwise 2
            'búiríl': 3, # otherwise 2
            'seitríl': 3, # otherwise 2
            'smaoisíl': 3, # otherwise 2
            'grianbhladhm': 3, # otherwise 2
            'uaim': 3, # otherwise 2
            'úim': 3, # otherwise 2
            'athsheinm': 3, # otherwise 2
            'seinm': 3, # otherwise 2
            'dúchan': 3, # otherwise 2
            'feadhain': 3, # otherwise 2
            'Samhain': 3, # otherwise 2
            'líomhain': 3, # otherwise 2
            'deoin': 3, # otherwise 2
            'goin': 3, # otherwise 2
            'síocháin': 3, # otherwise 2
            'eadráin': 3, # otherwise 2
            'táin': 3, # otherwise 2
            'cnuaisciúin': 3, # otherwise 2
            'fíniúin': 3, # otherwise 2
            'ríon': 3, # otherwise 2
            'banríon': 3, # otherwise 2
            'cearn': 3, # otherwise 2
            'starr': 3, # otherwise 2
            'taispeáint': 3, # otherwise 2
            'iomáint': 3, # otherwise 2
            'tiomáint': 3, # otherwise 2

            'mórphearsa': 4,
            'gabhair': 4,
            'feac': 4,
            'cadhc': 4,
            'faic': 4,
            'feic': 4,
            'sonc': 4,
            'bunc': 4,
            'hurlamaboc': 4,
            'trioc': 4,
            'stad': 4,
            'leathstad': 4,
            'grianstad': 4,
            'lánstad': 4,
            'idirstad': 4,
            'leagáid': 4,
            'iarmhéid': 4,
            'uasmhéid': 4,
            'bréid': 4,
            'triuf': 4,
            'dallamullóg': 4,
            'tiubh': 4,
            'neach': 4,
            'trach': 4,
            'bláthchuach': 4,
            'imchuach': 4,
            'cách': 4,
            'fáidh': 4,
            'príomháidh': 4,
            'aodh': 4,
            'anraith': 4,
            'líonrith': 4,
            'clíth': 4,
            'ceal': 4,
            'meal': 4,
            'Iúil': 4,
            'pléiseam': 4,
            'seachain': 4,
            'cliamhain': 4,
            'banchliamhain': 4,
            'dóthain': 4,
            'Céadaoin': 4,
            'Déardaoin': 4,
            'lachín': 4,
            'beainín': 4,
            'óinsín': 4,
            'bóín': 4,
            'lao': 4,
            'glao': 4,
            'trup': 4,
            'seáp': 4,
            'lear': 4,
            'sciar': 4,
            'riar': 4,
            'paor': 4,
            'gearr': 4,
            'seacht': 4,
            'ocht': 4,
            'ceant': 4,

            'caora': 5,
            'cara': 5,
            'cathaoir': 5,
            'fearchú': 5,
            'fóir': 5,
            'onchú': 5,
            'árchú': 5,
            'leaca': 5,
            'ionga': 5,
            'Lemma': 5,
            'céimseata': 5,
            'leite': 5,
            'cabhail': 5,
            'traein': 5,
            'cáin': 5,
            'mótarcháin': 5,
            'cráin': 5,
            'coróin': 5,
            'abhainn': 5,
            'siocair': 5,
            'carcair': 5,
            'dair': 5,
            'corcdhair': 5,
            'láthair': 5,
            'lasair': 5,
            'loinnir': 5,
            'láir': 5,
            'céir': 5,
            'fíor': 5,
            'deachú': 5,
            'cian': 5,
    }


    IRREGULAR_GROUPS = (
            lambda l, g: 5 if l in FAMILY else None, # Family
    )

    # This is not simply nouns that are in unexpected
    # declensions, but the nouns in the specific sixth
    # "Irregular Declension" of miscellaneous entries.
    IRREGULAR_DECLENSION = {
            'bean': 'mná',
            'deirfiúr': 'deirfear',
            'deoch': 'dí',
            'siúr': 'siúrach',
            'dia': 'dé',
            'lá': 'lae',
            'leaba': 'leapa',
            'mí': 'míosa',
            'olann': 'olla',
            'talamh': 'talún', # Also talaimh according to An Caighdeán
            'ó': 'uí', # thanks to Nualeargais
            # teach according to An Caighdeán, see below.
    }

    # Teach family is a funny one - according to Nualeargais,
    # teach is in the 2nd Declension. BuNaMo doesn't say (which
    # can mean irregular declension or simply not assigned), and
    # An Caighdeán says Irregular.
    #
    # However, BuNaMo puts two teach derivatives into 1st Decl and
    # omits info about any of the rest (including teach itself).
    #      craobhteach and díonteach
    # Note that this is not simply masculine nouns ending in teach,
    # these all have genitives formed with -t(h)í, and seem to somehow
    # relate to houses/buildings.
    TEACH_FAMILY = (
        'cloigtheach',
        'clubtheach',
        'cléirtheach',
        'coirmtheach',
        'cruinnteach',
        'cúlteach',
        'dairtheach',
        'fiailteach',
        'fleiteach',
        'fortheach',
        'longtheach',
        'mainteach',
        'máthairtheach',
        'plódteach',
        'proinnteach',
        'rítheach',
        'teach',
        'túrtheach',
        'urtheach',
        'íolteach',
    )
    TEACH_FAMILY_1ST = (
        'craobhtheach',
        'díonteach',
    )

    def guess(self, focal: Noun):
        if len(focal.sgNom) != 1 or len(focal.sgGen) != 1:
            raise FormsMissingException(
                f'{focal.getLemma()} has {len(focal.sgNom)} nom and {len(focal.sgGen)} gen'
            )

        lemma = focal.getLemma()
        gender = focal.getGender()

        if lemma in self.IRREGULAR_DECLENSION:
            if focal.declension and focal.declension in (1, 2, 3, 4, 5):
                if focal.declension == 5:
                    logging.warning(f'{lemma}: BuNaMo puts some irregular nouns as Dec.5 (e.g. deirfúir)')
                    return 5
                raise DeclensionInconsistentError(
                    f'Irregular declension not determined as expected for {lemma}! Expected {focal.declension}',
                    -1, focal.declension
                )
            return -1

        if lemma in self.MULTIPLE_WORDS:
            match = [
                dec for dec, gen in self.MULTIPLE_WORDS[lemma]
                if gen == focal.sgGen[0].value
            ]
            if len(match) == 1:
                return match[0]
            elif not match:
                raise DeclensionInconsistentError(
                    f'Could not match any for multi-declension {lemma}!',
                    self.MULTIPLE_WORDS[lemma], focal.declension
                )
            else:
                raise FormsAmbiguousException(
                    f'Matched {len(match)} allowed declensions for {lemma}'
                )

        if lemma in self.FULLY_IRREGULAR:
            dec, gen = self.FULLY_IRREGULAR[lemma]
            if focal.sgGen[0].value != gen:
                raise DeclensionInconsistentError(
                    f'Hard-coded genitive for dec{dec} not expected for {lemma}!',
                    dec, focal.declension
                )
            if focal.declension and focal.declension != dec:
                raise DeclensionInconsistentError(
                    f'Hard-coded declension {dec} not expected for {lemma}! Expected {focal.declension}',
                    dec, focal.declension
                )
            return dec

        for matcher in self.IRREGULAR_GROUPS:
            if (mdec := matcher(lemma, gender)) is not None:
                return mdec

        # We treat the teach family separately.
        if lemma in self.TEACH_FAMILY:
            return -1
        elif lemma in self.TEACH_FAMILY_1ST:
            # This makes very little sense, when An Caighdeán
            # Oifigiúil puts teach in the Irregulars, but we
            # follow BuNaMo, and these words are only derivatives
            # of teach.
            return 1

        for n, check in enumerate(self.checks):
            dec = 5 - n
            irregular_inclusion = self.IRREGULAR_INCLUSION.get(lemma, None)
            if irregular_inclusion == dec or (not irregular_inclusion and check(focal)):
                return dec
        return 3

    # The below are private as to save
    # duplication, they assume they have been run
    # in the order above.

    def _is_fourth(self, focal: Noun):
        lemma = focal.getLemma()
        gender = focal.getGender()

        irregularly_palatalized: dict[str, str] = {}

        if lemma in POSSIBLE_LOANWORDS_GENITIVELESS + BUNAMO_ONLY_GENITIVELESS:
            return True

        # Should we even be here?
        if (
                lemma.endswith('ín') and gender is Gender.Masc

                or

                gender is Gender.Masc and
                (
                    (
                        {lemma[-i:] for i in range(1, 4)} & {'ín', 'aí', 'ú', 'nm', 'iam', 'cs', 'ts', 'ns', 'eo'}
                        or re.search('[^óoé]ir$', lemma)
                    )
                    and not re.search('[eú]ir', lemma)
                    and lemma not in FAMILY # Masc family are usu. 5th
                )

                or

                {lemma[-i:] for i in range(1, 4)} & {'a', 'e', 'í', 'le', 'ne', 'é', 'aoi', 'ó', 'á'}
            ):
            return True

        return False

    def _is_second(self, focal: Noun):
        lemma = focal.getLemma()
        gender = focal.getGender()

        mono = not Opers.PolysyllabicV2(lemma)

        monosyllabic_i = {
            'cearc',
            'beanne',
            'beann',
        }
        polysyllabic_ei = {
            'meadar',
            'maoildearg',
            'taibhdhearc',
            'seamair',
            'díthreabh',
            'taibhdhearc',
            'aershreabh',
            'bláthfhleasc',
            'bonnleac',
            'cráinbheach',
            'díthreabh',
        }

        if gender == Gender.Masc and lemma != 'im':
            return False
        if mono:
            if not Opers.IsSlender(lemma):
                return True
            ends = [
                '[^eoéú]il',
                'ói[nr]',
            ]
            if re_ends(lemma, ends):
                return False
        else:
            ends = [
                'ail',
                'ain',
                'úil',
                'is?[msrtgbcdnh]+il',
                '[pb]h?[eé]il',
                'scoil',
            ]
            if re_ends(lemma, ends):
                return True
            #if not Opers.IsSlender(lemma):
            #    return True
            ends = [
                'il',
                'aíl',
                'ói[nr]',
                'c?ht?ain',
                '[oáa]chan',
                'bh?liain',
                'ch?uid',
                'ch?air',
                'e[aá]s',
                '[bc]h?ail',
                'laim',
                #'ain',
                f'^[{Opers.Cosonants}]*[aoáóuú]+[ií]n',
                #f'[{Opers.Cosonants}]*[eéií][aoáóuú]+[^{Opers.Cosonants}]*n',
            ]
            if re_ends(lemma, ends):
                return False
        return True

    def _is_third(self, focal: Noun):
        lemma = focal.getLemma()
        gender = focal.getGender()

        unsyncopated_exceptions = (
            'athbhliain',
            'bliain',
            'bonnbhliain',
            'idirbhliain',
            'scoilbhliain',
            'solasbhliain',

            'argain',
            'cluain',
            'dúnorgain',
            'foluain',
            'fothain',

            'féachaint',
            'súilfhéachaint',
            'tuargaint',

            'marthain',

            'cantain',
            'cianrochtain',
            'comhriachtain',
            'dámhachtain',
            'fionnachtain',
            'mainneachtain',
            'rochtain',
        )

        depalatalized = SingularInfoA(
            lemma,
            gender,
            syncope=False,
            v2=True,
            with_syncopated_ai_v2=lemma not in unsyncopated_exceptions,
        )

        if lemma in unsyncopated_exceptions:
            return True

        exception_endings = (
            '[^g][aá]irt$',
            'oirt$',
            '[ds]h?úil$',
            'bh?ail$',
            'fh?iacail$',
            '[bc]h?[aú]irt$',
            #'h?[aú]int$',
            'ol$',
            '[^e]oil$',
            '[aá]ch?an$',
            'an$',
            'aol$',
            '[^úc]int$',
            'ean$',
            'us$',
        )

        if any(map(lambda end: re.search(end, lemma), exception_endings)):
            return False

        endings = [
            'áil',
            'úil',
            'ail',
            'úint',
            'cht',
            'irt',
            'áint',
            'aint',
            'cht',
            'int',
            'chtain',
            'an',
        ]

        if re_ends(lemma, endings):
            return True

        endings = [
            'int',
            'éir',
            'ain',
            'us',
            'eir',
            'eoir',
            'óir',
            'úir',
            'cht',
        ]

        if re_ends(lemma, endings) and gender == Gender.Masc:
            return True

        return False

    def _is_first(self, focal: Noun):
        lemma = focal.getLemma()
        gender = focal.getGender()

        irregularly_palatalized = {
            'mac': 'i',
            'garmhac': 'i',

            'bligeard': 'eai',
            'seac': 'eai',

            'earc': 'ei',
            'gaistreintríteas': 'ei',
            'dearg': 'ei',
            'meadhg': 'ei',
            'corcairdhearg': 'ei',
            'infridhearg': 'ei',

            'Eiritréach': 'éai',
        }

        without_iai = {
            'cliabh',
            'fiach',
            'fial',
            'giall',
        }
        palatalized = SingularInfoC(
            lemma,
            focal.getGender(),
            slenderizationTarget=(
                irregularly_palatalized.get(lemma, "")
            ),
            v2=True,
            with_iai_v2=lemma not in without_iai
            # nearly all Dec.1 nouns with ia as final
            # vowel cluster become iai, except for
            # four in BuNaMo (and any ending iasc, which
            # are handled in SingularInfoC).
        )

        ends = [
            'th',
            'lus',
            'luach',
            'mheas',
            'rás',
            'bhr?éas',
            'd.*[ou]l',
            'ch?r?[ií]os',
            'rud',
            'íoc',
        ]
        if any(map(lambda end: re.search(f'{end}$', lemma), ends)):
            return False

        ends = [
            'ios',
            'am',
            'iol',
            '[eé]as',
        ]
        if any(map(lambda end: re.search(f'{end}$', lemma), ends)) and not Opers.PolysyllabicV2(lemma):
            return False

        if lemma[:2] == 'sn' and not Opers.PolysyllabicV2(lemma):
            return False

        if re.search("([" + Opers.VowelsBroad + "]|ae)[" + Opers.Cosonants + "]*$", lemma) and gender == Gender.Masc:
            return True

        if focal.declension and focal.declension == 1:
            raise DeclensionInconsistentError(
                f'Declension 1 not determined as expected for {lemma}! Expected {focal.declension}',
                1, focal.declension
            )
        return False

    def _is_fifth(self, focal: Noun):
        lemma = focal.getLemma()
        gender = focal.getGender()
        depalatalized = SingularInfoL(lemma, gender, v2=True)

        if lemma.endswith('ceathrú') or lemma.endswith('cheathrú'):
            return True

        if depalatalized.genitive[0].value == lemma and not re.search('a(rs|ch|rch|nm)a$', lemma):
            return False

        if gender == Gender.Fem:
            if focal.sgNom[0].value[-1] in ('r', 'l', 'n'):
                syncopated_ax = SingularInfoAX(lemma, gender, syncope=False, v2=True)
                if (
                    {lemma[-i:-1] for i in range(2, 6)} & {'riai', 'tiúi'} or
                    {lemma[-i:] for i in range(1, 10)} & {'thir', 'tir', 'mhir', 'eoir', 'athair', 'ochair', 'bhair', 'eorainn'}
                ):
                    return True

                if (
                    {lemma[-i:-1] for i in range(2, 4)} & {'í', 'úi', 'ói', 'éi', 'in', 'ái'} or
                    {lemma[-i:] for i in range(1, 7)} & {'eoil', 'coil', 'tir', 'bair', 'ain', 'ir', 'ill', 'il', 'in'}
                ):
                    return False

                return True
            elif focal.sgNom[0].value[-1] in Opers.Vowels:
                modified_n = SingularInfoN(lemma, gender)

                return True

        if focal.declension and focal.declension == 5:
            raise DeclensionInconsistentError(
                f'Declension 5 not determined as expected for {lemma}! Expected {focal.declension}',
                5, focal.declension
            )
        return False
