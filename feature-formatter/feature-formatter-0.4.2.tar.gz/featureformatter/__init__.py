import re
import string

import num2words

CURRENCY_WORD_MAPPING = {
    "en": {"$": "dollar", "€": "euro", "£": "pound"},
    "de": {"$": "Dollar", "€": "Euro", "£": "Pfund"},
    "fr": {"$": "dollar", "€": "euro", "£": "livre"},
    "es": {"$": "dólar", "€": "euro", "£": "libra"},
    "pt": {"$": "dólar", "€": "euro", "£": "libra"},
    "it": {"$": "dollaro", "€": "euro", "£": "libbra"},
    "sv": {"$": "dollar", "€": "euro", "£": "pund"},
    "da": {"$": "dollar", "€": "euro", "£": "pund"},
    "fi": {"$": "dollari", "€": "euroa", "£": "punta"},
    "no": {"$": "dollar", "€": "euro", "£": "pund"},
    "ru": {"$": "доллар", "€": "евро", "£": "фунт"},
}

INVALID_CHARS = {
    "en": r"[^a-zA-Z]",
    "de": r"[^a-zA-ZäöüÄÖÜß]",
    "fr": r"[^a-zA-ZÀ-ÿ]",
    "es": r"[^a-zA-ZÀ-ÿáéíñúüÁÉÍÑÓÚÜ]",
    "pt": r"[^a-zA-ZÀ-ÿ]",
    "it": r"[^a-zA-ZÀ-ÿ]",
    "sv": r"[^a-zA-ZÆØÅÄÖæøåäöÉÈÊÓÒÂÔéèêóòâôç]",
    "da": r"[^a-zA-ZÆØÅÄÖæøåäöÉÈÊÓÒÂÔéèêóòâôç]",
    "fi": r"[^a-zA-ZÅÄÖåäöŠšŽž]",
    "no": r"[^a-zA-ZÆØÅæøåÉÈÊÓÒÂÔéèêóòâôç]",
    "ru": r"[^А-Яа-яЁё]",
}

PERCENT_WORD = {
    "en": "percent",
    "de": "Prozent",
    "fr": "pour cent",
    "es": "por ciento",
    "pt": "por cento",
    "it": "per cento",
    "sv": "procent",
    "da": "procent",
    "fi": "prosenttia",
    "no": "prosent",
    "ru": "процентов",
}
AND_WORD = {
    "en": "and",
    "de": "und",
    "fr": "et",
    "es": "y",
    "pt": "e",
    "it": "e",
    "sv": "och",
    "da": "og",
    "fi": "ja",
    "no": "og",
    "ru": "и",
}

METRIC_WORD = {
    "en": {
        "km/h": "kilometers per hour",
        "mph": "miles per hour",
        "m/s": "meters per second",
        "kg": "kilogram",
        "cm": "centimeter",
    },
    "de": {
        "km/h": "Kilometer pro Stunde",
        "mph": "Meilen pro Stunde",
        "m/s": "Meter pro Sekunde",
        "kg": "Kilogramm",
        "cm": "Zentimeter",
    },
    "fr": {
        "km/h": "kilomètres par heure",
        "mph": "miles par heure",
        "m/s": "mètres par seconde",
        "kg": "kilogramme",
        "cm": "centimètre",
    },
    "es": {
        "km/h": "kilómetros por hora",
        "mph": "millas por hora",
        "m/s": "metros por segundo",
        "kg": "kilogramo",
        "cm": "centímetro",
    },
    "pt": {
        "km/h": "quilometros por hora",
        "mph": "milhas por hora",
        "m/s": "metros por segundo",
        "kg": "quilograma",
        "cm": "centímetro",
    },
    "it": {
        "km/h": "chilometri all'ora",
        "mph": "miglia all'ora",
        "m/s": "metri al secondo",
        "kg": "chilogrammo",
        "cm": "centimetro",
    },
    "sv": {
        "km/h": "kilometer i timmen",
        "mph": "Mil per timme",
        "m/s": "meter per sekund",
        "kg": "kilogram",
        "cm": "centimeter",
    },
    "da": {
        "km/h": "kilometer i timen",
        "mph": "mil i timen",
        "m/s": "meter i sekundet",
        "kg": "kilogram",
        "cm": "centimeter",
    },
    "fi": {
        "km/h": "kilometriä tunnissa",
        "mph": "mailia tunnissa",
        "m/s": "metriä sekunnissa",
        "kg": "kilogramma",
        "cm": "senttimetri",
    },
    "no": {
        "km/h": "kilometer i timen",
        "mph": "miles per time",
        "m/s": "meter per sekund",
        "kg": "kilogram",
        "cm": "centimeter",
    },
    "ru": {
        "km/h": "километров в час",
        "mph": "миль в час",
        "m/s": "метры в секунду",
        "kg": "килограмм",
        "cm": "сантиметр",
    },
}

