import re as _re
import json as _json
import os as _os
from typing import List
from pangeamt_nlp.seg import Seg
from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase


NGRAM_PATH = _os.path.join(
    _os.path.dirname(_os.path.realpath(__file__)), "ngram_probs.json"
)
with open(NGRAM_PATH, "r") as ngram_file:
    NGRAM_PROBS = _json.load(ngram_file)


class GermanCompoundSplitterNormalizer(NormalizerBase):

    NAME = "german_compound_splitter"
    DESCRIPTION_TRAINING = """
        Applies the german compound splitter to src or tgt, checking
        with the src_lang and tgt_lang to decide where to apply it.
    """
    DESCRIPTION_DECODING = """
        Apply the german compound splitter process to src if src_lang is
        german, do nothing otherwise.
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        if src_lang is not "de" and tgt_lang is not "de":
            raise ValueError("Americanizer processor requires German")

        super().__init__(src_lang, tgt_lang)
        self._regex = _re.compile(r'([ ,;:\.\{\}\[\]\/\\\(\)\?¡"\'])')

    def process_train(self, seg: Seg) -> None:
        if self.src_lang == "de":
            seg.src = self.normalize(seg.src)
        else:
            seg.tgt = self.normalize(seg.tgt)

    def process_src_decoding(self, seg: Seg) -> None:
        if self.src_lang == "de":
            seg.src = self.normalize(seg.src)

    def process_tgt_decoding(self, seg: Seg) -> None:
        pass

    def normalize(self, txt: str) -> str:
        entry = self._regex.split(txt)
        result = list()
        for item in entry:
            tmp = self.split_compound(item)[0]
            if tmp[0] == 0.0 or tmp[0] < -0.6:
                result.append(item)
            elif tmp[0] == 1:
                for i, item in enumerate(tmp):
                    if i > 0:
                        result.append(item)
                        result.append(" ")
            else:
                result.append(tmp[1])
                result.append(" ")
                result.append(tmp[2])
        return "".join(result)

    def split_compound(self, word: str) -> List:
        """ Return list of possible splits, best first """

        # If there is a hypen in the word, return part of the word
        # behind the last hyphen.
        if "-" in word:
            tmp = word.split("-")
            for item in tmp:
                if item.isdigit():
                    tmp.insert(0, 0.0)
                    return [tmp]
            tmp.insert(0, 1.0)
            return [tmp]
        # Enter encoding nightmare
        if str(type(word)) == "<type 'unicode'>":
            word = word.encode("utf8").lower()
        # try:
        #    word = word.decode("utf8").lower()
        # except:
        #    pass

        scores = []  # Score for each possible split position
        # Iterate through characters, start at forth character, go to 3rd last
        for n in range(3, len(word) - 2):
            # Cut of Fugen-S
            if (
                pre_slice.endswith("ts")
                or pre_slice.endswith("gs")
                or pre_slice.endswith("ks")
                or pre_slice.endswith("hls")
                or pre_slice.endswith("ns")
            ) and len(word[: n - 1]) > 2:

                pre_slice = word[: n - 1]
            else:
                pre_slice = word[:n]

            # Start, in, and end probabilities
            pre_slice_prob = []
            in_slice_prob = []
            start_slice_prob = []
            # Extract all ngrams
            for k in range(len(word) + 1, 2, -1):
                # Probability of first compound, given by its ending prob
                if pre_slice_prob == [] and k <= len(pre_slice):
                    end_ngram = pre_slice[-k:]  # Look backwards
                    # Punish unlikely pre_slice end_ngram
                    pre_slice_prob.append(
                        NGRAM_PROBS["suffix"].get(end_ngram, -1)
                    )
                # Probability of ngram in word, if high, split unlikely
                in_ngram = word[n: n + k]
                # Favor ngrams not occuring within words
                in_slice_prob.append(NGRAM_PROBS["infix"].get(in_ngram, 1))

                # Probability of word starting
                if start_slice_prob == []:
                    ngram = word[n: n + k]
                    # Cut Fugen-S
                    if (
                        ngram.endswith("ts")
                        or ngram.endswith("gs")
                        or ngram.endswith("ks")
                        or ngram.endswith("hls")
                        or ngram.endswith("ns")
                    ) and len(ngram[:-1]) > 2:

                        ngram = ngram[:-1]

                    start_slice_prob.append(
                        NGRAM_PROBS["prefix"].get(ngram, -1)
                    )

            if pre_slice_prob == [] or start_slice_prob == []:
                continue

            start_slice_prob = max(start_slice_prob)
            # Highest, best preslice
            pre_slice_prob = max(pre_slice_prob)
            # Lowest, punish splitting of good ingrams
            in_slice_prob = min(in_slice_prob)
            score = start_slice_prob - in_slice_prob + pre_slice_prob
            scores.append([score, word[:n].title(), word[n:].title()])

        scores.sort(reverse=True)
        if scores == []:
            scores = [[0.0, word.title(), word.title()]]

        return sorted(scores, reverse=True)
