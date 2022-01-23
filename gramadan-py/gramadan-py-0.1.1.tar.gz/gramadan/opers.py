import re
from typing import Optional, Sequence
from .features import Mutation


class Opers:
    @staticmethod
    def PolysyllabicV2(text: str) -> bool:
        check = ("["
            + Opers.Cosonants
            + "]+["
            + Opers.Vowels
            + "]+["
            + Opers.Cosonants
            + "]+")
        # PTW: Experimental
        if Opers.EndsVowel(text):
            check = f"{check}[{Opers.Vowels}]*$"
        else:
            check = f"[{Opers.Vowels}]{check}$"

        return re.search(check, text) is not None

    @staticmethod
    def Demutate(text: str) -> str:
        pattern: str
        pattern = "^[bB][hH]([fF].*)$"
        if re.search(pattern, text):
            text = re.sub(pattern, r"\1", text)
        pattern = "^([bcdfgmpstBCDFGMPST])[hH](.*)$"
        if re.search(pattern, text):
            text = re.sub(pattern, r"\1\2", text)
        pattern = "^[mM]([bB].*)$"
        if re.search(pattern, text):
            text = re.sub(pattern, r"\1", text)
        pattern = "^[gG]([cC].*)$"
        if re.search(pattern, text):
            text = re.sub(pattern, r"\1", text)
        pattern = "^[nN]([dD].*)$"
        if re.search(pattern, text):
            text = re.sub(pattern, r"\1", text)
        pattern = "^[nN]([gG].*)$"
        if re.search(pattern, text):
            text = re.sub(pattern, r"\1", text)
        pattern = "^[bB]([pP].*)$"
        if re.search(pattern, text):
            text = re.sub(pattern, r"\1", text)
        pattern = "^[tT]([sS].*)$"
        if re.search(pattern, text):
            text = re.sub(pattern, r"\1", text)
        pattern = "^[dD]([tT].*)$"
        if re.search(pattern, text):
            text = re.sub(pattern, r"\1", text)
        pattern = "^[dD]'([fF])[hH](.*)$"
        if re.search(pattern, text):
            text = re.sub(pattern, r"\1\2", text)
        pattern = "^[dD]'([aeiouaáéíóúAEIOUÁÉÍÓÚ].*)$"
        if re.search(pattern, text):
            text = re.sub(pattern, r"\1", text)
        pattern = "^[hH]([aeiouaáéíóúAEIOUÁÉÍÓÚ].*)$"
        if re.search(pattern, text):
            text = re.sub(pattern, r"\1", text)
        pattern = "^[nN]-([aeiouaáéíóúAEIOUÁÉÍÓÚ].*)$"
        if re.search(pattern, text):
            text = re.sub(pattern, r"\1", text)
        return text

    # Performs a mutation on the string:
    @staticmethod
    def Mutate(mutation: Mutation, text: str) -> str:
        ret: str = ""
        pattern: str

        if mutation == Mutation.Len1 or mutation == Mutation.Len1D:
            # lenition 1
            if ret == "":
                pattern = "^([pbmftdcgPBMFTDCG])[jJ]"
                if re.search(pattern, text):
                    ret = text
                    # do not mutate exotic words with J in second position, like Djibouti
            if ret == "":
                pattern = "^([pbmftdcgPBMFTDCG])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"\1h\2", text)
            if ret == "":
                pattern = "^([sS])([rnlRNLaeiouáéíóúAEIOUÁÉÍÓÚ].*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"\1h\2", text)
            if ret == "":
                ret = text
            if mutation == Mutation.Len1D:
                pattern = "^([aeiouáéíóúAEIOUÁÉÍÓÚfF])(.*)$"
                if re.search(pattern, ret):
                    ret = re.sub(pattern, r"d'\1\2", ret)
        elif mutation == Mutation.Len2 or mutation == Mutation.Len2D:
            # lenition 2: same as lenition 1 but leaves "d", "t" and "s" unmutated
            if ret == "":
                pattern = "^([pbmftdcgPBMFTDCG])[jJ]"
                if re.search(pattern, text):
                    ret = text
                    # do not mutate exotic words with J in second position, like Djibouti
            if ret == "":
                pattern = "^([pbmfcgPBMFCG])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"\1h\2", text)
            if ret == "":
                ret = text
            if mutation == Mutation.Len2D:
                pattern = "^([aeiouáéíóúAEIOUÁÉÍÓÚfF])(.*)$"
                if re.search(pattern, ret):
                    ret = re.sub(pattern, r"d'\1\2", ret)
        elif mutation == Mutation.Len3 or mutation == Mutation.Len3D:
            # lenition 3: same as lenition 2 but also changes "s" into "ts"
            if ret == "":
                pattern = "^([pbmftdcgPBMFTDCG])[jJ]"
                if re.search(pattern, text):
                    ret = text
                    # do not mutate exotic words with J in second position, like Djibouti
            if ret == "":
                pattern = "^([pbmfcgPBMFCG])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"\1h\2", text)
            if ret == "":
                pattern = "^([sS])([rnlRNLaeiouáéíóúAEIOUÁÉÍÓÚ].*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"t\1\2", text)
            if ret == "":
                ret = text
            if mutation == Mutation.Len3D:
                pattern = "^([aeiouáéíóúAEIOUÁÉÍÓÚfF])(.*)$"
                if re.search(pattern, ret):
                    ret = re.sub(pattern, r"d'\1\2", ret)
        elif mutation == Mutation.Ecl1:
            # eclisis 1
            if ret == "":
                pattern = "^([pP])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"b\1\2", text)
            if ret == "":
                pattern = "^([bB])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"m\1\2", text)
            if ret == "":
                pattern = "^([fF])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"bh\1\2", text)
            if ret == "":
                pattern = "^([cC])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"g\1\2", text)
            if ret == "":
                pattern = "^([gG])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"n\1\2", text)
            if ret == "":
                pattern = "^([tT])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"d\1\2", text)
            if ret == "":
                pattern = "^([dD])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"n\1\2", text)
            if ret == "":
                pattern = "^([aeiuoáéíúó])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"n-\1\2", text)
            if ret == "":
                pattern = "^([AEIUOÁÉÍÚÓ])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"n\1\2", text)
        elif mutation == Mutation.Ecl1x:
            # eclisis 1x: same as eclipsis 1 but leaves vowels unchanged
            if ret == "":
                pattern = "^([pP])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"b\1\2", text)
            if ret == "":
                pattern = "^([bB])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"m\1\2", text)
            if ret == "":
                pattern = "^([fF])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"bh\1\2", text)
            if ret == "":
                pattern = "^([cC])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"g\1\2", text)
            if ret == "":
                pattern = "^([gG])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"n\1\2", text)
            if ret == "":
                pattern = "^([tT])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"d\1\2", text)
            if ret == "":
                pattern = "^([dD])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"n\1\2", text)
        elif mutation == Mutation.Ecl2:
            # eclipsis 2: same as eclipsis 1 but leaves "t", "d" and vowels unchanged
            if ret == "":
                pattern = "^([pP])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"b\1\2", text)
            if ret == "":
                pattern = "^([bB])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"m\1\2", text)
            if ret == "":
                pattern = "^([fF])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"bh\1\2", text)
            if ret == "":
                pattern = "^([cC])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"g\1\2", text)
            if ret == "":
                pattern = "^([gG])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"n\1\2", text)
        elif mutation == Mutation.Ecl3:
            # eclipsis 3: same as eclipsis 2 but also changes "s" to "ts"
            if ret == "":
                pattern = "^([pP])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"b\1\2", text)
            if ret == "":
                pattern = "^([bB])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"m\1\2", text)
            if ret == "":
                pattern = "^([fF])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"bh\1\2", text)
            if ret == "":
                pattern = "^([cC])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"g\1\2", text)
            if ret == "":
                pattern = "^([gG])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"n\1\2", text)
            if ret == "":
                pattern = "^([sS])([rnlRNLaeiouáéíóúAEIOUÁÉÍÓÚ].*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"t\1\2", text)
        elif mutation == Mutation.PrefT:
            # t-prefixation
            if ret == "":
                pattern = "^([aeiuoáéíúó])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"t-\1\2", text)
            if ret == "":
                pattern = "^([AEIUOÁÉÍÚÓ])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"t\1\2", text)
        elif mutation == Mutation.PrefH:
            # h-prefixation
            if ret == "":
                pattern = "^([aeiuoáéíúóAEIUOÁÉÍÚÓ])(.*)$"
                if re.search(pattern, text):
                    ret = re.sub(pattern, r"h\1\2", text)

        if ret == "":
            ret = text
        return ret

    # Tells you whether the string ends in a "dentals" cosonant:
    @staticmethod
    def EndsDental(txt: str) -> bool:
        return re.search("[dntsDNTS]$", txt) is not None

    # Tells you whether the string ends in a slender consonant cluster:
    @staticmethod
    def IsSlender(txt: str) -> bool:
        return re.search("[eiéí][^aeiouáéíóú]+$", txt) is not None

    # Tells you whether the string ends in a slender consonant cluster where the slenderness is caused by an "i" (and not by an "e"):
    @staticmethod
    def IsSlenderI(txt: str) -> bool:
        return re.search("[ií][^aeiouáéíóú]+$", txt) is not None

    # Tells you whether the string has a vowel or 'fh' (but not 'fhl' or 'fhr') at its start:
    @staticmethod
    def StartsVowelFhx(txt: str) -> bool:
        ret: bool = False
        if re.search("^[aeiouáéíóúAEIOUÁÉÍÓÚ]", txt):
            ret = True
        if re.search("^fh[^lr]", txt, re.I):
            ret = True
        return ret

    # Tells you whether the string ends in a vowel:
    @staticmethod
    def EndsVowel(txt: str) -> bool:
        ret: bool = False
        if re.search("[aeiouáéíóúAEIOUÁÉÍÓÚ]$", txt):
            ret = True
        return ret

    # Tells you whether the string starts in a vowel:
    @staticmethod
    def StartsVowel(txt: str) -> bool:
        ret: bool = False
        if re.search("^[aeiouáéíóúAEIOUÁÉÍÓÚ]", txt):
            ret = True
        return ret

    # Tells you whether the string starts in F followed by a vowel:
    @staticmethod
    def StartsFVowel(txt: str) -> bool:
        ret: bool = False
        if re.search("^[fF][aeiouáéíóúAEIOUÁÉÍÓÚ]", txt):
            ret = True
        return ret

    # Tells you whether the string starts in b, m, p:
    @staticmethod
    def StartsBilabial(txt: str) -> bool:
        ret: bool = False
        if re.search("^[bmpBMP]", txt):
            ret = True
        return ret

    # Character types, for convenience when writing regular expressions:
    Cosonants: str = "bcdfghjklmnpqrstvwxz"
    Vowels: str = "aeiouáéíóú"
    VowelsBroad: str = "aouáóú"
    VowelsSlender: str = "eiéí"

    # Performs regular slenderization (attenuation): if the base ends in a consonant, and if the vowel cluster immediately before this consonant
    # ends in a broad vowel, then it changes this vowel cluster such that it ends in a slender vowel now.
    # Note: a base that's already slender passes through unchanged.
    @staticmethod
    def Slenderize(bayse: str, v2: bool = False, with_ei_v2: bool = False) -> str:
        ret: str = bayse

        sources: Sequence[str] = ("ea", "éa", "ia", "ío", "io", "iu", "ae")
        targets: Sequence[str] = ("ei" if v2 and with_ei_v2 else "i", "éi", "éi", "í", "i", "i", "aei")
        match: Optional[re.Match]
        for source, target in zip(sources, targets):
            infix = Opers.Cosonants
            if v2:
                # This seems to fix matching for
                # first declension nouns that end in e.g. uíomh,
                # such as forms of suíomh, cosnaíoch, claíomh, Haváíoch, diúlfaíoch, eachraíos, cómhaíomh, fuíoll,
                # Craíoch, maíomh, Traíoch, Molacaíoch, buíoc...
                infix += Opers.VowelsBroad
            match = re.search(
                "^(.*["
                + infix
                + "])?"
                + source
                + "(["
                + Opers.Cosonants
                + "]+)$",
                bayse,
            )
            if match:
                g1 = match.group(1) or ''
                ret = g1 + target + match.group(2)
                return ret

        # The generic case: insert "i" at the end of the vowel cluster:
        match = re.search(
            "^(.*[" + Opers.VowelsBroad + "])([" + Opers.Cosonants + "]+)$", bayse
        )
        if match:
            g1 = match.group(1) or ''
            ret = g1 + "i" + match.group(2)

        return ret

    # Performs irregular slenderization (attenuation): if the base ends in a consonant, and if the vowel cluster immediately before this consonant
    # ends in a broad vowel, then it changes this vowel cluster into the target (the second argument).
    # Note: if the target does not end in a slender vowel, then regular slenderization is attempted instead.
    # Note: a base that's already attenuated passes through unchanged.
    @staticmethod
    def SlenderizeWithTarget(bayse: str, target: str, v2: bool = False, with_ei_v2: bool = False) -> str:
        ret: str = bayse
        if not re.search("[" + Opers.VowelsSlender + "]$", target):
            ret = Opers.Slenderize(bayse, v2=v2, with_ei_v2=with_ei_v2)
            # attempt regular slenderization instead
        else:
            match: Optional[re.Match] = re.search(
                "^(.*?)["
                + Opers.Vowels
                + "]*["
                + Opers.VowelsBroad
                + "](["
                + Opers.Cosonants
                + "]+)$",
                bayse,
            )
            if match:
                g1 = match.group(1) or ''
                ret = g1 + target + match.group(2)
        return ret

    # Performs regular broadening: if the base ends in a consonant, and if the vowel cluster immediately before this consonant
    # ends in a slender vowel, then it changes this vowel cluster such that it ends in a broad vowel now.
    # Note: a base that's already broad passes through unchanged.
    @staticmethod
    def Broaden(bayse: str, with_io_v2: bool = False) -> str:
        ret: str = bayse

        sources: Sequence[str] = ("ói", "ei", "éi", "i", "aí", "í", "ui", "io")
        if not with_io_v2:
            # PTW: the final entry looks out of place, and fails for siocair, 4thD gen.
            # so this makes it a special request - for nouns, it seems to only appear
            # in 3rdD, e.g. crios, riocht
            sources = sources[:-1]
        targets: Sequence[str] = ("ó", "ea", "éa", "ea", "aío", "ío", "o", "ea")
        match: Optional[re.Match]
        for source, target in zip(sources, targets):
            match = re.search(
                "^(.*["
                + Opers.Cosonants
                + "])?"
                + source
                + "(["
                + Opers.Cosonants
                + "]+)$",
                bayse,
            )
            if match:
                g1 = match.group(1) or ''
                ret = g1 + target + match.group(2)
                return ret

        # The generic case: remove "i" from the end of the vowel cluster:
        match = re.search("^(.*)i([" + Opers.Cosonants + "]+)$", bayse)
        if match:
            ret = match.group(1) + match.group(2)

        return ret

    # Performs irregular broadening: if the base ends in a consonant, and if the vowel cluster immediately before this consonant
    # ends in a slender vowel, then it changes this vowel cluster into the target (the second argument).
    # Note: if the target does not end in a broad vowel, then regular broadening is attempted instead.
    # Note: a base that's already broad passes through unchanged.
    @staticmethod
    def BroadenWithTarget(bayse: str, target: str, with_io_v2: bool = False) -> str:
        ret: str = bayse
        if not re.search("[" + Opers.VowelsBroad + "]$", target):
            ret = Opers.Broaden(bayse, with_io_v2=with_io_v2)
            # attempt regular broadening instead
        else:
            match: Optional[re.Match] = re.search(
                "^(.*?)["
                + Opers.Vowels
                + "]*["
                + Opers.VowelsSlender
                + "](["
                + Opers.Cosonants
                + "]+)$",
                bayse,
            )
            if match:
                ret = match.group(1) + target + match.group(2)
        return ret

    # If the final consonant cluster consists of two consonants that differ in voicing,
    # and if neither one of them is "l", "n" or "r", then devoices the second one.
    @staticmethod
    def Devoice(bayse: str) -> str:
        ret: str = bayse
        match: Optional[re.Match] = re.search("^(.*)sd$", bayse)
        if match:
            ret = match.group(1) + "st"
            return ret
        # May need elaboration.
        return ret

    # Reduces any duplicated consonants at the end into a single consonant.
    @staticmethod
    def Unduplicate(bayse: str) -> str:
        ret: str = bayse

        match: Optional[re.Match] = re.search(
            "^.*[" + Opers.Cosonants + "][" + Opers.Cosonants + "]$", bayse
        )
        if match and bayse[len(bayse) - 1] == bayse[len(bayse) - 2]:
            ret = bayse[: len(bayse) - 1]

        return ret

    # Performs syncope by removing the final vowel cluster,
    # then unduplicates and devoices the consonant cluster at the end.
    @staticmethod
    def Syncope(bayse: str, v2: bool = False) -> str:
        ret: str = bayse

        match: Optional[re.Match] = re.search(
            "^(.*["
            + Opers.Cosonants
            + "])?["
            + Opers.Vowels
            + "]+(["
            + Opers.Cosonants
            + "]+)$",
            bayse,
        )
        if match:
            g1 = match.group(1) or ''
            ret = Opers.Devoice(Opers.Unduplicate(g1 + match.group(2)))
            if v2 and any(pair in ret for pair in ('ln', 'dl', 'nl', 'dn', 'nd')):
                # PTW: thanks to http://www.nualeargais.ie/gnag/palat.htm for codladh
                if ret in ('codladh', 'caibidl'):
                    return ret
                go = True
                # PTW: Ensure we only check actually modified characters
                prefix = [b for b, r in zip(bayse, ret) if go and (b == r or (go := False))]
                suffix = ret[len(prefix) - 2:]
                # PTW: I think we need to confirm the final unsyncopated characters aren't
                # an l/n/d pair before modifying below, as e.g. coinneal->coinnle not coinlle
                suffix = re.sub("([^lnd])(ln|dl|nl)", r"\1ll", suffix)
                suffix = re.sub("([^lnd])(dn|nd)", "nn", suffix)
                ret = ''.join(prefix[:-2]) + suffix

        return ret

    @staticmethod
    def HighlightMutations(text: str, bayse: str = "") -> str:
        text = re.sub(
            "(^| )([cdfgmpst])(h)", r"\1\2<u class='lenition'>\3</u>", text, re.I
        )
        text = re.sub(
            "(^| )(b)(h)([^f])", r"\1\2<u class='lenition'>\3</u>$4", text, re.I
        )
        text = re.sub("(^| )(t)(s)", r"\1<u class='lenition'>\2</u>\3", text, re.I)
        text = re.sub("(^| )(m)(b)", r"\1<u class='eclipsis'>\2</u>\3", text, re.I)
        text = re.sub("(^| )(g)(c)", r"\1<u class='eclipsis'>\2</u>\3", text, re.I)
        text = re.sub("(^| )(n)(d)", r"\1<u class='eclipsis'>\2</u>\3", text, re.I)
        text = re.sub("(^| )(bh)(f)", r"\1<u class='eclipsis'>\2</u>\3", text, re.I)
        text = re.sub("(^| )(n)(g)", r"\1<u class='eclipsis'>\2</u>\3", text, re.I)
        text = re.sub("(^| )(b)(p)", r"\1<u class='eclipsis'>\2</u>\3", text, re.I)
        text = re.sub("(^| )(d)(t)", r"\1<u class='eclipsis'>\2</u>\3", text, re.I)
        text = re.sub(
            "(^| )(n-)([aeiouáéíóú])", r"\1<u class='eclipsis'>\2</u>\3", text
        )
        if not bayse.startswith("n"):
            text = re.sub(
                "(^| )(n)([AEIOUÁÉÍÓÚ])", r"\1<u class='eclipsis'>\2</u>\3", text
            )
        if not bayse.startswith("t-"):
            text = re.sub(
                "(^| )(t-)([aeiouáéíóú])", r"\1<u class='lenition'>\2</u>\3", text
            )
        if not bayse.startswith("t"):
            text = re.sub(
                "(^| )(t)([AEIOUÁÉÍÓÚ])", r"\1<u class='lenition'>\2</u>\3", text
            )
        if not bayse.startswith("h"):
            text = re.sub(
                "(^| )(h)([aeiouáéíóú])", r"\1<u class='lenition'>\2</u>\3", text, re.I
            )
        return text

    @classmethod
    def Prefix(cls, prefix: str, body: str) -> str:
        m: Mutation = Mutation.Len1
        if Opers.EndsDental(prefix):
            m = Mutation.Len2
            # pick the right mutation
        if prefix[len(prefix) - 1] == body[0]:
            prefix += "-"
            # eg. "sean-nós"
        if cls.EndsVowel(prefix) and cls.StartsVowel(body):
            prefix += "-"
            # eg. "ró-éasca"
        if body[0:1] == body[0:1].upper():  # eg. "seanÉireannach" > "Sean-Éireannach"
            prefix = prefix[0:1].upper() + prefix[1:]
            if not prefix.endswith("-"):
                prefix += "-"

        ret: str = prefix + cls.Mutate(m, body)
        return ret