YEAR_PRECEEDING_WORDS = {
    "en": ["in", "year", "before", "after", "since"],
    "de": ["im", "jahr", "vor", "ab", "seit"],
    "fr": ["en", "année", "l'année", "avant", "depuis"],
    "es": ["en", "año", "desde"],
    "pt": ["em", "ano", "antes"],
    "it": ["nel", "anno", "prima"],
    "sv": ["år"],
    "da": ["år"],
    "fi": ["vuosi", "vuonna"],
    "no": ["år", "i"],
    "ru": ["в"],
}

# the dict key is regex
# in case of list: [sub regex, findall index, replace text for change_list]
ABBR_WORDS = {
    "en": {
        r"\ba\.m\.": "am",
        r"\bp\.m\.": "pm",
        r"\bmr[\. ]": "mister",
        r"\bmrs[\. ]": "missus",
        r"\bms[\. ]": "mizz",
        r"\bdr[\. ]": "doctor",
        r"\bprof[\. ]": "professor",
        r"\bcapt[\. ]": "captain",
        r"\betc\b": "et cetera",
        r"\bvs[\. ]": "versus",
        r"\bdept\.": "department",
        r"\bapprox\.": "approximately",
        r"\best\.": "established",
        r"\bmisc\.": "miscellaneous",
        r"\be\.g\.": "for example",
        r"\btv\b": "T V",
        r"\b(no\.) ?(\d+)": (r"number \2", 0, "number"),
    },
    "de": {
        r"\bz\.B\. ": "zum Beispiel",
        r"\bbzw\.": "beziehungsweise",
        r"\busw\.": "und so weiter",
        r"\betw\.": "etwas",
        r"\bBhf\.": "Bahnhof",
        r"\bHbf\.": "Hauptbahnhof",
        r"\bNr\.": "Nummer",
        r"\bStr\.": "Straße",
        r"\bca\.": "circa",
        r"\bDr\.": "Doktor",
        r"\bTel\.": "Telefon",
        r"\bMwSt\.": "Mehrwertsteuer",
        r"\bMWSt\.": "Mehrwertsteuer",
        r"\bPLZ\b": "Postleitzahl",
        r"\bNK\b": "Nebenkosten",
    },
    "fr": {
        r"\bAuj\. ": "aujourd'hui",
        r"\bEx.\.": "exemple",
        r"\bQQ\b": "quelque",
        r"\bQQ'un\b": "quelqu'un",
        r"\bS\.": "siècle",
    },
    "es": {
        r"\bSra\. ": "señora",
        r"\bSr\.": "señor",
        r"\bSrta\.": "señorita",
        r"\bDña\.": "doña",
        r"\bS\.": "siècle",
    },
    "pt": {
        r"\ba\.C\. ": "antes de cristo",
        r"\bDr\.": "doutor",
        r"\bDra\.": "doutora",
        r"\bEx\.": "exemplo",
        r"\bSr\.": "senhor",
        r"\bSra\.": "senhora",
    },
}

