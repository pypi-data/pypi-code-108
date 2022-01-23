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


class NualeargaisNounDeclensionGuesser(NounDeclensionGuesser):
    IRREGULAR_INCLUSION = {
        'im': 2,
        'sliabh': 2,
    }

    IRREGULAR_GROUPS = (
    )

    # This is not simply nouns that are in unexpected
    # declensions, but the nouns in the specific sixth
    # "Irregular Declension" of miscellaneous entries.
    IRREGULAR_DECLENSION = {
    }

    @property
    def checks(self):
        return [
            self._is_fifth,
            self._is_fourth,
            self._is_third,
            self._is_second,
            self._is_first,
        ]

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

        for n, check in enumerate(self.checks):
            dec = 5 - n
            irregular_inclusion = self.IRREGULAR_INCLUSION.get(lemma, None)
            if irregular_inclusion == dec or (not irregular_inclusion and check(focal)):
                return dec
        return 3

    def _is_fourth(self, focal: Noun):
        lemma = focal.getLemma()
        gender = focal.getGender()

        ends = [
            '[eí]',
        ]
        if gender == Gender.Fem and re_ends(lemma, ends):
            return True
        elif gender == Gender.Masc and re_ends(lemma, [f'[{Opers.Vowels}]', 'ín']):
            return True

        return False

    def _is_second(self, focal: Noun):
        lemma = focal.getLemma()
        gender = focal.getGender()

        if gender != Gender.Fem:
            return False

        if Opers.IsSlender(lemma):
            return True

        if re_ends(lemma, ['eog', 'óg', 'lann']):
            return True

        return False

    def _is_third(self, focal: Noun):
        lemma = focal.getLemma()
        gender = focal.getGender()

        endings = [
            'áil',
            'úil',
            'ail',
            'úint',
            'cht',
            'irt',
        ]

        if gender == Gender.Fem and re_ends(lemma, endings):
            return True

        endings = [
            'éir',
            'eoir',
            'óir',
            'úir',
        ]

        if gender == Gender.Masc and re_ends(lemma, endings):
            return True

        return False

    def _is_first(self, focal: Noun):
        lemma = focal.getLemma()
        gender = focal.getGender()

        if gender == Gender.Masc and not Opers.IsSlender(lemma):
            return True

        return False

    def _is_fifth(self, focal: Noun):
        return False

class NualeargaisFullNounDeclensionGuesser(NounDeclensionGuesser):
    IRREGULAR_INCLUSION = {
            'im': 2,
            'sliabh': 2,
            'teach': 2,

            'ainm': 4,
            'lucht': 4,
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
            'siúr': 'siúrach',
            'dia': 'dé',
            'lá': 'lae',
            'leaba': 'leapa',
            'mí': 'míosa',
            'olann': 'olla',
            'talamh': 'talún', # Also talaimh according to An Caighdeán
            'ó': 'uí', # thanks to Nualeargais
    }

    @property
    def checks(self):
        # No specific order is shown in subst1.html or dekl.htm, but
        # this sequence seems to give the fewest errors.
        return [
            (4, self._is_fourth),
            (1, self._is_first),
            (2, self._is_second),
            (5, self._is_fifth),
            # self._is_third, This is the vaguest, so leave as default
        ]

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

        for n, (dec, check) in enumerate(self.checks):
            irregular_inclusion = self.IRREGULAR_INCLUSION.get(lemma, None)
            if irregular_inclusion == dec or (not irregular_inclusion and check(focal)):
                return dec
        return 3

    def _is_fourth(self, focal: Noun):
        lemma = focal.getLemma()
        gender = focal.getGender()

        # "A few that end in a consonant (often foreign words...)
        if lemma in POSSIBLE_LOANWORDS_GENITIVELESS and lemma[-1] in Opers.Cosonants:
            return True

        if gender == Gender.Fem:
            return False

        if re_ends(lemma, [f'[{Opers.Vowels}]', 'ín']):
            return True

        return False

    def _is_second(self, focal: Noun):
        lemma = focal.getLemma()
        gender = focal.getGender()

        if gender != Gender.Fem or lemma[-1] in Opers.Vowels:
            return False

        return True

    def _is_first(self, focal: Noun):
        lemma = focal.getLemma()
        gender = focal.getGender()

        if gender == Gender.Masc and not Opers.IsSlender(lemma):
            return True

        return False

    def _is_fifth(self, focal: Noun):
        lemma = focal.getLemma()
        gender = focal.getGender()

        # Family relations are dealt with already

        if not gender == Gender.Fem:
            return False

        if Opers.IsSlender(lemma):
            return True

        if lemma[-1] in Opers.Vowels:
            return True

        return False
