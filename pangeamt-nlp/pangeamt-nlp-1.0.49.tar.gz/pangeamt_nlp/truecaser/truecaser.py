from sacremoses import MosesTruecaser
from sacremoses import MosesDetruecaser
import re


class _PangeaMTTruecaser(MosesTruecaser):
    def __init__(self, load_from=None, is_asr=None, encoding="utf8"):
        self.SKIP_LETTERS_REGEX = re.compile(
            u"[{}{}{}]".format(
                self.Lowercase_Letter,
                self.Uppercase_Letter,
                self.Titlecase_Letter,
            )
        )

        self.XML_SPLIT_REGX = re.compile("(<.*(?<=>))(.*)((?=</)[^>]*>)")

        self.SENT_END = {".", ":", "?", "!"}
        self.DELAYED_SENT_START = {
            "(",
            "[",
            '"',
            "'",
            "&apos;",
            "&quot;",
            "&#91;",
            "&#93;",
        }

        self.encoding = encoding

        self.is_asr = is_asr
        if load_from:
            self.model = self._load_model(load_from)

    def truecase(self, text, return_str=False, use_known=False):
        """
        Truecase a single sentence / line of text.
        :param text: A single string, i.e. sentence text.
        :type text: str
        :param use_known: Use the known case if a word is a known word but not the first word.
        :type use_known: bool
        """
        check_model_message = str(
            "\nUse Truecaser.train() to train a model.\n"
            "Or use Truecaser('modefile') to load a model."
        )
        assert hasattr(self, "model"), check_model_message
        # Keep track of first words in the sentence(s) of the line.
        is_first_word = True
        truecased_tokens = []
        tokens = self.split_xml(text)
        # best_cases = best_cases if best_cases else self.model['best']
        # known_cases = known_cases if known_cases else self.model['known']

        for i, token in enumerate(tokens):

            # Append XML tags and continue
            if re.search(r"(<\S[^>]*>)", token):
                truecased_tokens.append(token)
                continue

            # Note this shouldn't happen other if | are escaped as &#124;
            # To make the truecaser resilient,
            # we'll just any token starting with pipes as they are.
            if token == "|" or token.startswith("|"):
                truecased_tokens.append(token)
                continue

            # Reads the word token and factors separatedly
            word, other_factors = re.search(r"^([^\|]+)(.*)", token).groups()

            # Lowercase the ASR tokens.
            if self.is_asr:
                word = word.lower()

            # The actual case replacement happens here.
            # "Most frequent" case of the word.
            best_case = self.model["best"].get(word.lower(), None)
            # Other known cases of the word.
            known_case = self.model["known"].get(word, None)
            # If it's the start of sentence.
            # Truecase otherwise unknown words? Heh? From: https://github.com/
            # moses-smt/mosesdecoder/blob/master/scripts/recaser/truecase.perl#L66
            # Use always best case, i.e. most common casing
            if not word.islower() and best_case:
                word = best_case
            # Else, it's an unknown word, don't change the word.
            # Concat the truecased `word` with the `other_factors`
            word = word + other_factors
            # Adds the truecased word.
            truecased_tokens.append(word)

            # Resets sentence start if this token is an ending punctuation.
            is_first_word = word in self.SENT_END

            if word in self.DELAYED_SENT_START:
                is_first_word = False

        # return ' '.join(tokens)
        return " ".join(truecased_tokens) if return_str else truecased_tokens

    def _load_model(self, path):
        with open(path, "r") as file:
            best = {}
            known = {}
            for line in file:
                line = line.strip().split()
                most_rep = 0
                for i in range(0, len(line), 2):
                    try:
                        word = line[i]
                        count = int(line[i + 1].split("/")[0].strip("()"))
                        if count > most_rep:
                            most_rep = count
                            best[word.lower()] = word
                        known[word] = count
                    except:
                        pass
        return {"best": best, "known": known}


###############################################################################


class Truecaser:
    def __init__(self, model=None):
        if model:
            self._mtr = _PangeaMTTruecaser(model)
        self._mdr = MosesDetruecaser()

    def truecase(self, text):
        return (" ").join(self._mtr.truecase(text))

    def detruecase(self, text):
        return (" ").join(self._mdr.detruecase(text))

    train_from_file = _PangeaMTTruecaser().train_from_file