ABBR_SEARCH_FLAG = {
    "de": 0,
}


class BaseFormatter:
    def __init__(self, lang="en"):
        if lang not in [
            "en",
            "de",
            "fr",
            "es",
            "pt",
            "it",
            "ru",
            "da",
            "sv",
            "fi",
            "no",
        ]:
            raise Exception("language not implemented")

        self.lang = lang


class TextFormatter(BaseFormatter):
    def __init__(self, lang="en", return_case=0):
        super().__init__(lang)
        # the purpose is to remove ambiguity of cases
        # in German it might be unnecessary

        """
        return case:
            0: no change
            1: upper
            -1: lower
        """

        self.return_case = return_case

        self.__cache = {}

    def n2w(self, word, to="cardinal"):
        word = re.sub(r"[^0-9]", "", word)
        word = word[:15]  # 999 trillion most, should not handle too long digits
        numword = num2words.num2words(int(word), to=to, lang=self.lang)
        numword = numword.replace(",", "").replace("-", " ")
        return numword.split()

    def is_currency(self, word):
        symbol = word[0]
        name = CURRENCY_WORD_MAPPING.get(self.lang).get(symbol)
        if name and re.match(r"^[\d,]+$", word[1:]):
            value = re.sub(r"[^0-9]", "", word[1:])  # return string
            if int(value) > 1:
                if self.lang in ["en", "fr"]:
                    name += "s"
                elif self.lang in ["es", "pt"]:
                    if symbol == "$":
                        name += "es"
                    else:
                        name += "s"
                elif self.lang == "it":
                    if symbol in ["$", "£"]:
                        name = name[:-1] + "i"
                # German: no change
            return name, value
        return None

    def roman2w(self, s):
        rom_val = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
        int_val = 0
        for i in range(len(s)):
            if i > 0 and rom_val[s[i]] > rom_val[s[i - 1]]:
                int_val += rom_val[s[i]] - 2 * rom_val[s[i - 1]]
            else:
                int_val += rom_val[s[i]]
        return self.n2w(str(int_val))

    def remove_invalid_chars(self, text):
        return re.sub(INVALID_CHARS.get(self.lang), "", text)

    def is_valid_non_punc_char(self, c):
        if c in string.punctuation:
            return False

        return ord(c) < 128 or not re.match(INVALID_CHARS.get(self.lang), c)

    def contains_metric(self, word):
        w = word.lower()
        keys = METRIC_WORD.get(self.lang, {}).keys()
        for k in keys:
            if w.endswith(k):
                return k
        return None

    def same_case(self, word, ending):
        if word[-1] == word[-1].lower():
            return ending.lower()

        return ending.upper()

    def wrap_case(self, word):
        if self.return_case == 0:
            return word

        return word.lower() if self.return_case == -1 else word.upper()

    def plural_ending(self, word):
        if self.lang == "en":
            last_lower = word[-1].lower()
            if last_lower == "s":
                return word  # already plural
            if last_lower == "y":
                return word[:-1] + self.same_case(word, "ies")
            return word + self.same_case(word, "s")
        return word

    def preprocess_text(self, text):
        text = text.strip()

        # remove punctuation
        c_list = []
        for idx, c in enumerate(text):
            is_valid = False

            # replace common typing errors
            if c == "’":
                c = "'"
            elif c == "–":
                c = "-"

            if c == "%" or c == "&" or c == "/" or c == ".":
                # dot should be handled specially for abbr
                is_valid = True
            elif (
                c == "'"
                and idx > 0
                and text[idx - 1] != " "
                and (
                    (
                        idx + 1 < len(text)
                        and (text[idx + 1].isalpha() or text[idx - 1].lower() == "s")
                    )
                    or (idx + 1 == len(text) and text[idx - 1].lower() == "s")
                )
            ):
                is_valid = True
            elif (
                c == "-"
                and idx > 0
                and text[idx - 1] != " "
                and idx + 1 < len(text)
                and text[idx + 1] != " "
            ):
                is_valid = True
            elif (
                c in [",", ":"]
                and idx > 0
                and text[idx - 1].isdigit()
                and idx + 1 < len(text)
                and text[idx + 1].isdigit()
            ):
                is_valid = True  # finance number, or time
            elif c in CURRENCY_WORD_MAPPING[self.lang]:
                is_valid = True
            elif self.is_valid_non_punc_char(c):
                is_valid = True

            if is_valid:
                c_list.append(c)
            else:
                c_list.append(" ")  # adding a space, it will be trimmed later on

        text = "".join(c_list)

        return text

    def word_splitter(self, text):
        # can be overwritten
        text = text.replace(".", " ")
        return [t for t in text.split() if t]

    def format_text(self, text):
        """
        a whitelisted fashion as opposed to tokenizing
        """
        original_text = text
        if self.__cache.get(original_text):
            return self.__cache.get(original_text)

        text = self.preprocess_text(text)

        word_list = []
        change_list = {}

        # handle dot and abbr words first
        # so it not confuses with period and illegal dots
        search_flag = ABBR_SEARCH_FLAG.get(self.lang, re.IGNORECASE)
        for abbr, repl in ABBR_WORDS.get(self.lang, {}).items():
            if isinstance(repl, tuple):
                repl_reg, repl_idx, repl_string = repl
            else:
                repl_reg = repl + " "
                repl_string = repl
                repl_idx = -1

            for found in re.findall(abbr, text, flags=search_flag):
                if repl_idx == -1:
                    change_list[found] = self.wrap_case(repl_string)
                else:
                    change_list[found[repl_idx]] = self.wrap_case(repl_string)
            text = re.sub(abbr, repl_reg, text, flags=search_flag)

        text_iter = self.word_splitter(text)

        for idx, word in enumerate(text_iter):
            if not word:
                continue

            to_append = None

            if (
                len(word) == 4
                and word.isdigit()
                and (
                    int(word) < 2100
                    and int(word) > 1700
                    or idx > 0
                    and text_iter[idx - 1].lower()
                    in YEAR_PRECEEDING_WORDS.get(self.lang, [])
                )
            ):
                # this needs further improvements
                # in (year) 1900
                # match year before matching numbers
                # this is a best-guess approach
                to_append = self.n2w(word, to="year")
            elif re.match(r"^[\d,]+$", word):  # number or number with comma
                to_append = self.n2w(word)
            elif re.match(
                r"^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]*$", word
            ):  # complete telephone number regex, although it will only be like 123-123-123
                to_append = []
                for digit in re.sub("[^0-9]", "", word):
                    to_append += self.n2w(digit)
            elif "%" in word:
                newword = word.replace("%", "")
                if newword.isdigit():
                    to_append = self.n2w(newword) + [PERCENT_WORD.get(self.lang)]
                else:
                    newword = self.remove_invalid_chars(newword)
                    to_append = [newword, PERCENT_WORD.get(self.lang)]
            elif "&" in word:
                newword = word.replace("&", f" {AND_WORD.get(self.lang)} ")
                to_append = newword.strip().split()
            elif "-" in word:
                to_append = word.split("-")
            elif ":" in word:
                to_append = []
                for t in word.split(":"):
                    to_append += self.n2w(t)
            elif self.contains_metric(word):
                k = self.contains_metric(word)
                rep = METRIC_WORD[self.lang][k]
                to_append = word.lower().replace(k, f" {rep}").strip().split()
            elif "/" in word:
                # just ignore the slash
                to_append = word.split("/")
            elif (
                self.lang == "en"
                and len(word) > 2
                and word[:-2].isdigit()
                and word[-2:].lower() in ["th", "st", "rd", "nd"]
            ):
                # 125th
                # TODO this is English only
                to_append = self.n2w(word[:-2], to="ordinal")
            elif len(word) == 5 and word[:4].isdigit() and word[-1].lower() == "s":
                # 1900s
                to_append = self.n2w(word[:4], to="year")
                to_append[-1] = self.plural_ending(
                    to_append[-1]
                )  # nineteen hundreds instead of nineteen hundred
            elif len(word) > 2 and word[:-2].isdigit() and word[-2:].lower() == "'s":
                # 80's
                to_append = self.n2w(word[:-2])
                to_append.append(word[-2:])
            elif self.is_currency(word):
                name, value = self.is_currency(word)
                to_append = self.n2w(value)
                to_append.append(name)
            elif len(word) > 1 and re.match(
                r"^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", word
            ):
                # "I" will be One, but it is wrong. We prefer "I" to roman "One"
                # same applies for German, that M is probably a letter
                # it applis to all single X, M, I, etc.
                to_append = self.roman2w(word)
            else:
                m = re.match(
                    r"^([a-zA-Z]+)(\d+)$", word
                )  # particular case like "gate E25"
                if m:
                    if not m.group(1).lower().startswith("xx"):
                        # such as XXEY1, phonics
                        to_append = [m.group(1)] + self.n2w(m.group(2))
                else:
                    m = re.match(
                        r"^(\d+)([a-zA-Z]+)$", word
                    )  # particular case like "seat 12C"
                    if m:
                        to_append = self.n2w(m.group(1)) + [m.group(2)]

            if to_append is None:
                final_append = [word]
            else:
                # finally check whether there is still number in to_append
                final_append = []
                for ta in to_append:
                    if ta.isdigit():
                        final_append += self.n2w(ta)
                    else:
                        final_append.append(self.remove_invalid_chars(ta))

                change_list[word] = " ".join(
                    [self.wrap_case(x) for x in filter(len, final_append)]
                )

            word_list += final_append

        text = self.wrap_case(" ".join(word_list))

        self.__cache[original_text] = (text, change_list)
        return self.__cache[original_text]


class PhoneFormatter(BaseFormatter):
    def __init__(self, lang="en"):
        super().__init__(lang)

    def get_phone_root(self, phone, sep="_"):
        if not phone or phone == sep:
            return phone

        if self.lang == "en":
            phone_root = phone.split(sep)[0]
            if phone_root[-1].isdigit():
                return phone_root[:-1]

            return phone_root

        if self.lang == "de":
            # In German we have also numbers as phone code
            phone_root = (
                phone.split(sep)[0].replace("~", "").replace("'", "").replace('"', "")
            )
            return phone_root

        return phone.split(sep)[0]

    def get_phone_stress(self, phone, sep="_", return_detail=False):
        """
        0    — No stress
        1    — Primary stress
        2    — Secondary stress

        Return:
        None: no stress digit
        True/1 or 2: stress must be performed
        False/0: stress must not be performed
        """
        if not phone or phone == sep:
            return None
        if self.lang == "en":
            phone_root = phone.split(sep)[0]
            if phone_root[-1].isdigit():
                stress = int(phone_root[-1])
                return stress if return_detail else stress > 0

        return None

    def is_vowel(self, phone):
        if not phone:
            return False

        phone_root = self.get_phone_root(phone)

        if self.lang in ["it"]:
            return phone_root[0].lower() in ["a", "e", "i", "o", "u", "j"]

        # sampa common
        # https://en.wikipedia.org/wiki/SAMPA_chart
        if self.lang in ["de", "fr"]:
            return phone_root in [
                "i",
                "I",
                "e",
                "E",
                "{",
                "y",
                "Y",
                "2",
                "9",
                "1",
                "@",
                "6",
                "3",
                "a",
                "o",
                "}",
                "8",
                "&",
                "M",
                "7",
                "V",
                "A",
                "u",
                "U",
                "o",
                "O",
                "Q",
            ]

        # make aeiou it default
        return phone_root[0].lower() in ["a", "e", "i", "o", "u"]
